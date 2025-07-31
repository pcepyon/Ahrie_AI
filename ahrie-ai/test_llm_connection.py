#!/usr/bin/env python3
"""Test script to verify LangDB and OpenRouter connections."""

import os
import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

# Test 1: Environment Variables
print("=== Testing Environment Variables ===")
print(f"LANGDB_API_KEY: {'✓ Set' if os.getenv('LANGDB_API_KEY') else '✗ Missing'}")
print(f"LANGDB_PROJECT_ID: {'✓ Set' if os.getenv('LANGDB_PROJECT_ID') else '✗ Missing'}")
print(f"OPENROUTER_API_KEY: {'✓ Set' if os.getenv('OPENROUTER_API_KEY') else '✗ Missing'}")
print()

# Test 2: Direct LangDB Connection
print("=== Testing LangDB Connection ===")
try:
    from agno.models.langdb import LangDB
    from agno.agent import Agent
    
    # Try different model IDs
    model_ids = [
        "gpt-4o-mini",  # Direct OpenAI
        "openrouter/gemini-2.5-pro",  # Current setting
        "openrouter/google/gemini-2.0-flash",  # Alternative format
        "gemini-2.5-pro"  # Without prefix
    ]
    
    for model_id in model_ids:
        print(f"\nTesting model: {model_id}")
        try:
            model = LangDB(
                id=model_id,
                api_key=os.getenv('LANGDB_API_KEY'),
                project_id=os.getenv('LANGDB_PROJECT_ID')
            )
            
            agent = Agent(
                name="Test Agent",
                model=model,
                instructions=["You are a test agent. Say hello."]
            )
            
            # Test synchronous call
            response = agent.run("Hello, are you working?")
            print(f"✓ Success! Response: {response.content[:50]}...")
            
        except Exception as e:
            print(f"✗ Failed: {str(e)}")
            
except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: OpenRouter Direct Connection
print("\n=== Testing OpenRouter Direct Connection ===")
try:
    from agno.models.openrouter import OpenRouter
    
    model = OpenRouter(
        id="google/gemini-2.0-flash:free",
        api_key=os.getenv('OPENROUTER_API_KEY')
    )
    
    agent = Agent(
        name="OpenRouter Test",
        model=model,
        instructions=["You are a test agent."]
    )
    
    response = agent.run("Hello from OpenRouter")
    print(f"✓ OpenRouter Success! Response: {response.content[:50]}...")
    
except ImportError:
    print("✗ OpenRouter model not available in Agno")
except Exception as e:
    print(f"✗ OpenRouter Error: {e}")

# Test 4: Check LangDB HTTP endpoint
print("\n=== Testing LangDB HTTP Endpoint ===")
try:
    import httpx
    
    async def test_langdb_endpoint():
        headers = {
            "Authorization": f"Bearer {os.getenv('LANGDB_API_KEY')}",
            "x-project-id": os.getenv('LANGDB_PROJECT_ID')
        }
        
        # Test endpoint
        base_url = f"https://api.us-east-1.langdb.ai/{os.getenv('LANGDB_PROJECT_ID')}/v1"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{base_url}/models", headers=headers)
                if response.status_code == 200:
                    print(f"✓ LangDB API accessible")
                    models = response.json()
                    print(f"Available models: {models}")
                else:
                    print(f"✗ LangDB API returned: {response.status_code}")
                    print(f"Response: {response.text}")
            except Exception as e:
                print(f"✗ LangDB API error: {e}")
    
    asyncio.run(test_langdb_endpoint())
    
except ImportError:
    print("✗ httpx not installed")
except Exception as e:
    print(f"✗ Error testing endpoint: {e}")

print("\n=== Recommendations ===")
print("1. If OpenRouter models fail through LangDB, use direct OpenAI models")
print("2. Check LangDB dashboard for supported OpenRouter models")
print("3. Verify API keys are correct and have proper permissions")
print("4. Consider using 'gpt-4o-mini' as fallback")