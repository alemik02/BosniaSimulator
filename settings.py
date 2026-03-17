"""Konfiguracja i zapisywanie ustawień gry.

Ten plik zawiera wartości domyślne oraz pomocnicze funkcje do wczytywania i zapisywania
ustawień w pliku JSON (`settings.json`).

Zmiana poziomów (rozmiarów planszy i liczby min) powinna odbywać się tutaj.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


SETTINGS_FILE = Path("settings.json")

# Domyślne poziomy gry. Możesz dodać kolejny poziom, a menu automatycznie go uwzględni.
# Klucze to polskie nazwy poziomów.
LEVELS: Dict[str, "LevelConfig"] = {
    "nowicjusz": (9, 9, 10),
    "uczen": (12, 12, 20),
    "adept": (16, 16, 40),
    "ekspert": (24, 16, 99),
    "mistrz": (32, 20, 160),
}


@dataclass(frozen=True)
class LevelConfig:
    cols: int
    rows: int
    mines: int


@dataclass
class Settings:
    dark_mode: bool = False
    level: str = "uczen"
    seed: Optional[int] = None


def load_settings() -> Settings:
    """Wczytuje ustawienia z pliku JSON, ustawia wartości domyślne przy błędach."""
    if not SETTINGS_FILE.exists():
        return Settings()

    try:
        with SETTINGS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return Settings()

    return Settings(
        dark_mode=bool(data.get("dark_mode", False)),
        level=str(data.get("level", "uczen")),
        seed=data.get("seed"),
    )


def save_settings(settings: Settings) -> None:
    """Zapisuje ustawienia do pliku JSON.

    Nie wyrzuca wyjątków przy błędach zapisu (bezpieczny fallback).
    """
    try:
        with SETTINGS_FILE.open("w", encoding="utf-8") as f:
            json.dump(
                {
                    "dark_mode": settings.dark_mode,
                    "level": settings.level,
                    "seed": settings.seed,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )
    except Exception:
        # Nie przerywamy działania gry, jeżeli zapisu się nie uda.
        pass


def get_level_config(level_name: str) -> LevelConfig:
    """Zwraca konfigurację poziomu na podstawie nazwy.

    Jeśli poziom nie istnieje, zwraca konfigurację dla 'uczen'.
    """
    value = LEVELS.get(level_name)
    if value is None:
        value = LEVELS["uczen"]
    # value może być tuple lub LevelConfig
    if isinstance(value, LevelConfig):
        return value
    return LevelConfig(*value)
