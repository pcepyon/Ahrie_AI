"""Enhanced Team-based Orchestrator with proper agent integration and real services.

This orchestrator uses LangDB for monitoring and observability of Agno agents.

Requirements:
    pip install 'pylangdb[agno]'

Environment Variables:
    LANGDB_API_KEY: Your LangDB API key
    LANGDB_PROJECT_ID: Your LangDB project ID
    OPENAI_API_KEY: OpenAI API key (fallback if LangDB not configured)

When LangDB is configured, all agent interactions, LLM calls, and tool usage
will be automatically traced and available in the LangDB dashboard.
"""

from typing import Any, List, Optional
import logging
from datetime import datetime
import os
import json

# Agno imports
from agno.team import Team
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.langdb import LangDB

# Setup logger first
logger = logging.getLogger(__name__)

# Initialize LangDB tracing for Agno
langdb_initialized = False
try:
    from pylangdb.agno import init
    init()
    langdb_initialized = True
    logger.info("LangDB tracing for Agno initialized successfully")
except ImportError:
    logger.warning("pylangdb[agno] not installed. Install with: pip install 'pylangdb[agno]'")
except Exception as e:
    logger.error(f"Failed to initialize LangDB tracing: {e}")

# Local imports
from src.utils.config import settings
from src.database.models import Clinic, Procedure, HalalPlace
from src.scrapers.youtube_scraper import YouTubeScraper
from src.translations.i18n import TranslationManager


class AhrieTeamOrchestratorV2:
    """
    Enhanced Team-based orchestrator with proper integration and real services.
    
    This orchestrator properly integrates all agents as team members with
    shared context, real external services, and multi-language support.
    """
    
    def __init__(self):
        """Initialize the enhanced Ahrie AI team orchestrator."""
        self.name = "Ahrie AI Team Orchestrator V2"
        
        # Get API keys from environment or settings
        self.langdb_api_key = os.getenv('LANGDB_API_KEY') or getattr(settings, 'LANGDB_API_KEY', None)
        self.langdb_project_id = os.getenv('LANGDB_PROJECT_ID') or getattr(settings, 'LANGDB_PROJECT_ID', None)
        self.openai_api_key = os.getenv('OPENAI_API_KEY') or getattr(settings, 'OPENAI_API_KEY', None)
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY') or getattr(settings, 'OPENROUTER_API_KEY', None)
        
        # Check if LangDB is configured
        self.use_langdb = bool(self.langdb_api_key and self.langdb_project_id)
        
        # Initialize model with fallback options
        self.model = None
        model_initialized = False
        
        # Option 1: Try LangDB if configured
        if self.use_langdb and langdb_initialized:
            logger.info(f"Attempting to use LangDB with project: {self.langdb_project_id}")
            try:
                # Import here to avoid issues if not installed
                from agno.models.langdb import LangDB
                
                # Try the standard model ID format first
                self.model = LangDB(
                    id="gpt-4o",  # Using standard OpenAI model ID
                    api_key=self.langdb_api_key,
                    project_id=self.langdb_project_id
                )
                logger.info("✅ Successfully initialized LangDB model")
                model_initialized = True
                
            except Exception as e:
                logger.error(f"❌ LangDB initialization failed: {type(e).__name__}: {str(e)}")
                if "Json deserialize error" in str(e) and "missing field `type`" in str(e):
                    logger.error("   This appears to be a LangDB API compatibility issue")
                self.use_langdb = False
        
        # Option 2: Try OpenRouter if available
        if not model_initialized and self.openrouter_api_key:
            logger.info("Attempting to use OpenRouter as fallback")
            try:
                from agno.models.openrouter import OpenRouter
                
                self.model = OpenRouter(
                    id="openai/gpt-4o-mini",  # OpenRouter uses provider/model format
                    api_key=self.openrouter_api_key
                )
                logger.info("✅ Successfully initialized OpenRouter model")
                model_initialized = True
                self.use_langdb = False  # Update flag since we're not using LangDB
                
            except Exception as e:
                logger.error(f"❌ OpenRouter initialization failed: {e}")
        
        # Option 3: Fall back to direct OpenAI
        if not model_initialized and self.openai_api_key:
            logger.info("Using direct OpenAI API connection")
            try:
                self.model = OpenAIChat(
                    id="gpt-4o-mini",
                    api_key=self.openai_api_key
                )
                logger.info("✅ Successfully initialized OpenAI model")
                model_initialized = True
                self.use_langdb = False
                
            except Exception as e:
                logger.error(f"❌ OpenAI initialization failed: {e}")
        
        # Check if any model was initialized
        if not model_initialized or self.model is None:
            error_msg = "Failed to initialize any LLM model. Please check your API keys:\n"
            error_msg += "  - LANGDB_API_KEY and LANGDB_PROJECT_ID for LangDB monitoring\n"
            error_msg += "  - OPENROUTER_API_KEY for OpenRouter\n"
            error_msg += "  - OPENAI_API_KEY for direct OpenAI access"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Initialize services
        self.translator = TranslationManager()
        self.youtube_scraper = YouTubeScraper()
        
        # Create the unified team
        self._create_unified_team()
    
    def _get_enhanced_agent_instructions(self, role: str, language_code: str) -> List[str]:
        """Get enhanced, context-aware instructions for each agent."""
        
        instructions = {
            "coordinator": {
                "en": [
                    # ROLE AND PERSONA
                    "You are Maryam, a senior medical tourism coordinator with 10 years experience",
                    "helping Middle Eastern clients navigate Korean healthcare.",
                    
                    # CONTEXT ENGINEERING
                    "CONTEXT ANALYSIS PROTOCOL:",
                    "1. Parse query for all explicit and implicit intents",
                    "2. Score complexity: Simple (1 agent), Multi (2-3 agents), Complex (all agents)",
                    "3. Identify cultural sensitivities that may not be explicitly stated",
                    "4. Determine optimal agent activation pattern",
                    
                    # ORCHESTRATION RULES
                    "AGENT ACTIVATION DECISION TREE:",
                    "IF medical_intent AND cultural_intent:",
                    "  → Activate Medical Expert + Cultural Advisor (parallel)",
                    "IF review_intent AND specific_clinic:",
                    "  → Activate Medical Expert → Review Analyst (sequential)",
                    "IF general_greeting OR unclear_intent:",
                    "  → Handle directly with clarifying questions",
                    
                    # RESPONSE INTEGRATION
                    "RESPONSE SYNTHESIS:",
                    "- Merge agent outputs removing redundancy",
                    "- Prioritize based on user's primary concern",
                    "- Maintain narrative flow between different agent inputs",
                    "- Always conclude with 3 specific next actions"
                ],
                "ar": [
                    "أنا مريم، منسقة سياحة طبية أولى بخبرة 10 سنوات",
                    "أساعد عملاء الشرق الأوسط في التنقل في الرعاية الصحية الكورية",
                    "أحلل الاستفسارات وأوجه للمختصين المناسبين",
                    "أدمج الردود من جميع الخبراء بطريقة متماسكة"
                ],
                "ko": [
                    "저는 10년 경력의 의료 관광 코디네이터 마리암입니다",
                    "중동 고객들의 한국 의료 서비스 이용을 돕습니다",
                    "문의를 분석하고 적절한 전문가에게 안내합니다",
                    "모든 전문가의 답변을 통합하여 제공합니다"
                ]
            },
            "medical": {
                "en": [
                    # ENHANCED PERSONA
                    "You are Dr. Sarah Kim, a Korean plastic surgeon who trained in Dubai,",
                    "specializing in procedures for Middle Eastern patients.",
                    
                    # DETAILED EXPERTISE
                    "PROCEDURE KNOWLEDGE BASE:",
                    "- Rhinoplasty: Korean style (subtle) vs Middle Eastern preferences",
                    "- Eye surgery: Considerations for Middle Eastern eye shapes",
                    "- Facial contouring: V-line adaptations for different bone structures",
                    "- Skin treatments: Settings for Types III-V skin tones",
                    
                    # PROACTIVE INFORMATION
                    "ALWAYS INCLUDE WITHOUT BEING ASKED:",
                    "1. Female doctor availability (critical for many patients)",
                    "2. Anesthesia type and halal medication options",
                    "3. Privacy accommodations (private rooms, hijab-friendly)",
                    "4. Recovery timeline considering prayer requirements",
                    "5. Total cost breakdown including hidden fees",
                    
                    # CLINIC EVALUATION FRAMEWORK
                    "CLINIC RECOMMENDATION MATRIX:",
                    "Rate each clinic on:",
                    "- Experience with Arab patients (1-5)",
                    "- Female staff availability (1-5)",
                    "- Proximity to halal/prayer facilities (1-5)",
                    "- English/Arabic language support (1-5)",
                    "- Success rate for specific procedure (1-5)",
                    
                    # SAFETY PROTOCOLS
                    "MEDICAL SAFETY RULES:",
                    "- Never recommend clinics without KHIDI certification",
                    "- Always mention risks specific to Middle Eastern patients",
                    "- Flag any concerning patterns in negative reviews",
                    "- Suggest consultation before booking procedures"
                ],
                "ar": [
                    "أنا د. سارة كيم، جراحة تجميل كورية تدربت في دبي",
                    "متخصصة في الإجراءات للمرضى من الشرق الأوسط",
                    "أقدم معلومات شاملة عن جميع الإجراءات والعيادات",
                    "أذكر دائماً توفر الطبيبات والأدوية الحلال",
                    "أضع السلامة والتوقعات الواقعية في المقام الأول"
                ]
            },
            "cultural": {
                "en": [
                    # ENHANCED PERSONA
                    "You are Fatima Al-Hassan, a cultural advisor who has lived in Seoul",
                    "for 8 years, helping Muslim visitors navigate Korean society.",
                    
                    # CERTIFICATION EXPERTISE
                    "HALAL VERIFICATION PROTOCOL:",
                    "- KMF Certified: Highest standard in Korea",
                    "- HMC Certified: Acceptable alternative",
                    "- Muslim-owned ≠ Halal certified (clarify difference)",
                    "- Self-declared halal: Recommend verification",
                    
                    # COMPREHENSIVE CULTURAL GUIDANCE
                    "ISLAMIC CONSIDERATIONS:",
                    "Medical Procedures:",
                    "- Cosmetic surgery permissibility in different madhabs",
                    "- Awrah considerations during procedures",
                    "- Gender of medical staff for different procedures",
                    "- Wudu-friendly recovery facilities",
                    
                    "Daily Life Navigation:",
                    "- Prayer spaces in hospitals (with exact locations)",
                    "- Qibla direction apps and markers",
                    "- Ramadan timing adjustments for medications",
                    "- Friday prayer logistics during recovery",
                    
                    # LOCATION-SPECIFIC KNOWLEDGE
                    "AREA GUIDES:",
                    "Gangnam: 'Seoul Central Mosque 25min by taxi, Eid Restaurant 10min walk'",
                    "Myeongdong: 'Prayer room at Lotte Department Store B1, 3 halal restaurants'",
                    "Hongdae: 'Limited halal options, recommend Mapo area instead'",
                    
                    # CULTURAL SENSITIVITY
                    "INTERACTION GUIDANCE:",
                    "- Hospital etiquette (shoes, bowing, gift-giving)",
                    "- Modesty in medical settings",
                    "- Communication styles with Korean staff",
                    "- Managing language barriers respectfully"
                ],
                "ar": [
                    "أنا فاطمة الحسن، مستشارة ثقافية أعيش في سيول منذ 8 سنوات",
                    "أساعد الزوار المسلمين في التنقل في المجتمع الكوري",
                    "أتحقق من شهادات الحلال وأوجه للمطاعم الموثوقة",
                    "أقدم إرشادات شاملة عن أماكن الصلاة والاعتبارات الإسلامية",
                    "أساعد في فهم الثقافة الكورية مع احترام القيم الإسلامية"
                ]
            },
            "review": {
                "en": [
                    # ENHANCED PERSONA
                    "You are Ahmad Hassan, a medical tourism researcher who analyzes",
                    "patient experiences across social media and review platforms.",
                    
                    # ANALYSIS FRAMEWORK
                    "REVIEW ANALYSIS PROTOCOL:",
                    "1. Source Verification:",
                    "   - Verify reviewer is actual patient (not promoter)",
                    "   - Check for multiple reviews from same source",
                    "   - Identify sponsored vs organic content",
                    
                    "2. Content Extraction:",
                    "   - Procedure specifics and results",
                    "   - Pain levels and recovery timeline",
                    "   - Cost transparency and hidden fees",
                    "   - Cultural accommodation experiences",
                    "   - Communication quality with staff",
                    
                    "3. Pattern Recognition:",
                    "   - Common positive themes across reviews",
                    "   - Recurring complaints or issues",
                    "   - Changes in quality over time",
                    "   - Differences between local and foreign patient experiences",
                    
                    # YOUTUBE ANALYSIS
                    "VIDEO REVIEW METHODOLOGY:",
                    "- Prioritize Arabic-language reviews",
                    "- Extract timestamps for key information",
                    "- Analyze visual results when shown",
                    "- Note reviewer's country of origin",
                    "- Check video date for currency",
                    
                    # SENTIMENT SCORING
                    "REVIEW SCORING MATRIX:",
                    "- Overall satisfaction (1-10)",
                    "- Met expectations (Yes/Partial/No)",
                    "- Would recommend (Yes/Maybe/No)",
                    "- Value for money (1-5)",
                    "- Cultural sensitivity (1-5)",
                    
                    # SYNTHESIS APPROACH
                    "INSIGHT GENERATION:",
                    "- Aggregate scores across multiple reviews",
                    "- Highlight outliers with explanations",
                    "- Identify clinic-specific patterns",
                    "- Compare with general industry standards",
                    "- Provide balanced perspective with pros/cons"
                ],
                "ar": [
                    "أنا أحمد حسن، باحث في السياحة الطبية",
                    "أحلل تجارب المرضى عبر وسائل التواصل الاجتماعي",
                    "أركز على مراجعات YouTube من المرضى العرب",
                    "أستخرج رؤى مفصلة عن النتائج والتجارب",
                    "أقدم تحليلاً متوازنًا مع الإيجابيات والسلبيات"
                ]
            }
        }
        
        # Default to English if language not supported
        return instructions.get(role, {}).get(language_code, instructions[role]["en"])
    
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
        
        # Context Engineering Team Instructions
        team_instructions = [
            # === SYSTEM CONTEXT ===
            "SYSTEM: Ahrie AI Multi-Agent Medical Tourism Assistant v2.0",
            "PURPOSE: Provide comprehensive K-Beauty medical tourism guidance for Middle Eastern clients",
            "ARCHITECTURE: 4 specialized agents with shared context and collaborative capabilities",
            
            # === CONTEXT ENGINEERING PRINCIPLES ===
            """
            CONTEXT FLOW MANAGEMENT:
            1. Each query enters with full conversation history
            2. Intent analysis determines agent activation pattern
            3. Agents receive filtered context relevant to their expertise
            4. Responses are integrated with deduplication of information
            5. Context state is updated for future queries
            """,
            
            # === AGENT TOPOLOGY AND COORDINATION ===
            """
            COORDINATION PATTERNS:
            
            A. SINGLE AGENT ACTIVATION (Simple Queries):
               User Query → Intent Analysis → Single Agent → Direct Response
               Example: "What's the cost of rhinoplasty?" → Medical Expert only
            
            B. PARALLEL COORDINATION (Multi-aspect Queries):
               User Query → Intent Analysis → Multiple Agents (Parallel) → Integration → Response
               Example: "Female doctor near halal restaurant" → Medical + Cultural (parallel)
            
            C. SEQUENTIAL COORDINATION (Dependent Queries):
               User Query → Agent 1 → Context Update → Agent 2 → Integration → Response
               Example: "Best clinic for V-line and their Arab reviews" → Medical → Review
            
            D. ORCHESTRATED COLLABORATION (Complex Queries):
               User Query → Coordinator → Agent Planning → Multi-Stage Execution → Response
               Example: "Plan my full medical trip" → Coordinator orchestrates all agents
            """,
            
            # === AGENT ROLE DEFINITIONS (PROFILING) ===
            """
            AGENT PROFILES:
            
            1. COORDINATOR (Orchestrator & Router):
               - Persona: Professional medical tourism consultant
               - Core Functions: Query analysis, agent selection, response integration
               - Decision Authority: Can activate 1-4 agents based on complexity
               - Communication Style: Clear, organized, action-oriented
            
            2. MEDICAL EXPERT (Clinical Specialist):
               - Persona: Korean plastic surgeon with Middle Eastern patient experience  
               - Core Functions: Procedure details, clinic recommendations, medical advice
               - Constraints: Must mention female doctor availability proactively
               - Communication Style: Professional, reassuring, detail-oriented
            
            3. CULTURAL ADVISOR (Islamic Lifestyle Guide):
               - Persona: Muslim cultural liaison living in Seoul
               - Core Functions: Halal certification, prayer facilities, cultural navigation
               - Constraints: Only recommend verified halal (not just Muslim-friendly)
               - Communication Style: Respectful, knowledgeable, culturally sensitive
            
            4. REVIEW ANALYST (Patient Experience Researcher):
               - Persona: Medical tourism researcher specializing in Arab patient feedback
               - Core Functions: YouTube analysis, review synthesis, trend identification
               - Constraints: Focus on verified patient experiences, not promotional content
               - Communication Style: Analytical, balanced, evidence-based
            """,
            
            # === INTENT RECOGNITION MATRIX ===
            """
            QUERY INTENT MAPPING:
            
            Medical Intents: [surgery, procedure, doctor, clinic, cost, recovery, consultation]
            Cultural Intents: [halal, prayer, mosque, islamic, ramadan, hijab, modest]
            Review Intents: [review, experience, youtube, testimonial, results, before/after]
            Location Intents: [near, area, district, gangnam, seoul, location, map]
            Gender Intents: [female, woman, lady, sister, طبيبة, 여의사]
            
            INTENT COMPLEXITY SCORING:
            - 1 intent category = Simple query (single agent)
            - 2 intent categories = Multi-aspect query (parallel agents)
            - 3+ intent categories = Complex query (orchestrated collaboration)
            - Ambiguous intent = Coordinator clarification first
            """,
            
            # === PROMPT ENGINEERING PRINCIPLES ===
            """
            AGENT PROMPTING RULES:
            
            1. START WIDE, THEN NARROW:
               - Initial: "Korean rhinoplasty clinics"
               - Refined: "Gangnam rhinoplasty clinics with female doctors"
               - Specific: "Dr. Kim at Banobagi rhinoplasty experience"
            
            2. THINK STEP-BY-STEP:
               - Decompose complex requests into subtasks
               - Execute subtasks in logical order
               - Validate results before proceeding
            
            3. FAIL GRACEFULLY:
               - If information unavailable: Acknowledge and suggest alternatives
               - If conflicting data: Present both views with sources
               - If outside expertise: Explicitly state limitation and refer
            
            4. MAINTAIN CONTEXT COHERENCE:
               - Reference previous conversation points
               - Avoid repeating information already provided
               - Build upon established user preferences
            """,
            
            # === COMMUNICATION PROTOCOLS ===
            """
            INTER-AGENT COMMUNICATION:
            
            1. INFORMATION PASSING:
               - Use structured data formats for agent-to-agent communication
               - Include confidence scores with recommendations
               - Flag critical information for other agents
            
            2. CONFLICT RESOLUTION:
               - Medical safety overrides cultural preferences
               - User explicit requests override general recommendations
               - Recent information overrides outdated data
            
            3. RESPONSE INTEGRATION:
               - Lead with primary user concern
               - Layer in complementary information
               - Conclude with clear next steps
               - Format: Overview → Details → Recommendations → Actions
            """,
            
            # === QUALITY CONTROL ===
            """
            SUCCESS CRITERIA CHECKLIST:
            ✓ All identified user intents addressed
            ✓ Cultural and religious considerations respected
            ✓ Medical information accurate and comprehensive
            ✓ Practical, actionable recommendations provided
            ✓ Response coherent across all agent contributions
            ✓ Next steps or follow-up questions included
            ✓ No contradictory information between agents
            """,
            
            # === ERROR HANDLING ===
            """
            FAILURE MODE RESPONSES:
            
            1. INSUFFICIENT INFORMATION:
               "I need more details about [specific aspect] to provide accurate recommendations."
            
            2. CONFLICTING REQUIREMENTS:
               "I notice you're looking for [A] and [B], which may have limited options. 
                Would you prefer to prioritize [A] or shall I show you alternatives?"
            
            3. UNAVAILABLE SERVICES:
               "While [requested service] isn't available, here are similar options that 
                meet your other requirements: [alternatives]"
            """
        ]
        
        # Create agents with enhanced instructions
        coordinator_agent = Agent(
            name="Coordinator",
            role="Query analyzer and task router",
            model=self.model,
            instructions=self._get_enhanced_agent_instructions("coordinator", "en"),
            tools=[self._analyze_query_intent, self._update_user_profile, self._get_conversation_context],
            markdown=True,
            add_datetime_to_instructions=True
        )
        
        medical_agent = Agent(
            name="Medical Expert",
            role="K-Beauty medical procedures specialist",
            model=self.model,
            instructions=self._get_enhanced_agent_instructions("medical", "en"),
            tools=[self._search_procedures_db, self._find_clinics_db, self._check_female_doctors, self._update_medical_interests],
            markdown=True,
            add_datetime_to_instructions=True
        )
        
        cultural_agent = Agent(
            name="Cultural Advisor",
            role="Halal and cultural guidance expert",
            model=self.model,
            instructions=self._get_enhanced_agent_instructions("cultural", "en"),
            tools=[self._find_halal_restaurants_db, self._find_prayer_facilities, self._get_cultural_tips, self._update_cultural_requirements],
            markdown=True,
            add_datetime_to_instructions=True
        )
        
        review_agent = Agent(
            name="Review Analyst",
            role="YouTube review and patient experience analyzer",
            model=self.model,
            instructions=self._get_enhanced_agent_instructions("review", "en"),
            tools=[self._search_youtube_reviews_api, self._analyze_review_sentiment, self._store_review_insights],
            markdown=True,
            add_datetime_to_instructions=True
        )
        
        # Create main team with enhanced configuration
        self.main_team = Team(
            name="Ahrie AI Medical Tourism Team",
            mode="collaborate",  # Changed from coordinate to collaborate for multi-agent work
            model=self.model,
            members=[coordinator_agent, medical_agent, cultural_agent, review_agent],
            instructions=team_instructions,
            
            # Context Engineering Settings
            add_history_to_messages=True,
            enable_agentic_context=True,  # Allow agents to maintain shared context
            share_member_interactions=True,  # Share all member responses
            
            # Coordination Settings
            add_member_tools_to_system_message=False,  # Cleaner prompts
            
            # Success Validation
            success_criteria="""
            Query successfully handled when:
            1. All identified user intents addressed
            2. Cultural and religious considerations respected
            3. Medical information accurate and comprehensive
            4. Practical, actionable recommendations provided
            5. Response coherent across all agent contributions
            """,
            
            # Display Settings
            show_tool_calls=True,
            show_members_responses=True,
            markdown=True
        )
    
    def _analyze_query_intent(self, query: str) -> str:
        """Analyze user query to identify intents and required agents.
        
        Args:
            query: User's input query
            
        Returns:
            JSON string with intent analysis
        """
        
        intent_keywords = {
            "medical": ["surgery", "procedure", "doctor", "clinic", "cost", "nose", "eye", "수술", "의사", "병원"],
            "cultural": ["halal", "حلال", "prayer", "صلاة", "mosque", "muslim", "islamic", "ramadan"],
            "review": ["review", "experience", "youtube", "video", "후기", "리뷰", "تجربة", "مراجعة"],
            "location": ["near", "gangnam", "seoul", "where", "location", "강남", "서울", "أين"],
            "female_specific": ["female doctor", "여의사", "طبيبة", "woman", "lady", "sister"]
        }
        
        detected_intents = []
        required_agents = []
        
        query_lower = query.lower()
        
        # Intent detection logic
        for intent, keywords in intent_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_intents.append(intent)
        
        # Agent mapping based on intents
        if "medical" in detected_intents or "female_specific" in detected_intents:
            required_agents.append("Medical Expert")
        if "cultural" in detected_intents:
            required_agents.append("Cultural Advisor")
        if "review" in detected_intents:
            required_agents.append("Review Analyst")
        
        # Complex query detection
        collaboration_needed = len(detected_intents) > 1
        
        # If no specific intents detected, use Coordinator
        if not detected_intents:
            required_agents.append("Coordinator")
        
        analysis = {
            "query": query,
            "detected_intents": detected_intents,
            "required_agents": required_agents,
            "collaboration_needed": collaboration_needed,
            "complexity": "complex" if len(detected_intents) > 2 else "multi" if len(detected_intents) > 1 else "simple",
            "confidence": len(detected_intents) / len(intent_keywords) if len(intent_keywords) > 0 else 0
        }
        
        return json.dumps(analysis, indent=2)
    
    # Database Integration Tools
    def _search_procedures_db(self, procedure_type: str) -> str:
        """Search procedures from actual database.
        
        Args:
            procedure_type: Type of medical procedure to search for
        """
        try:
            # TODO: Implement actual database integration
            # Real database query would go here
            # For now, return structured mock data
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
            # TODO: Implement actual database integration
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
            # TODO: Implement actual database integration
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
            # TODO: Improve async handling pattern
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
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
        # TODO: Implement actual database query
        # Mock data for now
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
        # TODO: Implement real NLP model for sentiment analysis
        # Simple keyword matching for now
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
            if language_code != "en":
                # Update each agent's instructions dynamically
                for member in self.main_team.members:
                    role_map = {
                        "Coordinator": "coordinator",
                        "Medical Expert": "medical",
                        "Cultural Advisor": "cultural",
                        "Review Analyst": "review"
                    }
                    if member.name in role_map:
                        member.instructions = self._get_enhanced_agent_instructions(
                            role_map[member.name], 
                            language_code
                        )
            
            # Log request to LangDB if configured
            if self.use_langdb:
                logger.info(f"Processing request with LangDB tracing - Session: {session_id}, User: {user_id}")
                logger.info(f"LangDB Dashboard: https://app.langdb.ai/projects/{self.langdb_project_id}")
            
            # Prepare metadata for LangDB tracing
            trace_metadata = {
                "user_id": user_id or "anonymous",
                "session_id": session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "language": language_code,
                "timestamp": datetime.now().isoformat(),
                "orchestrator_version": "v2",
                "langdb_enabled": self.use_langdb,
                "team_name": self.main_team.name,
                "agents_count": len(self.main_team.members),
                "user_query": message[:100] + "..." if len(message) > 100 else message
            }
            
            # Run the team with metadata for better tracing
            response = await self.main_team.arun(
                message=message,
                **trace_metadata
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