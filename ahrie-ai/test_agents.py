"""Test script for Ahrie AI agents."""

import asyncio
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.coordinator import CoordinatorAgent
from src.agents.medical_expert import MedicalExpertAgent
from src.agents.review_analyst import ReviewAnalystAgent
from src.agents.cultural_advisor import CulturalAdvisorAgent


async def test_coordinator_agent():
    """Test the Coordinator Agent."""
    print("\n🤖 Testing Coordinator Agent...")
    print("-" * 50)
    
    coordinator = CoordinatorAgent()
    
    # Test 1: General inquiry
    print("\n📝 Test 1: General greeting")
    response = await coordinator.process("안녕하세요! 한국에서 코성형을 하고 싶어요.")
    print(f"Response: {response['content']}\n")
    
    # Test 2: Medical inquiry
    print("📝 Test 2: Medical inquiry")
    response = await coordinator.process("What are the best clinics for rhinoplasty in Seoul?")
    print(f"Response: {response['content']}\n")
    
    # Test 3: Cultural inquiry
    print("📝 Test 3: Cultural inquiry")
    response = await coordinator.process("Where can I find halal restaurants near Gangnam?")
    print(f"Response: {response['content']}\n")


async def test_medical_expert():
    """Test the Medical Expert Agent."""
    print("\n🏥 Testing Medical Expert Agent...")
    print("-" * 50)
    
    medical = MedicalExpertAgent()
    
    # Test medical queries
    print("\n📝 Testing medical procedure inquiry")
    response = await medical.process("Tell me about facial contouring surgery in Korea")
    print(f"Response: {response['content']}\n")


async def test_review_analyst():
    """Test the Review Analyst Agent."""
    print("\n📹 Testing Review Analyst Agent...")
    print("-" * 50)
    
    review = ReviewAnalystAgent()
    
    # Test review analysis
    print("\n📝 Testing review analysis")
    response = await review.process("What do YouTube reviews say about Banobagi clinic?")
    print(f"Response: {response['content']}\n")


async def test_cultural_advisor():
    """Test the Cultural Advisor Agent."""
    print("\n🕌 Testing Cultural Advisor Agent...")
    print("-" * 50)
    
    cultural = CulturalAdvisorAgent()
    
    # Test cultural guidance
    print("\n📝 Testing cultural guidance")
    response = await cultural.process("Where are the prayer rooms in Seoul hospitals?")
    print(f"Response: {response['content']}\n")


async def main():
    """Run all tests."""
    print("🚀 Starting Ahrie AI Agent Tests")
    print("=" * 50)
    
    try:
        # Test Coordinator Agent
        await test_coordinator_agent()
        
        # Test other agents
        await test_medical_expert()
        await test_review_analyst()
        await test_cultural_advisor()
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())