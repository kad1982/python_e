import { getWidget } from './registry.js';

const CONFIG_KEY = 'mydash-config';
const THEMES = ['light', 'dark', 'gold', 'birch'];

let currentConfig = null;

async function loadConfig() {
  const response = await fetch('data/default-config.json');
  const defaults = JSON.parse(await response.text());

  const saved = localStorage.getItem(CONFIG_KEY);
  if (!saved) {
    return defaults;
  }

  const parsed = JSON.parse(saved);
  const ids = Array.isArray(parsed.widgets) ? parsed.widgets : [];
  const known = new Set(ids);
  for (const id of defaults.widgets ?? []) {
    if (!known.has(id)) {
      ids.push(id);
    }
  }
  parsed.widgets = ids;
  return parsed;
}

function saveConfig(config) {
  localStorage.setItem(CONFIG_KEY, JSON.stringify(config));
}

function normalizeTheme(theme) {
  return THEMES.includes(theme) ? theme : 'light';
}

function applyTheme(theme) {
  const normalized = normalizeTheme(theme);
  for (const name of THEMES) {
    document.body.classList.remove(`theme-${name}`);
  }
  document.body.classList.add(`theme-${normalized}`);
}

function renderWidgetGrid(widgetIds, config) {
  const grid = document.getElementById('widget-grid');
  grid.innerHTML = '';

  for (const id of widgetIds) {
    const widget = getWidget(id);
    if (!widget) continue;

    const card = document.createElement('article');
    card.className = 'widget-card';
    card.dataset.widgetId = id;

    const header = document.createElement('div');
    header.className = 'widget-header';

    const title = document.createElement('h2');
    title.className = 'widget-title';
    title.textContent = widget.title;

    const handle = document.createElement('span');
    handle.className = 'widget-drag-handle';
    handle.draggable = true;
    handle.textContent = '⠿';
    handle.title = 'Перетащите карточку, чтобы изменить порядок';

    header.appendChild(title);
    header.appendChild(handle);

    const body = document.createElement('div');
    body.className = 'widget-body';

    card.appendChild(header);
    card.appendChild(body);
    grid.appendChild(card);

    widget.init(config);
    widget.render(body);
  }
}

function getDropTarget(grid, x, y, draggedCard) {
  const cards = [...grid.querySelectorAll('.widget-card')].filter(
    (card) => card !== draggedCard
  );

  if (!cards.length) return null;

  let nearest = cards.find((card) => {
    const rect = card.getBoundingClientRect();
    return x >= rect.left && x <= rect.right && y >= rect.top && y <= rect.bottom;
  });

  if (!nearest) {
    let minDistance = Infinity;
    for (const card of cards) {
      const rect = card.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      const distance = Math.hypot(x - centerX, y - centerY);
      if (distance < minDistance) {
        minDistance = distance;
        nearest = card;
      }
    }
  }

  const rect = nearest.getBoundingClientRect();
  const centerX = rect.left + rect.width / 2;
  const centerY = rect.top + rect.height / 2;
  const sameRow = y >= rect.top && y <= rect.bottom;
  const before = sameRow ? x < centerX : y < centerY;

  return { card: nearest, before };
}

function initDragAndDrop(grid, config) {
  let draggedCard = null;

  grid.addEventListener('dragstart', (event) => {
    const handle = event.target.closest('.widget-drag-handle');
    if (!handle) return;

    const card = handle.closest('.widget-card');
    if (!card) return;

    draggedCard = card;
    card.classList.add('dragging');
    event.dataTransfer.effectAllowed = 'move';
    event.dataTransfer.setData('text/plain', card.dataset.widgetId ?? '');
    event.dataTransfer.setDragImage(card, 24, 24);
  });

  grid.addEventListener('dragover', (event) => {
    if (!draggedCard) return;
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';

    const target = getDropTarget(grid, event.clientX, event.clientY, draggedCard);
    if (!target) return;

    if (target.before) {
      grid.insertBefore(draggedCard, target.card);
    } else {
      grid.insertBefore(draggedCard, target.card.nextSibling);
    }
  });

  grid.addEventListener('dragend', () => {
    if (!draggedCard) return;
    draggedCard.classList.remove('dragging');
    draggedCard = null;

    const order = [...grid.querySelectorAll('.widget-card')]
      .map((card) => card.dataset.widgetId)
      .filter(Boolean);

    if (!order.length) return;
    config.widgets = order;
    saveConfig(config);
  });
}

function initThemePicker(config) {
  const select = document.getElementById('theme-select');
  if (!select) return;

  select.value = normalizeTheme(config.settings?.theme);

  select.addEventListener('change', () => {
    const next = normalizeTheme(select.value);
    config.settings = config.settings ?? {};
    config.settings.theme = next;
    saveConfig(config);
    applyTheme(next);
  });
}

function showError(message) {
  const grid = document.getElementById('widget-grid');
  grid.innerHTML = '';
  const el = document.createElement('p');
  el.className = 'error-message';
  el.textContent = message;
  grid.appendChild(el);
}

async function main() {
  try {
    currentConfig = await loadConfig();
    applyTheme(currentConfig.settings?.theme);
    renderWidgetGrid(currentConfig.widgets, currentConfig);
    initThemePicker(currentConfig);
    initDragAndDrop(document.getElementById('widget-grid'), currentConfig);
  } catch {
    showError('Не удалось загрузить конфиг. Проверьте data/default-config.json');
  }
}

main();
