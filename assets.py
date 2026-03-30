"""Ładowanie grafiki i obsługa trybu ciemnego (dark mode).

Gra stara się załadować grafiki PNG z katalogu `assets/`. Jeżeli pliki nie istnieją, rysuje prostą zastępczą grafikę.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional

import pygame


ASSETS_DIR = Path("assets")

# Lista zasobów, których oczekujemy w katalogu assets.
EXPECTED_ASSETS = [
    "tile",
    "cover",
    "flag",
    "mine",
    "bg",
] + [f"number_{i}" for i in range(1, 9)] + ["background_music"]


class AssetManager:
    """Zarządza wczytywaniem obrazków i trybem dark mode."""

    def __init__(self, dark_mode: bool = False) -> None:
        self.dark_mode = dark_mode
        self._cache: Dict[str, pygame.Surface] = {}

    def set_dark_mode(self, enabled: bool) -> None:
        self.dark_mode = enabled
        self._cache.clear()

    def _asset_path(self, name: str) -> Path:
        mode = "dark" if self.dark_mode else "light"
        return ASSETS_DIR / mode / f"{name}.png"

    def load(self, name: str, scale: Optional[int] = None) -> pygame.Surface:
        """Wczytuje (lub tworzy) obrazek. Skaluje jeśli podano rozmiar."""
        key = f"{name}:{scale}:{self.dark_mode}"
        if key in self._cache:
            return self._cache[key]

        surface = self._load_image(name)
        if scale is not None:
            surface = pygame.transform.smoothscale(surface, (scale, scale))
        self._cache[key] = surface
        return surface

    def _load_image(self, name: str) -> pygame.Surface:
        """Wczytuje obrazek PNG z dysku, a jeżeli to się nie uda, tworzy zastępczy prosty obrazek."""
        path_light = ASSETS_DIR / "light" / f"{name}.png"
        path_dark = ASSETS_DIR / "dark" / f"{name}.png"

        target_path = self._asset_path(name)
        if target_path.exists():
            return AssetManager._safe_load(target_path)

        # fallback do wersji light (nawet gdy jesteśmy w dark mode)
        if path_light.exists():
            base = self._safe_load(path_light)
            if self.dark_mode and not path_dark.exists():
                return self._darken_surface(base)
            return base

        # Brak pliku - rysujemy zastępcze
        return self._make_fallback(name)

    @staticmethod
    def _make_fallback(name: str, size: int = 64) -> pygame.Surface:
        """Tworzy prostą zastępczą grafikę.

        Ta funkcja jest używana gdy brakuje pliku PNG.
        """
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        surf.fill((180, 180, 180, 255))
        pygame.draw.rect(surf, (100, 100, 100), surf.get_rect(), 2)

        # Rysuje literę lub cyfrę na środku jako informację.
        font = pygame.font.SysFont(None, int(size * 0.6))
        if name.startswith("number_"):
            text = name.split("_")[1]
        else:
            text = name[:2].upper()
        text_rendered = font.render(text, True, (20, 20, 20))
        rect = text_rendered.get_rect(center=surf.get_rect().center)
        surf.blit(text_rendered, rect)
        return surf

    @staticmethod
    def _darken_surface(surface: pygame.Surface) -> pygame.Surface:
        """Przyciemnia powierzchnię dla trybu dark mode."""
        darkened = surface.copy()
        # Przyciemniamy przez zmniejszenie jasności
        arr = pygame.surfarray.pixels3d(darkened)
        arr = (arr * 0.7).astype('uint8')  # 70% jasności
        return darkened

    def load_music(self, name: str) -> Optional[pygame.mixer.Sound]:
        """Ładuje muzykę w tle. Zwraca None jeśli nie istnieje (fallback: brak muzyki)."""
        path = ASSETS_DIR / f"{name}.ogg"
        if not path.exists():
            path = ASSETS_DIR / f"{name}.mp3"
        if not path.exists():
            return None
        try:
            return pygame.mixer.Sound(str(path))
        except Exception:
            return None
