"""Direct test for YouTube Scraper functionality only."""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variables if not set
if not os.getenv('YOUTUBE_API_KEY'):
    # Read from .env file
    from dotenv import load_dotenv
    load_dotenv()

async def test_youtube_scraper():
    """Test YouTube Scraper directly."""
    
    print("🧪 Testing YouTube Scraper Directly...")
    print("=" * 50)
    
    try:
        # Import here to avoid early import errors
        # Direct import to avoid __init__.py dependencies
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "youtube_scraper", 
            "src/scrapers/youtube_scraper.py"
        )
        youtube_module = importlib.util.module_from_spec(spec)
        
        # Temporarily add required modules to sys.modules
        sys.modules['src'] = type(sys)('src')
        sys.modules['src.utils'] = type(sys)('src.utils')
        sys.modules['src.utils.config'] = type(sys)('src.utils.config')
        
        # Create a mock settings object
        class MockSettings:
            YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
        
        sys.modules['src.utils.config'].settings = MockSettings()
        
        # Now load the module
        spec.loader.exec_module(youtube_module)
        YouTubeScraper = youtube_module.YouTubeScraper
        
        # Check YouTube API key
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            print("❌ YOUTUBE_API_KEY not found in environment")
            return
        
        print(f"✅ YouTube API Key found: {api_key[:10]}...")
        
        # Initialize scraper
        scraper = YouTubeScraper()
        print("✅ YouTube Scraper initialized")
        
        # Test 1: Search for videos
        print("\n📹 Test 1: Searching for rhinoplasty videos...")
        videos = await scraper.search_videos(
            query="Korea rhinoplasty review experience",
            max_results=3,
            language="en"
        )
        
        print(f"Found {len(videos)} videos")
        for i, video in enumerate(videos, 1):
            print(f"\n  Video {i}:")
            print(f"  - Title: {video.get('title', 'N/A')}")
            print(f"  - Video ID: {video.get('video_id', 'N/A')}")
            print(f"  - Views: {video.get('view_count', 0):,}")
            print(f"  - Has captions: {video.get('has_captions', False)}")
        
        # Test 2: Get transcript for first video
        if videos:
            print("\n\n📝 Test 2: Getting transcript for first video...")
            video_id = videos[0]['video_id']
            transcript_data = await scraper.get_video_transcript(
                video_id=video_id,
                languages=['en', 'ko', 'ar']
            )
            
            if transcript_data['success']:
                print(f"✅ Transcript retrieved successfully!")
                print(f"  - Language: {transcript_data['language']}")
                print(f"  - Is auto-generated: {transcript_data['is_generated']}")
                print(f"  - Length: {len(transcript_data['transcript'])} characters")
                print(f"  - Preview: {transcript_data['transcript'][:200]}...")
            else:
                print(f"❌ Failed to get transcript: {transcript_data['error']}")
        
        # Test 3: Search and analyze reviews
        print("\n\n🔍 Test 3: Search and analyze rhinoplasty reviews...")
        analyzed_videos = await scraper.search_and_analyze_reviews(
            procedure="rhinoplasty",
            language="en",
            max_videos=2
        )
        
        for i, video in enumerate(analyzed_videos, 1):
            print(f"\n📺 Analyzed Video {i}:")
            print(f"  Title: {video.get('title', 'N/A')}")
            print(f"  Channel: {video.get('channel_title', 'N/A')}")
            
            insights = video.get('insights', {})
            if insights.get('has_transcript'):
                print(f"\n  📊 Analysis Results:")
                print(f"  - Mentions pain: {insights.get('mentions_pain', False)}")
                print(f"  - Mentions recovery: {insights.get('mentions_recovery', False)}")
                print(f"  - Mentions satisfaction: {insights.get('mentions_satisfaction', False)}")
                print(f"  - Mentions cost: {insights.get('mentions_cost', False)}")
                print(f"  - Procedure mentioned: {insights.get('procedure_mentioned', False)}")
                print(f"  - Word count: {insights.get('transcript_length', 0)}")
            else:
                print(f"  ❌ No transcript: {insights.get('error', 'Unknown error')}")
        
        print("\n\n✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_youtube_scraper())