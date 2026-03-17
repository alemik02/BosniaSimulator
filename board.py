"""Logika planszy gry "Saper".

Ta warstwa nie zna Pygame'a i może być użyta w testach jednostkowych.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Set, Tuple


@dataclass(frozen=True)
class Cell:
    """Reprezentacja pojedynczego pola na planszy."""

    row: int
    col: int


@dataclass
class Tile:
    """Stan pojedynczego kafelka w planszy."""

    has_mine: bool = False
    revealed: bool = False
    flagged: bool = False
    adjacent: int = 0


class Board:
    """Plansza gry "Saper".

    Zasady:
    - Kafelki są indeksowane (row, col), zaczynając od (0, 0) w lewym górnym rogu.
    - Pierwsze odsłonięcie nigdy nie trafia na minę (jeśli użyto `first_click_safe=True`).
    """

    def __init__(
        self,
        rows: int,
        cols: int,
        mines: int,
        seed: Optional[int] = None,
        first_click_safe: bool = True,
    ) -> None:
        self.rows = max(1, rows)
        self.cols = max(1, cols)
        self.mines = max(0, min(mines, self.rows * self.cols - 1))
        self.seed = seed
        self.first_click_safe = first_click_safe
        self._grid: List[List[Tile]] = [
            [Tile() for _ in range(self.cols)] for _ in range(self.rows)
        ]
        self._mines_placed = False
        self._revealed_count = 0
        self._game_over = False
        self._won = False

    def reset(self) -> None:
        """Resetuje stan planszy (bez zmiany rozmiaru/mine count)."""
        self._grid = [
            [Tile() for _ in range(self.cols)] for _ in range(self.rows)
        ]
        self._mines_placed = False
        self._revealed_count = 0
        self._game_over = False
        self._won = False

    def _neighbors(self, row: int, col: int) -> Iterable[Cell]:
        """Zwraca sąsiadujące komórki (8 kierunków)."""
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    yield Cell(nr, nc)

    def _place_mines(self, safe_zone: Optional[Cell] = None) -> None:
        """Losuje mine, pomijając strefę bezpieczną (najczęściej pierwsze kliknięcie)."""
        rand = random.Random(self.seed)
        all_cells = [Cell(r, c) for r in range(self.rows) for c in range(self.cols)]
        if safe_zone is not None and self.first_click_safe:
            # Wykluczamy strefę (bezpieczne pole + otoczenie) z losowania.
            safe_cells: Set[Tuple[int, int]] = set()
            safe_cells.add((safe_zone.row, safe_zone.col))
            for n in self._neighbors(safe_zone.row, safe_zone.col):
                safe_cells.add((n.row, n.col))
            safe_excluded = [c for c in all_cells if (c.row, c.col) not in safe_cells]

            # Jeśli po wykluczeniu strefy nie ma wystarczająco dużo pól,
            # cofamy się do wykluczenia tylko pierwszego kliknięcia.
            if len(safe_excluded) >= self.mines:
                all_cells = safe_excluded
            else:
                all_cells = [
                    c
                    for c in (Cell(r, c) for r in range(self.rows) for c in range(self.cols))
                    if not (c.row == safe_zone.row and c.col == safe_zone.col)
                ]

        chosen = rand.sample(all_cells, k=self.mines)
        for cell in chosen:
            self._grid[cell.row][cell.col].has_mine = True

        self._calculate_adjacency()
        self._mines_placed = True

    def _calculate_adjacency(self) -> None:
        """Oblicza, ile min jest wokół każdego kafelka."""
        for r in range(self.rows):
            for c in range(self.cols):
                if self._grid[r][c].has_mine:
                    self._grid[r][c].adjacent = -1
                    continue
                count = 0
                for n in self._neighbors(r, c):
                    if self._grid[n.row][n.col].has_mine:
                        count += 1
                self._grid[r][c].adjacent = count

    def in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.cols

    def get_tile(self, row: int, col: int) -> Tile:
        return self._grid[row][col]

    def reveal(self, row: int, col: int) -> None:
        """Odsłania pole.

        - Pierwsze odsłonięcie inicjalizuje losowanie min (jeżeli nie wylosowano).
        - Jeżeli odsłonięto minę-> przegrana.
        - Jeżeli odsłonięto puste pole -> flood fill odsłania okolicę.
        """
        if self._game_over or not self.in_bounds(row, col):
            return

        if not self._mines_placed:
            self._place_mines(safe_zone=Cell(row, col) if self.first_click_safe else None)

        tile = self._grid[row][col]
        if tile.revealed or tile.flagged:
            return

        tile.revealed = True
        self._revealed_count += 1

        if tile.has_mine:
            self._game_over = True
            self._won = False
            return

        if tile.adjacent == 0:
            # Flood fill
            for n in self._neighbors(row, col):
                if not self._grid[n.row][n.col].revealed:
                    self.reveal(n.row, n.col)

        self._update_win_state()

    def toggle_flag(self, row: int, col: int) -> None:
        """Oznacza / odznacza flagę."""
        if self._game_over or not self.in_bounds(row, col):
            return
        tile = self._grid[row][col]
        if tile.revealed:
            return
        tile.flagged = not tile.flagged

    def chord(self, row: int, col: int) -> None:
        """Jeśli liczba flag wokół kafelka równa jest liczbie, odsłania sąsiadujące pola."""
        if self._game_over or not self.in_bounds(row, col):
            return
        tile = self._grid[row][col]
        if not tile.revealed or tile.adjacent <= 0:
            return

        flags = 0
        for n in self._neighbors(row, col):
            if self._grid[n.row][n.col].flagged:
                flags += 1

        if flags != tile.adjacent:
            return

        for n in self._neighbors(row, col):
            n_tile = self._grid[n.row][n.col]
            if not n_tile.revealed and not n_tile.flagged:
                self.reveal(n.row, n.col)

    def remaining_flags(self) -> int:
        """Liczba pozostałych flag (nieujemna)."""
        used = sum(1 for r in range(self.rows) for c in range(self.cols) if self._grid[r][c].flagged)
        return max(0, self.mines - used)

    def is_win(self) -> bool:
        return self._won

    def is_loss(self) -> bool:
        return self._game_over and not self._won

    def _update_win_state(self) -> None:
        """Aktualizuje stan wygranej na podstawie odsłoniętych pól."""
        if self._game_over:
            return

        total_tiles = self.rows * self.cols
        if self._revealed_count >= total_tiles - self.mines:
            self._game_over = True
            self._won = True

    def get_neighbors(self, row: int, col: int) -> List[Cell]:
        """Zwraca listę sąsiednich komórek. Użyteczne w testach."""
        return list(self._neighbors(row, col))

    def all_cells(self) -> List[Cell]:
        """Zwraca wszystkie komórki planszy."""
        return [Cell(r, c) for r in range(self.rows) for c in range(self.cols)]
