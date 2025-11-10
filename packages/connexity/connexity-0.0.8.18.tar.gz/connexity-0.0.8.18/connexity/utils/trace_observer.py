from collections import deque
from typing import Any, Mapping, Optional, Sequence

# --------------------------------------------------
# Optional tracing helper
# --------------------------------------------------

def _looks_like_llm_message_list(obj: Any) -> bool:
    if not isinstance(obj, Sequence) or not obj:
        return False
    sample = obj[0]
    return isinstance(sample, Mapping) and ("role" in sample and "content" in sample)

def _full_classname(obj: Any) -> str:
    try:
        return f"{obj.__class__.__module__}.{obj.__class__.__name__}"
    except Exception:
        return type(obj).__name__

class _TraceObserver:
    def __init__(self, ring: deque, max_msgs: int = 40):
        self._ring = ring
        self._max_msgs = max_msgs
        self._last_llm_messages: Optional[Sequence[Mapping]] = None

    async def on_process_frame(self, frame: Any, *_, **__):
        self._record(frame)

    async def on_push_frame(self, frame: Any, *_, **__):
        self._record(frame)

    def _record(self, frame: Any):
        try:
            cls = _full_classname(frame)
            item = {
                "id": getattr(frame, "id", None),
                "name": getattr(frame, "name", None),
                "class": cls,
                "pts": getattr(frame, "pts", None),
            }
            if hasattr(frame, "messages"):
                messages = getattr(frame, "messages")
                if _looks_like_llm_message_list(messages):
                    self._last_llm_messages = messages[-self._max_msgs :]
            self._ring.append(item)
        except Exception:
            pass


def attach_trace_observer(task_observer: Any, ring_size: int = 200) -> None:
    if task_observer is None:
        return
    if getattr(task_observer, "_debug_trace", None) is None:
        task_observer._debug_trace = deque(maxlen=ring_size)          # type: ignore[attr-defined]
        task_observer._debug_last_llm_messages = None                 # type: ignore[attr-defined]
    ring: deque = task_observer._debug_trace                          # type: ignore[attr-defined]
    observer = _TraceObserver(ring)
    try:
        add = getattr(task_observer, "add_observer", None)
        if callable(add):
            add(observer)
            setattr(task_observer, "_debug_last_llm_messages", observer._last_llm_messages)  # type: ignore[attr-defined]
    except Exception:
        pass