import logging
import asyncio
from abc import abstractmethod
from dataclasses import dataclass
from typing import Literal, Optional, List, Dict, Any

from pipecat.transports.base_output import BaseOutputTransport

from connexity.calls.messages.error_message import ErrorMessage
from connexity.client import ConnexityClient
from twilio.rest import Client
from pipecat.frames.frames import (
    BotStartedSpeakingFrame,
    BotStoppedSpeakingFrame,
    UserStartedSpeakingFrame,
    UserStoppedSpeakingFrame,
    TTSTextFrame,
    TranscriptionFrame,
    CancelFrame,
    FunctionCallInProgressFrame,
    FunctionCallResultFrame,
    LLMFullResponseStartFrame,
    TTSStartedFrame, EndFrame,
)
from pipecat.observers.base_observer import BaseObserver, FramePushed
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import ErrorFrame

from pipecat.processors.frame_processor import FrameDirection
from pipecat.services.llm_service import LLMService
from pipecat.services.tts_service import TTSService
from pipecat.services.stt_service import STTService
from connexity.calls.base_call import BaseCall
from connexity.metrics.utils.twilio_module import TwilioCallManager
from connexity.calls.messages.user_message import UserMessage
from connexity.calls.messages.assistant_message import AssistantMessage
from connexity.calls.messages.tool_call_message import ToolCallMessage
from connexity.calls.messages.tool_result_message import ToolResultMessage
from connexity.metrics.utils.validate_json import validate_json
from connexity.utils.snapshot_error_frame import snapshot_error_frame, extract_llm_messages_from_mappings

logger = logging.getLogger(__name__)

Role = Literal["user", "assistant", "tool_call"]


@dataclass
class Latency:
    tts: Optional[float] = None  # milliseconds
    llm: Optional[float] = None  # milliseconds
    stt: Optional[float] = None  # milliseconds
    vad: Optional[float] = None  # milliseconds

    def get_metrics(self):
        return {"tts": self.tts,
                "llm": self.llm,
                "stt": self.stt,
                "vad": self.vad}


@dataclass
class MessageData:
    role: Role
    start: Optional[float] = None  # seconds from call start
    end: Optional[float] = None    # seconds from call start
    content: str = ""
    latency: Optional[Latency] = None

    def has_valid_window(self) -> bool:
        return (
            self.start is not None
            and self.end is not None
            and self.content.strip() != ""
            and self.start < self.end
        )

    def reset(self) -> None:
        self.start = None
        self.end = None
        self.content = ""
        if self.latency:
            self.latency = Latency()  # reset subfields

    def get_metrics(self):
        return {"role": self.role,
                "start": self.start,
                "end": self.end,
                "content": self.content,
                "latency": self.latency}


@dataclass
class ToolCallData:
    role: Role = "tool_call"
    start: Optional[float] = None
    end: Optional[float] = None
    tool_call_id: Optional[str] = None
    function_name: Optional[str] = None
    arguments: Optional[str] = None
    content: str = ""


@dataclass
class InterruptionAttempt:
    start: float
    stt_words: int = 0
    first_transcript_at: Optional[float] = None
    saw_cancel: bool = False
    user_stop: Optional[float] = None
    bot_stop: Optional[float] = None


class InterfaceConnexityObserver(BaseObserver):

    MIN_SEPARATION = 0.5

    def __init__(self):
        super().__init__()
        self.call: BaseCall | None = None
        self.user_data = MessageData(role="user")
        self.assistant_data = MessageData(role="assistant", latency=Latency())
        self.tool_calls = ToolCallData()

        self.messages: List[Dict[str, Any]] = []

        # additional data for connexity
        self.sid = None
        self.twilio_client: Client | None = None
        self.final = False

        self.stt_start = None
        self.tts_start = None
        self.llm_start = None
        self.vad_stop_secs = None
        self.vad_start_secs = None

        # interruption tracking
        self._bot_speaking: bool = False
        self._active_interrupt: Optional["InterruptionAttempt"] = None
        self.INTERRUPT_MIN_WORDS = 2
        self.INTERRUPT_MIN_OVERLAP_SECS = 0.5
        self.INTERRUPT_EXPECT_CANCEL_WITHIN_SECS = 2

        # user VAD de-duplication and state
        self._user_speaking: bool = False
        self._last_user_start_ts: Optional[float] = None
        self._last_user_stop_ts: Optional[float] = None
        self.USER_EVENT_DEDUP_SECS = 0.1

        # system prompt tracking
        self._system_prompts: set[str] = set()

    @abstractmethod
    async def initialize(
        self,
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
            voice_engine="pipecat",
            call_type=call_type,
            phone_call_provider=phone_call_provider,
            stream=False,
            env=env,
            vad_analyzer=vad_analyzer
        )

    @staticmethod
    def _ns_to_s(ns: int) -> float:
        return ns / 1_000_000_000

    @staticmethod
    def _is_downstream_output(src: Any, direction: FrameDirection) -> bool:
        return isinstance(src, BaseOutputTransport) and direction == FrameDirection.DOWNSTREAM

    @staticmethod
    def _apply_min_separation(prev_time: Optional[float], current_time: float, min_sep: float) -> float:
        if prev_time is None or (current_time - prev_time) > min_sep:
            return current_time
        return prev_time

    @staticmethod
    def _debug(msg: str, **kv: Any) -> None:
        if kv:
            msg = f"{msg} | " + " ".join(f"{k}={v}" for k, v in kv.items())
        print("CONNEXITY SDK DEBUG | %s", msg, flush=True)

    # --- event handlers ------------------------------------------------------

    @staticmethod
    def _trace_upstream(node, max_hops: int = 20) -> list:
        chain = []
        seen = set()
        cur = node
        for _ in range(max_hops):
            if cur is None or id(cur) in seen:
                break
            seen.add(id(cur))
            chain.append(cur)
            cur = getattr(cur, "_prev", None)
        return chain

    @staticmethod
    def _find_by_class_name(nodes: list, needle: str):
        result = []
        for n in nodes:
            if needle in n.__class__.__name__:
                result.append(n)
        return result

    @staticmethod
    def _get_switcher_active_service(switcher) -> object | None:
        strategy = getattr(switcher, "strategy", None)
        return getattr(strategy, "active_service", None) if strategy else None

    @staticmethod
    def _guess_provider(obj) -> str | None:
        hay = f"{obj.__class__.__module__}.{obj.__class__.__name__}".lower()

        tokens = [
            # LLM
            ("azure", "azure"),
            ("anthropic", "anthropic"),
            ("mistral", "mistral"),
            ("deepseek", "deepseek"),
            ("fireworks", "fireworks"),
            ("perplexity", "perplexity"),
            ("openrouter", "openrouter"),
            ("openpipe", "openpipe"),
            ("together", "together"),
            ("grok", "grok"),
            ("groq", "groq"),
            ("ollama", "ollama"),
            ("cerebras", "cerebras"),
            ("qwen", "qwen"),
            ("sambanova", "sambanova"),
            ("nim", "nvidia"),
            ("aws", "aws"),
            ("google", "google"),
            ("gemini", "google"),
            ("vertex", "google"),
            ("openai", "openai"),
            # STT
            ("assemblyai", "assemblyai"),
            ("deepgram", "deepgram"),
            ("speechmatics", "speechmatics"),
            ("soniox", "soniox"),
            ("gladia", "gladia"),
            ("ultravox", "ultravox"),
            ("whisper", "openai"),
            ("elevenlabs", "elevenlabs"),
            ("cartesia", "cartesia"),
            ("riva", "nvidia"),
            # TTS
            ("playht", "playht"),
            ("piper", "coqui"),
            ("xtts", "coqui"),
            ("hume", "hume"),
            ("lmnt", "lmnt"),
            ("neuphonic", "neuphonic"),
            ("minimax", "minimax"),
            ("rime", "rime"),
            # Other service families (safe to map to their own name)
            ("inworld", "inworld"),
            ("heygen", "heygen"),
            ("simli", "simli"),
            ("tavus", "tavus"),
            ("fal", "fal"),
            ("fish", "fish"),
            # generic fallbacks
            ("polly", "aws"),
            ("bedrock", "aws"),
            ("nvidia", "nvidia"),
        ]

        for token, provider in tokens:
            if token in hay:
                return provider
        return None

    @staticmethod
    def _extract_model_voice(service) -> tuple[str | None, str | None]:
        model = getattr(service, "model_name", None) or getattr(service, "_model_name", None)
        voice = getattr(service, "_voice_id", None) or getattr(service, "voice_id", None) or getattr(service, "voice",
                                                                                                     None)
        settings = getattr(service, "_settings", None)
        if isinstance(settings, dict):
            model = model or settings.get("model")
            voice = voice or settings.get("voice") or settings.get("voice_id")
        # Try adapter (LLM)
        get_ad = getattr(service, "get_llm_adapter", None)
        if callable(get_ad):
            try:
                ad = get_ad()
                model = model or getattr(ad, "model", None) or getattr(ad, "model_name", None)
            except Exception:
                pass
        return model, voice

    async def _update_service_timeline(
        self,
        frame: Any,
        src: Any,
        direction: FrameDirection,
        t: float,
    ) -> None:
        if not self.call:
            return

        upstream_nodes = self._trace_upstream(src)

        families: list[tuple[Literal["stt", "llm", "tts"], type, bool, bool]] = [
            (
                "stt",
                STTService,
                isinstance(frame, TranscriptionFrame),
                False,
            ),
            (
                "llm",
                LLMService,
                isinstance(frame, LLMFullResponseStartFrame)
                and self._is_downstream_output(src, direction),
                False,
            ),
            (
                "tts",
                TTSService,
                isinstance(frame, TTSStartedFrame)
                and self._is_downstream_output(src, direction),
                True,
            ),
        ]

        for family, service_cls, should_process, include_voice in families:
            if not should_process:
                continue

            provider: Optional[str] = None
            model: Optional[str] = None
            voice: Optional[str] = None

            switchers = self._find_by_class_name(upstream_nodes, "ServiceSwitcher")
            for sw in switchers:
                active = self._get_switcher_active_service(sw)
                if active and isinstance(active, service_cls):
                    provider = self._guess_provider(active)
                    m, v = self._extract_model_voice(active)
                    model = m
                    if include_voice:
                        voice = v
                    break

            if provider is None and model is None:
                nodes = self._find_by_class_name(upstream_nodes, service_cls.__name__)
                node = nodes[0] if nodes else None
                if node:
                    provider = self._guess_provider(node)
                    m, v = self._extract_model_voice(node)
                    model = m
                    if include_voice:
                        voice = v

            if (
                provider is not None
                or model is not None
                or (include_voice and voice is not None)
            ):
                if family == "tts":
                    await self.call.update_service_timeline(
                        "tts",
                        provider=provider,
                        model=model,
                        voice=voice,
                        at_seconds=t,
                    )
                else:
                    await self.call.update_service_timeline(
                        family,
                        provider=provider,
                        model=model,
                        at_seconds=t,
                    )

    def _handle_latency_markers(self, frame: Any, src: Any, direction: FrameDirection, t: float) -> None:
        # User finished speaking -> STT starts
        if isinstance(frame, UserStoppedSpeakingFrame):
            self.stt_start = t

        # LLM full response begins (first token) => close STT latency
        if isinstance(frame, LLMFullResponseStartFrame) and self._is_downstream_output(src, direction):
            if self.stt_start is not None and self.assistant_data.latency.stt is None:
                self.llm_start = t
                stt_ms = (t - self.stt_start) * 1000
                self.assistant_data.latency.stt = stt_ms
                self.stt_start = None
                self._debug("STT METRIC", ms=f"{stt_ms:.0f}")

        # TTS start => close LLM latency
        if isinstance(frame, TTSStartedFrame) and self._is_downstream_output(src,
                                                                             direction) and self.tts_start is None:
            if self.llm_start is not None:
                llm_ms = (t - self.llm_start) * 1000
                self.assistant_data.latency.llm = llm_ms
                self._debug("LLM METRIC", ms=f"{llm_ms:.0f}")
            self.tts_start = t

        # Bot audio actually starts => close TTS prepare latency
        if isinstance(frame, BotStartedSpeakingFrame) and self._is_downstream_output(src,
                                                                                     direction) and self.tts_start:
            tts_ms = (t - self.tts_start) * 1000
            self.assistant_data.latency.tts = tts_ms
            self.tts_start = None
            self._debug("TTS METRIC", ms=f"{tts_ms:.0f}")

        # Cancellation seen (counts as successful interruption if attempt is active)
        if isinstance(frame, CancelFrame) and self._is_downstream_output(src, direction):
            if self._active_interrupt and self._bot_speaking:
                self._active_interrupt.saw_cancel = True
                self._debug("CANCEL DURING ATTEMPT", t=t)

    def _handle_bot_window(self, frame: Any, src: Any, direction: FrameDirection, t: float) -> None:
        if not self._is_downstream_output(src, direction):
            return

        if isinstance(frame, BotStartedSpeakingFrame):
            self._bot_speaking = True
            self.assistant_data.start = self._apply_min_separation(
                self.assistant_data.start, t, self.MIN_SEPARATION
            )
            self._debug("BOT START SPEAKING", t=t)

        elif isinstance(frame, BotStoppedSpeakingFrame):
            self.assistant_data.end = self._apply_min_separation(
                self.assistant_data.end, t, self.MIN_SEPARATION
            )
            self._debug("BOT STOP SPEAKING", t=t)
            if self._active_interrupt:
                self._finalize_interrupt_attempt(t, "bot_stopped")
            self._bot_speaking = False

    def _handle_user_window(self, frame: Any, src: Any, direction: FrameDirection, t: float) -> None:
        if isinstance(frame, UserStartedSpeakingFrame):
            if self._user_speaking:
                if self._last_user_start_ts is not None and (t - self._last_user_start_ts) < self.USER_EVENT_DEDUP_SECS:
                    return
                return

            self._user_speaking = True
            self._last_user_start_ts = t
            # include VAD pre-roll to approximate true start
            vad_start = t
            true_start = vad_start - (self.vad_start_secs or 0.0)
            self.user_data.start = true_start
            if self._bot_speaking:
                self._start_interrupt_attempt(true_start)
            self._debug("USER START SPEAKING", t=t, true_start=true_start)

        elif isinstance(frame, UserStoppedSpeakingFrame):
            if not self._user_speaking:
                if self._last_user_stop_ts is not None and (t - self._last_user_stop_ts) < self.USER_EVENT_DEDUP_SECS:
                    return
                return

            self._user_speaking = False
            self._last_user_stop_ts = t

            self.user_data.end = t
            self._debug("USER STOP SPEAKING", t=t)
            if self._active_interrupt:
                self._finalize_interrupt_attempt(t, "user_stopped")

    async def _handle_tool_call_start(self, frame: Any, src: Any, direction: FrameDirection, t: float) -> None:
        if not (isinstance(frame, FunctionCallInProgressFrame) and self._is_downstream_output(src, direction)):
            return

        self.tool_calls.start = self._apply_min_separation(self.tool_calls.start, t, self.MIN_SEPARATION)
        self.tool_calls.tool_call_id = frame.tool_call_id
        self.tool_calls.function_name = frame.function_name
        self.tool_calls.arguments = frame.arguments

        await self.call.register_message(
            ToolCallMessage(
                arguments=frame.arguments,
                tool_call_id=frame.tool_call_id,
                content="",
                name=frame.function_name,
                seconds_from_start=t,
            )
        )
        self._debug("FUNCTION CALL STARTED",
                    tool_call_id=frame.tool_call_id, function=frame.function_name, args=str(frame.arguments))

    async def _handle_tool_call_end(self, frame: Any, src: Any, direction: FrameDirection, t: float) -> None:
        if not (isinstance(frame, FunctionCallResultFrame) and self._is_downstream_output(src, direction)):
            return

        self.tool_calls.end = self._apply_min_separation(self.tool_calls.end, t, self.MIN_SEPARATION)
        self.tool_calls.content = frame.result

        is_json, json_data = validate_json(frame.result)
        await self.call.register_message(
            ToolResultMessage(
                content="",
                tool_call_id=frame.tool_call_id,
                result_type="JSON" if is_json else "string",
                result=json_data if is_json else frame.result,
                seconds_from_start=t,
            )
        )
        self._debug("FUNCTION CALL END",
                    tool_call_id=frame.tool_call_id, function=getattr(frame, "function_name", None))

    def _start_interrupt_attempt(self, t: float) -> None:
        if self._active_interrupt is None:
            self._active_interrupt = InterruptionAttempt(start=t)
            self._debug("INTERRUPT ATTEMPT START", t=t)

    def _finalize_interrupt_attempt(self, t: float, reason: str) -> None:
        attempt = self._active_interrupt
        if not attempt:
            return

        if reason == "user_stopped" and attempt.user_stop is None:
            attempt.user_stop = t
        if reason == "bot_stopped" and attempt.bot_stop is None:
            attempt.bot_stop = t

        stop_t = attempt.user_stop or attempt.bot_stop or t
        overlap_secs = max(0.0, stop_t - attempt.start)

        meaningful_attempt = (attempt.stt_words >= self.INTERRUPT_MIN_WORDS) or \
                             (overlap_secs >= self.INTERRUPT_MIN_OVERLAP_SECS)

        time_since_start = stop_t - attempt.start
        no_cancel_within_threshold = (not attempt.saw_cancel) and \
                                     (time_since_start >= self.INTERRUPT_EXPECT_CANCEL_WITHIN_SECS)

        unsuccessful = meaningful_attempt and no_cancel_within_threshold

        if unsuccessful:
            root_cause = "unknown"
            if attempt.stt_words == 0 and overlap_secs >= self.INTERRUPT_MIN_OVERLAP_SECS:
                root_cause = "no_transcripts_during_overlap"

            error_frame_id = int(attempt.start * 1000)

            err = ErrorMessage(
                content="Unsuccessful user interruption (agent continued speaking)",
                source="observer",
                error_frame_id=error_frame_id,
                seconds_from_start=attempt.start,
                code="unsuccessful_interruption",
                metadata={
                    "attempt": {
                        "start": attempt.start,
                        "user_stop": attempt.user_stop,
                        "bot_stop": attempt.bot_stop,
                        "overlap_secs": overlap_secs,
                        "stt_words": attempt.stt_words,
                        "first_transcript_at": attempt.first_transcript_at,
                        "saw_cancel": attempt.saw_cancel,
                    },
                    "thresholds": {
                        "min_words": self.INTERRUPT_MIN_WORDS,
                        "min_overlap_secs": self.INTERRUPT_MIN_OVERLAP_SECS,
                        "expect_cancel_within_secs": self.INTERRUPT_EXPECT_CANCEL_WITHIN_SECS,
                        "vad_start_secs": self.vad_start_secs,
                        "vad_stop_secs": self.vad_stop_secs,
                    },
                    "root_cause_heuristic": root_cause,
                },
            )
            self._debug("UNSUCCESSFUL INTERRUPTION", overlap=overlap_secs, words=attempt.stt_words)
            try:
                asyncio.create_task(self.call.register_error(err))
            except Exception:
                pass

        self._active_interrupt = None

    def _accumulate_content(self, frame: Any, src: Any, direction: FrameDirection, t: float) -> None:
        # STT text (guard against non-STT sources)
        if isinstance(frame, TranscriptionFrame) and getattr(src, "name", "").find("STTService") != -1:
            self.user_data.content += frame.text
            if self._bot_speaking:
                if self._active_interrupt is None:
                    self._start_interrupt_attempt(t)
                words = [w for w in frame.text.strip().split() if w]
                if words and self._active_interrupt:
                    self._active_interrupt.stt_words += len(words)
                    if self._active_interrupt.first_transcript_at is None:
                        self._active_interrupt.first_transcript_at = t

        # TTS text (bot message accumulation)
        if isinstance(frame, TTSTextFrame) and self._is_downstream_output(src, direction):
            self.assistant_data.content += frame.text + " "

    async def _maybe_flush_user(self) -> None:
        if not self.user_data.has_valid_window():
            return

        self.messages.append(self.user_data.get_metrics())
        await self.call.register_message(
            UserMessage(
                content=self.user_data.content,
                seconds_from_start=self.user_data.start,
            )
        )
        self._debug("USER DATA COLLECTED", content_len=len(self.user_data.content or ""))
        self.user_data.reset()

    async def _maybe_flush_assistant(self) -> None:
        if not self.assistant_data.has_valid_window():
            return

        # VAD-based latency to first audio from end of last user utterance
        latency_ms: Optional[float] = None
        if self.messages and self.messages[-1].get("role") == "user":
            last_user_end_vad = self.messages[-1]["end"]
            real_end = last_user_end_vad - (self.vad_stop_secs or 0.0)
            latency_ms = (self.assistant_data.start - real_end) * 1000
            self.assistant_data.latency.vad = (self.vad_stop_secs or 0.0) * 1000

        self.messages.append(self.assistant_data.get_metrics())
        await self.call.register_message(
            AssistantMessage(
                content=self.assistant_data.content,
                time_to_first_audio=latency_ms,
                seconds_from_start=self.assistant_data.start,
                latency=self.assistant_data.latency.get_metrics(),
            )
        )
        self._debug("BOT DATA COLLECTED", content_len=len(self.assistant_data.content or ""),
                    t_start=self.assistant_data.start)
        self.assistant_data.reset()

    async def _extract_system_prompts(self, frame: Any, src: Any, direction: FrameDirection) -> None:
        if not (isinstance(frame, LLMFullResponseStartFrame) and self._is_downstream_output(src, direction)):
            return

        upstream_nodes = self._trace_upstream(src)

        for node in upstream_nodes:
            if "contextaggregator" in node.__class__.__name__.lower():
                print(f"CONTEXT AGGREGATOR FOUND: {node.__class__.__name__}")
                messages_attr = getattr(node, "messages", None)
                if isinstance(messages_attr, list):
                    for msg in messages_attr:
                        if isinstance(msg, dict) and msg.get("role") == "system":
                            content = msg.get("content", "")
                            if content and isinstance(content, str):
                                self._system_prompts.add(content)
                                self._debug(
                                    "SYSTEM PROMPT EXTRACTED",
                                    content_len=len(content),
                                    preview=content[:50] + "..." if len(content) > 50 else content
                                )
                                await self.call.register_system_prompts(self._system_prompts)

        # --- main entry ----------------------------------------------------------

    async def on_push_frame(self, data: FramePushed) -> None:
        src = data.source
        frame = data.frame
        direction = data.direction
        t = self._ns_to_s(data.timestamp)

        # 0) update service timelines (STT/LLM/TTS)
        await self._update_service_timeline(frame, src, direction, t)

        # 1) latency anchors / metrics
        self._handle_latency_markers(frame, src, direction, t)

        # 2) speaking windows
        self._handle_bot_window(frame, src, direction, t)
        self._handle_user_window(frame, src, direction, t)

        # 3) tool-call lifecycle
        await self._handle_tool_call_start(frame, src, direction, t)
        await self._handle_tool_call_end(frame, src, direction, t)

        # 4) accumulate text content
        self._accumulate_content(frame, src, direction, t)

        # 5) flush messages if windows are valid
        await self._maybe_flush_user()
        await self._maybe_flush_assistant()

        # 6) Record errors from error frames
        if isinstance(frame, ErrorFrame):
            current_error = snapshot_error_frame(frame, self._ns_to_s(data.timestamp))
            print(f"\nSNAPSHOT OF ERROR FRAME:\n{current_error.__dict__}")
            await self.call.register_error(current_error)

        # 7) Extract system prompts from LLM-related frames
        await self._extract_system_prompts(frame, src, direction)

        # 8) handle cancellation (ensure finalization runs exactly once)
        if (isinstance(frame, CancelFrame) or isinstance(frame, EndFrame)) and not self.final:
            if self._active_interrupt:
                self._finalize_interrupt_attempt(t, "call_ending")
            self.final = True
            await self.post_process_data()

    @abstractmethod
    async def post_process_data(self):
        ...
