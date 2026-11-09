import * as storage from '../storage.js';

const WORK_SECONDS = 25 * 60;
const BREAK_SECONDS = 5 * 60;

let remaining = WORK_SECONDS;
let mode = 'work';
let running = false;
let completed = 0;
let timerId = null;

function persist() {
  storage.set('pomodoro', { remaining, mode, completed });
}

function pad(n) {
  return String(n).padStart(2, '0');
}

function formatTime(total) {
  const minutes = Math.floor(total / 60);
  const seconds = total % 60;
  return `${pad(minutes)}:${pad(seconds)}`;
}

function clearTimer() {
  if (timerId !== null) {
    clearInterval(timerId);
    timerId = null;
  }
}

function startTimer(onTick) {
  clearTimer();
  timerId = setInterval(onTick, 1000);
}

export default {
  id: 'pomodoro',
  title: 'Pomodoro',

  init() {
    const saved = storage.get('pomodoro', null);
    remaining = typeof saved?.remaining === 'number' ? saved.remaining : WORK_SECONDS;
    mode = saved?.mode === 'break' ? 'break' : 'work';
    completed = typeof saved?.completed === 'number' ? saved.completed : 0;
    running = false;
    clearTimer();
  },

  render(container) {
    clearTimer();
    running = false;

    const timeEl = document.createElement('div');
    timeEl.className = 'pomodoro-time';

    const modeEl = document.createElement('div');
    modeEl.className = 'pomodoro-mode';

    const countEl = document.createElement('div');
    countEl.className = 'pomodoro-count';

    const controls = document.createElement('div');
    controls.className = 'pomodoro-controls';

    const startBtn = document.createElement('button');
    startBtn.type = 'button';
    startBtn.textContent = 'Старт';

    const pauseBtn = document.createElement('button');
    pauseBtn.type = 'button';
    pauseBtn.textContent = 'Пауза';

    const resetBtn = document.createElement('button');
    resetBtn.type = 'button';
    resetBtn.className = 'pomodoro-reset';
    resetBtn.textContent = 'Сброс';

    controls.appendChild(startBtn);
    controls.appendChild(pauseBtn);
    controls.appendChild(resetBtn);

    function paint() {
      timeEl.textContent = formatTime(remaining);
      modeEl.textContent = mode === 'work' ? 'Работа · 25 мин' : 'Отдых · 5 мин';
      countEl.textContent = `Завершено циклов: ${completed}`;
      startBtn.disabled = running;
      pauseBtn.disabled = !running;
    }

    function tick() {
      if (remaining > 0) {
        remaining -= 1;
        persist();
        paint();
        return;
      }

      if (mode === 'work') {
        completed += 1;
        mode = 'break';
        remaining = BREAK_SECONDS;
      } else {
        mode = 'work';
        remaining = WORK_SECONDS;
      }
      persist();
      paint();
    }

    startBtn.addEventListener('click', () => {
      if (running) return;
      running = true;
      startTimer(tick);
      paint();
    });

    pauseBtn.addEventListener('click', () => {
      running = false;
      clearTimer();
      persist();
      paint();
    });

    resetBtn.addEventListener('click', () => {
      running = false;
      clearTimer();
      mode = 'work';
      remaining = WORK_SECONDS;
      persist();
      paint();
    });

    container.appendChild(timeEl);
    container.appendChild(modeEl);
    container.appendChild(countEl);
    container.appendChild(controls);
    paint();
  },
};
