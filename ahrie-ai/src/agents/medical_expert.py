"""Medical Expert Agent specialized in K-Beauty medical procedures and consultations."""

from typing import Dict, List, Optional, Any
from agno.agent import Agent, RunResponse
from agno.models.langdb import LangDB
from agno.tools.duckduckgo import DuckDuckGoTools
import logging
from datetime import datetime
import os
from src.utils.config import settings

logger = logging.getLogger(__name__)

# Initialize LangDB tracing
try:
    from pylangdb.agno import init
    init()
except ImportError:
    logger.warning("pylangdb not installed, tracing will not be available")


class MedicalExpertAgent:
    """
    Medical expert agent specialized in Korean beauty medical procedures.
    
    Provides information about procedures, clinics, doctors, and medical considerations
    for Middle Eastern clients seeking K-Beauty treatments.
    """
    
    def __init__(self, name: str = "MedicalExpert"):
        self.name = name
        
        # Get API keys from settings
        self.langdb_api_key = getattr(settings, 'LANGDB_API_KEY', None) or os.getenv('LANGDB_API_KEY')
        self.langdb_project_id = getattr(settings, 'LANGDB_PROJECT_ID', None) or os.getenv('LANGDB_PROJECT_ID')
        
        if not self.langdb_api_key or not self.langdb_project_id:
            logger.error("LANGDB_API_KEY or LANGDB_PROJECT_ID not found")
            raise ValueError("LANGDB_API_KEY and LANGDB_PROJECT_ID must be set")
        
        # LangDB configuration
        self.model = "gpt-4o-mini"  # Using direct OpenAI model via LangDB
        
        self.agent = Agent(
            name=name,
            model=LangDB(
                id=self.model,
                api_key=self.langdb_api_key,
                project_id=self.langdb_project_id
            ),
            description="Medical expert specializing in K-Beauty procedures and treatments.",
            instructions=[
                "You are a medical expert specializing in K-Beauty procedures.",
                "Provide accurate, helpful information about medical procedures, clinics, and recovery.",
                "Consider cultural sensitivities for Middle Eastern clients.",
                "Always include medical disclaimers when giving advice.",
                "Mention halal-friendly options and female doctors when relevant."
            ],
            tools=[DuckDuckGoTools()],
            markdown=True,
            show_tool_calls=True
        )
        self.procedures_knowledge = self._load_procedures_knowledge()
        
    def _load_procedures_knowledge(self) -> Dict[str, Any]:
        """
        Load medical procedures knowledge base.
        
        Returns:
            Dictionary of procedure information
        """
        return {
            "rhinoplasty": {
                "duration": "1-2 hours",
                "recovery": "7-14 days",
                "popular_clinics": ["Banobagi", "JK Plastic Surgery", "ID Hospital"],
                "price_range": "3,000-8,000 USD"
            },
            "double_eyelid": {
                "duration": "30-60 minutes",
                "recovery": "5-7 days",
                "popular_clinics": ["Dream Medical Group", "Wonjin", "Grand Plastic Surgery"],
                "price_range": "1,500-3,000 USD"
            },
            "facial_contouring": {
                "duration": "2-4 hours",
                "recovery": "2-3 weeks",
                "popular_clinics": ["View Plastic Surgery", "EU Oral & Maxillofacial Surgery", "THE PLUS"],
                "price_range": "7,000-15,000 USD"
            }
        }
    
    async def get_procedure_info(self, procedure_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific procedure.
        
        Args:
            procedure_name: Name of the medical procedure
            
        Returns:
            Detailed procedure information
        """
        procedure_key = procedure_name.lower().replace(" ", "_")
        
        if procedure_key in self.procedures_knowledge:
            info = self.procedures_knowledge[procedure_key]
            return {
                "procedure": procedure_name,
                "details": info,
                "recommendations": self._get_procedure_recommendations(procedure_key)
            }
        
        return {
            "error": f"Procedure '{procedure_name}' not found in knowledge base",
            "suggestions": list(self.procedures_knowledge.keys())
        }
    
    def _get_procedure_recommendations(self, procedure: str) -> List[str]:
        """
        Get personalized recommendations for a procedure.
        
        Args:
            procedure: Procedure identifier
            
        Returns:
            List of recommendations
        """
        general_recommendations = [
            "Consult with multiple clinics before deciding",
            "Check surgeon credentials and certifications",
            "Review before/after photos of previous patients",
            "Consider recovery time in your travel plans",
            "Arrange for a translator if needed"
        ]
        
        # Add procedure-specific recommendations
        if procedure == "facial_contouring":
            general_recommendations.append("This is a major surgery - ensure adequate recovery time")
        elif procedure == "rhinoplasty":
            general_recommendations.append("Discuss your aesthetic preferences clearly with the surgeon")
            
        return general_recommendations
    
    async def find_suitable_clinics(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find suitable clinics based on patient criteria.
        
        Args:
            criteria: Dictionary containing search criteria (procedure, budget, location, etc.)
            
        Returns:
            List of suitable clinics with details
        """
        # This would integrate with actual clinic database
        # For now, returning mock data
        return [
            {
                "name": "Banobagi Plastic Surgery",
                "location": "Gangnam, Seoul",
                "specialties": ["Rhinoplasty", "Facial Contouring"],
                "halal_friendly": True,
                "arabic_support": True,
                "rating": 4.8
            },
            {
                "name": "ID Hospital",
                "location": "Gangnam, Seoul",
                "specialties": ["All procedures"],
                "halal_friendly": True,
                "arabic_support": False,
                "rating": 4.7
            }
        ]
    
    async def medical_consultation(self, query: str, patient_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Provide medical consultation based on patient query.
        
        Args:
            query: Medical question or concern
            patient_info: Optional patient information for personalized advice
            
        Returns:
            Medical consultation response
        """
        # Analyze query for medical terms
        medical_terms = self._extract_medical_terms(query)
        
        response = {
            "consultation_date": datetime.now().isoformat(),
            "query": query,
            "medical_terms_identified": medical_terms,
            "advice": self._generate_medical_advice(query, medical_terms),
            "disclaimer": "This is general information only. Please consult with a qualified medical professional for personalized advice."
        }
        
        if patient_info:
            response["personalized_considerations"] = self._get_personalized_considerations(patient_info)
            
        return response
    
    def _extract_medical_terms(self, text: str) -> List[str]:
        """
        Extract medical terms from text.
        
        Args:
            text: Input text
            
        Returns:
            List of identified medical terms
        """
        medical_keywords = [
            "surgery", "procedure", "anesthesia", "recovery", "swelling",
            "pain", "medication", "doctor", "clinic", "treatment"
        ]
        
        found_terms = []
        text_lower = text.lower()
        
        for term in medical_keywords:
            if term in text_lower:
                found_terms.append(term)
                
        return found_terms
    
    def _generate_medical_advice(self, query: str, medical_terms: List[str]) -> str:
        """
        Generate medical advice based on query.
        
        Args:
            query: User's medical query
            medical_terms: Identified medical terms
            
        Returns:
            Medical advice string
        """
        # This would use more sophisticated NLP in production
        if "recovery" in medical_terms:
            return "Recovery times vary by procedure and individual. Follow your surgeon's post-operative instructions carefully."
        elif "pain" in medical_terms:
            return "Pain management is an important part of recovery. Your surgeon will prescribe appropriate medication."
        else:
            return "Please provide more specific details about your medical concern for better guidance."
    
    def _get_personalized_considerations(self, patient_info: Dict[str, Any]) -> List[str]:
        """
        Get personalized medical considerations.
        
        Args:
            patient_info: Patient information
            
        Returns:
            List of personalized considerations
        """
        considerations = []
        
        if patient_info.get("age", 0) > 50:
            considerations.append("Additional medical tests may be required due to age")
        
        if patient_info.get("medical_conditions"):
            considerations.append("Existing medical conditions must be discussed with surgeon")
            
        if patient_info.get("medications"):
            considerations.append("Current medications may need to be adjusted before surgery")
            
        return considerations
    
    def run(self, message: str) -> RunResponse:
        """
        Run the medical expert agent synchronously.
        
        Args:
            message: User's medical query
            
        Returns:
            Agent's response
        """
        # Enhance the query with medical context
        enhanced_query = f"As a medical expert for K-Beauty procedures, please help with: {message}"
        return self.agent.run(enhanced_query)
    
    async def arun(self, message: str) -> RunResponse:
        """
        Run the medical expert agent asynchronously.
        
        Args:
            message: User's medical query
            
        Returns:
            Agent's response
        """
        # Enhance the query with medical context
        enhanced_query = f"As a medical expert for K-Beauty procedures, please help with: {message}"
        return await self.agent.arun(enhanced_query)
    
    async def process(self, message: str) -> Dict[str, Any]:
        """
        Process medical-related queries.
        
        Args:
            message: Incoming message
            
        Returns:
            Medical expert response
        """
        try:
            content = message
            
            # Determine the type of medical query
            if "procedure" in content.lower():
                # Get procedure information
                procedure_name = self._extract_procedure_name(content)
                result = await self.get_procedure_info(procedure_name)
            elif "clinic" in content.lower():
                # Find suitable clinics
                criteria = self._extract_clinic_criteria(content)
                result = await self.find_suitable_clinics(criteria)
            else:
                # General medical consultation
                result = await self.medical_consultation(content)
            
            return {
                "content": self._format_medical_response(result),
                "metadata": {
                    "agent": self.name,
                    "response_type": "medical_consultation",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in medical expert agent: {str(e)}")
            return {
                "content": "I apologize, but I couldn't process your medical query. Please try rephrasing.",
                "metadata": {"error": str(e)}
            }
    
    def _extract_procedure_name(self, text: str) -> str:
        """Extract procedure name from text."""
        # Simple extraction - enhance with NLP
        for procedure in self.procedures_knowledge.keys():
            if procedure.replace("_", " ") in text.lower():
                return procedure.replace("_", " ")
        return "general"
    
    def _extract_clinic_criteria(self, text: str) -> Dict[str, Any]:
        """Extract clinic search criteria from text."""
        return {
            "location": "Seoul",  # Default
            "halal_required": "halal" in text.lower(),
            "arabic_support": "arabic" in text.lower() or "عربي" in text
        }
    
    def _format_medical_response(self, result: Dict[str, Any]) -> str:
        """Format medical response for user display."""
        # Implement proper formatting based on result type
        return str(result)  # Placeholder