
from __future__ import annotations

from livekit.agents import AutoSubscribe, llm, JobContext, WorkerOptions, cli
from livekit.agents.multimodal import MultimodalAgent
from livekit.plugins import openai

from dotenv import load_dotenv
import os

from api import AssistantFnc
from prompts import Intructions, Welcome_Message
load_dotenv()

async def entrypoint(ctx: JobContext):
    await ctx.connect(auto_subscribe=AutoSubscribe.SUBSCRIBE_ALL)

    await ctx.wait_for_participant()

    model = openai.realtime.RealtimeModel(
        instructions=Intructions,
        voice="shimmer",
        temperature=0.8,
        modalities=["audio", "text"]
    )

    assistant_func = AssistantFnc()

    assistant = MultimodalAgent(model = model, fnc_ctx = assistant_func)

    assistant.start(ctx.room)

    session = model.sessions[0]

    session.conversation.item.create(
        llm.ChatMessage(
            role = "assistant",
            content = Welcome_Message)
    )

    session.response.create()

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc = entrypoint))