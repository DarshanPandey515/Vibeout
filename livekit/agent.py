import os
from pathlib import Path

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentSession

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

os.environ.setdefault("LIVEKIT_URL", "ws://localhost:7880")


async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()

    session = AgentSession()
    await session.start(
        room=ctx.room,
        agent=Agent(instructions="You are a helpful voice AI assistant."),
    )
    await session.generate_reply(instructions="Greet the user and offer your assistance.")


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))