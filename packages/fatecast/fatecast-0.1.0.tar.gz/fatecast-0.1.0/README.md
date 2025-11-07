# Chaoshan Cup Divination Mini Game

This is a Textual-powered terminal toy that recreates the Chaoshan folk ritual of cup divination (also known as moon blocks or poe). Interact with the deity by tossing two cups and read the verdict instantly:

- Press the **Throw Cups** button (or shortcuts) to perform a toss.
- Outcomes:
  - **Shengbei (Approval)** – one cup face up and one face down → divine consent.
  - **Yinbei (Laughing Cup)** – both up or both down → ask again or show more sincerity.
  - **Anger Cup** – three Yinbei in a row counts as divine displeasure.
- Hitting **three Shengbei in a row** unlocks a blessing banner.

Reference framework: [Textual](https://github.com/Textualize/textual)

## Run It (Users)

1. Install via PyPI (once released):

```bash
pip install fatecast
```

Or install from source (Python 3.10+ recommended):

```bash
pip install -r requirements.txt
# or just the essentials
pip install textual textual-dev
```

2. Start the TUI:

```bash
python -m fatecast
# or, if installed as a CLI
fatecast
# run directly via textual (no entry script required)
textual run fatecast.ui:CupThrowApp
# serve over Textual Web
textual serve "python -m fatecast"
```

3. Optional: open the Textual developer console from another terminal to watch logs.

```bash
textual console
```

## Development

Editable install and tooling are recommended:

```bash
# install runtime + project in editable mode
pip install -e .

# dev helpers (formatting, lint, tests)
pip install -r requirements-dev.txt
```

Handy Makefile targets:

```bash
make run      # launch the app
make test     # run pytest
make lint     # ruff + mypy
make format   # black
```

### Project Layout

```
fatecast/
  fatecast/
    __init__.py
    __main__.py
    cli.py        # CLI entry point
    logic.py      # cup rules & stats
    ui.py         # Textual interface
  tests/
    test_logic.py
  pyproject.toml
  requirements*.txt
  Makefile
  README.md
```

### Shortcuts

- `t` / `space`: throw cups
- `r`: reset stats
- `q`: quit

### CLI Options

```bash
fatecast --seed 42 --anger-threshold 3
```

## Inspiration

- [rogvibe](https://github.com/yihong0618/rogvibe): a Textual-based terminal raffle that demonstrates clean CLIs and multi-mode UX.
- [Textual](https://github.com/Textualize/textual): the framework powering this TUI.

> Note: rogvibe is on PyPI, so `uvx rogvibe` works out of the box. If fatecast is ever published, `uvx fatecast` would offer the same experience.

## Notes & Odds

- Statistically, Shengbei and Yinbei each appear roughly half of the time (two favorable combinations out of four).
- The anger meter follows a pragmatic rule: every 3 consecutive Yinbei trigger one anger count and reset the streak.
- This project is for cultural interaction and entertainment only—no real divination is implied.

## License

MIT
