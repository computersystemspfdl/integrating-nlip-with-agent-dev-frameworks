"""
LlamaIndex Agent for Inter-Agent Communication Demo

This agent executes the actual weather tool implementations and serves
requests delegated from the LangChain agent via NLIP protocol.
"""

import asyncio
import os
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

from llama_index.core.tools import FunctionTool
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.workflow import Context
from llama_index.llms.openai_like import OpenAILike

# Import NLIP components
from nlip_sdk.nlip import NLIP_Factory
from nlip_sdk import nlip
from nlip_server import server

# Import shared utilities
from ..shared.weather_tools import get_weather_alerts, get_weather_forecast

# Load environment variables
load_dotenv()


class LlamaIndexApplication(server.NLIP_Application):
    """LlamaIndex application for inter-agent communication."""
    
    async def startup(self):
        print("🔧 Starting LlamaIndex Agent...")
        print("This agent executes weather tools for requests delegated via NLIP protocol")

    async def shutdown(self):
        print("🛑 Shutting down LlamaIndex Agent")
        return None

    async def create_session(self) -> server.NLIP_Session:
        return LlamaIndexSession()


class LlamaIndexSession(server.NLIP_Session):
    """Chat session using LlamaIndex with actual tool implementations."""
    
    def __init__(self):
        super().__init__()
        self.llm = None
        self.agent = None
        self.tools = []
        self.context = None

    async def start(self):
        """Initialize LlamaIndex components for tool execution."""
        try:
            print("🔧 Initializing LlamaIndex components...")
            
            # Check for API key
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY environment variable is required. Get your key from https://openrouter.ai/")
            
            print(f"🔑 Using OpenRouter API key: {api_key[:10]}...")
            
            # Initialize Claude model via OpenRouter
            self.llm = OpenAILike(
                model="anthropic/claude-3.5-sonnet",
                api_key=api_key,
                api_base="https://openrouter.ai/api/v1",
                temperature=0.7,
                context_window=200000,
                is_chat_model=True,
                is_function_calling_model=True,
            )
            
            # Create FunctionTool objects from our async functions
            self.tools = [
                FunctionTool.from_defaults(
                    fn=get_weather_alerts,
                    name="get_weather_alerts",
                    description="Get weather alerts for a US state. Takes a state code like 'CA', 'NY', 'IN'."
                ),
                FunctionTool.from_defaults(
                    fn=get_weather_forecast,
                    name="get_weather_forecast", 
                    description="Get weather forecast for coordinates. Takes latitude and longitude as numbers."
                ),
            ]
            
            # Create LlamaIndex FunctionAgent
            self.agent = FunctionAgent(
                tools=self.tools,
                llm=self.llm,
                verbose=True,
                system_prompt=(
                    "You are a specialized weather agent. You execute weather-related tasks "
                    "that are delegated to you by other agents. You have direct access to weather APIs "
                    "and can provide detailed weather alerts and forecasts. Always provide complete, "
                    "accurate information based on the tool results."
                )
            )
            
            # Initialize context for maintaining conversation state
            self.context = Context(self.agent)
            
            print("✅ LlamaIndex components initialized successfully.")
            print(f"🛠️ Available weather tools: {[tool.metadata.name for tool in self.tools]}")
            
        except Exception as e:
            print(f"❌ Error initializing LlamaIndex components: {e}")
            raise

    async def execute(self, msg: nlip.NLIP_Message) -> nlip.NLIP_Message:
        """Execute delegated query using LlamaIndex agent with real tools."""
        logger = self.get_logger()
        text = msg.extract_text()
        
        try:
            print(f"\n🔧 [LlamaIndex] Processing delegated query: {text}")
            print("=" * 80)
            
            # Reset context for fresh conversation
            self.context = Context(self.agent)
            
            # Use the agent to process the query
            response = await self.agent.run(text, ctx=self.context)
            response_text = str(response)
            
            print("=" * 80)
            print(f"✅ [LlamaIndex] Completed processing, returning result to coordinator\n")
            logger.info(f"LlamaIndex Response: {response_text}")
            return NLIP_Factory.create_text(response_text)
            
        except Exception as e:
            logger.error(f"Exception in LlamaIndex execution: {e}")
            return NLIP_Factory.create_text(f"❌ Error processing delegated request: {str(e)}")

    async def stop(self):
        """Clean up resources."""
        print("🛑 Stopping LlamaIndex session")

    async def stop(self):
        """Clean up resources."""
        print("🛑 Stopping LlamaIndex worker session")
        self.llm = None
        self.agent = None
        self.tools = []
        self.context = None


# Standalone demo function for testing
async def standalone_demo():
    """Run a standalone demo to test the functionality."""
    print("=== LlamaIndex Standalone Demo ===")
    print("This demo tests the agent that executes actual weather tools.")
    print("Available commands:")
    print("- Weather alerts: 'Get weather alerts for Indiana'")
    print("- Weather forecast: 'What's the weather forecast for Bloomington, Indiana?'")
    print("- Direct tool calls: 'Get weather forecast for latitude 39.1612 longitude -86.5264'")
    print("- Quit: 'quit' or 'exit'")
    print()
    
    # Check for API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ ERROR: OPENROUTER_API_KEY environment variable is required!")
        print("Get your API key from: https://openrouter.ai/")
        print("Set it with: export OPENROUTER_API_KEY='your-key-here'")
        return
    
    # Initialize LlamaIndex components
    llm = OpenAILike(
        model="anthropic/claude-3.5-sonnet",
        api_key=api_key,
        api_base="https://openrouter.ai/api/v1",
        temperature=0.7,
        context_window=200000,
        is_chat_model=True,
        is_function_calling_model=True,
    )
    
    tools = [
        FunctionTool.from_defaults(
            fn=get_weather_alerts,
            name="get_weather_alerts",
            description="Get weather alerts for a US state. Takes a state code like 'CA', 'NY', 'IN'."
        ),
        FunctionTool.from_defaults(
            fn=get_weather_forecast,
            name="get_weather_forecast", 
            description="Get weather forecast for coordinates. Takes latitude and longitude as numbers."
        ),
    ]
    
    agent = FunctionAgent(
        tools=tools,
        llm=llm,
        verbose=True,
        system_prompt=(
            "You are a specialized weather agent. You execute weather-related tasks "
            "that are delegated to you by other agents. You have direct access to weather APIs "
            "and can provide detailed weather alerts and forecasts. Always provide complete, "
            "accurate information based on the tool results."
        )
    )
    
    context = Context(agent)
    
    print("🤖 LlamaIndex initialized with real weather tools:")
    for tool in tools:
        print(f"  - {tool.metadata.name}: {tool.metadata.description}")
    print()
    
    # Chat loop
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit']:
                break
                
            if not user_input:
                continue
                
            print("\nAgent: ", end="")
            response = await agent.run(user_input, ctx=context)
            print(f"{str(response)}\n")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}\n")


# Create the FastAPI app
app = server.setup_server(LlamaIndexApplication())

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "standalone":
        # Run standalone demo
        asyncio.run(standalone_demo())
    else:
        print("🌟 LlamaIndex NLIP Server Ready!")
        print("This server executes weather tools for requests delegated from coordinator agents.")
        print("🚀 Start with: poetry run uvicorn demo.inter_agent.llamaindex_worker:app --host 0.0.0.0 --port 8013 --reload")
