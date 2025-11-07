from __future__ import annotations

import argparse
from .ui import CupThrowApp


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fatecast",
        description="杯问天心 - 潮汕掷杯（杯筊）小游戏 - Textual TUI",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="随机数种子，便于复现实验（默认随机）",
    )
    parser.add_argument(
        "--anger-threshold",
        type=int,
        default=3,
        help="连续多少次阴杯触发一次怒杯（默认 3）",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    app = CupThrowApp(rng_seed=args.seed, anger_threshold=args.anger_threshold)
    app.run()


