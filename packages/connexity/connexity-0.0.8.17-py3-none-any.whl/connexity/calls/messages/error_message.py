import json
import uuid
from typing import Optional, Literal, Dict, Any


class ErrorMessage:
    def __init__(
        self,
        content: str,
        source: Literal["transport", "frame_filter", "observer", "frame_processor", "frame_serializer", "switcher", "llm_service", "tts_service", "stt_service", "tool_call", "unknown"],
        error_frame_id: int,
        seconds_from_start: Optional[float] = None,
        code: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        # generating uuid based on error_frame_id to avoid registering duplicates
        self.id = uuid.uuid5(uuid.NAMESPACE_OID, str(error_frame_id))
        self.content = content
        self.source = source
        self.seconds_from_start = seconds_from_start
        self.code = code
        self.metadata = metadata or {}

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "content": self.content,
            "source": self.source,
            "seconds_from_start": self.seconds_from_start,
            "code": self.code,
            "metadata": self.metadata,
        }
