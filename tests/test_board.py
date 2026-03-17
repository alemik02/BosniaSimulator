"""Testy jednostkowe dla logiki planszy Saper."""

from board import Board


def test_mine_count_and_unique_positions() -> None:
    board = Board(rows=10, cols=10, mines=15, seed=12345)
    # Pierwsze odsłonięcie inicjalizuje losowanie min.
    board.reveal(0, 0)

    mines = [
        (r, c)
        for r in range(board.rows)
        for c in range(board.cols)
        if board.get_tile(r, c).has_mine
    ]
    assert len(mines) == 15
    assert len(set(mines)) == 15


def test_adjacent_count() -> None:
    board = Board(rows=3, cols=3, mines=0)
    # Ręcznie wstawiamy mine w rogu, aby sprawdzić obliczenia.
    board.get_tile(0, 0).has_mine = True
    board._calculate_adjacency()

    assert board.get_tile(0, 0).adjacent == -1
    assert board.get_tile(0, 1).adjacent == 1
    assert board.get_tile(1, 1).adjacent == 1
    assert board.get_tile(2, 2).adjacent == 0


def test_flood_fill_reveal_empty_region() -> None:
    board = Board(rows=4, cols=4, mines=0)
    board._calculate_adjacency()
    board.reveal(2, 2)

    # Przy 0 min wszystkie pola powinny być odsłonięte.
    assert all(board.get_tile(r, c).revealed for r in range(4) for c in range(4))
    assert board.is_win()


def test_win_and_loss_states() -> None:
    board = Board(rows=2, cols=2, mines=1, seed=42)
    # Pierwsze odsłonięcie ustawia miny losowo, ale nie trafia w pole (0,0)
    board.reveal(0, 0)
    assert not board.is_loss()

    # Odsłoń pole z miną
    mine_cell = next(
        (r, c)
        for r in range(board.rows)
        for c in range(board.cols)
        if board.get_tile(r, c).has_mine
    )
    board.reveal(*mine_cell)
    assert board.is_loss()
