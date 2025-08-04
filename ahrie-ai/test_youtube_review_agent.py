"""Test script for YouTube Review Agent functionality."""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.team_orchestrator_v2 import AhrieTeamOrchestratorV2
from src.utils.config import settings

async def test_review_agent():
    """Test the Review Agent's YouTube analysis functionality."""
    
    print("🧪 Testing YouTube Review Agent...")
    print("=" * 50)
    
    try:
        # Initialize orchestrator
        orchestrator = AhrieTeamOrchestratorV2()
        print("✅ Orchestrator initialized successfully")
        
        # Test queries for different procedures
        test_queries = [
            {
                "message": "I want to know about rhinoplasty reviews in Korea",
                "language": "en"
            },
            {
                "message": "أريد معرفة تجارب عملية تجميل الأنف في كوريا",
                "language": "ar"
            }
        ]
        
        for query in test_queries:
            print(f"\n📝 Testing query: {query['message']}")
            print(f"🌐 Language: {query['language']}")
            print("-" * 30)
            
            # Process the query
            response = await orchestrator.process(
                message=query["message"],
                user_id="test_user",
                session_id="test_session",
                language_code=query["language"]
            )
            
            print(f"\n📊 Response:")
            print(f"Content: {response['content'][:500]}...")  # First 500 chars
            print(f"\nMetadata:")
            print(f"- Language: {response['metadata']['language']}")
            print(f"- Reviews analyzed: {response['metadata']['session_state']['reviews_analyzed']}")
            print(f"- Recommendations: {response['metadata']['session_state']['recommendations']}")
            
        # Test direct YouTube scraper functionality
        print("\n\n🔍 Testing Direct YouTube Scraper...")
        print("=" * 50)
        
        from src.scrapers.youtube_scraper import YouTubeScraper
        
        scraper = YouTubeScraper()
        
        # Search for rhinoplasty reviews
        print("\n📹 Searching for rhinoplasty reviews...")
        videos = await scraper.search_and_analyze_reviews(
            procedure="rhinoplasty",
            language="en",
            max_videos=3
        )
        
        for i, video in enumerate(videos, 1):
            print(f"\n📺 Video {i}:")
            print(f"Title: {video.get('title', 'N/A')}")
            print(f"Channel: {video.get('channel_title', 'N/A')}")
            print(f"Views: {video.get('view_count', 0):,}")
            
            if video.get('insights', {}).get('has_transcript'):
                insights = video['insights']
                print(f"\n📝 Transcript Analysis:")
                print(f"- Mentions pain: {insights.get('mentions_pain', False)}")
                print(f"- Mentions recovery: {insights.get('mentions_recovery', False)}")
                print(f"- Mentions satisfaction: {insights.get('mentions_satisfaction', False)}")
                print(f"- Mentions cost: {insights.get('mentions_cost', False)}")
                print(f"- Transcript length: {insights.get('transcript_length', 0)} words")
                print(f"\n🔍 Snippet: {insights.get('snippet', '')[:200]}...")
            else:
                print(f"❌ No transcript available: {video.get('insights', {}).get('error', 'Unknown error')}")
        
        print("\n\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Check if YouTube API key is set
    if not getattr(settings, 'YOUTUBE_API_KEY', None) and not os.getenv('YOUTUBE_API_KEY'):
        print("⚠️  Warning: YOUTUBE_API_KEY not found in settings or environment")
        print("Please set YOUTUBE_API_KEY in your .env file")
        sys.exit(1)
    
    # Run the test
    asyncio.run(test_review_agent())