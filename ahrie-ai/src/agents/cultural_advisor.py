"""Cultural & Halal Advisor Agent for Middle Eastern clients in Korea."""

from typing import Dict, List, Optional, Any
from agno.agent import Agent, RunResponse
from agno.models.langdb import LangDB
from agno.tools.duckduckgo import DuckDuckGoTools
import logging
from datetime import datetime, time
import os
from src.utils.config import settings

logger = logging.getLogger(__name__)

# Initialize LangDB tracing
try:
    from pylangdb.agno import init
    init()
except ImportError:
    logger.warning("pylangdb not installed, tracing will not be available")


class CulturalAdvisorAgent:
    """
    Cultural advisor agent specialized in Islamic/Halal considerations and cultural guidance.
    
    Provides guidance on halal facilities, prayer locations, cultural etiquette,
    and helps Middle Eastern clients navigate Korean culture during medical tourism.
    """
    
    def __init__(self, name: str = "CulturalAdvisor"):
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
            description="Cultural advisor for Middle Eastern clients visiting Korea for medical tourism.",
            instructions=[
                "You are a cultural advisor for Middle Eastern clients visiting Korea for medical tourism.",
                "Provide guidance on halal food, prayer facilities, and Islamic considerations.",
                "Help navigate Korean culture while respecting Islamic values.",
                "Offer practical advice for Muslim travelers in Korea.",
                "Be sensitive to cultural and religious needs of Saudi and UAE clients."
            ],
            tools=[DuckDuckGoTools()],
            markdown=True,
            show_tool_calls=True
        )
        self.prayer_times_api = None  # Will be initialized with prayer times API
        self.halal_database = self._load_halal_database()
        
    def _load_halal_database(self) -> Dict[str, Any]:
        """
        Load database of halal facilities and Islamic resources in Korea.
        
        Returns:
            Dictionary of halal resources by category
        """
        return {
            "restaurants": {
                "gangnam": [
                    {
                        "name": "Eid Halal Korean Restaurant",
                        "address": "Gangnam-gu, Seoul",
                        "cuisine": "Korean Halal",
                        "certification": "KMF",
                        "distance_from_clinics": "5-10 min"
                    },
                    {
                        "name": "Makan Halal Restaurant",
                        "address": "Gangnam-gu, Seoul", 
                        "cuisine": "Middle Eastern",
                        "certification": "KMF",
                        "distance_from_clinics": "10-15 min"
                    }
                ],
                "itaewon": [
                    {
                        "name": "Babylon Restaurant",
                        "address": "Itaewon, Seoul",
                        "cuisine": "Arabic",
                        "certification": "Self-certified",
                        "distance_from_clinics": "30-40 min"
                    }
                ]
            },
            "mosques": [
                {
                    "name": "Seoul Central Mosque",
                    "address": "Itaewon, Seoul",
                    "facilities": ["Prayer halls", "Wudu areas", "Islamic library"],
                    "friday_prayer": "12:30 PM",
                    "languages": ["Arabic", "English", "Korean"]
                },
                {
                    "name": "Gangnam Prayer Room",
                    "address": "Gangnam-gu, Seoul",
                    "facilities": ["Small prayer room", "Wudu area"],
                    "capacity": 50,
                    "notes": "Located in office building, call ahead"
                }
            ],
            "halal_markets": [
                {
                    "name": "Seoul Halal Mart",
                    "address": "Itaewon, Seoul",
                    "products": ["Halal meat", "Middle Eastern groceries", "Prayer items"],
                    "delivery": True
                }
            ]
        }
    
    async def find_halal_restaurants(self, 
                                   location: str,
                                   cuisine_preference: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Find halal restaurants near a specific location.
        
        Args:
            location: Area in Seoul (e.g., Gangnam, Itaewon)
            cuisine_preference: Optional cuisine type preference
            
        Returns:
            List of halal restaurants with details
        """
        location_lower = location.lower()
        restaurants = []
        
        # Search in database
        for area, area_restaurants in self.halal_database["restaurants"].items():
            if location_lower in area.lower():
                for restaurant in area_restaurants:
                    if not cuisine_preference or cuisine_preference.lower() in restaurant["cuisine"].lower():
                        restaurants.append(restaurant)
        
        # Add delivery options
        if not restaurants:
            restaurants.append({
                "name": "Halal Delivery Options",
                "service": "Multiple halal delivery services available",
                "apps": ["Yogiyo", "Baemin - search 'halal'"],
                "note": "Many restaurants offer halal delivery to your location"
            })
            
        return restaurants
    
    async def get_prayer_facilities(self, location: str) -> Dict[str, Any]:
        """
        Get information about prayer facilities and mosques.
        
        Args:
            location: Area in Seoul
            
        Returns:
            Prayer facility information including times and directions
        """
        mosques = self.halal_database["mosques"]
        prayer_times = await self._get_prayer_times_seoul()
        
        return {
            "nearest_mosques": mosques,
            "prayer_times_today": prayer_times,
            "prayer_apps": [
                "Muslim Pro - includes Korea prayer times",
                "Athan Pro - prayer reminders"
            ],
            "qibla_direction": "285° (West-Northwest from Seoul)",
            "prayer_mats_available_at": [
                "Seoul Central Mosque",
                "Most halal restaurants",
                "Can purchase at Halal marts"
            ]
        }
    
    async def _get_prayer_times_seoul(self) -> Dict[str, str]:
        """
        Get prayer times for Seoul.
        
        Returns:
            Dictionary of prayer times
        """
        # This would integrate with actual prayer times API
        # Mock data for now
        return {
            "fajr": "04:45",
            "sunrise": "06:15",
            "dhuhr": "12:30",
            "asr": "15:45",
            "maghrib": "18:30",
            "isha": "20:00"
        }
    
    async def cultural_etiquette_guide(self, context: str) -> Dict[str, Any]:
        """
        Provide cultural etiquette guidance for specific contexts.
        
        Args:
            context: Specific situation (e.g., "clinic visit", "restaurant", "public transport")
            
        Returns:
            Relevant cultural guidance
        """
        general_etiquette = {
            "greetings": [
                "Slight bow when greeting is common",
                "Handshakes are acceptable in medical settings",
                "Some Koreans may understand limited handshaking between opposite genders"
            ],
            "clinic_visits": [
                "Remove shoes when entering certain areas",
                "Punctuality is highly valued",
                "Bring a translator or use translation app",
                "Inform about prayer time needs in advance"
            ],
            "general_tips": [
                "Dress modestly is generally respected",
                "Hijab is accepted and respected",
                "Public displays of affection are uncommon",
                "Tipping is not customary"
            ]
        }
        
        context_specific = {
            "clinic": {
                "tips": [
                    "Medical staff are generally respectful of religious needs",
                    "Request same-gender staff if needed",
                    "Prayer rooms may be available - ask reception",
                    "Halal meals can be arranged with advance notice"
                ],
                "useful_phrases": {
                    "I need to pray": "기도해야 해요 (gido-haeya haeyo)",
                    "Halal food only": "할랄 음식만 (halal eumsik-man)",
                    "No pork/alcohol": "돼지고기/술 안 돼요 (dwaejigogi/sul an dwaeyo)"
                }
            },
            "accommodation": {
                "tips": [
                    "Request rooms with qibla direction marked",
                    "Many hotels near Gangnam understand Muslim needs",
                    "Kitchen facilities helpful for halal cooking",
                    "Some hotels offer prayer mats"
                ],
                "recommended_areas": [
                    "Gangnam - close to clinics",
                    "Itaewon - more halal options but further",
                    "Myeongdong - good shopping, some halal food"
                ]
            }
        }
        
        context_key = context.lower()
        specific_guide = context_specific.get(context_key, {})
        
        return {
            "general_etiquette": general_etiquette,
            "context_specific": specific_guide,
            "emergency_contacts": {
                "Saudi Embassy": "+82-2-739-0631",
                "UAE Embassy": "+82-2-790-3235",
                "Halal Emergency Hotline": "1330 (Korea Tourism)"
            }
        }
    
    async def ramadan_guidance(self) -> Dict[str, Any]:
        """
        Provide specific guidance for patients visiting during Ramadan.
        
        Returns:
            Ramadan-specific guidance and considerations
        """
        return {
            "medical_considerations": [
                "Discuss fasting with surgeon before procedures",
                "Some medications can be adjusted for fasting",
                "IV fluids may be needed for major surgeries",
                "Recovery may take longer while fasting"
            ],
            "iftar_options": {
                "restaurants": self.halal_database["restaurants"],
                "mosque_iftars": [
                    "Seoul Central Mosque hosts community iftar",
                    "Some Indonesian/Malaysian restaurants offer iftar specials"
                ],
                "grocery_delivery": [
                    "Order dates and traditional items from Halal marts",
                    "Korean dates (대추) available in regular markets"
                ]
            },
            "suhoor_tips": [
                "24-hour convenience stores for basic needs",
                "Prepare meals in accommodation",
                "Some halal restaurants open early during Ramadan"
            ],
            "special_arrangements": [
                "Clinics can schedule procedures post-iftar",
                "Request fasting-friendly medication schedules",
                "Tarawih prayers at Seoul Central Mosque"
            ]
        }
    
    async def female_specific_guidance(self) -> Dict[str, Any]:
        """
        Provide guidance specific to female Muslim patients.
        
        Returns:
            Female-specific cultural and religious guidance
        """
        return {
            "hijab_considerations": [
                "Hijab is widely accepted in Korea",
                "No restrictions in public places",
                "Medical staff will respect hijab during procedures",
                "Hijab-friendly salons available in Itaewon"
            ],
            "medical_privacy": [
                "Request female doctors/nurses in advance",
                "Private recovery rooms available",
                "Clinics understand modesty requirements",
                "Female translators can be arranged"
            ],
            "shopping_tips": [
                "Myeongdong has modest fashion options",
                "Ewha Women's University area good for shopping",
                "Some stores have women-only fitting rooms",
                "Online shopping widely available"
            ],
            "safety": [
                "Korea is very safe for women",
                "Public transport is safe at all hours",
                "Women-only taxi services available",
                "Emergency numbers work in English"
            ],
            "beauty_services": [
                "Halal nail polish available in some shops",
                "Wudu-friendly beauty treatments",
                "Female-only spas (jjimjilbang) available",
                "Hijab-friendly hair salons in international areas"
            ]
        }
    
    def run(self, message: str) -> RunResponse:
        """
        Run the cultural advisor agent synchronously.
        
        Args:
            message: User's cultural/religious query
            
        Returns:
            Agent's response
        """
        # Enhance the query with cultural context
        enhanced_query = f"As a cultural advisor for Muslim visitors to Korea, please help with: {message}"
        return self.agent.run(enhanced_query)
    
    async def arun(self, message: str) -> RunResponse:
        """
        Run the cultural advisor agent asynchronously.
        
        Args:
            message: User's cultural/religious query
            
        Returns:
            Agent's response
        """
        # Enhance the query with cultural context
        enhanced_query = f"As a cultural advisor for Muslim visitors to Korea, please help with: {message}"
        return await self.agent.arun(enhanced_query)
    
    async def process(self, message: str) -> Dict[str, Any]:
        """
        Process cultural and religious guidance requests.
        
        Args:
            message: Incoming message
            
        Returns:
            Cultural guidance response
        """
        try:
            content = message.lower()
            
            # Determine the type of cultural guidance needed
            if "halal" in content and "food" in content:
                location = self._extract_location(content)
                result = await self.find_halal_restaurants(location)
                response_type = "halal_restaurants"
            elif "pray" in content or "mosque" in content:
                location = self._extract_location(content)
                result = await self.get_prayer_facilities(location)
                response_type = "prayer_facilities"
            elif "ramadan" in content:
                result = await self.ramadan_guidance()
                response_type = "ramadan_guidance"
            elif "women" in content or "female" in content:
                result = await self.female_specific_guidance()
                response_type = "female_guidance"
            else:
                # General cultural etiquette
                context_type = self._extract_context_type(content)
                result = await self.cultural_etiquette_guide(context_type)
                response_type = "cultural_etiquette"
            
            return {
                "content": self._format_cultural_response(result, response_type),
                "metadata": {
                    "agent": self.name,
                    "response_type": response_type,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in cultural advisor agent: {str(e)}")
            return {
                "content": "I apologize, I couldn't process your cultural inquiry. Please try again.",
                "metadata": {"error": str(e)}
            }
    
    def _extract_location(self, text: str) -> str:
        """Extract location from query text."""
        locations = ["gangnam", "itaewon", "myeongdong", "hongdae", "seoul"]
        
        for location in locations:
            if location in text:
                return location.capitalize()
                
        return "Gangnam"  # Default to Gangnam (clinic area)
    
    def _extract_context_type(self, text: str) -> str:
        """Extract context type from query."""
        contexts = ["clinic", "accommodation", "restaurant", "transport"]
        
        for context in contexts:
            if context in text:
                return context
                
        return "general"
    
    def _format_cultural_response(self, result: Dict[str, Any], response_type: str) -> str:
        """Format cultural response for user display."""
        # Implement proper formatting based on response type
        return str(result)  # Placeholder