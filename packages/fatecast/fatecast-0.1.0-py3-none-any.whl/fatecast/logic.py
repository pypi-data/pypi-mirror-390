from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Tuple
import random


class CupResult(Enum):
    SHENGBEI = auto()  # 圣杯：一正一反
    YINBEI = auto()    # 阴杯：两面相同


@dataclass
class TossStats:
    total_throws: int = 0
    shengbei_count: int = 0
    yincup_count: int = 0
    anger_count: int = 0
    consecutive_shengbei: int = 0
    consecutive_yin: int = 0


def simulate_cups(rng: random.Random | None = None) -> CupResult:
    """Simulate one toss of two cups and return the raw outcome.

    True/False stand in for the two faces; different → 圣杯, same → 阴杯.
    """
    if rng is None:
        rng = random
    a = rng.choice((True, False))
    b = rng.choice((True, False))
    return CupResult.SHENGBEI if a != b else CupResult.YINBEI


def toss_once(stats: TossStats, rng: random.Random | None = None, anger_threshold: int = 3) -> Tuple[CupResult, bool]:
    """Apply a single toss to stats and return (result, anger_triggered)."""
    result = simulate_cups(rng)
    stats.total_throws += 1

    anger_triggered = False
    if result is CupResult.SHENGBEI:
        stats.shengbei_count += 1
        stats.consecutive_shengbei += 1
        stats.consecutive_yin = 0
    else:
        stats.yincup_count += 1
        stats.consecutive_yin += 1
        stats.consecutive_shengbei = 0

        if stats.consecutive_yin >= anger_threshold:
            stats.anger_count += 1
            stats.consecutive_yin = 0
            anger_triggered = True

    return result, anger_triggered


