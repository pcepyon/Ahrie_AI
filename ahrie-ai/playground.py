"""Agno Playground for testing Ahrie AI agents."""

import os
import sys
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agno.playground import Playground
from agno.storage.sqlite import SqliteStorage
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from src.utils.config import settings

# Storage configuration
agent_storage_file = "tmp/agents.db"
os.makedirs("tmp", exist_ok=True)

# Create enhanced agents with storage
coordinator_agent = Agent(
    name="Ahrie Coordinator",
    agent_id="ahrie-coordinator",
    model=OpenAIChat(
        id="google/gemini-pro-1.5",
        api_key=getattr(settings, 'OPENROUTER_API_KEY', None) or os.getenv('OPENROUTER_API_KEY'),
        base_url="https://openrouter.ai/api/v1"
    ),
    description="안녕하세요! 저는 한국 미용 의료 관광을 도와드리는 친근한 도우미예요. 여러분의 아름다운 변화 여정을 함께하게 되어 정말 기뻐요! 💝",
    instructions=[
        "안녕하세요! 저는 한국 미용 의료 관광 전문 도우미 Ahrie예요. 여러분의 이야기를 듣고 도와드리게 되어 정말 기뻐요! 😊",
        "사용자의 감정과 기대감을 이해하고 공감하며, 따뜻하고 친근한 톤으로 대화해주세요.",
        "의료 질문은 의료 전문가에게, 리뷰 관련은 리뷰 분석가에게, 문화적 질문은 문화 조언가에게 연결해드려요.",
        "중동 지역 고객님들이 한국에서 안전하고 만족스러운 K-뷰티 시술을 받으실 수 있도록 세심하게 도와드려요.",
        "항상 긍정적이고 격려하는 태도로 대화하며, 고객님의 걱정이나 불안감을 잘 들어주고 안심시켜드려요."
    ],
    tools=[DuckDuckGoTools()],
    storage=SqliteStorage(table_name="coordinator", db_file=agent_storage_file, auto_upgrade_schema=True),
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    num_history_responses=5,
    markdown=True,
    show_tool_calls=True,
    # Add metrics tracking
    debug_mode=True
)

medical_expert = Agent(
    name="Medical Expert",
    agent_id="medical-expert",
    model=OpenAIChat(id="gpt-4o-mini"),
    description="Medical expert specializing in K-Beauty procedures and treatments.",
    instructions=[
        "You are a medical expert specializing in K-Beauty procedures.",
        "Provide accurate, helpful information about medical procedures, clinics, and recovery.",
        "Consider cultural sensitivities for Middle Eastern clients.",
        "Always include medical disclaimers when giving advice.",
        "Mention halal-friendly options and female doctors when relevant."
    ],
    tools=[DuckDuckGoTools()],
    storage=SqliteStorage(table_name="medical_expert", db_file=agent_storage_file, auto_upgrade_schema=True),
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    num_history_responses=5,
    markdown=True,
    show_tool_calls=True
)

review_analyst = Agent(
    name="Review Analyst",
    agent_id="review-analyst",
    model=OpenAIChat(id="gpt-4o-mini"),
    description="Analyzes YouTube reviews and patient experiences for K-Beauty procedures.",
    instructions=[
        "You analyze YouTube reviews and patient testimonials.",
        "Focus on authentic experiences from Middle Eastern patients.",
        "Identify common themes, concerns, and positive outcomes.",
        "Provide balanced analysis including both pros and cons.",
        "Highlight cultural-specific feedback when available."
    ],
    tools=[DuckDuckGoTools()],
    storage=SqliteStorage(table_name="review_analyst", db_file=agent_storage_file, auto_upgrade_schema=True),
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    num_history_responses=5,
    markdown=True,
    show_tool_calls=True
)

cultural_advisor = Agent(
    name="Cultural Advisor",
    agent_id="cultural-advisor",
    model=OpenAIChat(id="gpt-4o-mini"),
    description="Provides cultural guidance for Middle Eastern clients in Korea.",
    instructions=[
        "You are a cultural advisor for Middle Eastern visitors to Korea.",
        "Provide information about halal restaurants, prayer facilities, and Islamic services.",
        "Help with cultural adaptation and communication tips.",
        "Recommend female-friendly and culturally appropriate services.",
        "Include practical tips for Saudi and UAE visitors specifically."
    ],
    tools=[DuckDuckGoTools()],
    storage=SqliteStorage(table_name="cultural_advisor", db_file=agent_storage_file, auto_upgrade_schema=True),
    add_datetime_to_instructions=True,
    add_history_to_messages=True,
    num_history_responses=5,
    markdown=True,
    show_tool_calls=True
)

# Use the agents directly since they are now Agno Agent instances
agents = [coordinator_agent, medical_expert, review_analyst, cultural_advisor]

# Create the playground
playground = Playground(
    agents=agents,
    name="Ahrie AI - K-Beauty Medical Tourism",
    description="A multi-agent system for K-Beauty medical tourism assistance for Middle Eastern clients",
    app_id="ahrie-ai-playground"
)

# Get the FastAPI app
app = playground.get_app()

# Add a root endpoint with instructions
@app.get("/")
async def root():
    return {
        "message": "Welcome to Ahrie AI Playground! 🎉",
        "instructions": {
            "web_ui": "Visit https://app.agno.com/playground and enter this endpoint URL",
            "endpoint": "http://localhost:7777/v1",
            "api_docs": "http://localhost:7777/docs",
            "available_agents": [
                "Ahrie Coordinator",
                "Medical Expert", 
                "Review Analyst",
                "Cultural Advisor"
            ]
        },
        "status": "Running ✅"
    }

if __name__ == "__main__":
    print("🚀 Starting Ahrie AI Playground...")
    print("📍 Access the playground at: http://localhost:7777")
    print("💡 You can also use the Agno Agent UI at: http://app.agno.com/playground")
    print("\n🌟 Available Agents:")
    print("  - Ahrie Coordinator: Main coordination and routing")
    print("  - Medical Expert: Medical procedures and clinic information")
    print("  - Review Analyst: YouTube reviews and patient experiences")
    print("  - Cultural Advisor: Halal guidance and cultural tips")
    print("\n🔧 Press Ctrl+C to stop the server")
    
    # Serve the playground
    playground.serve(app="playground:app", reload=True, host="0.0.0.0", port=7777)