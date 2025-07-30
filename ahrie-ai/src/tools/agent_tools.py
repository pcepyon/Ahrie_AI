"""Agent tools for orchestration - wrapping agents as callable tools."""

from typing import Dict, Any, Optional
from agno.tools import tool
import logging

logger = logging.getLogger(__name__)


@tool(
    name="general_conversation",
    description="Handle general K-Beauty tourism conversation and provide basic information"
)
async def coordinator_tool(agent: Any, query: str) -> str:
    """
    Use the coordinator agent for general conversation management.
    
    Args:
        agent: The agent instance (injected by tool decorator)
        query: User's query
        
    Returns:
        Coordinator's response
    """
    try:
        coordinator = agent.session_state.get("coordinator_agent")
        if not coordinator:
            return "Coordinator agent not available"
            
        response = await coordinator.arun(query)
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        logger.error(f"Error in coordinator tool: {str(e)}")
        return f"Error processing general query: {str(e)}"


@tool(
    name="medical_consultation", 
    description="Consult medical expert for K-Beauty procedures, clinics, doctors, and medical advice"
)
async def medical_expert_tool(agent: Any, query: str, procedure: Optional[str] = None) -> str:
    """
    Consult the medical expert agent for procedure and clinic information.
    
    Args:
        agent: The agent instance (injected by tool decorator)
        query: Medical-related query
        procedure: Optional specific procedure name
        
    Returns:
        Medical expert's response
    """
    try:
        medical_agent = agent.session_state.get("medical_agent")
        if not medical_agent:
            return "Medical expert agent not available"
        
        # If specific procedure is mentioned, get detailed info
        if procedure:
            procedure_info = await medical_agent.get_procedure_info(procedure)
            return str(procedure_info)
        else:
            response = await medical_agent.arun(query)
            return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        logger.error(f"Error in medical expert tool: {str(e)}")
        return f"Error consulting medical expert: {str(e)}"


@tool(
    name="review_analysis",
    description="Analyze YouTube reviews and patient experiences for K-Beauty procedures"
)
async def review_analyst_tool(agent: Any, query: str, procedure: Optional[str] = None, num_reviews: int = 5) -> str:
    """
    Analyze reviews and patient experiences using the review analyst agent.
    
    Args:
        agent: The agent instance (injected by tool decorator)
        query: Review-related query
        procedure: Optional specific procedure to analyze
        num_reviews: Number of reviews to analyze
        
    Returns:
        Review analysis results
    """
    try:
        review_agent = agent.session_state.get("review_agent")
        if not review_agent:
            return "Review analyst agent not available"
            
        if procedure:
            # Get aggregated insights for specific procedure
            insights = await review_agent.aggregate_review_insights(procedure, num_reviews)
            return f"Review Analysis for {procedure}:\n{str(insights)}"
        else:
            response = await review_agent.arun(query)
            return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        logger.error(f"Error in review analyst tool: {str(e)}")
        return f"Error analyzing reviews: {str(e)}"


@tool(
    name="cultural_guidance",
    description="Provide Islamic/Halal guidance, prayer facilities info, and cultural advice for Middle Eastern visitors"
)
async def cultural_advisor_tool(agent: Any, query: str, location: str = "Gangnam") -> str:
    """
    Get cultural and religious guidance from the cultural advisor agent.
    
    Args:
        agent: The agent instance (injected by tool decorator)
        query: Cultural/religious query
        location: Location in Seoul (default: Gangnam)
        
    Returns:
        Cultural advisor's response
    """
    try:
        cultural_agent = agent.session_state.get("cultural_agent")
        if not cultural_agent:
            return "Cultural advisor agent not available"
            
        # Check for specific cultural needs
        query_lower = query.lower()
        
        if "halal" in query_lower and "food" in query_lower:
            restaurants = await cultural_agent.find_halal_restaurants(location)
            return f"Halal restaurants in {location}:\n{str(restaurants)}"
        elif "pray" in query_lower or "mosque" in query_lower:
            prayer_info = await cultural_agent.get_prayer_facilities(location)
            return f"Prayer facilities in {location}:\n{str(prayer_info)}"
        elif "ramadan" in query_lower:
            ramadan_info = await cultural_agent.ramadan_guidance()
            return f"Ramadan guidance:\n{str(ramadan_info)}"
        else:
            response = await cultural_agent.arun(query)
            return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        logger.error(f"Error in cultural advisor tool: {str(e)}")
        return f"Error getting cultural guidance: {str(e)}"


@tool(
    name="find_clinics",
    description="Find suitable K-Beauty clinics based on criteria like procedure, location, and cultural needs"
)
async def find_clinics_tool(agent: Any, criteria: Dict[str, Any]) -> str:
    """
    Find suitable clinics based on specific criteria.
    
    Args:
        agent: The agent instance (injected by tool decorator)
        criteria: Dictionary with search criteria (procedure, budget, halal_friendly, etc.)
        
    Returns:
        List of suitable clinics
    """
    try:
        medical_agent = agent.session_state.get("medical_agent")
        if not medical_agent:
            return "Medical expert agent not available"
            
        clinics = await medical_agent.find_suitable_clinics(criteria)
        return f"Found {len(clinics)} suitable clinics:\n{str(clinics)}"
    except Exception as e:
        logger.error(f"Error finding clinics: {str(e)}")
        return f"Error finding clinics: {str(e)}"