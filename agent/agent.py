import json
import logging
from dataclasses import dataclass, field
from typing import Annotated, Optional

from dotenv import load_dotenv
from pydantic import Field

from livekit import rtc
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.llm import function_tool
from livekit.agents.voice import Agent, AgentSession, RunContext
from livekit.agents.voice.room_io import RoomInputOptions
from livekit.plugins import deepgram, openai, silero

# from livekit.plugins import noise_cancellation

logger = logging.getLogger("form-filler-agent")
logger.setLevel(logging.INFO)

load_dotenv()


@dataclass
class UserData:
    ctx: Optional[JobContext] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    should_submit: bool = False


RunContext_T = RunContext[UserData]


async def send_to_frontend(userdata: UserData):
    metrics = {
        "customer_name": userdata.customer_name,
        "customer_phone": userdata.customer_phone,
        "customer_email": userdata.customer_email,
        "should_submit": userdata.should_submit,
    }
    payload = json.dumps(metrics).encode("utf-8")
    # Publish via the data channel (lossy for speed here)
    await userdata.ctx.room.local_participant.publish_data(
        payload,
        reliable=False
    )


class FormFiller(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                f"You are a friendly form filler assistant for an ice cream party. "
                "Your jobs are to ask for the user's name, phone number, and email. "
                "You will need to use the tools provided to you to fill out the form. "
                "After confirming a response, do not say you are setting the value, just move on to the next question."
            )
        )
    
    async def on_enter(self):
        # userdata: UserData = self.session.userdata
        await self.session.say("Hello! I'm here to help you sign up for the ice cream party. What's your name?")

    @function_tool()
    async def update_name(
        self,
        name: Annotated[str, Field(description="The customer's name")],
        context: RunContext_T,
    ) -> str:
        """Called when the user provides their name."""
        userdata = context.userdata
        userdata.customer_name = name
        await send_to_frontend(userdata)
        return f"The name is updated to {name}"

    @function_tool()
    async def update_phone(
        self,
        phone: Annotated[str, Field(description="The customer's phone number")],
        context: RunContext_T,
    ) -> str:
        """Called when the user provides their phone number."""
        userdata = context.userdata
        userdata.customer_phone = phone
        await send_to_frontend(userdata)
        return f"The phone number is updated to {phone}"

    @function_tool()
    async def update_email(
        self,
        email: Annotated[str, Field(description="The customer's email")],
        context: RunContext_T,
    ) -> str:
        """Called when the user provides their email."""
        userdata = context.userdata
        userdata.customer_email = email
        await send_to_frontend(userdata)
        return f"The email is updated to {email}"
    
    @function_tool()
    async def get_name(self, context: RunContext_T) -> str:
        """Called to get the user's stored name."""
        return f"User's name is {context.userdata.customer_name}"
    
    @function_tool()
    async def get_phone(self, context: RunContext_T) -> str:
        """Called to get the user's stored phone number."""
        return f"User's phone number is {context.userdata.customer_phone}"
    
    @function_tool()
    async def get_email(self, context: RunContext_T) -> str:
        """Called to get the user's stored email."""
        return f"User's email is {context.userdata.customer_email}"
    
    @function_tool()
    async def submit_form(self, context: RunContext_T) -> str:
        """Called when the user wants to submit the form.
        Confirm with the user before calling the function."""
        userdata = context.userdata
        if userdata.customer_name is None:
            return "Please provide your name."
        if userdata.customer_phone is None:
            return "Please provide your phone number."
        if userdata.customer_email is None:
            return "Please provide your email."
        userdata.should_submit = True
        await send_to_frontend(userdata)
        return f"The form is submitted"


async def entrypoint(ctx: JobContext):
    await ctx.connect()
    userdata = UserData(ctx=ctx)
    session = AgentSession[UserData](
        userdata=userdata,
        llm=openai.LLM(model="gpt-4.1"),
        stt=deepgram.STT(model="nova-3", language="multi"),
        tts=openai.TTS(voice="ash"),
        vad=silero.VAD.load(),
        max_tool_steps=5,
        # to use realtime model, replace the stt, llm, tts and vad with the following
        # llm=openai.realtime.RealtimeModel(voice="alloy"),
    )

    @ctx.room.on("data_received")
    def handle_data(packet: rtc.DataPacket):
        try:
            obj = json.loads(packet.data.decode("utf-8"))
            logger.info(f"received data: {obj}")
            if obj.get("field") == "name":
                userdata.customer_name = obj["value"]
                logger.info(f"updated name: {userdata.customer_name}")
            elif obj.get("field") == "phone":
                userdata.customer_phone = obj["value"]
                logger.info(f"updated phone: {userdata.customer_phone}")
            elif obj.get("field") == "email":
                userdata.customer_email = obj["value"]
                logger.info(f"updated email: {userdata.customer_email}")
            else:
                logger.error(f"unknown field: {obj.get('field')}")
        except Exception as e:
            logger.error(f"failed to parse data packet: {e}")

    await session.start(
        agent=FormFiller(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # noise_cancellation=noise_cancellation.BVC(),
        ),
    )


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))