
import os
import requests
from dotenv import load_dotenv
import chainlit as cl
from typing import Optional, Dict
from agents import function_tool

from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    function_tool,
)
from agents.run import RunConfig

# Load .env variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ Missing GEMINI_API_KEY in .env file")

# Configure OpenAI-compatible Gemini client
external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai"
)

# Define the model
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

# Run configuration
config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True,
)


@function_tool
def get_country_info(country_name: str) -> Dict[str, Optional[str]]:
    """
    Returns detailed information about a given country using the REST Countries API.
    """
    try:
        response = requests.get(f"https://restcountries.com/v3.1/name/{country_name}")
        if response.status_code != 200:
            return {"error": "Country not found or API error."}
        
        data = response.json()[0]

        country = data.get("name", {}).get("common", "Unknown")
        capital = data.get("capital", ["Unknown"])[0]
        population = f"{data.get('population', 'Unknown'):,}"
        languages = ", ".join(data.get("languages", {}).values()) or "Unknown"
        flag_url = data.get("flags", {}).get("png")
        map_link = data.get("maps", {}).get("googleMaps", "")

        return {
            "country": country,
            "capital": capital,
            "population": population,
            "languages": languages,
            "flag_url": flag_url,
            "map_link": map_link
        }

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}




# Define the agent
agent = Agent(
    name="country_info_agent",
    instructions="""
You are a helpful assistant that takes a country name and uses a tool to provide:
- Capital
- Population
- Official languages

You must always use the `get_country_info` tool when a country is mentioned.
Return results clearly in a readable format.
""",
    model=model,
    tools=[get_country_info],
)

# Chainlit message handler
@cl.on_message
async def handle_user_input(message: cl.Message):
    user_input = message.content

    try:
        # Run the agent and capture its output
        result = await Runner.run(
            agent,
            input=user_input,
            run_config=config
        )
        # Pull from the correct field
        output = result.final_output

        # If it's a simple string, send it directly
        if isinstance(output, str):
            await cl.Message(content=output).send()
        else:
            # Otherwise it's a dict; format it nicely
            response_str = "\n".join(f"**{k}**: {v}" for k, v in output.items())
            await cl.Message(content=response_str).send()

    except Exception as e:
        await cl.Message(content=f"❌ Error: {str(e)}").send()
