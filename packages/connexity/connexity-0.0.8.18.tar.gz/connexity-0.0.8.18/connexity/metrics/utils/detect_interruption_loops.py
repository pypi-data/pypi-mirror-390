from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Sequence


@dataclass(frozen=True)
class InterruptionLoopConfig:
    min_interrupter_words: int = 2
    min_overlap_duration: float = 0.5
    min_overlaps_in_loop: int = 2
    max_gap_between_overlaps: float = 10.0


DEFAULT_INTERRUPTION_LOOP_CONFIG = InterruptionLoopConfig()


def _overlap_duration(overlap: Dict[str, Any]) -> float | None:
    first_ts = overlap.get("first_transcript_at")
    end_ts = overlap.get("end")
    if first_ts is None or end_ts is None:
        return None
    return max(0.0, end_ts - first_ts)


def _qualifies(overlap: Dict[str, Any], config: InterruptionLoopConfig) -> bool:
    duration = _overlap_duration(overlap)
    if duration is None:
        return False
    if duration < config.min_overlap_duration:
        return False
    if overlap.get("interrupter_words", 0) < config.min_interrupter_words:
        return False
    return True


def detect_interruption_loops(
    overlaps: Sequence[Dict[str, Any]] | None,
    *,
    config: InterruptionLoopConfig = DEFAULT_INTERRUPTION_LOOP_CONFIG,
) -> List[Dict[str, Any]]:
    """Detect interruption loops from a sequence of overlaps.

    Args:
        overlaps: Iterable of overlap dictionaries. Each overlap should contain at
            least the keys: ``first_transcript_at`` (float), ``end`` (float),
            ``interrupter_words`` (int).
        config: Configuration thresholds for detection.

    Returns:
        List of dicts, each representing an interruption loop with keys:
            ``start``: first transcript time of first overlap in loop
            ``end``: end time of last overlap in loop
            ``overlaps``: list of overlap dicts in the loop (shallow copies)
    """

    if not overlaps:
        return []

    qualifying = [
        overlap
        for overlap in overlaps
        if _qualifies(overlap, config)
    ]

    if len(qualifying) < config.min_overlaps_in_loop:
        return []

    # sort by first transcript time to evaluate chronological order
    qualifying.sort(key=lambda o: o.get("first_transcript_at", float("inf")))

    loops: List[Dict[str, Any]] = []
    loop_candidate_overlaps: List[Dict[str, Any]] = []

    for overlap in qualifying:
        first_ts = overlap.get("first_transcript_at")
        end_ts = overlap.get("end")
        if first_ts is None or end_ts is None:
            continue

        if not loop_candidate_overlaps:
            loop_candidate_overlaps.append(overlap)
            continue

        prev = loop_candidate_overlaps[-1]
        prev_end = prev.get("end")
        gap = (first_ts - prev_end) if (prev_end is not None) else None

        if gap is not None and gap < config.max_gap_between_overlaps:
            loop_candidate_overlaps.append(overlap)
        else:
            if len(loop_candidate_overlaps) >= config.min_overlaps_in_loop:
                loops.append(_record_loop(
                    overlaps=loop_candidate_overlaps,
                    config=config
                ))
            loop_candidate_overlaps = [overlap]

    if len(loop_candidate_overlaps) >= config.min_overlaps_in_loop:
        loops.append(_record_loop(
            overlaps=loop_candidate_overlaps,
            config=config
        ))

    return loops


def _record_loop(overlaps: Sequence[Dict[str, Any]], config: InterruptionLoopConfig) -> Dict[str, Any]:
    start_ts = overlaps[0].get("first_transcript_at")
    end_ts = overlaps[-1].get("end")
    overlaps_copy = [dict(overlap) for overlap in overlaps]
    return {
        "loop_start": start_ts,
        "loop_end": end_ts,
        "overlaps": overlaps_copy,
        "thresholds": {
            "min_interrupter_words": config.min_interrupter_words,
            "min_overlap_duration_secs": config.min_overlap_duration,
            "min_overlaps_in_loop": config.min_overlaps_in_loop,
            "max_gap_between_overlaps_secs": config.max_gap_between_overlaps
        }
    }