from __future__ import annotations

import math
import random
import asyncio
from typing import Optional
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Button, Static

from .logic import TossStats, CupResult, toss_once


class CupThrowApp(App):
    CSS_PATH = "styles.tcss"
    BINDINGS = [
        ("space", "throw", "掷杯"),
        ("t", "throw", "掷杯"),
        ("r", "reset", "重置"),
        ("q", "quit", "退出"),
    ]
    _ACTOR_FRAMES: tuple[str, ...] = (
        "     ╭─╮    ○ ○\n"
        "    (•‿•)   ╲\n"
        "    /|\\\n"
        "   _/ \\_",
        "     ╭─╮  ○ ○\n"
        "    (•‿•)╲\n"
        "   ╱/|\\\n"
        "    / \\",
        "     ╭─╮\n"
        "    (☆‿☆) ✦\n"
        "  ○○/ |╲\n"
        "    / \\",
        "     ╭─╮\n"
        "  ✦ (•‿•) ✦\n"
        "     |╲\n"
        "    / \\",
        "     ╭─╮\n"
        "    (•‿•)  🙏\n"
        "    /|\\\n"
        "   _/ \\_",
    )

    def __init__(self, rng_seed: Optional[int] = None, anger_threshold: int = 3) -> None:
        super().__init__()
        self._rng = random.Random(rng_seed)
        self._stats = TossStats()
        self._anger_threshold = anger_threshold

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("杯问天心", id="title")

        with Horizontal(id="stage"):
            yield Static(self._actor_frame_drop(0, total=2), id="actor")
            yield Static("", id="arena")

        yield Static(self._result_text(initial=True), id="result")

        with Horizontal(id="controls"):
            yield Button("掷杯", id="throw", variant="success")
            yield Button("重置统计", id="reset", variant="primary")

        yield Static(self._stats_text(), id="stats")
        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "throw":
            await self._throw_with_animation()
        elif event.button.id == "reset":
            self._reset_stats()

    async def action_throw(self) -> None:
        await self._throw_with_animation()

    def action_reset(self) -> None:
        self._reset_stats()

    def action_quit(self) -> None:
        self.exit()

    def _throw_once(self) -> None:
        result, anger = toss_once(self._stats, self._rng, anger_threshold=self._anger_threshold)

        result_widget = self.query_one("#result", Static)
        stats_widget = self.query_one("#stats", Static)

        if result is CupResult.SHENGBEI:
            last = "圣杯（允杯）：一正一反，神明同意、吉祥如意。"
        else:
            last = "阴杯（笑杯）：两面相同，需再问或心诚再请示。"

        extra: list[str] = []
        if self._stats.consecutive_shengbei >= 3:
            extra.append("连得三圣杯：神明允准 ✅")
            extra.append("问过关帝圣君了，这事可行！")
        if self._stats.consecutive_yin >= 3:
            extra.append("连得三阴杯：诸事不宜，先静心再问。")
        if anger:
            extra.append("触发怒杯：神明不悦，请更虔诚地请示 ⚠️")

        result_widget.update(self._result_text(last_result=last, extra=extra))
        stats_widget.update(self._stats_text())

    async def _throw_with_animation(self) -> None:
        """Show a short character animation, then commit the real toss result."""
        throw_btn = self.query_one('#throw', Button)
        reset_btn = self.query_one('#reset', Button)
        throw_btn.disabled = True
        reset_btn.disabled = True

        result_widget = self.query_one('#result', Static)
        actor_widget = self.query_one('#actor', Static)
        arena_widget = self.query_one('#arena', Static)

        spinner = ["⠋", "⠙", "⠚", "⠞", "⠖", "⠦", "⠴", "⠲", "⠳", "⠓"]
        frames = 18
        for i in range(frames):
            # Random preview faces to simulate tumbling cups
            face = lambda: "凹" if self._rng.choice((True, False)) else "凸"
            s = spinner[i % len(spinner)]
            preview = f"掷杯中… {s}\n〔{face()} · {face()}〕"
            result_widget.update(preview)
            await asyncio.sleep(0.04 + i * 0.004)  # slight ease-out, a bit faster

            # 更新人物与舞台（杯子飞行轨迹）
            actor_widget.update(self._actor_frame_drop(i, total=frames))
            arena_widget.update(self._arena_frame_drop(i, total=frames))

        # Commit real toss outcome
        self._throw_once()

        throw_btn.disabled = False
        reset_btn.disabled = False

        # 清理舞台占位，避免留空白
        actor_widget.update(self._actor_frame_drop(0, total=2))
        arena_widget.update("")

    def _actor_frame_drop(self, i: int, total: int) -> str:
        # 依据进度挑选对应的火柴人动作，让掷杯更具画面感
        phase = i / max(1, total - 1)
        idx = min(len(self._ACTOR_FRAMES) - 1, int(phase * (len(self._ACTOR_FRAMES) - 1)))
        return self._ACTOR_FRAMES[idx]

    def _arena_frame_drop(self, i: int, total: int) -> str:
        # 杯子沿抛物线飞向神桌，带出流光轨迹，适合社交媒体截图
        width = 36
        height = 7
        t = i / max(1, total - 1)
        rows = [[" "] * width for _ in range(height - 2)]

        arc = math.sin(t * math.pi)
        row_index = max(0, (height - 3) - int(arc * (height - 3)))
        x_start = 2
        x_end = width - 6
        x_pos = int(x_start + (x_end - x_start) * t)

        cups = ["⚆", "⚈", "◍", "◐", "◑", "◒", "◓"]
        cup_a = cups[i % len(cups)]
        cup_b = cups[(i + 3) % len(cups)]

        def place(row: int, col: int, ch: str) -> None:
            if 0 <= row < len(rows) and 0 <= col < width:
                rows[row][col] = ch

        place(row_index, min(width - 1, x_pos), cup_a)
        place(max(0, row_index - 1), min(width - 1, x_pos + 2), cup_b)

        trails = ("⋰", "⋱", "⋰", "⋱")
        for offset, symbol in enumerate(trails, start=1):
            place(min(height - 3, row_index + offset), max(0, x_pos - offset * 2), symbol)

        if t > 0.65:
            sparkle_row = min(height - 3, row_index + 1)
            for dx in (-2, 0, 2):
                place(sparkle_row, min(width - 1, max(0, x_pos + dx)), "✦")

        rows_text = ["".join(line) for line in rows]
        altar = "╭─香案─╮".center(width)
        blessing = "╰╂祈福╂╯".center(width, "─")
        return "\n".join(rows_text + [altar, blessing])

    def _reset_stats(self) -> None:
        self._stats = TossStats()
        self.query_one("#result", Static).update(self._result_text(initial=True))
        self.query_one("#stats", Static).update(self._stats_text())

    def _result_text(self, initial: bool = False, last_result: str | None = None, extra: list[str] | None = None) -> str:
        if initial:
            return "按下“掷杯”开始请示神意。"
        lines = [last_result or ""]
        if extra:
            lines.extend(extra)
        return "\n".join(lines)

    def _stats_text(self) -> str:
        s = self._stats
        return (
            f"总次数：{s.total_throws}\n"
            f"圣杯（允杯）：{s.shengbei_count}\n"
            f"阴杯（笑杯）：{s.yincup_count}\n"
            f"怒杯（累计）：{s.anger_count}\n"
            f"连圣杯：{s.consecutive_shengbei}  连阴杯：{s.consecutive_yin}"
        )
