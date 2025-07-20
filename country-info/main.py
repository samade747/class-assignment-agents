# main.py
import chainlit as cl
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig
from tools import get_country_info
import os
from dotenv import load_dotenv

# Load API key from .env (if needed)
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

agent = Agent(
    name="country_info_agent",
    instructions="""
You are a helpful assistant that takes a country name and returns:
- Capital
- Population
- Official languages
- Flag image
- Google Maps link

Use the tool provided and return everything in a single, user-friendly response.
""",
    model=model,
    tools=[get_country_info]
)

@cl.on_message
async def on_message(message: cl.Message):
    country = message.content
    query = f"Give me all details of {country}"

    result = await Runner.run(agent, query, run_config=config)
    info = result.tool_outputs[0] if result.tool_outputs else {}

    if info.get("error"):
        await cl.Message(content=f"❌ {info['error']}").send()
    else:
        response = f"""📍 **{info['country']}**
**🏛 Capital:** {info['capital']}
**🗣 Languages:** {info['languages']}
**👥 Population:** {info['population']}
🌍 [View on Map]({info['map_link']})
"""
        msg = cl.Message(content=response)
        if info.get("flag_url"):
            msg.elements = [
                cl.Image(name="Flag", display="inline", url=info["flag_url"])
            ]
        await msg.send()
