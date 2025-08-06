#!/usr/bin/env python3
"""
Simple test to verify LangDB setup.
"""

import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_langdb():
    """Test basic LangDB functionality."""
    
    # Check environment
    api_key = os.getenv('LANGDB_API_KEY')
    project_id = os.getenv('LANGDB_PROJECT_ID')
    
    print(f"LANGDB_API_KEY exists: {bool(api_key)}")
    print(f"LANGDB_PROJECT_ID: {project_id}")
    
    if not api_key or not project_id:
        print("❌ Missing required environment variables")
        return
    
    # Test 1: Import and init
    print("\n1. Testing import and init...")
    try:
        from pylangdb.agno import init
        init()
        print("✅ LangDB init successful")
    except ImportError:
        print("❌ pylangdb[agno] not installed")
        print("   Run: pip install 'pylangdb[agno]'")
        return
    except Exception as e:
        print(f"❌ Init failed: {e}")
        return
    
    # Test 2: Create model
    print("\n2. Testing model creation...")
    try:
        from agno.models.langdb import LangDB
        
        # Test with simple model ID
        model = LangDB(
            id="gpt-4",
            api_key=api_key,
            project_id=project_id
        )
        print("✅ Model created successfully")
        
    except Exception as e:
        print(f"❌ Model creation failed: {type(e).__name__}: {e}")
        
        # Try with OpenRouter instead
        print("\n3. Trying OpenRouter fallback...")
        try:
            from agno.models.openrouter import OpenRouter
            openrouter_key = os.getenv('OPENROUTER_API_KEY')
            
            if openrouter_key:
                model = OpenRouter(
                    id="openai/gpt-4o-mini",
                    api_key=openrouter_key
                )
                print("✅ OpenRouter model created successfully")
            else:
                print("❌ No OPENROUTER_API_KEY found")
                
        except Exception as e2:
            print(f"❌ OpenRouter also failed: {e2}")


if __name__ == "__main__":
    test_langdb()