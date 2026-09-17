import pytest

from sudoku_logic import count_solutions, generate_puzzle


def test_generate_puzzle_returns_valid_grids():
    puzzle, solution = generate_puzzle(35)

    assert len(puzzle) == 9
    assert all(len(row) == 9 for row in puzzle)
    assert len(solution) == 9
    assert all(len(row) == 9 for row in solution)


def test_generated_puzzle_has_exactly_one_solution():
    puzzle, solution = generate_puzzle(35)

    assert count_solutions(puzzle) == 1
    assert count_solutions(solution) == 1


def test_generate_puzzle_validates_clue_count():
    with pytest.raises(ValueError):
        generate_puzzle(0)

    with pytest.raises(ValueError):
        generate_puzzle(82)
