// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];
let timerInterval = null;
let elapsedSeconds = 0;
let hintCount = 0;
let gameCompleted = false;

const SCORES_KEY = 'sudokuTopScores';
const MAX_SCORES = 10;

function formatTime(seconds) {
  const mm = String(Math.floor(seconds / 60)).padStart(2, '0');
  const ss = String(seconds % 60).padStart(2, '0');
  return `${mm}:${ss}`;
}

function updateTimerDisplay() {
  document.getElementById('timer').textContent = formatTime(elapsedSeconds);
}

function startTimer() {
  stopTimer();
  elapsedSeconds = 0;
  updateTimerDisplay();
  timerInterval = setInterval(() => {
    elapsedSeconds += 1;
    updateTimerDisplay();
  }, 1000);
}

function stopTimer() {
  if (timerInterval !== null) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

function getCurrentBoard() {
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const val = inputs[i * SIZE + j].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  return board;
}

function updateHintCount() {
  document.getElementById('hint-count').textContent = hintCount;
}

function handleCellInput(event) {
  const input = event.target;
  if (!input.matches('.sudoku-cell') || input.disabled) return;

  const message = document.getElementById('message');
  if (input.value && !/^[1-9]$/.test(input.value)) {
    input.value = '';
    input.classList.add('invalid-input');
    input.setAttribute('aria-invalid', 'true');
    message.style.color = '#b71c1c';
    message.innerText = 'Invalid entry cleared. Enter a digit from 1 to 9.';
    return;
  }

  input.classList.remove('invalid-input');
  input.setAttribute('aria-invalid', 'false');
}

function loadScores() {
  try {
    const storedScores = localStorage.getItem(SCORES_KEY);
    const scores = storedScores ? JSON.parse(storedScores) : [];
    return Array.isArray(scores) ? scores : [];
  } catch (error) {
    return [];
  }
}

function renderScores() {
  const scoreBody = document.getElementById('score-body');
  const scores = loadScores();
  scoreBody.innerHTML = '';

  if (scores.length === 0) {
    const row = document.createElement('tr');
    const cell = document.createElement('td');
    cell.colSpan = 5;
    cell.textContent = 'No completed games yet.';
    row.appendChild(cell);
    scoreBody.appendChild(row);
    return;
  }

  scores.forEach((score, index) => {
    const row = document.createElement('tr');
    [index + 1, score.name, formatTime(score.time), score.hints, score.difficulty]
      .forEach((value) => {
        const cell = document.createElement('td');
        cell.textContent = value;
        row.appendChild(cell);
      });
    scoreBody.appendChild(row);
  });
}

function saveScore() {
  const playerName = window.prompt('Enter your name for the Top 10 scores:', '');
  const score = {
    name: playerName && playerName.trim() ? playerName.trim() : 'Anonymous',
    time: elapsedSeconds,
    hints: hintCount,
    difficulty: document.getElementById('difficulty').value,
  };

  const scores = loadScores();
  scores.push(score);
  scores.sort((first, second) => first.time - second.time);
  const topScores = scores.slice(0, MAX_SCORES);
  try {
    localStorage.setItem(SCORES_KEY, JSON.stringify(topScores));
  } catch (error) {
    // The game remains usable when browser storage is unavailable.
  }
  renderScores();
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className += ' prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

async function newGame() {
  const difficulty = document.getElementById('difficulty').value;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
  const data = await res.json();
  if (data.error) {
    document.getElementById('message').innerText = data.error;
    return;
  }
  renderPuzzle(data.puzzle);
  gameCompleted = false;
  hintCount = 0;
  updateHintCount();
  document.getElementById('message').innerText = '';
  startTimer();
}

async function useHint() {
  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board: getCurrentBoard()})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }

  const input = document.querySelector(
    `.sudoku-cell[data-row="${data.row}"][data-col="${data.col}"]`
  );
  input.value = data.value;
  input.disabled = true;
  input.className = 'sudoku-cell hinted';
  hintCount += 1;
  updateHintCount();
  msg.style.color = '#388e3c';
  msg.innerText = 'A correct cell was filled in.';
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = getCurrentBoard();
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.className = 'sudoku-cell';
    if (incorrect.has(idx)) {
      inp.className = 'sudoku-cell incorrect';
    } else if (inp.value) {
      inp.className = 'sudoku-cell correct';
    }
  }
  if (incorrect.size === 0) {
    msg.style.color = '#388e3c';
    const hintLabel = hintCount === 1 ? 'hint' : 'hints';
    msg.innerText = `Congratulations! You solved it in ${formatTime(elapsedSeconds)} using ${hintCount} ${hintLabel}.`;
    // Stop/freeze the timer when puzzle is completed correctly
    stopTimer();
    if (!gameCompleted) {
      gameCompleted = true;
      saveScore();
    }
  } else {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some cells are incorrect.';
  }
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('sudoku-board').addEventListener('input', handleCellInput);
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('hint').addEventListener('click', useHint);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  renderScores();
  // initialize
  newGame();
});