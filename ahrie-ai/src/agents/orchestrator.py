"""Orchestrator Agent that coordinates all other agents for optimal responses."""

from typing import Dict, Any, List, Optional
from agno.agent import Agent, RunResponse
from agno.models.langdb import LangDB
import logging
from datetime import datetime
import os

from src.utils.config import settings
from src.tools.agent_tools import (
    coordinator_tool,
    medical_expert_tool,
    review_analyst_tool,
    cultural_advisor_tool,
    find_clinics_tool
)

logger = logging.getLogger(__name__)

# Initialize LangDB tracing
try:
    from pylangdb.agno import init
    init()
except ImportError:
    logger.warning("pylangdb not installed, tracing will not be available")


class OrchestratorAgent:
    """
    Meta-agent that analyzes queries and orchestrates other specialized agents.
    
    This agent acts as the main conductor, determining which agents to use
    and how to combine their responses for the best possible answer.
    """
    
    def __init__(self, agents: Dict[str, Any]):
        """
        Initialize the orchestrator with access to all specialized agents.
        
        Args:
            agents: Dictionary of initialized specialized agents
        """
        self.name = "Orchestrator"
        self.agents = agents
        
        # Get API keys from settings
        self.langdb_api_key = getattr(settings, 'LANGDB_API_KEY', None) or os.getenv('LANGDB_API_KEY')
        self.langdb_project_id = getattr(settings, 'LANGDB_PROJECT_ID', None) or os.getenv('LANGDB_PROJECT_ID')
        
        if not self.langdb_api_key or not self.langdb_project_id:
            logger.error("LANGDB_API_KEY or LANGDB_PROJECT_ID not found")
            raise ValueError("LANGDB_API_KEY and LANGDB_PROJECT_ID must be set")
        
        # LangDB configuration
        self.model = "gpt-4o-mini"  # Using direct OpenAI model via LangDB
        
        # Initialize the Agno agent with tools
        self.agent = Agent(
            name=self.name,
            model=LangDB(
                id=self.model,
                api_key=self.langdb_api_key,
                project_id=self.langdb_project_id
            ),
            description="You are an intelligent orchestrator for K-Beauty medical tourism assistance",
            instructions=[
                "You are the master orchestrator for K-Beauty medical tourism inquiries.",
                "Analyze each query to understand the user's intent and needs.",
                "You have access to specialized tools - use them wisely:",
                "- general_conversation: For general chat and basic K-Beauty info",
                "- medical_consultation: For procedures, clinics, doctors, medical advice", 
                "- review_analysis: For patient experiences and YouTube reviews",
                "- cultural_guidance: For halal, prayer, and cultural considerations",
                "- find_clinics: For finding specific clinics based on criteria",
                "You can use multiple tools for complex queries.",
                "Always provide comprehensive, helpful responses.",
                "Be culturally sensitive to Middle Eastern clients.",
                "If a query spans multiple domains, use all relevant tools.",
                "Synthesize information from multiple sources when needed."
            ],
            tools=[
                coordinator_tool,
                medical_expert_tool,
                review_analyst_tool,
                cultural_advisor_tool,
                find_clinics_tool
            ],
            session_state={
                "coordinator_agent": agents.get("coordinator"),
                "medical_agent": agents.get("medical_expert"),
                "review_agent": agents.get("review_analyst"),
                "cultural_agent": agents.get("cultural_advisor")
            },
            markdown=True,
            show_tool_calls=True
        )
        
        self.conversation_history: List[Dict[str, Any]] = []
        
    async def process(self, message: str) -> Dict[str, Any]:
        """
        Process user message using orchestrated agent approach.
        
        Args:
            message: User's message
            
        Returns:
            Orchestrated response
        """
        try:
            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Run the orchestrator agent
            response = await self.agent.arun(message)
            
            # Extract and format the response
            response_content = response.content if hasattr(response, 'content') else str(response)
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_content,
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "content": response_content,
                "metadata": {
                    "agent": self.name,
                    "timestamp": datetime.now().isoformat(),
                    "tools_used": self._extract_tools_used(response),
                    "response_type": "orchestrated"
                }
            }
            
        except Exception as e:
            logger.error(f"Error in orchestrator agent: {str(e)}")
            return {
                "content": "I apologize, but I encountered an error processing your request. Please try again.",
                "metadata": {
                    "agent": self.name,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            }
    
    def _extract_tools_used(self, response: RunResponse) -> List[str]:
        """
        Extract which tools were used in the response.
        
        Args:
            response: Agent's run response
            
        Returns:
            List of tool names used
        """
        # This would extract tool usage from the response
        # For now, returning empty list
        return []
    
    def run(self, message: str) -> RunResponse:
        """
        Run the orchestrator synchronously.
        
        Args:
            message: User's query
            
        Returns:
            Orchestrated response
        """
        return self.agent.run(message)
    
    async def arun(self, message: str) -> RunResponse:
        """
        Run the orchestrator asynchronously.
        
        Args:
            message: User's query
            
        Returns:
            Orchestrated response
        """
        return await self.agent.arun(message)
    
    def get_conversation_summary(self) -> str:
        """
        Get a summary of the conversation history.
        
        Returns:
            Conversation summary
        """
        if not self.conversation_history:
            return "No conversation history yet."
            
        summary = "Conversation Summary:\n\n"
        for i, entry in enumerate(self.conversation_history[-10:], 1):  # Last 10 entries
            role = entry["role"].capitalize()
            content = entry["content"][:100] + "..." if len(entry["content"]) > 100 else entry["content"]
            summary += f"{i}. {role}: {content}\n"
            
        return summary