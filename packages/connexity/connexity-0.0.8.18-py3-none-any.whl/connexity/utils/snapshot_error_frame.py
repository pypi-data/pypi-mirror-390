import asyncio
import inspect
import json
import os
import re
import sys
import time
from collections import deque
from dataclasses import is_dataclass, asdict
from importlib import metadata as importlib_metadata
from typing import Any, Dict, Iterable, Mapping, Optional, Sequence, Literal

from connexity.calls.messages.error_message import ErrorMessage

NETWORK_LABEL: str = "network"

# --------------------------
# Version + redaction utils
# --------------------------

REDACT_KEYS_EXACT = {
    "api_key",
    "apikey",
    "token",
    "access_token",
    "refresh_token",
    "id_token",
    "auth",
    "authorization",
    "secret",
    "password",
    "bearer",
}
REDACT_SAFE_TOK_KEYS = {"max_tokens", "max_completion_tokens"}
REDACT_KEY_SUFFIXES = ("_key", "_api_key", "_apikey", "_token", "_tokens", "_secret", "_password", "_auth", "_authorization")

REDACT_VALUE_PATTERNS = [
    re.compile(r"\bsk_[A-Za-z0-9]{16,}\b"),
    re.compile(r"\bbearer\s+[A-Za-z0-9\-\._~\+\/]+=*\b", re.I),
    re.compile(r"eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}"),
]


def _pipecat_version() -> Optional[str]:
    for dist in ("pipecat-ai", "pipecat"):
        try:
            return importlib_metadata.version(dist)
        except importlib_metadata.PackageNotFoundError:
            continue
    try:
        import pipecat  # type: ignore
        return getattr(pipecat, "__version__", None)
    except Exception:
        return None


def _should_redact_key(key: str) -> bool:
    lk = (key or "").lower()
    if lk in REDACT_SAFE_TOK_KEYS:
        return False
    if lk in REDACT_KEYS_EXACT:
        return True
    if any(lk.endswith(suf) for suf in REDACT_KEY_SUFFIXES):
        if lk in REDACT_SAFE_TOK_KEYS:
            return False
        return True
    return False


def _should_redact_value(val: Any) -> bool:
    if not isinstance(val, str):
        return False
    return any(p.search(val) for p in REDACT_VALUE_PATTERNS)


def _short_repr(obj: Any, max_len: int = 200) -> str:
    try:
        s = repr(obj)
    except Exception:
        try:
            s = str(obj)
        except Exception:
            s = f"<unreprable {type(obj).__name__} at 0x{id(obj):x}>"
    return s if len(s) <= max_len else s[: max_len - 1] + "…"


def _full_classname(obj: Any) -> str:
    try:
        return f"{obj.__class__.__module__}.{obj.__class__.__name__}"
    except Exception:
        return type(obj).__name__


# --------------------------
# JSON-safe conversion
# --------------------------

def _to_jsonable(value: Any, depth: int = 0, max_depth: int = 3) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return "***REDACTED***" if _should_redact_value(value) else value

    if depth >= max_depth:
        return _short_repr(value)

    if is_dataclass(value):
        try:
            return _to_jsonable(asdict(value), depth + 1, max_depth)
        except Exception:
            return _short_repr(value)

    if isinstance(value, Mapping):
        out = {}
        for k, v in list(value.items())[:1000]:
            key = str(k)
            out[key] = "***REDACTED***" if _should_redact_key(key) else _to_jsonable(v, depth + 1, max_depth)
        return out

    if isinstance(value, (list, tuple, set)):
        seq: Iterable[Any] = list(value)
        return [_to_jsonable(v, depth + 1, max_depth) for v in seq[:200]]

    if isinstance(value, (bytes, bytearray)):
        return {"type": type(value).__name__, "len": len(value)}

    return _short_repr(value)


# --------------------------
# Type probes
# --------------------------

def _is_queue(obj: Any) -> bool:
    try:
        import queue as std_queue
        return isinstance(obj, (asyncio.Queue, std_queue.Queue))
    except Exception:
        return isinstance(obj, asyncio.Queue)


def _is_event(obj: Any) -> bool:
    return isinstance(obj, asyncio.Event)


def _is_task(obj: Any) -> bool:
    return isinstance(obj, asyncio.Task)


def _queue_snapshot(q: Any) -> Dict[str, Any]:
    snap = {"type": type(q).__name__}
    try:
        snap["qsize"] = q.qsize()
    except Exception:
        pass
    snap["repr"] = _short_repr(q)
    for attr in ("_queue", "queue"):
        if hasattr(q, attr):
            try:
                buf = list(getattr(q, attr))
                snap["peek"] = _to_jsonable(buf[:3], max_depth=1)
                break
            except Exception:
                pass
    return snap


def _event_snapshot(ev: asyncio.Event) -> Dict[str, Any]:
    return {"type": type(ev).__name__, "is_set": ev.is_set()}


def _task_stack_summary(t: asyncio.Task, limit: int = 1) -> Optional[Dict[str, Any]]:
    frames = t.get_stack(limit)
    if not frames:
        return None
    f = frames[-1]
    info = inspect.getframeinfo(f)
    return {"file": info.filename, "line": info.lineno, "func": info.function}


def _task_snapshot(t: asyncio.Task, with_stack: bool) -> Dict[str, Any]:
    data = {
        "type": type(t).__name__,
        "name": t.get_name() if hasattr(t, "get_name") else None,
        "done": t.done(),
        "cancelled": t.cancelled(),
    }
    if with_stack and not t.done():
        try:
            data["top_stack"] = _task_stack_summary(t)
        except Exception:
            pass
    if t.done() and not t.cancelled():
        try:
            exc = t.exception()
            if exc is not None:
                data["exception_type"] = type(exc).__name__
                data["exception"] = _short_repr(exc, 400)
        except Exception as e:
            data["exception_probe_error"] = str(e)
    return data


# --------------------------
# LLM message extraction
# --------------------------

def _looks_like_llm_message_list(obj: Any) -> bool:
    if not isinstance(obj, Sequence) or not obj:
        return False
    sample = obj[0]
    return isinstance(sample, Mapping) and ("role" in sample and "content" in sample)


def extract_llm_messages_from_mappings(m: Mapping, max_depth: int = 2) -> Optional[Sequence[Mapping]]:
    try:
        for k, v in m.items():
            if str(k).lower() == "messages" and _looks_like_llm_message_list(v):
                return v
            if max_depth > 0 and isinstance(v, Mapping):
                inner = extract_llm_messages_from_mappings(v, max_depth - 1)
                if inner:
                    return inner
    except Exception:
        pass
    return None


# --------------------------
# Categorization helpers
# --------------------------

def _categorize_attr(name: str, value: Any) -> str:
    """
    Classify a processor attribute into a stable category label.
    Rules are ordered (most specific → most general).
    """

    # 0) Normalization
    n = (name or "").lower()

    # Helper: safe token check with minimal collisions (special-case "ws")
    def _contains_any(substrings: tuple[str, ...]) -> bool:
        for s in substrings:
            if s == "ws":
                if n == "ws" or n.startswith("ws_") or n.endswith("_ws") or "_ws_" in n or n.startswith("ws") or n.endswith("ws"):
                    return True
                continue
            if s in n:
                return True
        return False

    # 1) Exact-name overrides
    if n in {"_settings", "_session_properties"}:
        return "config"
    if n in {"_task_manager", "_clock", "_observer"}:
        return "runtime"

    # 2) Identity with exceptions
    if "voice" in n:
        return "model_audio"
    if n in {"context_id", "_context_id", "session_id", "_session_id"}:
        return "contexts"
    if n in {"_id", "id", "_name", "name"} or n.endswith("_id"):
        return "identity"

    # 3) Event handlers
    if "event_handler" in n or n.startswith("on_"):
        return "event_handlers"

    # 4) Async primitives
    if "queue" in n:
        return "asyncio_queues"
    if n.endswith("_tasks") or ("task" in n and not isinstance(value, asyncio.Task)):
        return "asyncio_tasks"
    if "event" in n:
        return "asyncio_events"

    # 5) Model/Audio
    if _contains_any(("voice", "sample_rate", "samplerate", "channels", "codec", "format", "output_format", "bitrate", "audio")):
        return "model_audio"

    if "model" in n:
        return "model"

    # 6) Metrics
    if "metrics" in n:
        return "metrics"

    # 7) Timing
    if _contains_any(("retry", "timeout", "time", "timestamp", "ttfb", "latency", "duration", "cumulative")):
        return "timing"

    # 8) Network (generic)
    if _contains_any(("url", "websocket", "ws", "client", "adapter", "endpoint", "host", "port", "headers", "api_key", "apikey", "token", "auth", "reconnect")):
        return NETWORK_LABEL

    # 9) Contexts (generic)
    if "context" in n or "session" in n:
        return "contexts"

    # 10) Fallback
    return "flags_other"


# --------------------------
# Object snapshots (expand opaque reprs)
# --------------------------

def _scalar_state_from_dictish(obj: Any, max_items: int = 20) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    d = getattr(obj, "__dict__", None)
    if not isinstance(d, dict):
        return out
    for i, (k, v) in enumerate(d.items()):
        if i >= max_items:
            break
        if isinstance(v, (bool, int, float, str, type(None))):
            out[k] = v
    return out


def _snapshot_clock(clock: Any) -> Dict[str, Any]:
    data: Dict[str, Any] = {"class": _full_classname(clock)}
    data.update(_scalar_state_from_dictish(clock))
    return data


def _snapshot_task_manager(tm: Any) -> Dict[str, Any]:
    data: Dict[str, Any] = {"class": _full_classname(tm)}
    try:
        tasks = getattr(tm, "_tasks", None)
        if isinstance(tasks, (set, list, tuple)):
            data["pending_tasks"] = len(tasks)
    except Exception:
        pass
    data.update(_scalar_state_from_dictish(tm))
    return data


def _snapshot_task_observer(obs: Any) -> Dict[str, Any]:
    data: Dict[str, Any] = {"class": _full_classname(obs)}
    try:
        ring = getattr(obs, "_debug_trace", None)
        if isinstance(ring, deque):
            data["trace_len"] = len(ring)
    except Exception:
        pass
    data.update(_scalar_state_from_dictish(obs))
    return data


def _snapshot_strategy(strategy: Any) -> Dict[str, Any]:
    data: Dict[str, Any] = {"class": _full_classname(strategy)}
    data.update(_scalar_state_from_dictish(strategy))
    return data


def _schema_to_json(schema: Any) -> Any:
    try:
        if schema is None:
            return None
        dump = getattr(schema, "model_dump", None)
        if callable(dump):
            return _to_jsonable(dump())
        dump = getattr(schema, "dict", None)
        if callable(dump):
            return _to_jsonable(dump())
        return _to_jsonable(schema)
    except Exception:
        return _short_repr(schema)

def _extract_schema_from_entry(entry: Any) -> Any:
    """
    Pull a function schema from parent class.
    """
    handler = entry.handler
    if handler:
        try:
            handler_class_entity= handler.__self__.__class__(metadata={})
            schema = getattr(handler_class_entity, "schema", None)
            return schema.__dict__ if schema else schema
        except Exception as e:
            print(f"ERROR: {e}")
            pass
    return None

# --------------------------
# Frame + Processor snapshots
# --------------------------

def snapshot_frame_common(frame: Any) -> Dict[str, Any]:
    fields = ("id", "name", "pts", "metadata", "transport_source", "transport_destination")
    data = {}
    for f in fields:
        v = getattr(frame, f, None)
        data[f] = _to_jsonable(v)
    return data


def _snapshot_event_handlers(ev_handlers: Any) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    if isinstance(ev_handlers, Mapping):
        for name, handler in ev_handlers.items():
            info = {"repr": _short_repr(handler)}
            try:
                handlers = getattr(handler, "handlers", None)
                if handlers is not None:
                    info["handlers_count"] = len(list(handlers)) if isinstance(handlers, (list, tuple, set)) else None
            except Exception:
                pass
            info["is_sync"] = getattr(handler, "is_sync", None)
            out[str(name)] = info
    else:
        out["repr"] = _short_repr(ev_handlers)
    return out


def _snapshot_metrics(m: Any) -> Dict[str, Any]:
    if m is None:
        return {}
    data: Dict[str, Any] = {"class": _full_classname(m)}
    try:
        data["ttfb"] = getattr(m, "ttfb", None)
    except Exception:
        pass
    for priv in ("_start_ttfb_time", "_last_ttfb_time", "_start_processing_time"):
        if hasattr(m, priv):
            data[priv] = getattr(m, priv)
    try:
        st = getattr(m, "_start_processing_time", 0) or 0
        if st > 0:
            data["processing_in_progress"] = True
            data["processing_elapsed"] = time.time() - st
        else:
            data["processing_in_progress"] = False
    except Exception:
        pass
    cmd = getattr(m, "_core_metrics_data", None)
    if cmd is not None:
        data["core"] = {
            "processor": getattr(cmd, "processor", None),
            "model": getattr(cmd, "model", None),
        }
    tm = getattr(m, "_task_manager", None)
    if tm is not None:
        data["task_manager"] = {"class": _full_classname(tm)}
    return data


def snapshot_processor(proc: Any, *, include_task_stacks: bool = True) -> Dict[str, Any]:
    if proc is None:
        return {}

    snap: Dict[str, Any] = {"class": _full_classname(proc)}
    for k in ("_name", "_id"):
        if hasattr(proc, k):
            snap["name" if k == "_name" else "id"] = _to_jsonable(getattr(proc, k))

    # prev/next links
    for side in ("_prev", "_next"):
        obj = getattr(proc, side, None)
        if obj is not None:
            snap[side] = {
                "class": _full_classname(obj),
                "name": _short_repr(getattr(obj, "_name", None)),
                "id": getattr(obj, "_id", None),
                "repr": _short_repr(obj),
            }

    # structured known fields
    if hasattr(proc, "_settings"):
        snap["_settings"] = _to_jsonable(getattr(proc, "_settings"), max_depth=3)
    if hasattr(proc, "_session_properties"):
        snap["_session_properties"] = _to_jsonable(getattr(proc, "_session_properties"), max_depth=3)
    if hasattr(proc, "_event_handlers"):
        snap["_event_handlers"] = _snapshot_event_handlers(getattr(proc, "_event_handlers"))

    # special: metrics object (resolved) & contexts summarized
    if hasattr(proc, "_metrics"):
        snap["metrics"] = _snapshot_metrics(getattr(proc, "_metrics"))

    if hasattr(proc, "_contexts"):
        ctx = getattr(proc, "_contexts")
        if isinstance(ctx, Mapping):
            details = {}
            for k, v in ctx.items():
                details[str(k)] = _queue_snapshot(v) if _is_queue(v) else _short_repr(v)
            snap["_contexts"] = {"count": len(ctx), "items": details}
        else:
            snap["_contexts"] = _short_repr(ctx)

    # dynamic scan of remaining attributes (skip ones we already handled)
    skip = {"_name", "_id", "_settings", "_session_properties", "_event_handlers", "_prev", "_next", "_metrics", "_contexts"}
    buckets: Dict[str, Dict[str, Any]] = {}

    for name, val in getattr(proc, "__dict__", {}).items():
        if name in skip:
            continue

        # Expand specific opaque objects
        if name == "_clock":
            buckets.setdefault("runtime", {})[name] = _snapshot_clock(val)
            continue
        if name == "_task_manager":
            buckets.setdefault("runtime", {})[name] = _snapshot_task_manager(val)
            continue
        if name == "_observer":
            buckets.setdefault("runtime", {})[name] = _snapshot_task_observer(val)
            continue
        if name == "_interruption_strategies":
            items = []
            try:
                for s in (list(val) if isinstance(val, (list, tuple, set)) else []):
                    items.append(_snapshot_strategy(s))
            except Exception:
                pass
            buckets.setdefault("flags_other", {})[name] = items
            continue
        if name == "_functions":
            expanded: Dict[str, Any] = {}
            try:
                if isinstance(val, Mapping):
                    for fname, raw in val.items():
                        rec: Dict[str, Any] = {}
                        # include known fields if present (mapping or object)
                        if isinstance(raw, Mapping):
                            rec["function_name"] = str(raw.get("function_name", fname))
                            rec["cancel_on_interruption"] = raw.get("cancel_on_interruption")
                            rec["handler_deprecated"] = raw.get("handler_deprecated")
                            rec["handler"] = _short_repr(raw.get("handler", raw))
                            schema_obj = _extract_schema_from_entry(raw)
                        else:
                            # registry item / handler object
                            rec["function_name"] = getattr(raw, "function_name", fname)
                            rec["cancel_on_interruption"] = getattr(raw, "cancel_on_interruption", None)
                            rec["handler_deprecated"] = getattr(raw, "handler_deprecated", None)
                            handler_obj = getattr(raw, "handler", raw)
                            rec["handler"] = _short_repr(handler_obj)
                            schema_obj = _extract_schema_from_entry(raw)
                        rec["schema"] = _schema_to_json(schema_obj)
                        expanded[str(fname)] = rec
                else:
                    expanded["repr"] = _short_repr(val)
            except Exception:
                expanded["repr"] = _short_repr(val)
            buckets.setdefault("flags_other", {})[name] = expanded
            continue

        # type-based buckets
        try:
            if _is_queue(val):
                buckets.setdefault("asyncio_queues", {})[name] = _queue_snapshot(val)
                continue
            if _is_event(val):
                buckets.setdefault("asyncio_events", {})[name] = _event_snapshot(val)
                continue
            if _is_task(val):
                buckets.setdefault("asyncio_tasks", {})[name] = _task_snapshot(val, include_task_stacks)
                continue
            if isinstance(val, (set, list, tuple)) and val and all(isinstance(x, asyncio.Task) for x in val):
                buckets.setdefault("asyncio_tasks", {})[name] = [_task_snapshot(x, include_task_stacks) for x in val]  # type: ignore
                continue
        except Exception:
            pass

        # generic categorization
        cat = _categorize_attr(name, val)
        if name == "_task_manager" and cat == "asyncio_tasks":
            cat = "runtime"
        buckets.setdefault(cat, {})[name] = _to_jsonable(val)

    # promote buckets
    promotion_order = (
        "runtime",
        "flags_other",
        "model_audio",
        NETWORK_LABEL,
        "network_llm",  # legacy
        "timing",
        "metrics",
        "contexts",
        "config",
        "asyncio_queues",
        "asyncio_events",
        "asyncio_tasks",
    )
    for cat in promotion_order:
        if cat in buckets and buckets[cat]:
            if cat == "metrics":
                snap.setdefault("metrics", {}).update(buckets[cat])
            else:
                snap[cat] = buckets[cat]
    for cat, payload in buckets.items():
        if cat not in promotion_order and payload:
            snap[cat] = payload

    # adapter/client handy summary
    for key in ("_adapter", "_client"):
        if hasattr(proc, key):
            val = getattr(proc, key)
            snap[key] = {"class": _full_classname(val), "repr": _short_repr(val)}

    # heuristic LLM messages
    try:
        llm_messages = extract_llm_messages_from_mappings(getattr(proc, "__dict__", {}))
        if llm_messages:
            snap["llm_messages"] = _to_jsonable(llm_messages, max_depth=3)
    except Exception:
        pass

    # observer debug ring
    obs = getattr(proc, "_observer", None)
    if obs is not None:
        ring = getattr(obs, "_debug_trace", None)
        if isinstance(ring, deque):
            snap["trace"] = list(ring)[-20:]
        last_msgs = getattr(obs, "_debug_last_llm_messages", None)
        if last_msgs:
            snap.setdefault("llm_messages", _to_jsonable(last_msgs, max_depth=3))

    return snap

def _get_error_source(processor) -> Literal["transport", "frame_filter", "observer", "frame_processor", "frame_serializer", "switcher", "llm_service", "tts_service", "stt_service", "tool_call", "unknown"]:
    """
    Heuristically determine component from which the error came from and find the correspondent error type.
    """
    error_sources = {
        "Transport": "transport",
        "Filter": "frame_filter",
        "Observer": "observer",
        "FrameProcessor": "frame_processor",
        "FrameSerializer": "frame_serializer",
        "Switcher": "switcher",
        "LLMService": "llm_service",
        "TTSService": "tts_service",
        "STTService": "stt_service",
        "ToolCall": "tool_call",
    }

    for postfix, source_name in error_sources.items():
        if postfix in processor.name:
            return source_name
    return "unknown"

def snapshot_error_frame(err_frame: Any, seconds_from_start: float, *, include_task_stacks: bool = True) -> ErrorMessage:
    err_obj = ErrorMessage(
        content=getattr(err_frame, "error", None),
        source=_get_error_source(err_frame.processor),
        seconds_from_start=seconds_from_start,
        metadata={
            "error_frame": snapshot_frame_common(err_frame),
            "processor": snapshot_processor(getattr(err_frame, "processor", None),
                                            include_task_stacks=include_task_stacks),
            "pipecat_version": _pipecat_version(),
            "python": sys.version.split()[0],
        },
        error_frame_id=err_frame.id
    )

    return err_obj