import * as storage from '../storage.js';

let tasks = [];

function persist() {
  storage.set('todos', tasks);
}

function nextId() {
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export default {
  id: 'todos',
  title: 'Список дел',

  init() {
    const saved = storage.get('todos', []);
    tasks = Array.isArray(saved) ? saved : [];
  },

  render(container) {
    const form = document.createElement('form');
    form.className = 'todos-form';

    const input = document.createElement('input');
    input.className = 'todos-input';
    input.type = 'text';
    input.placeholder = 'Новая задача…';
    input.setAttribute('aria-label', 'Новая задача');

    const addBtn = document.createElement('button');
    addBtn.type = 'submit';
    addBtn.textContent = 'Добавить';

    form.appendChild(input);
    form.appendChild(addBtn);

    const list = document.createElement('ul');
    list.className = 'todos-list';

    function drawList() {
      list.replaceChildren();

      for (const task of tasks) {
        const item = document.createElement('li');
        item.className = 'todos-item';
        if (task.done) item.classList.add('todos-item-done');

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'todos-check';
        checkbox.checked = Boolean(task.done);
        checkbox.setAttribute('aria-label', 'Выполнена');

        const label = document.createElement('span');
        label.className = 'todos-text';
        label.textContent = task.text;

        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'todos-remove';
        removeBtn.textContent = 'Удалить';

        checkbox.addEventListener('change', () => {
          task.done = checkbox.checked;
          persist();
          drawList();
        });

        removeBtn.addEventListener('click', () => {
          tasks = tasks.filter((t) => t.id !== task.id);
          persist();
          drawList();
        });

        item.appendChild(checkbox);
        item.appendChild(label);
        item.appendChild(removeBtn);
        list.appendChild(item);
      }
    }

    form.addEventListener('submit', (event) => {
      event.preventDefault();
      const text = input.value.trim();
      if (!text) return;
      tasks.push({ id: nextId(), text, done: false });
      persist();
      input.value = '';
      drawList();
    });

    container.appendChild(form);
    container.appendChild(list);
    drawList();
  },
};
