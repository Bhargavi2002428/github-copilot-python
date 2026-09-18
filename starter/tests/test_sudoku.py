import pytest

from app import CURRENT, app
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


def test_hint_fills_an_empty_cell_with_the_solution_value():
    client = app.test_client()
    new_response = client.get('/new?difficulty=medium')
    assert new_response.status_code == 200
    puzzle = new_response.get_json()['puzzle']
    board = [row[:] for row in puzzle]

    response = client.post('/hint', json={'board': board})

    assert response.status_code == 200
    hint = response.get_json()
    assert puzzle[hint['row']][hint['col']] == 0
    assert hint['value'] == CURRENT['solution'][hint['row']][hint['col']]


def test_hint_does_not_overwrite_user_entered_cells():
    client = app.test_client()
    new_response = client.get('/new?difficulty=medium')
    assert new_response.status_code == 200
    puzzle = new_response.get_json()['puzzle']
    board = [row[:] for row in puzzle]
    empty_cells = [
        (row, col)
        for row in range(9)
        for col in range(9)
        if puzzle[row][col] == 0
    ]
    entered_row, entered_col = empty_cells[0]
    board[entered_row][entered_col] = 9

    response = client.post('/hint', json={'board': board})

    assert response.status_code == 200
    hint = response.get_json()
    assert (hint['row'], hint['col']) != (entered_row, entered_col)


def test_hint_rejects_board_with_no_empty_cells():
    client = app.test_client()
    new_response = client.get('/new?difficulty=medium')
    assert new_response.status_code == 200

    response = client.post('/hint', json={'board': [[1] * 9 for _ in range(9)]})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'There are no empty cells left for a hint.'}
