#!/usr/bin/env python3
"""
Debug script for LangDB integration issues.
Tests different model ID formats and configurations.
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

def test_langdb_models():
    """Test different LangDB model configurations."""
    
    # Check environment
    api_key = os.getenv('LANGDB_API_KEY')
    project_id = os.getenv('LANGDB_PROJECT_ID')
    
    if not api_key or not project_id:
        logger.error("Missing LANGDB_API_KEY or LANGDB_PROJECT_ID")
        return
    
    logger.info(f"Using project: {project_id}")
    
    # Test 1: Initialize LangDB tracing
    logger.info("\n=== Test 1: Initialize LangDB tracing ===")
    try:
        from pylangdb.agno import init
        init()
        logger.info("✅ LangDB tracing initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize tracing: {e}")
        return
    
    # Test 2: Import LangDB model
    logger.info("\n=== Test 2: Import LangDB model ===")
    try:
        from agno.models.langdb import LangDB
        logger.info("✅ LangDB model imported")
    except Exception as e:
        logger.error(f"❌ Failed to import LangDB: {e}")
        return
    
    # Test different model ID formats
    model_ids = [
        "gpt-4",
        "openai/gpt-4", 
        "openai/gpt-4.1",
        "gpt-4o",
        "openai/gpt-4o",
        "gpt-4o-mini",
        "openai/gpt-4o-mini"
    ]
    
    for model_id in model_ids:
        logger.info(f"\n=== Testing model ID: {model_id} ===")
        try:
            model = LangDB(
                id=model_id,
                api_key=api_key,
                project_id=project_id
            )
            logger.info(f"✅ Model created successfully: {model_id}")
            
            # Try to use the model
            from agno.agent import Agent
            agent = Agent(
                name="Test Agent",
                model=model,
                instructions=["You are a test agent"]
            )
            
            # Test a simple query
            response = agent.run("Say 'Hello'")
            logger.info(f"✅ Model response: {response.content[:50]}...")
            break  # Success, stop trying other formats
            
        except Exception as e:
            logger.error(f"❌ Failed with {model_id}: {type(e).__name__}: {str(e)}")
            if "Json deserialize error" in str(e):
                logger.error("   -> JSON deserialization issue")
            if "missing field `type`" in str(e):
                logger.error("   -> Missing 'type' field in response")


def test_openrouter_alternative():
    """Test OpenRouter as an alternative."""
    logger.info("\n=== Testing OpenRouter Alternative ===")
    
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    if not openrouter_key:
        logger.warning("No OPENROUTER_API_KEY found")
        return
    
    try:
        from agno.models.openrouter import OpenRouter
        model = OpenRouter(
            id="openai/gpt-4",
            api_key=openrouter_key
        )
        logger.info("✅ OpenRouter model created")
        
        from agno.agent import Agent
        agent = Agent(
            name="Test Agent",
            model=model,
            instructions=["You are a test agent"]
        )
        
        response = agent.run("Say 'Hello'")
        logger.info(f"✅ OpenRouter response: {response.content}")
        
    except Exception as e:
        logger.error(f"❌ OpenRouter failed: {e}")


def check_langdb_api():
    """Check LangDB API directly."""
    logger.info("\n=== Checking LangDB API ===")
    
    api_key = os.getenv('LANGDB_API_KEY')
    project_id = os.getenv('LANGDB_PROJECT_ID')
    
    if not api_key or not project_id:
        return
    
    import requests
    
    # Test API endpoint
    base_url = f"https://api.us-east-1.langdb.ai/{project_id}/v1"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test models endpoint
        response = requests.get(f"{base_url}/models", headers=headers)
        logger.info(f"API Response Status: {response.status_code}")
        if response.ok:
            logger.info(f"Available models: {response.json()}")
        else:
            logger.error(f"API Error: {response.text}")
    except Exception as e:
        logger.error(f"API check failed: {e}")


if __name__ == "__main__":
    print("=== LangDB Debug Script ===\n")
    
    # Run tests
    test_langdb_models()
    test_openrouter_alternative()
    check_langdb_api()
    
    print("\n=== Debug Complete ===")