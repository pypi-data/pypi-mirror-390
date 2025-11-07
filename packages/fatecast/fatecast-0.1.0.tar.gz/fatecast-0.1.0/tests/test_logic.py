from __future__ import annotations

from fatecast.logic import TossStats, CupResult, toss_once


class FakeRng:
    def __init__(self, sequence: list[bool]):
        self._seq = sequence[:]

    def choice(self, _: tuple[bool, bool]) -> bool:
        if not self._seq:
            raise RuntimeError("FakeRng sequence exhausted")
        return self._seq.pop(0)


def test_three_yin_triggers_anger_and_resets_consecutive_yin():
    # Sequence pairs (a,b): same,same,same → three YIN then one SHENGBEI
    # bool stream below is consumed two at a time by simulate_cups
    rng = FakeRng([True, True, False, False, True, True, True, False])
    stats = TossStats()

    r1, a1 = toss_once(stats, rng, anger_threshold=3)
    r2, a2 = toss_once(stats, rng, anger_threshold=3)
    r3, a3 = toss_once(stats, rng, anger_threshold=3)
    r4, a4 = toss_once(stats, rng, anger_threshold=3)

    assert r1 is CupResult.YINBEI
    assert r2 is CupResult.YINBEI
    assert r3 is CupResult.YINBEI
    assert a3 is True  # anger triggered on third consecutive yin
    assert stats.anger_count == 1
    assert stats.consecutive_yin == 0  # reset after anger

    assert r4 is CupResult.SHENGBEI
    assert a4 is False
    assert stats.consecutive_shengbei == 1


def test_shengbei_increments_streak():
    rng = FakeRng([True, False, False, True, True, False])  # different, different, different
    stats = TossStats()
    for _ in range(3):
        result, anger = toss_once(stats, rng, anger_threshold=3)
        assert result is CupResult.SHENGBEI
        assert anger is False
    assert stats.shengbei_count == 3
    assert stats.consecutive_shengbei == 3


