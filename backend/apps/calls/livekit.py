import asyncio
import json

from django.conf import settings
from livekit import api


def prepare_room(call, context_text):
    async def _run():
        client = api.LiveKitAPI(
            settings.LIVEKIT_URL,
            settings.LIVEKIT_API_KEY,
            settings.LIVEKIT_API_SECRET,
        )
        try:
            # ponytail: create-then-check guard, race-safe enough for sequential dials; per-room lock if parallel dialing grows
            await client.room.create_room(
                api.CreateRoomRequest(name=call.livekit_room_name, empty_timeout=120)
            )
            if await client.agent_dispatch.list_dispatch(call.livekit_room_name):
                return
            await client.agent_dispatch.create_dispatch(
                api.CreateAgentDispatchRequest(
                    agent_name="",
                    room=call.livekit_room_name,
                    metadata=json.dumps({"call_id": str(call.id), "context": context_text}),
                )
            )
        finally:
            await client.aclose()

    asyncio.run(_run())