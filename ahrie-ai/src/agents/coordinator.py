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
        
        # Ensure OPENAI_API_KEY is set
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            logger.error("OPENAI_API_KEY not found in settings")
            raise ValueError("OPENAI_API_KEY must be set in environment variables")
        
        # Set the API key for OpenAI in environment
        os.environ["OPENAI_API_KEY"] = api_key
        
        self.agent = Agent(
            name=name,
            model=OpenAIChat(id="gpt-4o-mini"),
            description="You are the main coordinator for K-Beauty medical tourism assistance. Analyze user queries and route them appropriately.",
            instructions=[
                "You are the main coordinator for K-Beauty medical tourism assistance.",
                "Analyze user queries and determine which specialized agent to consult.",
                "Route medical questions to medical expert, reviews to review analyst, and cultural questions to cultural advisor.",
                "Provide helpful, accurate information for Middle Eastern clients seeking K-Beauty treatments in Korea."
            ],
            tools=[DuckDuckGoTools()],
            markdown=True,
            show_tool_calls=True
        )
        self.conversation_history: List[Dict[str, Any]] = []
        
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
                "content": "I apologize, but I encountered an error processing your request. Please try again.",
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
            return "I'm sorry, I couldn't process your request. Please try again."
        
        # Check if there's any data in the response
        data = result.get("data", {})
        if not data:
            # If no specific agent was triggered, use the general Agno agent response
            return "I understand you're looking for information about K-Beauty medical tourism. How can I help you today? You can ask me about:\n\n• Medical procedures (rhinoplasty, facial contouring, etc.)\n• Clinic recommendations\n• Halal restaurants and prayer facilities\n• Patient reviews and experiences\n\nPlease feel free to ask your question!"
        
        # Format responses from different agents
        responses = []
        
        if "medical" in data:
            responses.append("🏥 **Medical Information:**\n" + self._format_medical_data(data["medical"]))
        
        if "reviews" in data:
            responses.append("📹 **Reviews & Experiences:**\n" + self._format_review_data(data["reviews"]))
        
        if "cultural" in data:
            responses.append("🕌 **Cultural Guidance:**\n" + self._format_cultural_data(data["cultural"]))
        
        return "\n\n".join(responses) if responses else "How can I assist you with your K-Beauty medical tourism journey?"
    
    def _format_medical_data(self, data: Dict[str, Any]) -> str:
        """Format medical expert response."""
        return str(data.get("content", "Medical information will be provided here."))
    
    def _format_review_data(self, data: Dict[str, Any]) -> str:
        """Format review analyst response."""
        return str(data.get("content", "Review analysis will be shown here."))
    
    def _format_cultural_data(self, data: Dict[str, Any]) -> str:
        """Format cultural advisor response."""
        return str(data.get("content", "Cultural guidance will be provided here."))