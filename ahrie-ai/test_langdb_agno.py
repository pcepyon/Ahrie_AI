#!/usr/bin/env python3
"""
Test script for LangDB integration with Agno framework.

This script verifies that LangDB tracing is properly configured
and working with the Ahrie AI Team Orchestrator V2.

Requirements:
    pip install 'pylangdb[agno]'
    
Environment:
    export LANGDB_API_KEY="your_api_key"
    export LANGDB_PROJECT_ID="your_project_id"
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Check environment variables
def check_environment():
    """Check if required environment variables are set."""
    required_vars = ['LANGDB_API_KEY', 'LANGDB_PROJECT_ID']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set them using:")
        print("   export LANGDB_API_KEY='your_api_key'")
        print("   export LANGDB_PROJECT_ID='your_project_id'")
        return False
    
    print("✅ Environment variables configured")
    print(f"   - LANGDB_PROJECT_ID: {os.getenv('LANGDB_PROJECT_ID')}")
    print(f"   - Dashboard: https://app.langdb.ai/projects/{os.getenv('LANGDB_PROJECT_ID')}")
    return True


async def test_orchestrator():
    """Test the team orchestrator with LangDB monitoring."""
    try:
        from src.agents.team_orchestrator_v2 import AhrieTeamOrchestratorV2
        
        print("\n🚀 Initializing Ahrie Team Orchestrator V2...")
        orchestrator = AhrieTeamOrchestratorV2()
        
        print("\n📝 Testing different types of queries...")
        
        # Test queries
        test_queries = [
            {
                "message": "What are the best clinics for rhinoplasty in Gangnam?",
                "language": "en",
                "description": "Medical query"
            },
            {
                "message": "أين يمكنني أن أجد مطاعم حلال بالقرب من المستشفى؟",
                "language": "ar", 
                "description": "Cultural query in Arabic"
            },
            {
                "message": "Show me YouTube reviews for double eyelid surgery",
                "language": "en",
                "description": "Review query"
            }
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n--- Test {i}: {query['description']} ---")
            print(f"Query: {query['message']}")
            
            result = await orchestrator.process(
                message=query['message'],
                user_id=f"test_user_{i}",
                session_id=f"test_session_{i}",
                language_code=query['language']
            )
            
            print(f"Response: {result['content'][:200]}...")
            print(f"Metadata: {result['metadata']}")
            
            if orchestrator.use_langdb:
                print(f"\n📊 View trace in LangDB: https://app.langdb.ai/projects/{os.getenv('LANGDB_PROJECT_ID')}")
        
        # Get session insights
        print("\n📈 Session Insights:")
        insights = orchestrator.get_session_insights()
        print(f"   - User interests: {len(insights['user_journey']['interests'])} procedures")
        print(f"   - Clinics recommended: {len(insights['recommendations']['clinics'])}")
        print(f"   - Reviews analyzed: {insights['recommendations']['reviews_analyzed']}")
        print(f"   - Monitoring URL: {insights['monitoring']['tracking_url']}")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main test function."""
    print("=== LangDB + Agno Integration Test ===")
    
    # Check environment
    if not check_environment():
        return
    
    # Check if pylangdb is installed
    try:
        import pylangdb
        print("✅ pylangdb is installed")
    except ImportError:
        print("❌ pylangdb not installed")
        print("   Install with: pip install 'pylangdb[agno]'")
        return
    
    # Run tests
    await test_orchestrator()
    
    print("\n🎉 Test completed! Check your LangDB dashboard for traces.")


if __name__ == "__main__":
    asyncio.run(main())