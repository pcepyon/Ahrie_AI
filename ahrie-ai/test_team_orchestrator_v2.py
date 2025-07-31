"""Test script for the enhanced team orchestrator v2."""

import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.team_orchestrator_v2 import AhrieTeamOrchestratorV2


async def test_orchestrator():
    """Test the team orchestrator with various queries."""
    
    print("🚀 Starting Ahrie AI Team Orchestrator V2 Test...")
    print("=" * 60)
    
    # Check LangDB configuration
    langdb_configured = bool(os.getenv("LANGDB_API_KEY") and os.getenv("LANGDB_PROJECT_ID"))
    if langdb_configured:
        print("✅ LangDB monitoring is enabled!")
        print(f"📊 View traces at: https://app.langdb.ai/projects/{os.getenv('LANGDB_PROJECT_ID')}")
    else:
        print("ℹ️  LangDB monitoring is not configured (optional)")
    
    try:
        # Initialize the orchestrator
        orchestrator = AhrieTeamOrchestratorV2()
        print("✅ Orchestrator initialized successfully!")
        
        # Test queries
        test_queries = [
            {
                "message": "Hello, I'm interested in rhinoplasty in Korea",
                "language": "en",
                "description": "Basic medical inquiry"
            },
            {
                "message": "Can you find halal restaurants near Gangnam clinics?",
                "language": "en",
                "description": "Cultural/halal inquiry"
            },
            {
                "message": "أريد معلومات عن عيادات التجميل في كوريا",
                "language": "ar",
                "description": "Arabic language test"
            },
            {
                "message": "What are people saying about Banobagi clinic on YouTube?",
                "language": "en",
                "description": "Review analysis request"
            }
        ]
        
        # Run tests
        for i, test in enumerate(test_queries, 1):
            print(f"\n📝 Test {i}: {test['description']}")
            print(f"Query: {test['message']}")
            print("-" * 40)
            
            try:
                # Process the query
                response = await orchestrator.process(
                    message=test['message'],
                    user_id=f"test_user_{i}",
                    session_id=f"test_session_{i}",
                    language_code=test['language']
                )
                
                print(f"Response: {response['content'][:200]}...")
                print(f"Language: {response['metadata']['language']}")
                print(f"Session State: {response['metadata']['session_state']}")
                
            except Exception as e:
                print(f"❌ Error in test {i}: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Get session insights
        print("\n" + "=" * 60)
        print("📊 Session Insights:")
        insights = orchestrator.get_session_insights()
        print(f"User Journey: {insights['user_journey']}")
        print(f"Recommendations: {insights['recommendations']}")
        print(f"Summary: {insights['session_summary']}")
        if insights['monitoring']['langdb_enabled']:
            print(f"\n🔗 LangDB Tracking URL: {insights['monitoring']['tracking_url']}")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY") and not (os.getenv("LANGDB_API_KEY") and os.getenv("LANGDB_PROJECT_ID")):
        print("❌ Error: Either OPENAI_API_KEY or LANGDB credentials must be set!")
        print("\nOption 1: Set OpenAI API key:")
        print("  export OPENAI_API_KEY='your-key-here'")
        print("\nOption 2: Set LangDB credentials for monitoring:")
        print("  export LANGDB_API_KEY='your-langdb-key'")
        print("  export LANGDB_PROJECT_ID='your-project-id'")
        sys.exit(1)
    
    # Run the test
    asyncio.run(test_orchestrator())