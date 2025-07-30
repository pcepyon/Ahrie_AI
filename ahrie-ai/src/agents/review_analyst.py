"""YouTube Review Analyst Agent for analyzing K-Beauty medical tourism reviews."""

from typing import Dict, List, Optional, Any, Tuple
from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
import logging
from datetime import datetime
import asyncio
import os
from src.utils.config import settings

logger = logging.getLogger(__name__)


class ReviewAnalystAgent:
    """
    Review analyst agent specialized in analyzing YouTube reviews and testimonials.
    
    Analyzes Arabic and English YouTube content about K-Beauty medical tourism experiences,
    extracting insights about clinics, procedures, and patient satisfaction.
    """
    
    def __init__(self, name: str = "ReviewAnalyst"):
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
            description="Review analyst specializing in K-Beauty medical tourism YouTube content.",
            instructions=[
                "You are a review analyst specializing in K-Beauty medical tourism YouTube content.",
                "Analyze reviews in Arabic and English to extract insights about patient experiences.",
                "Focus on clinic quality, procedure outcomes, and patient satisfaction.",
                "Identify common concerns and recommendations from Middle Eastern patients.",
                "Provide balanced analysis considering both positive and negative feedback."
            ],
            tools=[DuckDuckGoTools()],
            markdown=True,
            show_tool_calls=True
        )
        self.youtube_client = None  # Will be initialized with YouTube API
        self.sentiment_analyzer = None  # Will be initialized with sentiment analysis model
        
    async def search_youtube_reviews(self, 
                                   procedure: str, 
                                   clinic: Optional[str] = None,
                                   language: str = "ar") -> List[Dict[str, Any]]:
        """
        Search YouTube for reviews about specific procedures or clinics.
        
        Args:
            procedure: Medical procedure to search for
            clinic: Optional clinic name to filter results
            language: Language code (ar for Arabic, en for English)
            
        Returns:
            List of relevant YouTube videos with metadata
        """
        search_query = self._build_search_query(procedure, clinic, language)
        
        # Mock data for now - will integrate with YouTube API
        mock_results = [
            {
                "video_id": "abc123",
                "title": "تجربتي مع عملية تجميل الأنف في كوريا",
                "channel": "Saudi Beauty Journey",
                "views": 150000,
                "likes": 8500,
                "published_date": "2024-01-15",
                "duration": "15:30",
                "language": "ar",
                "thumbnail": "https://example.com/thumb1.jpg"
            },
            {
                "video_id": "def456",
                "title": "My Korean Plastic Surgery Experience - Honest Review",
                "channel": "UAE Lifestyle Vlog",
                "views": 89000,
                "likes": 5200,
                "published_date": "2024-02-20",
                "duration": "22:45",
                "language": "en",
                "thumbnail": "https://example.com/thumb2.jpg"
            }
        ]
        
        return mock_results
    
    def _build_search_query(self, procedure: str, clinic: Optional[str], language: str) -> str:
        """
        Build YouTube search query based on parameters.
        
        Args:
            procedure: Procedure name
            clinic: Optional clinic name
            language: Language preference
            
        Returns:
            Formatted search query
        """
        base_terms = {
            "ar": ["كوريا", "تجميل", "تجربتي", "عملية"],
            "en": ["Korea", "plastic surgery", "experience", "review"]
        }
        
        query_parts = base_terms.get(language, base_terms["en"])
        query_parts.append(procedure)
        
        if clinic:
            query_parts.append(clinic)
            
        return " ".join(query_parts)
    
    async def analyze_video_content(self, video_id: str) -> Dict[str, Any]:
        """
        Analyze content of a specific YouTube video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Detailed analysis of video content
        """
        # This would fetch video captions/comments and analyze them
        # Mock analysis for now
        analysis = {
            "video_id": video_id,
            "sentiment": {
                "overall": "positive",
                "score": 0.85,
                "aspects": {
                    "clinic_service": 0.9,
                    "results_satisfaction": 0.88,
                    "value_for_money": 0.75,
                    "recovery_experience": 0.7
                }
            },
            "key_topics": [
                "Professional staff",
                "Clean facilities", 
                "Natural results",
                "Language barrier mentioned",
                "Satisfied with outcome"
            ],
            "mentioned_clinics": ["Banobagi", "ID Hospital"],
            "mentioned_procedures": ["Rhinoplasty", "Fat grafting"],
            "warnings_or_concerns": [
                "Communication challenges without translator",
                "Recovery took longer than expected"
            ],
            "recommendations": [
                "Bring a translator",
                "Book accommodation near clinic",
                "Plan for 2-week stay minimum"
            ]
        }
        
        return analysis
    
    async def aggregate_review_insights(self, 
                                      procedure: str,
                                      num_reviews: int = 10) -> Dict[str, Any]:
        """
        Aggregate insights from multiple reviews for a procedure.
        
        Args:
            procedure: Procedure to analyze
            num_reviews: Number of reviews to aggregate
            
        Returns:
            Aggregated insights and statistics
        """
        # Search for reviews
        ar_reviews = await self.search_youtube_reviews(procedure, language="ar")
        en_reviews = await self.search_youtube_reviews(procedure, language="en")
        
        all_reviews = ar_reviews + en_reviews
        all_reviews = all_reviews[:num_reviews]  # Limit to requested number
        
        # Analyze each video
        analyses = []
        for review in all_reviews:
            analysis = await self.analyze_video_content(review["video_id"])
            analyses.append(analysis)
        
        # Aggregate findings
        aggregated = {
            "procedure": procedure,
            "total_reviews_analyzed": len(analyses),
            "overall_sentiment": self._calculate_overall_sentiment(analyses),
            "top_clinics": self._aggregate_clinics(analyses),
            "common_positives": self._extract_common_themes(analyses, "positive"),
            "common_concerns": self._extract_common_themes(analyses, "negative"),
            "average_satisfaction_scores": self._calculate_average_scores(analyses),
            "key_recommendations": self._aggregate_recommendations(analyses),
            "analysis_date": datetime.now().isoformat()
        }
        
        return aggregated
    
    def _calculate_overall_sentiment(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall sentiment from multiple analyses."""
        total_score = sum(a["sentiment"]["score"] for a in analyses)
        avg_score = total_score / len(analyses) if analyses else 0
        
        return {
            "average_score": round(avg_score, 2),
            "interpretation": self._interpret_sentiment_score(avg_score),
            "distribution": {
                "positive": sum(1 for a in analyses if a["sentiment"]["overall"] == "positive"),
                "neutral": sum(1 for a in analyses if a["sentiment"]["overall"] == "neutral"),
                "negative": sum(1 for a in analyses if a["sentiment"]["overall"] == "negative")
            }
        }
    
    def _interpret_sentiment_score(self, score: float) -> str:
        """Interpret sentiment score into human-readable format."""
        if score >= 0.8:
            return "Highly Positive"
        elif score >= 0.6:
            return "Positive"
        elif score >= 0.4:
            return "Mixed"
        elif score >= 0.2:
            return "Negative"
        else:
            return "Highly Negative"
    
    def _aggregate_clinics(self, analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Aggregate clinic mentions and ratings."""
        clinic_mentions = {}
        
        for analysis in analyses:
            for clinic in analysis.get("mentioned_clinics", []):
                if clinic not in clinic_mentions:
                    clinic_mentions[clinic] = {
                        "name": clinic,
                        "mention_count": 0,
                        "sentiment_scores": []
                    }
                clinic_mentions[clinic]["mention_count"] += 1
                clinic_mentions[clinic]["sentiment_scores"].append(
                    analysis["sentiment"]["score"]
                )
        
        # Calculate average sentiment for each clinic
        for clinic_data in clinic_mentions.values():
            scores = clinic_data["sentiment_scores"]
            clinic_data["average_sentiment"] = round(sum(scores) / len(scores), 2)
            del clinic_data["sentiment_scores"]  # Remove raw scores
        
        # Sort by mention count
        return sorted(
            clinic_mentions.values(), 
            key=lambda x: x["mention_count"], 
            reverse=True
        )[:5]  # Top 5 clinics
    
    def _extract_common_themes(self, analyses: List[Dict[str, Any]], theme_type: str) -> List[str]:
        """Extract common positive or negative themes."""
        theme_key = "key_topics" if theme_type == "positive" else "warnings_or_concerns"
        all_themes = []
        
        for analysis in analyses:
            all_themes.extend(analysis.get(theme_key, []))
        
        # Count occurrences (simple approach - enhance with NLP)
        theme_counts = {}
        for theme in all_themes:
            theme_lower = theme.lower()
            if theme_lower in theme_counts:
                theme_counts[theme_lower] += 1
            else:
                theme_counts[theme_lower] = 1
        
        # Return top themes
        sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
        return [theme.title() for theme, _ in sorted_themes[:5]]
    
    def _calculate_average_scores(self, analyses: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate average satisfaction scores across different aspects."""
        aspect_scores = {
            "clinic_service": [],
            "results_satisfaction": [],
            "value_for_money": [],
            "recovery_experience": []
        }
        
        for analysis in analyses:
            aspects = analysis["sentiment"].get("aspects", {})
            for aspect, score_list in aspect_scores.items():
                if aspect in aspects:
                    score_list.append(aspects[aspect])
        
        # Calculate averages
        avg_scores = {}
        for aspect, scores in aspect_scores.items():
            if scores:
                avg_scores[aspect] = round(sum(scores) / len(scores), 2)
            else:
                avg_scores[aspect] = 0.0
                
        return avg_scores
    
    def _aggregate_recommendations(self, analyses: List[Dict[str, Any]]) -> List[str]:
        """Aggregate common recommendations from reviews."""
        all_recommendations = []
        
        for analysis in analyses:
            all_recommendations.extend(analysis.get("recommendations", []))
        
        # Count and return most common (enhance with NLP)
        rec_counts = {}
        for rec in all_recommendations:
            rec_lower = rec.lower()
            if rec_lower in rec_counts:
                rec_counts[rec_lower] += 1
            else:
                rec_counts[rec_lower] = 1
        
        sorted_recs = sorted(rec_counts.items(), key=lambda x: x[1], reverse=True)
        return [rec.title() for rec, _ in sorted_recs[:5]]
    
    def run(self, message: str) -> RunResponse:
        """
        Run the review analyst agent synchronously.
        
        Args:
            message: User's query about reviews
            
        Returns:
            Agent's response
        """
        # Enhance the query with review context
        enhanced_query = f"As a YouTube review analyst for K-Beauty medical tourism, please help with: {message}"
        return self.agent.run(enhanced_query)
    
    async def arun(self, message: str) -> RunResponse:
        """
        Run the review analyst agent asynchronously.
        
        Args:
            message: User's query about reviews
            
        Returns:
            Agent's response
        """
        # Enhance the query with review context
        enhanced_query = f"As a YouTube review analyst for K-Beauty medical tourism, please help with: {message}"
        return await self.agent.arun(enhanced_query)
    
    async def process(self, message: str) -> Dict[str, Any]:
        """
        Process review analysis requests.
        
        Args:
            message: Incoming message
            
        Returns:
            Review analysis response
        """
        try:
            content = message.lower()
            
            # Determine the type of review analysis needed
            if "search" in content and "review" in content:
                # Search for reviews
                procedure = self._extract_procedure_from_query(content)
                results = await self.search_youtube_reviews(procedure)
                response_data = {
                    "action": "search_results",
                    "data": results
                }
            elif "analyze" in content and "video" in content:
                # Analyze specific video
                video_id = self._extract_video_id(content)
                analysis = await self.analyze_video_content(video_id)
                response_data = {
                    "action": "video_analysis",
                    "data": analysis
                }
            else:
                # Aggregate insights for a procedure
                procedure = self._extract_procedure_from_query(content)
                insights = await self.aggregate_review_insights(procedure)
                response_data = {
                    "action": "aggregated_insights",
                    "data": insights
                }
            
            return {
                "content": self._format_review_response(response_data),
                "metadata": {
                    "agent": self.name,
                    "response_type": "review_analysis",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in review analyst agent: {str(e)}")
            return {
                "content": "I couldn't analyze the reviews at this moment. Please try again.",
                "metadata": {"error": str(e)}
            }
    
    def _extract_procedure_from_query(self, query: str) -> str:
        """Extract procedure name from query."""
        procedures = ["rhinoplasty", "eyelid", "contouring", "liposuction", "facelift"]
        
        for procedure in procedures:
            if procedure in query:
                return procedure
                
        return "plastic surgery"  # Default
    
    def _extract_video_id(self, query: str) -> str:
        """Extract YouTube video ID from query."""
        # Simple extraction - enhance with regex
        parts = query.split()
        for part in parts:
            if len(part) == 11:  # YouTube IDs are typically 11 characters
                return part
        return "default_id"
    
    def _format_review_response(self, response_data: Dict[str, Any]) -> str:
        """Format review analysis response for user display."""
        # Implement proper formatting based on action type
        return str(response_data)  # Placeholder