#!/usr/bin/env python3
"""Simple test of Team without complex tools."""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

async def test_simple_team():
    """Test a simple team configuration."""
    print("=== Testing Simple Team Configuration ===\n")
    
    try:
        from agno.team import Team
        from agno.agent import Agent
        from agno.models.langdb import LangDB
        
        # Simple model
        model = LangDB(
            id="openrouter/gemini-2.5-pro",
            api_key=os.getenv('LANGDB_API_KEY'),
            project_id=os.getenv('LANGDB_PROJECT_ID')
        )
        
        # Simple team with minimal agents
        team = Team(
            name="Simple Test Team",
            mode="coordinate",
            model=model,
            members=[
                Agent(
                    name="Assistant",
                    role="Helpful assistant",
                    model=model,
                    instructions=["You are a helpful assistant for K-Beauty tourism"],
                    markdown=True
                )
            ],
            instructions=["Help users with K-Beauty medical tourism questions"],
            markdown=True
        )
        
        # Test message
        print("Sending test message...")
        response = await team.arun("Tell me about rhinoplasty in Korea")
        
        print(f"\nResponse: {response.content[:200]}...")
        print("\n✓ API call successful!")
        
    except Exception as e:
        print(f"\n✗ Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_team())