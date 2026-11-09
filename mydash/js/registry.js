import clock from './widgets/clock.js';
import worldClock from './widgets/world-clock.js';
import weather from './widgets/weather.js';
import notes from './widgets/notes.js';
import todos from './widgets/todos.js';
import pomodoro from './widgets/pomodoro.js';
import quotes from './widgets/quotes.js';
import currency from './widgets/currency.js';

const widgets = new Map([
  [clock.id, clock],
  [worldClock.id, worldClock],
  [weather.id, weather],
  [notes.id, notes],
  [todos.id, todos],
  [pomodoro.id, pomodoro],
  [quotes.id, quotes],
  [currency.id, currency],
]);

export function getWidget(id) {
  return widgets.get(id);
}

export function getAllWidgets() {
  return [...widgets.values()];
}
