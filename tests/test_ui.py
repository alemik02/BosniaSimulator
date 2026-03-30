import os

import pygame
import pytest

from settings import Settings
from ui import UI


def test_timer_stops_after_game_over(monkeypatch):
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()

    settings = Settings(dark_mode=False, level="uczen", seed=None)
    ui = UI(settings)

    ui.start_time = 1000.0
    ui.end_time = 1006.5

    assert ui._format_timer() == "00:06:50"

    # Jeżeli end_time jest ustawiony, timer się nie zwiększa.
    monkeypatch.setattr("time.time", lambda: 1100.0)
    assert ui._format_timer() == "00:06:50"

    pygame.quit()
