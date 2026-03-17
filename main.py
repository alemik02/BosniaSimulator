"""Punkt wejścia do gry "Saper".

Uruchomienie: `python main.py`
"""

from __future__ import annotations

from settings import load_settings
from ui import UI


def main() -> None:
    settings = load_settings()
    ui = UI(settings)
    ui.run()


if __name__ == "__main__":
    main()
