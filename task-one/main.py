import os
from dotenv import load_dotenv
import chainlit as cl
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig

# Load environment variables from .env file
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")

# Set up Gemini client
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


#Define model
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

#config
config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True,
)

# Define Chainlit chatbot logic
@cl.on_message
async def handle_message(message: cl.Message):
    agent = Agent(
        name="Product Suggester Agent",
        instructions="""
        You are an intelligent AI Product Suggester designed to help users find relevant products, remedies, learning materials, or advice based on their requests in natural language.

        🎯 Goals:
        - Understand if the query is about health, fashion, education, or general products.
        - Suggest specific remedies, products, or educational resources.

        🩺 Health:
        "I have a headache" → suggest water, oils, OTC meds like Panadol.

        👗 Fashion:
        "I want a red dress" → suggest casual, formal, party options.

        📚 Education:
        "I want to learn coding" → suggest books, courses, tools by level.

        📌 Format:
        ✅ Suggestions:
        - [Method/Product 1]
        - [Method/Product 2]
        - [Method/Product 3]

        💡 Tips or Notes:
        - [Helpful note or advice]

        ⚠️ Medical Safety:
        - Avoid diagnoses.
        - Recommend consulting a doctor.

        🤖 Tone:
        - Friendly, informative, and domain-appropriate.
        """,
        model=model
    )

    
    # Run the agent on user's message
    result = await Runner.run(agent, message.content, run_config=config)

    # Send the result back to the Chainlit frontend
    await cl.Message(content=result.final_output).send()
