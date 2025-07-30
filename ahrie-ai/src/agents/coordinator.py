"""Main Coordinator Agent that orchestrates other agents and manages conversations."""

from typing import Dict, List, Optional, Any
from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
import logging
from datetime import datetime
import os
from src.utils.config import settings

logger = logging.getLogger(__name__)


class CoordinatorAgent:
    """
    Main coordinator agent that manages user interactions and delegates tasks to specialized agents.
    
    This agent serves as the primary interface for user conversations, analyzing queries
    and routing them to appropriate specialized agents based on the request type.
    """
    
    def __init__(self, name: str = "Coordinator"):
        self.name = name
        
        # Get OpenRouter API key from settings or environment
        self.openrouter_api_key = getattr(settings, 'OPENROUTER_API_KEY', None) or os.getenv('OPENROUTER_API_KEY')
        if not self.openrouter_api_key:
            logger.error("OPENROUTER_API_KEY not found in settings or environment")
            raise ValueError("OPENROUTER_API_KEY must be set in environment variables")
        
        # OpenRouter 설정
        self.openrouter_base_url = "https://openrouter.ai/api/v1"
        self.model = "google/gemini-pro-1.5"
        
        # Store original environment variables to restore later
        self._original_openai_key = os.environ.get("OPENAI_API_KEY")
        self._original_openai_base = os.environ.get("OPENAI_API_BASE")
        
        # Temporarily set for OpenRouter compatibility
        os.environ["OPENAI_API_KEY"] = self.openrouter_api_key
        os.environ["OPENAI_API_BASE"] = self.openrouter_base_url
        
        self.agent = Agent(
            name=name,
            model=OpenAIChat(
                id=self.model,
                api_key=self.openrouter_api_key,
                base_url=self.openrouter_base_url
            ),
            description="안녕하세요! 저는 한국 미용 의료 관광을 도와드리는 친근한 도우미예요. 여러분의 아름다운 변화 여정을 함께하게 되어 정말 기뻐요! 💝",
            instructions=[
                "안녕하세요! 저는 한국 미용 의료 관광 전문 도우미 Ahrie예요. 여러분의 이야기를 듣고 도와드리게 되어 정말 기뻐요! 😊",
                "사용자의 감정과 기대감을 이해하고 공감하며, 따뜻하고 친근한 톤으로 대화해주세요.",
                "의료 질문은 의료 전문가에게, 리뷰 관련은 리뷰 분석가에게, 문화적 질문은 문화 조언가에게 연결해드려요.",
                "중동 지역 고객님들이 한국에서 안전하고 만족스러운 K-뷰티 시술을 받으실 수 있도록 세심하게 도와드려요.",
                "항상 긍정적이고 격려하는 태도로 대화하며, 고객님의 걱정이나 불안감을 잘 들어주고 안심시켜드려요."
            ],
            tools=[DuckDuckGoTools()],
            markdown=True,
            show_tool_calls=True
        )
        self.conversation_history: List[Dict[str, Any]] = []
    
    def __del__(self):
        """Restore original environment variables when agent is destroyed."""
        if hasattr(self, '_original_openai_key'):
            if self._original_openai_key is not None:
                os.environ["OPENAI_API_KEY"] = self._original_openai_key
            else:
                os.environ.pop("OPENAI_API_KEY", None)
        
        if hasattr(self, '_original_openai_base'):
            if self._original_openai_base is not None:
                os.environ["OPENAI_API_BASE"] = self._original_openai_base
            else:
                os.environ.pop("OPENAI_API_BASE", None)
        
    async def analyze_intent(self, message: str) -> Dict[str, Any]:
        """
        Analyze user message to determine intent and required agents.
        
        Args:
            message: User's input message
            
        Returns:
            Dictionary containing intent classification and agent recommendations
        """
        intents = {
            "medical_consultation": ["procedures", "surgery", "treatment", "clinic", "doctor"],
            "review_inquiry": ["review", "experience", "youtube", "video", "testimonial"],
            "cultural_guidance": ["halal", "prayer", "islamic", "culture", "arab", "saudi", "uae"],
            "general_inquiry": ["price", "cost", "duration", "location", "booking"]
        }
        
        message_lower = message.lower()
        detected_intents = []
        
        for intent, keywords in intents.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_intents.append(intent)
                
        return {
            "intents": detected_intents if detected_intents else ["general_inquiry"],
            "requires_translation": self._detect_language(message) != "en"
        }
    
    def _detect_language(self, text: str) -> str:
        """
        Simple language detection (to be enhanced with proper library).
        
        Args:
            text: Input text
            
        Returns:
            Language code (ar, ko, en)
        """
        # Simplified detection - enhance with langdetect or similar
        if any(ord(char) >= 0x0600 and ord(char) <= 0x06FF for char in text):
            return "ar"
        elif any(ord(char) >= 0xAC00 and ord(char) <= 0xD7AF for char in text):
            return "ko"
        return "en"
    
    async def route_query(self, message: str) -> Dict[str, Any]:
        """
        Route user query to appropriate specialized agents.
        
        Args:
            message: User's query
            
        Returns:
            Aggregated response from specialized agents
        """
        intent_analysis = await self.analyze_intent(message)
        
        # If no specific intent detected, use the general agent
        if intent_analysis["intents"] == ["general_inquiry"]:
            # Use the Agno agent directly for general queries
            response = await self.arun(message)
            return {
                "status": "success",
                "data": {"general": {"content": response.content if hasattr(response, 'content') else str(response)}},
                "response_type": "general_response"
            }
        
        responses = {}
        
        for intent in intent_analysis["intents"]:
            if intent == "medical_consultation":
                # In real implementation, would call medical_expert agent
                responses["medical"] = {"status": "would_route_to_medical_expert"}
            elif intent == "review_inquiry":
                # In real implementation, would call review_analyst agent
                responses["reviews"] = {"status": "would_route_to_review_analyst"}
            elif intent == "cultural_guidance":
                # In real implementation, would call cultural_advisor agent
                responses["cultural"] = {"status": "would_route_to_cultural_advisor"}
                
        return self._aggregate_responses(responses)
    
    def _aggregate_responses(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate and format responses from multiple agents.
        
        Args:
            responses: Dictionary of responses from different agents
            
        Returns:
            Formatted aggregated response
        """
        return {
            "status": "success",
            "data": responses,
            "response_type": "multi_agent" if len(responses) > 1 else "single_agent"
        }
    
    async def process(self, message: str) -> Dict[str, Any]:
        """
        Main processing method for coordinator agent.
        
        Args:
            message: Incoming message
            
        Returns:
            Processed response
        """
        try:
            self.conversation_history.append({"role": "user", "content": message})
            
            # Route the query to appropriate agents
            result = await self.route_query(message)
            
            # Format the response
            response_content = self._format_response(result)
            
            return {
                "content": response_content,
                "metadata": {
                    "agent": self.name,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in coordinator agent: {str(e)}")
            return {
                "content": "앗, 죄송해요! 😔 잠시 문제가 생겼어요. 조금만 기다려주시면 다시 도와드릴게요. 여러분의 소중한 질문을 놓치고 싶지 않아요!",
                "metadata": {"error": str(e)}
            }
    
    def run(self, message: str) -> RunResponse:
        """
        Run the agent synchronously using Agno's run method.
        
        Args:
            message: User's query
            
        Returns:
            Agent's response
        """
        return self.agent.run(message)
    
    async def arun(self, message: str) -> RunResponse:
        """
        Run the agent asynchronously.
        
        Args:
            message: User's query
            
        Returns:
            Agent's response
        """
        return await self.agent.arun(message)
    
    def _format_response(self, result: Dict[str, Any]) -> str:
        """
        Format the aggregated result into a user-friendly response.
        
        Args:
            result: Aggregated result from agents
            
        Returns:
            Formatted response string
        """
        if not result or not isinstance(result, dict):
            return "어머, 죄송해요! 😢 제가 잠시 헷갈렸나봐요. 다시 한 번 말씀해주시면 더 잘 도와드릴게요!"
        
        # Check if there's any data in the response
        data = result.get("data", {})
        if not data:
            # If no specific agent was triggered, use the general Agno agent response
            return """안녕하세요! K-뷰티 의료 관광에 관심을 가져주셔서 정말 감사해요! 💕

여러분의 아름다운 변화를 위한 여정을 도와드릴 수 있어서 기뻐요. 어떤 것이든 편하게 물어보세요!

제가 도와드릴 수 있는 것들이에요:
• 🏥 의료 시술 정보 (코성형, 안면윤곽, 가슴성형 등)
• 👩‍⚕️ 믿을 수 있는 클리닉과 의사 추천
• 🕌 할랄 레스토랑과 기도실 정보
• ⭐ 실제 환자분들의 리뷰와 경험담
• 💰 가격 정보와 여행 팁

어떤 것부터 도와드릴까요? 여러분의 이야기를 들려주세요! 😊"""
        
        # Format responses from different agents
        responses = []
        
        if "medical" in data:
            responses.append("🏥 **Medical Information:**\n" + self._format_medical_data(data["medical"]))
        
        if "reviews" in data:
            responses.append("📹 **Reviews & Experiences:**\n" + self._format_review_data(data["reviews"]))
        
        if "cultural" in data:
            responses.append("🕌 **Cultural Guidance:**\n" + self._format_cultural_data(data["cultural"]))
        
        return "\n\n".join(responses) if responses else "여러분의 K-뷰티 여정을 어떻게 도와드릴까요? 무엇이든 편하게 물어보세요! 💖"
    
    def _format_medical_data(self, data: Dict[str, Any]) -> str:
        """Format medical expert response."""
        return str(data.get("content", "의료 정보를 준비하고 있어요! 곧 자세한 내용을 알려드릴게요. 😊"))
    
    def _format_review_data(self, data: Dict[str, Any]) -> str:
        """Format review analyst response."""
        return str(data.get("content", "다른 분들의 경험담을 찾아보고 있어요! 실제 후기들을 곧 보여드릴게요. ⭐"))
    
    def _format_cultural_data(self, data: Dict[str, Any]) -> str:
        """Format cultural advisor response."""
        return str(data.get("content", "문화적인 정보를 준비하고 있어요! 편안한 한국 여행이 되도록 도와드릴게요. 🕌"))