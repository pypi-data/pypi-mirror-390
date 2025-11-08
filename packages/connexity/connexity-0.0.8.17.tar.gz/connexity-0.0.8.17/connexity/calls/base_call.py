import asyncio
import datetime
import logging
from dataclasses import dataclass
from typing import List, Optional, Literal, Dict

from connexity.calls.messages.error_message import ErrorMessage
from connexity.calls.messages.interface_message import InterfaceMessage
from connexity.utils.send_data import send_data

logger = logging.getLogger(__name__)


@dataclass
class ServiceSegment:
    provider: Optional[str]
    model: Optional[str]
    voice: Optional[str]
    start: Optional[float]
    end: Optional[float] = None


class BaseCall:

    def __init__(self,
                 sid: str,
                 call_type: Literal["inbound", "outbound", "web"],
                 api_key: str,
                 agent_id: str,
                 user_phone_number: Optional[str] = None,
                 agent_phone_number: Optional[str] = None,
                 created_at=None,
                 voice_engine: Optional[str] = None,
                 phone_call_provider: Optional[str] = None,
                 stream: Optional[bool] = False,
                 env: Optional[Literal["production", "development"]] = 'development',
                 vad_analyzer: Optional[str] = None,
                 ):
        self._sid = sid
        self._call_type = call_type
        self._user_phone_number = user_phone_number
        self._agent_phone_number = agent_phone_number
        self._created_at = created_at
        self._agent_id = agent_id
        self._api_key = api_key
        self._voice_engine = voice_engine
        self._transcriber = None
        self._stt_model = None
        self._tts_model = None
        self._tts_voice = None
        self._voice_provider = None
        self._llm_model = None
        self._llm_provider = None
        self._phone_call_provider = phone_call_provider
        self._stream = stream
        self._run_mode = env
        self._vad_analyzer = vad_analyzer

        self._duration_in_seconds = None
        self._recording_url = None
        self._system_prompts: set[str] = set()
        self._messages: List[InterfaceMessage] = []
        self._errors: List[ErrorMessage] = []
        self._errors_registered: set[str] = set()

        self._services_timeline: Dict[str, List[ServiceSegment]] = {
            "stt": [],
            "llm": [],
            "tts": [],
        }

    async def initialize(self):
        """Async method to handle post-init operations."""
        await self._send_data_to_connexity(update_type="status_update", status="in_progress", first=True)

    async def register_message(self, message: InterfaceMessage):
        self._messages.append(message)

        await self._send_data_to_connexity(update_type="conversation_update")

    async def register_error(self, error: ErrorMessage):
        if error.id and error.id not in self._errors_registered:
            self._errors.append(error)
            self._errors_registered.add(error.id)
        # # TODO: delete else before pushing to prod
        # else:
        #     logger.warning(
        #         f"Duplicate error is not registered. Error id: '{error.id}'.",
        #     )
        await self._send_data_to_connexity(update_type="error_update")

    async def update_last_message(self, message: InterfaceMessage):
        self._messages[-1] = message

        await self._send_data_to_connexity(update_type="conversation_update")

    async def register_system_prompts(self, prompts: set[str]):
        self._system_prompts.update(prompts)

    async def init_post_call_data(self, recording_url: str, duration_in_seconds: float,
                                  created_at: datetime.datetime | None):
        self._recording_url = recording_url
        self._duration_in_seconds = duration_in_seconds
        self._created_at = created_at

        self.finalize_services_timeline(self._duration_in_seconds)

        await self._send_data_to_connexity(update_type="conversation_update")
        await self._send_data_to_connexity(update_type="status_update", status="completed")
        await self._send_data_to_connexity(update_type="end_of_call")

    def _to_dict(self) -> dict:
        """
        Returns a JSON representation of the BaseCall instance.

        Returns:
            str: JSON string of the instance.
        """
        return {
            'sid': self._sid,
            'call_type': self._call_type,
            'user_phone_number': self._user_phone_number,
            'agent_phone_number': self._agent_phone_number,
            'created_at': self._created_at.isoformat() if hasattr(self._created_at, 'isoformat')
            else self._created_at,
            'agent_id': self._agent_id,
            'voice_engine': self._voice_engine,
            'transcriber': self._transcriber,
            'voice_provider': self._voice_provider,
            'llm_model': self._llm_model,
            'llm_provider': self._llm_provider,
            'phone_call_provider': self._phone_call_provider,
            'duration_in_seconds': self._duration_in_seconds,
            'recording_url': self._recording_url,
            'messages': [message.to_dict() for message in self._messages]
            if self._messages else [],
            'run_mode': self._run_mode,
            'vad_analyzer': self._vad_analyzer,
            'stt_model': self._stt_model,
            'tts_model': self._tts_model,
            'tts_voice': self._tts_voice,
            'errors': [e.to_dict() for e in self._errors] if self._errors else [],
            'system_prompts': sorted(list(self._system_prompts)) if self._system_prompts else [],
            'services_timeline': {
                k: [
                    {
                        'provider': s.provider,
                        'model': s.model,
                        'voice': s.voice,
                        'start': s.start,
                        'end': s.end,
                    }
                    for s in v
                ]
                for k, v in self._services_timeline.items()
            },

        }

    async def _send_data_to_connexity(self, update_type: str, status: Optional[str] = None, first=False):
        """
        Sends accumulated data to Connexity's backend.

        Returns:
            dict: Response from the Connexity API.
        """

        data = self._to_dict()
        data['event_type'] = update_type
        data["status"] = status

        if update_type == "end_of_call":
            asyncio.create_task(send_data(data, self._api_key))

    # --- services timeline management -------------------------------------------

    def _last_segment(self, kind: Literal["stt", "llm", "tts"]) -> Optional[ServiceSegment]:
        segs = self._services_timeline.get(kind) or []
        return segs[-1] if segs else None

    async def update_service_timeline(self,
                                      kind: Literal["stt", "llm", "tts"],
                                      *,
                                      provider: Optional[str] = None,
                                      model: Optional[str] = None,
                                      voice: Optional[str] = None,
                                      at_seconds: Optional[float] = None):
        def norm(v: Optional[str]) -> str:
            return (v or "").strip().lower()

        last = self._last_segment(kind)
        changed = (
                not last or
                norm(last.provider) != norm(provider) or
                norm(last.model) != norm(model) or
                (kind == "tts" and norm(last.voice) != norm(voice))
        )

        if changed:
            if last and last.end is None:
                last.end = at_seconds
            self._services_timeline[kind].append(
                ServiceSegment(
                    provider=provider,
                    model=model,
                    voice=(voice if kind == "tts" else None),
                    start=at_seconds,
                )
            )

            if kind == "stt":
                self._transcriber = provider
                self._stt_model = model
            elif kind == "llm":
                self._llm_provider = provider
                self._llm_model = model
            elif kind == "tts":
                self._voice_provider = provider
                self._tts_model = model
                self._tts_voice = voice

            await self._send_data_to_connexity(
                update_type="status_update",
                status="in_progress",
            )

    def finalize_services_timeline(self, at_seconds: Optional[float] = None):
        for segs in self._services_timeline.values():
            if segs and segs[-1].end is None:
                segs[-1].end = at_seconds
