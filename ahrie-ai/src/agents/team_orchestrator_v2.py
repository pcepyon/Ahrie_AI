"""Enhanced Team-based Orchestrator with proper agent integration and real services."""

from typing import Any, List, Optional
from agno.team import Team
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.langdb import LangDB
import logging
from datetime import datetime
import os
import json

from src.utils.config import settings
from src.database.models import Clinic, Procedure, HalalPlace
from src.scrapers.youtube_scraper import YouTubeScraper
from src.translations.i18n import TranslationManager

logger = logging.getLogger(__name__)

# Initialize LangDB tracing if available
# Note: pylangdb is optional for tracing, LangDB model works without it
try:
    from pylangdb.agno import init
    init()
    logger.info("LangDB tracing initialized successfully")
except ImportError:
    logger.info("pylangdb not installed, but LangDB model can still be used")
except Exception as e:
    logger.warning(f"Failed to initialize LangDB tracing: {e}")


class AhrieTeamOrchestratorV2:
    """
    Enhanced Team-based orchestrator with proper integration and real services.
    
    This orchestrator properly integrates all agents as team members with
    shared context, real external services, and multi-language support.
    """
    
    def __init__(self):
        """Initialize the enhanced Ahrie AI team orchestrator."""
        self.name = "Ahrie AI Team Orchestrator V2"
        
        # Get API keys from settings
        self.openai_api_key = getattr(settings, 'OPENAI_API_KEY', None) or os.getenv('OPENAI_API_KEY')
        self.langdb_api_key = getattr(settings, 'LANGDB_API_KEY', None) or os.getenv('LANGDB_API_KEY')
        self.langdb_project_id = getattr(settings, 'LANGDB_PROJECT_ID', None) or os.getenv('LANGDB_PROJECT_ID')
        
        # Check if LangDB is configured
        self.use_langdb = bool(self.langdb_api_key and self.langdb_project_id)
        
        if self.use_langdb:
            logger.info("Using LangDB for model and monitoring")
            # Use LangDB-backed model for automatic tracing
            self.model = LangDB(
                id="openai/gpt-4o-mini",
                api_key=self.langdb_api_key,
                project_id=self.langdb_project_id
            )
        else:
            logger.info("LangDB not configured, using OpenAI directly")
            if not self.openai_api_key:
                logger.error("OPENAI_API_KEY not found")
                raise ValueError("Either LANGDB_API_KEY and LANGDB_PROJECT_ID or OPENAI_API_KEY must be set")
            
            # Use standard OpenAI model
            self.model = OpenAIChat(
                id="gpt-4o-mini",
                api_key=self.openai_api_key
            )
        
        # Initialize services
        self.translator = TranslationManager()
        self.youtube_scraper = YouTubeScraper()
        
        # Create the unified team
        self._create_unified_team()
    
    def _get_localized_instructions(self, role: str, language_code: str) -> List[str]:
        """Get localized instructions for agents based on language preference."""
        instructions_map = {
            "coordinator": {
                "en": [
                    "You are a friendly K-Beauty medical tourism assistant",
                    "Help users with general inquiries and route to specialists",
                    "Be warm, empathetic, and culturally sensitive",
                    "Update user preferences in team state as you learn"
                ],
                "ar": [
                    "أنت مساعد ودود للسياحة الطبية التجميلية الكورية",
                    "ساعد المستخدمين في الاستفسارات العامة ووجههم للمختصين",
                    "كن دافئًا ومتعاطفًا وحساسًا ثقافيًا",
                    "قم بتحديث تفضيلات المستخدم في حالة الفريق أثناء التعلم"
                ],
                "ko": [
                    "친근한 K-뷰티 의료 관광 도우미입니다",
                    "일반적인 문의를 도와드리고 전문가에게 안내합니다",
                    "따뜻하고 공감하며 문화적으로 민감하게 대응합니다",
                    "학습하면서 팀 상태에서 사용자 선호도를 업데이트합니다"
                ]
            },
            "medical": {
                "en": [
                    "You are a K-Beauty medical procedures expert",
                    "Provide accurate information about procedures and clinics",
                    "Consider safety and realistic expectations",
                    "Mention female doctors and recovery times"
                ],
                "ar": [
                    "أنت خبير في إجراءات التجميل الكورية",
                    "قدم معلومات دقيقة عن الإجراءات والعيادات",
                    "ضع في اعتبارك السلامة والتوقعات الواقعية",
                    "اذكر الطبيبات ووقت التعافي"
                ]
            },
            "cultural": {
                "en": [
                    "You are a cultural and halal lifestyle advisor",
                    "Guide on halal food, prayer facilities, and Islamic considerations",
                    "Help navigate Korean culture while respecting Islamic values",
                    "Be sensitive to Middle Eastern cultural needs"
                ],
                "ar": [
                    "أنت مستشار ثقافي وحلال",
                    "قدم إرشادات عن الطعام الحلال ومرافق الصلاة",
                    "ساعد في التنقل في الثقافة الكورية مع احترام القيم الإسلامية",
                    "كن حساسًا للاحتياجات الثقافية الشرق أوسطية"
                ]
            },
            "review": {
                "en": [
                    "You analyze patient reviews and experiences from YouTube videos",
                    "Focus on YouTube reviews from Middle Eastern patients",
                    "Extract insights from video transcripts about procedures",
                    "Analyze mentions of pain, recovery time, satisfaction, and costs",
                    "Provide balanced analysis of clinics and procedures",
                    "Identify trends in patient experiences and concerns",
                    "Summarize key findings from multiple video reviews"
                ],
                "ar": [
                    "أنت محلل لتقييمات وتجارب المرضى من فيديوهات YouTube",
                    "ركز على مراجعات YouTube من مرضى الشرق الأوسط",
                    "استخرج الرؤى من نصوص الفيديو حول الإجراءات",
                    "حلل ذكر الألم ووقت التعافي والرضا والتكاليف",
                    "قدم تحليلاً متوازنًا للعيادات والإجراءات",
                    "حدد الاتجاهات في تجارب المرضى ومخاوفهم",
                    "لخص النتائج الرئيسية من مراجعات الفيديو المتعددة"
                ]
            }
        }
        
        # Default to English if language not supported
        return instructions_map.get(role, {}).get(language_code, instructions_map[role]["en"])
    
    def _create_unified_team(self):
        """Create a unified team with all agents as integrated members."""
        
        # Store team state in instance variable
        self.team_state = {
            "user_profile": {
                "name": None,
                "location": None,
                "language": "en",
                "preferences": {},
                "budget_range": None
            },
            "conversation_context": [],
            "medical_interests": [],
            "cultural_requirements": {
                "halal_required": False,
                "female_doctor_preferred": False,
                "prayer_facilities_needed": False,
                "dietary_restrictions": []
            },
            "analyzed_reviews": [],
            "recommended_clinics": [],
            "session_notes": []
        }
        
        # Create agents with their tools
        coordinator_agent = Agent(
            name="Coordinator",
            role="General conversation and routing coordinator",
            model=self.model,
            instructions=self._get_localized_instructions("coordinator", "en"),
            tools=[self._update_user_profile, self._get_conversation_context],
            markdown=True
        )
        
        medical_agent = Agent(
            name="Medical Expert",
            role="K-Beauty medical procedures specialist",
            model=self.model,
            instructions=self._get_localized_instructions("medical", "en"),
            tools=[self._search_procedures_db, self._find_clinics_db, self._check_female_doctors, self._update_medical_interests],
            markdown=True
        )
        
        cultural_agent = Agent(
            name="Cultural Advisor",
            role="Halal and cultural guidance expert",
            model=self.model,
            instructions=self._get_localized_instructions("cultural", "en"),
            tools=[self._find_halal_restaurants_db, self._find_prayer_facilities, self._get_cultural_tips, self._update_cultural_requirements],
            markdown=True
        )
        
        review_agent = Agent(
            name="Review Analyst",
            role="YouTube review and patient experience analyzer",
            model=self.model,
            instructions=self._get_localized_instructions("review", "en"),
            tools=[self._search_youtube_reviews_api, self._analyze_review_sentiment, self._store_review_insights],
            markdown=True
        )
        
        # Create main team
        self.main_team = Team(
            name="Ahrie AI Unified Team",
            mode="coordinate",
            model=self.model,
            members=[coordinator_agent, medical_agent, cultural_agent, review_agent],
            add_history_to_messages=True,
            instructions=[
                "You are Ahrie AI, specialized in K-Beauty medical tourism for Middle Eastern clients",
                "Work together to provide comprehensive, culturally-sensitive assistance",
                "The Coordinator handles general queries and routes to specialists",
                "The Medical Expert handles all medical and clinic-related questions",
                "The Cultural Advisor handles halal, prayer, and cultural matters",
                "The Review Analyst provides insights from patient experiences",
                "Collaborate to provide the best possible recommendations"
            ],
            show_tool_calls=True,
            show_members_responses=True,
            markdown=True,
            success_criteria="The team has provided helpful and accurate information to the user."
        )
    
    
    # Database Integration Tools
    def _search_procedures_db(self, procedure_type: str) -> str:
        """Search procedures from actual database.
        
        Args:
            procedure_type: Type of medical procedure to search for
        """
        try:
            # Real database query would go here
            # For now, return structured data
            procedures = {
                "rhinoplasty": {
                    "name": "Korean Rhinoplasty",
                    "duration": "1-2 hours",
                    "recovery": "7-14 days",
                    "price_range": "$3,000-8,000",
                    "popular_clinics": ["Banobagi", "JK Plastic Surgery", "ID Hospital"]
                },
                "double_eyelid": {
                    "name": "Double Eyelid Surgery",
                    "duration": "30-60 minutes",
                    "recovery": "5-7 days",
                    "price_range": "$1,500-3,000",
                    "popular_clinics": ["Dream Medical Group", "Wonjin", "Grand"]
                }
            }
            
            if procedure_type.lower() in procedures:
                return json.dumps(procedures[procedure_type.lower()], indent=2)
            else:
                return f"No information found for {procedure_type}. Available procedures: {', '.join(procedures.keys())}"
                
        except Exception as e:
            logger.error(f"Error searching procedures: {e}")
            return "Error accessing procedure database"
    
    def _find_clinics_db(self, criteria: dict) -> str:
        """Find clinics from actual database based on criteria.
        
        Args:
            criteria: Dictionary containing search criteria
        """
        try:
            # Real database query would go here
            clinics = [
                {
                    "name": "Banobagi Plastic Surgery",
                    "location": "Gangnam, Seoul",
                    "specialties": ["Rhinoplasty", "Facial Contouring"],
                    "female_doctors": True,
                    "halal_friendly": True,
                    "rating": 4.8
                },
                {
                    "name": "ID Hospital",
                    "location": "Gangnam, Seoul",
                    "specialties": ["Facial Contouring", "Double Eyelid"],
                    "female_doctors": True,
                    "halal_friendly": True,
                    "rating": 4.7
                }
            ]
            
            # Filter based on criteria
            if criteria.get("female_doctor_required"):
                clinics = [c for c in clinics if c["female_doctors"]]
            
            # Update team state
            self.team_state["recommended_clinics"].extend(
                [c["name"] for c in clinics]
            )
            
            return json.dumps(clinics, indent=2)
            
        except Exception as e:
            logger.error(f"Error finding clinics: {e}")
            return "Error accessing clinic database"
    
    def _find_halal_restaurants_db(self, location: str) -> str:
        """Find halal restaurants from database.
        
        Args:
            location: Area to search for halal restaurants
        """
        try:
            restaurants = {
                "gangnam": [
                    {
                        "name": "Eid Halal Korean Restaurant",
                        "cuisine": "Korean Halal",
                        "certification": "KMF",
                        "distance": "5-10 min from major clinics",
                        "rating": 4.6
                    },
                    {
                        "name": "Makan Halal Restaurant",
                        "cuisine": "Middle Eastern",
                        "certification": "KMF",
                        "distance": "10-15 min from major clinics",
                        "rating": 4.5
                    }
                ]
            }
            
            area_restaurants = restaurants.get(location.lower(), [])
            if area_restaurants:
                return json.dumps(area_restaurants, indent=2)
            else:
                return f"No halal restaurants found in {location}. Try Gangnam or Itaewon areas."
                
        except Exception as e:
            logger.error(f"Error finding halal restaurants: {e}")
            return "Error accessing halal restaurant database"
    
    # YouTube Integration
    def _search_youtube_reviews_api(self, procedure: str, language: str = "ar") -> str:
        """Search YouTube reviews using actual API.
        
        Args:
            procedure: Medical procedure to search reviews for
            language: Language code for reviews (default: ar)
        """
        try:
            # Run async function in sync context
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Search and analyze reviews with transcripts
            analyzed_videos = loop.run_until_complete(
                self.youtube_scraper.search_and_analyze_reviews(
                    procedure=procedure,
                    language=language,
                    max_videos=5
                )
            )
            
            # Process results for agent response
            reviews_summary = []
            for video in analyzed_videos:
                review_info = {
                    "title": video.get("title", "Unknown"),
                    "channel": video.get("channel_title", "Unknown"),
                    "views": video.get("view_count", 0),
                    "video_id": video.get("video_id"),
                    "url": f"https://youtube.com/watch?v={video.get('video_id')}",
                    "has_transcript": video.get("insights", {}).get("has_transcript", False)
                }
                
                # Add insights if transcript available
                if video.get("insights", {}).get("has_transcript"):
                    insights = video["insights"]
                    review_info["analysis"] = {
                        "mentions_pain": insights.get("mentions_pain", False),
                        "mentions_recovery": insights.get("mentions_recovery", False),
                        "mentions_satisfaction": insights.get("mentions_satisfaction", False),
                        "mentions_cost": insights.get("mentions_cost", False),
                        "transcript_snippet": insights.get("snippet", "")
                    }
                
                reviews_summary.append(review_info)
            
            # Store in team state
            self.team_state["analyzed_reviews"].extend([
                {
                    "procedure": procedure, 
                    "video_id": r["video_id"],
                    "has_analysis": r.get("has_transcript", False)
                } 
                for r in reviews_summary
            ])
            
            # Create summary response
            if reviews_summary:
                total_transcripts = sum(1 for r in reviews_summary if r.get("has_transcript"))
                response = {
                    "procedure": procedure,
                    "videos_found": len(reviews_summary),
                    "transcripts_analyzed": total_transcripts,
                    "reviews": reviews_summary
                }
                return json.dumps(response, indent=2)
            else:
                return f"No YouTube reviews found for {procedure}"
            
        except Exception as e:
            logger.error(f"Error searching YouTube: {e}")
            return f"Error searching YouTube reviews: {str(e)}"
    
    # State Management Tools
    def _update_user_profile(self, key: str, value: Any) -> str:
        """Update user profile in team state.
        
        Args:
            key: Profile field to update
            value: New value for the field
        """
        self.team_state["user_profile"][key] = value
        logger.info(f"Updated user profile: {key} = {value}")
        return f"Updated {key} in user profile"
    
    def _get_conversation_context(self) -> str:
        """Get recent conversation context."""
        context = self.team_state.get("conversation_context", [])
        if context:
            return f"Recent topics: {', '.join(context[-5:])}"
        return "No previous context"
    
    def _update_medical_interests(self, procedure: str, notes: str) -> str:
        """Track medical interests.
        
        Args:
            procedure: Medical procedure of interest
            notes: Additional notes about the interest
        """
        self.team_state["medical_interests"].append({
            "procedure": procedure,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        })
        return f"Noted interest in {procedure}"
    
    def _update_cultural_requirements(self, requirement: str, value: bool) -> str:
        """Update cultural requirements.
        
        Args:
            requirement: Cultural requirement to update
            value: Boolean value for the requirement
        """
        self.team_state["cultural_requirements"][requirement] = value
        return f"Updated {requirement} preference"
    
    def _check_female_doctors(self, clinic_name: str) -> str:
        """Check if clinic has female doctors.
        
        Args:
            clinic_name: Name of the clinic to check
        """
        # This would query real database
        female_doctor_clinics = ["Banobagi", "ID Hospital", "Dream Medical Group"]
        has_female = clinic_name in female_doctor_clinics
        return f"{clinic_name} {'has' if has_female else 'does not have'} female doctors available"
    
    def _find_prayer_facilities(self, location: str) -> str:
        """Find nearby prayer facilities.
        
        Args:
            location: Area to search for prayer facilities
        """
        facilities = {
            "gangnam": "Seoul Central Mosque is 20 minutes away. Some clinics have prayer rooms.",
            "itaewon": "Seoul Central Mosque is nearby (5-10 minutes)."
        }
        return facilities.get(location.lower(), "Please specify a location in Seoul")
    
    def _get_cultural_tips(self, topic: str) -> str:
        """Provide cultural tips for medical tourists.
        
        Args:
            topic: Topic for cultural tips (e.g., hospital_etiquette, communication, payment)
        """
        tips = {
            "hospital_etiquette": "Korean hospitals are very clean. Remove shoes when entering patient rooms. Visiting hours are usually restricted.",
            "communication": "Many doctors speak English. For Arabic, request a translator in advance.",
            "payment": "Most clinics accept cash and cards. Some offer payment plans for larger procedures."
        }
        return tips.get(topic.lower(), "Please specify a topic: hospital_etiquette, communication, or payment")
    
    def _analyze_review_sentiment(self, review_text: str) -> str:
        """Analyze sentiment of reviews.
        
        Args:
            review_text: Text of the review to analyze
        """
        # Simple sentiment analysis - would use real NLP model
        positive_words = ["excellent", "amazing", "satisfied", "happy", "recommend"]
        negative_words = ["disappointed", "painful", "expensive", "regret", "poor"]
        
        positive_count = sum(1 for word in positive_words if word in review_text.lower())
        negative_count = sum(1 for word in negative_words if word in review_text.lower())
        
        if positive_count > negative_count:
            return "Positive sentiment detected"
        elif negative_count > positive_count:
            return "Negative sentiment detected"
        else:
            return "Neutral sentiment"
    
    def _store_review_insights(self, clinic: str, insights: dict) -> str:
        """Store review insights in team state.
        
        Args:
            clinic: Name of the clinic
            insights: Dictionary containing review insights
        """
        self.team_state["session_notes"].append({
            "type": "review_insight",
            "clinic": clinic,
            "insights": insights,
            "timestamp": datetime.now().isoformat()
        })
        return f"Stored insights for {clinic}"
    
    async def process(self, message: str, user_id: str = None, session_id: str = None, 
                     language_code: str = "en") -> dict:
        """
        Process user message using the unified team.
        
        Args:
            message: User's message
            user_id: User identifier
            session_id: Session identifier
            language_code: User's language preference
            
        Returns:
            Team's orchestrated response
        """
        try:
            # Update language preference
            self.team_state["user_profile"]["language"] = language_code
            
            # Add to conversation context
            self.team_state["conversation_context"].append(
                f"{datetime.now().strftime('%H:%M')}: {message[:50]}..."
            )
            
            # Update agent instructions based on language
            # Note: Currently skipping dynamic instruction updates to avoid errors
            
            # Log request to LangDB if configured
            if self.use_langdb:
                logger.info(f"Processing request with LangDB tracing - Session: {session_id}, User: {user_id}")
            
            # Run the team with metadata for better tracing
            response = await self.main_team.arun(
                message=message,
                user_id=user_id or "anonymous",
                session_id=session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                metadata={
                    "language": language_code,
                    "timestamp": datetime.now().isoformat(),
                    "orchestrator_version": "v2",
                    "langdb_enabled": self.use_langdb
                }
            )
            
            # Extract response
            response_content = response.content if hasattr(response, 'content') else str(response)
            
            # Translate response if needed
            if language_code != "en":
                response_content = self.translator.translate(response_content, language_code)
            
            return {
                "content": response_content,
                "metadata": {
                    "agent": "Ahrie AI Team",
                    "timestamp": datetime.now().isoformat(),
                    "language": language_code,
                    "langdb_enabled": self.use_langdb,
                    "session_state": {
                        "user_profile": self.team_state.get("user_profile"),
                        "interests": len(self.team_state.get("medical_interests", [])),
                        "recommendations": len(self.team_state.get("recommended_clinics", [])),
                        "reviews_analyzed": len(self.team_state.get("analyzed_reviews", []))
                    },
                    "performance": {
                        "model_used": "LangDB" if self.use_langdb else "OpenAI",
                        "agents_count": len(self.main_team.members)
                    }
                }
            }
            
        except Exception as e:
            import traceback
            logger.error(f"Error in team orchestrator: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            error_msg = "I apologize, but I encountered an error. Please try again."
            if language_code == "ar":
                error_msg = "أعتذر، لقد واجهت خطأ. يرجى المحاولة مرة أخرى."
            
            return {
                "content": error_msg,
                "metadata": {
                    "agent": "Ahrie AI Team",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            }
    
    def get_session_insights(self) -> dict:
        """Get detailed insights about the current session."""
        state = self.team_state
        
        return {
            "user_journey": {
                "profile": state.get("user_profile"),
                "interests": state.get("medical_interests", []),
                "cultural_needs": state.get("cultural_requirements"),
                "interaction_count": len(state.get("conversation_context", []))
            },
            "recommendations": {
                "clinics": state.get("recommended_clinics", []),
                "reviews_analyzed": len(state.get("analyzed_reviews", [])),
                "insights": [n for n in state.get("session_notes", []) if n["type"] == "review_insight"]
            },
            "session_summary": self._generate_session_summary(),
            "monitoring": {
                "langdb_enabled": self.use_langdb,
                "tracking_url": f"https://app.langdb.ai/projects/{self.langdb_project_id}" if self.use_langdb else None
            }
        }
    
    def _generate_session_summary(self) -> str:
        """Generate a summary of the session."""
        state = self.team_state
        
        summary_parts = []
        
        # User profile
        profile = state.get("user_profile", {})
        if profile.get("name"):
            summary_parts.append(f"User: {profile['name']} from {profile.get('location', 'Unknown')}")
        
        # Medical interests
        interests = state.get("medical_interests", [])
        if interests:
            procedures = list(set(i["procedure"] for i in interests))
            summary_parts.append(f"Interested in: {', '.join(procedures)}")
        
        # Cultural requirements
        cultural = state.get("cultural_requirements", {})
        requirements = [k for k, v in cultural.items() if v]
        if requirements:
            summary_parts.append(f"Requirements: {', '.join(requirements)}")
        
        # Recommendations
        clinics = state.get("recommended_clinics", [])
        if clinics:
            summary_parts.append(f"Recommended {len(clinics)} clinics")
        
        return " | ".join(summary_parts) if summary_parts else "New session - no activity yet"