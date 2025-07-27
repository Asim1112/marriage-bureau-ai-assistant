import os
from dotenv import load_dotenv
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner, function_tool
import chainlit as cl
import requests

load_dotenv()

@function_tool()
def get_user_data(min_age: int) -> dict:
    """
        Retrieve user data based on minimum age
    
    """
    
    users = [
        {"name": "markaram", "age": 21},
        {"name": "whistle", "age": 19},
        {"name": "alex", "age": 25},
        {"name": "james", "age": 27}
    ]
    
    filtered_users = []
    
    for user in users:
        if user["age"] >= min_age:
            filtered_users.append(user)

    return filtered_users



@function_tool()
def send_message(number: str, message: str):
    instance_id = os.getenv("INSTANCE_ID")
    token = os.getenv("API_TOKEN")
    url = f"https://api.ultramsg.com/{instance_id}/messages/chat"

    payload = {
        "token": token,
        "to": number,
        "body": message
    }

    response = requests.post(url, data=payload)

    if response.status_code == 200:
        return f"Message sent successfully to {number}"
    else:
        return f"Failed to send message. Error: {response.text}"

API_KEY = os.getenv("GEMINI_API_KEY")

client = AsyncOpenAI(api_key=API_KEY, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
model = OpenAIChatCompletionsModel(openai_client=client, model="gemini-2.0-flash")

Marriage_Bureau_Assistant = Agent(
    name="Marriage Bureau Uncle",
    instructions="""
    You are a helpful and intelligent Marriage Bureau Assistant.
    Your job is to help users find suitable matches based on their preferences such as age or other criteria.
    You have access to useful tools that can help you get user data, send responses via WhatsApp, and perform other tasks.
    Only call tools when required. Think step by step before using a tool.
    """,
    tools=[get_user_data, send_message],
    model=model
)

@cl.on_chat_start
async def start():
    cl.user_session.set("history", [])
    await cl.Message(content="Hello! I am Marriage Bureau Uncle, please tell me your credentails so I can find a perfect match for you").send()

@cl.on_message
async def main(message: cl.Message):
    await cl.Message(content="Thinking...").send()
    history = cl.user_session.get("history")
    history.append({"role": "user", "content": message.content})

    result = await Runner.run(
        starting_agent=Marriage_Bureau_Assistant,
        input=history
    )

    history.append({"role": "assistant", "content": result.final_output})
    cl.user_session.set("history", history)

    await cl.Message(content=result.final_output).send()