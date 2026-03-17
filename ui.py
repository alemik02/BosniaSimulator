"""Warstwa UI gry Saper.

Renderuje planszę, pasek stanu, menu, obługi wejścia i skalowanie.
"""

from __future__ import annotations

import time
from enum import Enum, auto
from typing import Optional, Tuple

import pygame

from assets import AssetManager
from board import Board, Cell
from settings import LEVELS, Settings, get_level_config, save_settings


VIRTUAL_WIDTH = 1280
VIRTUAL_HEIGHT = 720
MIN_WINDOW_WIDTH = 640
MIN_WINDOW_HEIGHT = 480

STATUS_BAR_HEIGHT = 80
PADDING = 16


class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    GAME_OVER = auto()


class UI:
    def __init__(self, settings: Settings) -> None:
        pygame.init()
        pygame.display.set_caption("Saper")
        self.settings = settings
        self.asset_manager = AssetManager(dark_mode=self.settings.dark_mode)

        self.window = pygame.display.set_mode(
            (VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.RESIZABLE
        )
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)
        self.large_font = pygame.font.SysFont(None, 40)

        self.state = GameState.MENU
        self.selected_level = settings.level
        self.board: Optional[Board] = None
        self.cursor: Optional[Cell] = None
        self.start_time: Optional[float] = None
        self.pause_time: Optional[float] = None
        self.paused = False
        self.last_key_repeat = 0.0
        self._init_game()

    def _init_game(self) -> None:
        """Inicjalizuje planszę (lub restartuje) na podstawie aktualnych ustawień."""
        cfg = get_level_config(self.selected_level)
        self.board = Board(
            rows=cfg.rows,
            cols=cfg.cols,
            mines=cfg.mines,
            seed=self.settings.seed,
        )
        self.cursor = Cell(0, 0)
        self.start_time = None
        self.pause_time = None
        self.paused = False
        self.state = GameState.PLAYING
        self._save_settings()

    def _save_settings(self) -> None:
        self.settings.level = self.selected_level
        self.settings.dark_mode = self.asset_manager.dark_mode
        save_settings(self.settings)

    def run(self) -> None:
        """Główna pętla gry."""
        running = True
        while running:
            self.clock.tick(60)
            self._handle_events()

            if self.state == GameState.PLAYING and not self.paused:
                self._update_timer()

            self._render()
            pygame.display.flip()

            if self.state == GameState.GAME_OVER:
                # Opóźnienie po wygranej/przegranej (dla lepszego wrażenia)
                time.sleep(0.1)

        pygame.quit()

    def _handle_events(self) -> None:
        """Obsługa zdarzeń Pygame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise SystemExit

            if event.type == pygame.WINDOWFOCUSLOST:
                self.paused = True
                self.pause_time = time.time()
            elif event.type == pygame.WINDOWFOCUSGAINED:
                if self.paused and self.pause_time is not None:
                    # Przesuwamy start time o czas pauzy
                    paused_for = time.time() - self.pause_time
                    if self.start_time is not None:
                        self.start_time += paused_for
                    self.paused = False

            if event.type == pygame.VIDEORESIZE:
                self.window = pygame.display.set_mode(
                    (event.w, event.h), pygame.RESIZABLE
                )

            if self.state == GameState.MENU:
                self._handle_menu_event(event)
            else:
                self._handle_game_event(event)

    def _handle_menu_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                raise SystemExit
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self._init_game()
            if event.key == pygame.K_m:
                self._toggle_dark()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mx, my = event.pos
                self._try_click_menu(mx, my)

    def _try_click_menu(self, mx: int, my: int) -> None:
        w, h = self.window.get_size()
        vw, vh, ox, oy = self._scale_params(w, h)
        if vw < 300 or vh < 300:
            return

        # Przelicz kliknięcia na wirtualne współrzędne
        vx = (mx - ox) / (vw / VIRTUAL_WIDTH)
        vy = (my - oy) / (vh / VIRTUAL_HEIGHT)

        # Przycisk zmiany trybu dark
        btn_w = 240
        btn_h = 48
        btn_x = VIRTUAL_WIDTH - btn_w - PADDING
        btn_y = PADDING
        if btn_x <= vx <= btn_x + btn_w and btn_y <= vy <= btn_y + btn_h:
            self._toggle_dark()
            return

        # Lista poziomów
        line_h = 40
        start_y = 200
        for idx, key in enumerate(LEVELS.keys()):
            y = start_y + idx * (line_h + 8)
            if PADDING <= vx <= VIRTUAL_WIDTH - PADDING and y <= vy <= y + line_h:
                self.selected_level = key
                return

    def _handle_game_event(self, event: pygame.event.Event) -> None:
        if self.board is None:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = GameState.MENU
                return
            if event.key == pygame.K_r:
                self._init_game()
                return
            if event.key == pygame.K_m:
                self._toggle_dark()
                return
            if event.key in (pygame.K_UP, pygame.K_w):
                self._move_cursor(dy=-1)
                return
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self._move_cursor(dy=1)
                return
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self._move_cursor(dx=-1)
                return
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                self._move_cursor(dx=1)
                return
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._reveal_cursor()
                return
            if event.key == pygame.K_f:
                self._toggle_flag_cursor()
                return

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if event.button in (1, 2, 3):
                self._handle_click(mx, my, event.button)

    def _handle_click(self, mx: int, my: int, button: int) -> None:
        w, h = self.window.get_size()
        vw, vh, ox, oy = self._scale_params(w, h)

        if vw < MIN_WINDOW_WIDTH or vh < MIN_WINDOW_HEIGHT:
            return

        vx = (mx - ox) / (vw / VIRTUAL_WIDTH)
        vy = (my - oy) / (vh / VIRTUAL_HEIGHT)

        grid_origin = (PADDING, STATUS_BAR_HEIGHT + PADDING)
        if vx < grid_origin[0] or vy < grid_origin[1]:
            return

        tile_size = self._compute_tile_size()
        if tile_size <= 0:
            return

        col = int((vx - grid_origin[0]) / tile_size)
        row = int((vy - grid_origin[1]) / tile_size)
        if not self.board.in_bounds(row, col):
            return

        self.cursor = Cell(row, col)
        # Chord: oba przyciski myszy jednocześnie lub środkowy przycisk
        pressed = pygame.mouse.get_pressed()
        chord = button == 2 or (button == 1 and pressed[2]) or (button == 3 and pressed[0])

        if chord:
            self.board.chord(row, col)
            return

        if button == 1:
            self._reveal(row, col)
        elif button == 3:
            self.board.toggle_flag(row, col)

    def _move_cursor(self, dx: int = 0, dy: int = 0) -> None:
        if self.board is None or self.cursor is None:
            return
        nr = max(0, min(self.board.rows - 1, self.cursor.row + dy))
        nc = max(0, min(self.board.cols - 1, self.cursor.col + dx))
        self.cursor = Cell(nr, nc)

    def _reveal_cursor(self) -> None:
        if not self.cursor:
            return
        self._reveal(self.cursor.row, self.cursor.col)

    def _toggle_flag_cursor(self) -> None:
        if not self.cursor:
            return
        self.board.toggle_flag(self.cursor.row, self.cursor.col)

    def _reveal(self, row: int, col: int) -> None:
        if self.board is None:
            return
        if self.start_time is None:
            self.start_time = time.time()
        self.board.reveal(row, col)
        if self.board.is_win() or self.board.is_loss():
            self.state = GameState.GAME_OVER

    def _toggle_dark(self) -> None:
        self.asset_manager.set_dark_mode(not self.asset_manager.dark_mode)
        self._save_settings()

    def _update_timer(self) -> None:
        if self.start_time is None:
            return
        # Timer jest odczytywany przy renderowaniu, więc tutaj nic nie robimy.
        pass

    def _render(self) -> None:
        """Rysuje całą scenę. Skaluje do rozmiaru okna."""
        w, h = self.window.get_size()
        canvas = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

        if w < MIN_WINDOW_WIDTH or h < MIN_WINDOW_HEIGHT:
            canvas.fill((40, 40, 40))
            self._draw_text_center(
                canvas,
                "Za małe okno — powiększ, proszę (min 640×480)",
                y=VIRTUAL_HEIGHT // 2,
                font=self.large_font,
                color=(230, 230, 230),
            )
            self._blit_scaled(canvas, w, h)
            return

        # Tło
        bg = self.asset_manager.load("bg", scale=VIRTUAL_HEIGHT)
        bg = pygame.transform.smoothscale(bg, (VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
        canvas.blit(bg, (0, 0))

        if self.state == GameState.MENU:
            self._render_menu(canvas)
        else:
            self._render_game(canvas)

        self._blit_scaled(canvas, w, h)

    def _render_menu(self, canvas: pygame.Surface) -> None:
        canvas.fill((50, 50, 60))
        self._draw_text_center(
            canvas, "Saper", y=80, font=self.large_font, color=(240, 240, 240)
        )

        self._draw_text_center(
            canvas,
            "Wybierz poziom i naciśnij ENTER",
            y=140,
            font=self.font,
            color=(200, 200, 200),
        )

        # Lista poziomów
        levels = list(LEVELS.keys())
        start_y = 220
        for idx, name in enumerate(levels):
            y = start_y + idx * 48
            color = (240, 240, 240) if name == self.selected_level else (200, 200, 200)
            cfg = get_level_config(name)
            text = f"{name.title()} ({cfg.cols}×{cfg.rows})"
            self._draw_text(canvas, text, x=160, y=y, font=self.font, color=color)

        # Przycisk trybu ciemnego
        btn_w = 240
        btn_h = 48
        btn_x = VIRTUAL_WIDTH - btn_w - PADDING
        btn_y = PADDING
        pygame.draw.rect(canvas, (60, 60, 60), (btn_x, btn_y, btn_w, btn_h), border_radius=8)
        text = "Dark mode: ON" if self.asset_manager.dark_mode else "Dark mode: OFF"
        self._draw_text(
            canvas,
            text,
            x=btn_x + 14,
            y=btn_y + 12,
            font=self.font,
            color=(220, 220, 220),
        )

        self._draw_text_center(
            canvas,
            "Naciśnij M żeby przełączyć tryb ciemny",
            y=VIRTUAL_HEIGHT - 60,
            font=self.font,
            color=(200, 200, 200),
        )

    def _render_game(self, canvas: pygame.Surface) -> None:
        assert self.board is not None

        # Pasek stanu
        self._render_status_bar(canvas)

        # Plansza
        tile_size = self._compute_tile_size()
        self._render_board(canvas, tile_size)

        if self.state == GameState.GAME_OVER:
            msg = "Wygrana!" if self.board.is_win() else "Przegrałeś"
            self._draw_text_center(
                canvas,
                f"{msg} - naciśnij R, aby zagrać ponownie",
                y=VIRTUAL_HEIGHT - 40,
                font=self.font,
                color=(255, 240, 100),
            )

    def _render_status_bar(self, canvas: pygame.Surface) -> None:
        assert self.board is not None
        pygame.draw.rect(canvas, (30, 30, 40), (0, 0, VIRTUAL_WIDTH, STATUS_BAR_HEIGHT))

        mines_left = self.board.remaining_flags()
        timer = self._format_timer()

        self._draw_text(
            canvas,
            f"Poziom: {self.selected_level.title()}",
            x=PADDING,
            y=16,
            font=self.font,
            color=(240, 240, 240),
        )
        self._draw_text(
            canvas,
            f"Miny: {mines_left}",
            x=PADDING,
            y=44,
            font=self.font,
            color=(240, 240, 240),
        )
        self._draw_text(
            canvas,
            f"Czas: {timer}",
            x=VIRTUAL_WIDTH // 2 - 50,
            y=16,
            font=self.font,
            color=(240, 240, 240),
        )
        self._draw_text(
            canvas,
            "R - reset  |  M - tryb  |  F - flaga  |  strzałki/ENTER",  # instrukcja
            x=VIRTUAL_WIDTH // 2 - 150,
            y=44,
            font=self.font,
            color=(190, 190, 190),
        )

    def _compute_tile_size(self) -> int:
        """Oblicza wielkość kafelka tak, aby cała plansza zmieściła się w oknie."""
        assert self.board is not None
        max_width = VIRTUAL_WIDTH - 2 * PADDING
        max_height = VIRTUAL_HEIGHT - STATUS_BAR_HEIGHT - 2 * PADDING
        raw = min(max_width // self.board.cols, max_height // self.board.rows)
        return max(8, raw)

    def _render_board(self, canvas: pygame.Surface, tile_size: int) -> None:
        assert self.board is not None
        origin_x = PADDING
        origin_y = STATUS_BAR_HEIGHT + PADDING

        for r in range(self.board.rows):
            for c in range(self.board.cols):
                x = origin_x + c * tile_size
                y = origin_y + r * tile_size
                self._render_tile(canvas, r, c, x, y, tile_size)

        # Kursor (dla sterowania klawiaturą)
        if self.cursor:
            cx = origin_x + self.cursor.col * tile_size
            cy = origin_y + self.cursor.row * tile_size
            rect = pygame.Rect(cx, cy, tile_size, tile_size)
            pygame.draw.rect(canvas, (255, 255, 255), rect, width=2)

    def _render_tile(
        self,
        canvas: pygame.Surface,
        row: int,
        col: int,
        x: int,
        y: int,
        tile_size: int,
    ) -> None:
        """Rysuje pojedynczy kafelek na podstawie stanu planszy."""
        assert self.board is not None
        tile = self.board.get_tile(row, col)

        if not tile.revealed:
            cover = self.asset_manager.load("cover", scale=tile_size)
            canvas.blit(cover, (x, y))
            if tile.flagged:
                flag = self.asset_manager.load("flag", scale=tile_size)
                canvas.blit(flag, (x, y))
            return

        if tile.has_mine:
            mine = self.asset_manager.load("mine", scale=tile_size)
            canvas.blit(mine, (x, y))
            return

        # Puste pole lub numer
        tile_img = self.asset_manager.load("tile", scale=tile_size)
        canvas.blit(tile_img, (x, y))
        if tile.adjacent > 0:
            num = self.asset_manager.load(f"number_{tile.adjacent}", scale=tile_size)
            canvas.blit(num, (x, y))

    def _format_timer(self) -> str:
        if self.start_time is None:
            return "00:00"
        elapsed = int(max(0, time.time() - self.start_time))
        minutes = elapsed // 60
        seconds = elapsed % 60
        return f"{minutes:02d}:{seconds:02d}"

    def _blit_scaled(self, canvas: pygame.Surface, w: int, h: int) -> None:
        """Skaluje główny canvas do rozmiaru okna, zachowując proporcje."""
        vw, vh, ox, oy = self._scale_params(w, h)
        scaled = pygame.transform.smoothscale(canvas, (int(vw), int(vh)))
        self.window.fill((0, 0, 0))
        self.window.blit(scaled, (ox, oy))

    def _scale_params(self, w: int, h: int) -> Tuple[float, float, int, int]:
        """Oblicza skalę + offset do renderowania canvas w oknie."""
        scale = min(w / VIRTUAL_WIDTH, h / VIRTUAL_HEIGHT)
        vw = VIRTUAL_WIDTH * scale
        vh = VIRTUAL_HEIGHT * scale
        ox = int((w - vw) / 2)
        oy = int((h - vh) / 2)
        return vw, vh, ox, oy

    def _draw_text(
        self,
        surface: pygame.Surface,
        text: str,
        x: int,
        y: int,
        font: pygame.font.Font,
        color: Tuple[int, int, int] = (255, 255, 255),
    ) -> None:
        rendered = font.render(text, True, color)
        surface.blit(rendered, (x, y))

    def _draw_text_center(
        self,
        surface: pygame.Surface,
        text: str,
        y: int,
        font: pygame.font.Font,
        color: Tuple[int, int, int] = (255, 255, 255),
    ) -> None:
        rendered = font.render(text, True, color)
        rect = rendered.get_rect(center=(VIRTUAL_WIDTH // 2, y))
        surface.blit(rendered, rect)
