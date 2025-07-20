

import os
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig
import asyncio

# Load the environment variables from the .env file
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

# Check if the API key is present; if not, raise an error
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

#Reference: https://ai.google.dev/gemini-api/docs/openai
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
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

happy_agent = Agent(
    name="Happy mood Agent",
    instructions="""
You are the Happy mood Agent. Your job is to respond to users who are in a happy or joyful mood.

Acknowledge their positive state, celebrate their happiness, and encourage them.
Offer helpful, positive suggestions or fun ideas to keep their good mood going.

Use friendly, lighthearted, and cheerful language.

if the agent is called start the respose with: "Happy Agent tool called".
""",
    model=model
)


sad_agent = Agent (
    name = "Sad mood Agent",
    instructions = """
You are the Sad mood Agent. Your job is to respond to users who are feeling sad, low, or emotionally distressed.

Acknowledge their feelings with empathy and compassion.
Offer kind, comforting words and suggest small, healthy steps that might help improve their mood — like deep breathing, talking to a friend, or taking a walk.

Use gentle, supportive, and warm language.

if the agent is called start the respose with: "Sad Agent tool called".
""",
    model=model
)


async def main():
    triage_agent = Agent(
            name="Mood Analyzer Agent",
        instructions="""
    You are a Mood Analyzer Agent. Your task is to analyze the mood of the user's message.

    Classify the mood into one of the following:
    - Happy
    - Sad

    If the mood is happy or joyful, handoff to the 'Happy mood Agent'.
    If the mood is sad, depressed, or anxious, handoff to the 'Sad mood Agent'.

    Only route to these two agents. Do not answer the user yourself.
    """,
            model=model,
            handoffs = [happy_agent, sad_agent]
        )

    result = await Runner.run(triage_agent, "i am heartbroken today.", run_config=config)
    response = await Runner.run(happy_agent,"i am calm now.",run_config = config)
    print(result.final_output)
    print(response.final_output)
    # Function calls itself,
    # Looping in smaller pieces,
    # Endless by design.


if __name__ == "__main__":
    asyncio.run(main())
