import json
import os
from pathlib import Path

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import AgentSession
from livekit.plugins import groq

load_dotenv(Path(__file__).resolve().parents[1] / "backend" / ".env")

SYSTEM_PROMPT = (
    "You are a friendly AI sales agent for Vibeout, calling on behalf of a company. "
    "Be concise, warm, and professional. Never invent facts that are not in the lead "
    "context provided to you."
)


async def entrypoint(ctx: JobContext):
    await ctx.connect()
    instructions = SYSTEM_PROMPT
    if ctx.job.metadata:
        try:
            meta = json.loads(ctx.job.metadata)
            if meta.get("context"):
                instructions += "\n\nLead context:\n" + meta["context"]
        except json.JSONDecodeError:
            pass
    session = AgentSession(
        stt=groq.STT(),
        llm=groq.LLM(model=os.environ.get("GROQ_LLM_MODEL", "openai/gpt-oss-20b")),
        tts=groq.TTS(),
    )
    await session.start(room=ctx.room, agent=agents.Agent(instructions=instructions))
    await session.generate_reply(
        instructions="Greet the person by name and briefly explain the reason for the call."
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))