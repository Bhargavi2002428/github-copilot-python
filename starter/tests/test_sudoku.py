import pytest

from app import app
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


@pytest.mark.parametrize(
    ('difficulty', 'expected_clues'),
    [('easy', 45), ('medium', 35), ('hard', 25)],
)
def test_new_game_uses_difficulty_clue_count(difficulty, expected_clues):
    client = app.test_client()

    response = client.get(f'/new?difficulty={difficulty}')

    assert response.status_code == 200
    puzzle = response.get_json()['puzzle']
    assert sum(cell != 0 for row in puzzle for cell in row) == expected_clues


def test_new_game_defaults_to_medium_difficulty():
    client = app.test_client()

    response = client.get('/new')

    assert response.status_code == 200
    puzzle = response.get_json()['puzzle']
    assert sum(cell != 0 for row in puzzle for cell in row) == 35


def test_new_game_rejects_invalid_difficulty():
    client = app.test_client()

    response = client.get('/new?difficulty=extreme')

    assert response.status_code == 400
    assert response.get_json() == {
        'error': 'Invalid difficulty. Choose easy, medium, or hard.'
    }
