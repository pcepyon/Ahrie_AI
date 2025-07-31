#!/usr/bin/env python3
"""Direct test of the Team Orchestrator API call."""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

async def test_orchestrator():
    """Test the orchestrator directly."""
    print("=== Testing Team Orchestrator Directly ===\n")
    
    try:
        from src.agents.team_orchestrator_v2 import AhrieTeamOrchestratorV2
        
        # Initialize orchestrator
        print("1. Initializing orchestrator...")
        orchestrator = AhrieTeamOrchestratorV2()
        print("✓ Orchestrator initialized successfully\n")
        
        # Test message
        test_message = "Hello, I want to know about rhinoplasty in Korea"
        print(f"2. Sending test message: '{test_message}'")
        
        # Process message
        response = await orchestrator.process(
            message=test_message,
            user_id="test_user_123",
            session_id="test_session_456",
            language_code="en"
        )
        
        print("\n3. Response received:")
        print(f"Content: {response['content'][:200]}...")
        print(f"Metadata: {response['metadata']}")
        
        # Check if API was actually called
        print("\n4. Session insights:")
        insights = orchestrator.get_session_insights()
        print(f"User journey: {insights['user_journey']}")
        print(f"Recommendations: {insights['recommendations']}")
        
    except Exception as e:
        print(f"\n✗ Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting direct orchestrator test...\n")
    asyncio.run(test_orchestrator())