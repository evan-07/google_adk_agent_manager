from google.adk.agents import Agent

from adk_short_bot.prompt import ROOT_AGENT_INSTRUCTION
from adk_short_bot.tools import count_characters, format_as_json

root_agent = Agent(
    name="adk_short_bot",
    model="gemini-2.0-flash",
    description="A bot that shortens messages and provides output in JSON format.",
    instruction=ROOT_AGENT_INSTRUCTION,
    tools=[count_characters, format_as_json],
)