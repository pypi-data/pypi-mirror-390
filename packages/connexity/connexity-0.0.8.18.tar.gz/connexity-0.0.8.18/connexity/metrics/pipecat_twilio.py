from typing import Literal

from connexity.client import ConnexityClient
from pipecat.audio.vad.vad_analyzer import VADParams
from twilio.rest import Client

from connexity.metrics.pipecat_interface import InterfaceConnexityObserver
from connexity.metrics.utils.twilio_module import TwilioCallManager


class ConnexityTwilioObserver(InterfaceConnexityObserver):

    async def initialize(self,
                         sid: str,
                         agent_id: str,
                         api_key: str,
                         call_type: Literal["inbound", "outbound", "web"],
                         vad_params: VADParams,
                         env: Literal["development", "production"],
                         vad_analyzer: str,
                         phone_call_provider: str = None,
                         user_phone_number: str = None,
                         agent_phone_number: str = None,
                         twilio_client: Client = None,
                         daily_api_key: str = None
                         ):
        if not twilio_client:
            raise ValueError("No twilio client provided")
        self.sid = sid
        self.twilio_client = TwilioCallManager(twilio_client)
        self.vad_stop_secs = vad_params.stop_secs
        self.vad_start_secs = vad_params.start_secs

        connexity_client = ConnexityClient(api_key=api_key)
        self.call = await connexity_client.register_call(
            sid=sid,
            agent_id=agent_id,
            user_phone_number=user_phone_number,
            agent_phone_number=agent_phone_number,
            created_at=None,
            voice_engine='pipecat',
            call_type=call_type,
            phone_call_provider=phone_call_provider,
            stream=False,
            env=env,
            vad_analyzer=vad_analyzer
        )

    async def post_process_data(self):
        recording_url = await self.twilio_client.get_call_recording_url(self.sid)
        created_at = await self.twilio_client.get_start_call_data(self.sid)
        duration = await self.twilio_client.get_call_duration(self.sid)

        await self.call.init_post_call_data(recording_url=recording_url, created_at=created_at,
                                            duration_in_seconds=duration)


