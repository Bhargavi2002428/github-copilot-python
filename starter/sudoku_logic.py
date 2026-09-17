import copy
import random

SIZE = 9
EMPTY = 0


def deep_copy(board):
    return copy.deepcopy(board)


def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def is_safe(board, row, col, num):
    """Return True when num can be placed in board[row][col]."""
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False

    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def fill_board(board):
    """Fill an empty board with a complete valid Sudoku solution."""
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def count_solutions(board, limit=2):
    """Count solutions for a Sudoku board, stopping early once limit is reached."""
    working = deep_copy(board)
    solutions = 0

    def search():
        nonlocal solutions
        if solutions >= limit:
            return

        empty_cell = None
        for row in range(SIZE):
            for col in range(SIZE):
                if working[row][col] == EMPTY:
                    empty_cell = (row, col)
                    break
            if empty_cell is not None:
                break

        if empty_cell is None:
            solutions += 1
            return

        row, col = empty_cell
        possible = list(range(1, SIZE + 1))
        random.shuffle(possible)
        for candidate in possible:
            if is_safe(working, row, col, candidate):
                working[row][col] = candidate
                search()
                working[row][col] = EMPTY
                if solutions >= limit:
                    return

    search()
    return solutions


def remove_cells(board, clues):
    """Remove cells while preserving a unique Sudoku solution."""
    if clues < 1 or clues > SIZE * SIZE:
        raise ValueError("Clues must be between 1 and 81.")

    cells_to_remove = SIZE * SIZE - clues
    positions = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(positions)

    while cells_to_remove > 0 and positions:
        row, col = positions.pop()
        current_value = board[row][col]
        if current_value == EMPTY:
            continue

        board[row][col] = EMPTY
        if count_solutions(board) != 1:
            board[row][col] = current_value
        else:
            cells_to_remove -= 1

    if cells_to_remove > 0:
        raise ValueError("Unable to generate a unique Sudoku puzzle with the requested clue count.")


def generate_puzzle(clues=35):
    """Generate a valid Sudoku puzzle and its matching solution."""
    if not isinstance(clues, int):
        raise ValueError("Clues must be an integer.")

    if clues < 1 or clues > SIZE * SIZE:
        raise ValueError("Clues must be between 1 and 81.")

    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    puzzle = deep_copy(solution)
    remove_cells(puzzle, clues)
    return puzzle, solution
