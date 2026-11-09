import { get, set } from '../storage.js';

const STORAGE_KEY = 'world-clock-zones';

const ZONES = [
  { id: 'Europe/Kaliningrad', city: 'Калининград' },
  { id: 'Europe/Moscow', city: 'Москва' },
  { id: 'Asia/Yekaterinburg', city: 'Екатеринбург' },
  { id: 'Asia/Novosibirsk', city: 'Новосибирск' },
  { id: 'Asia/Vladivostok', city: 'Владивосток' },
  { id: 'Europe/London', city: 'Лондон' },
  { id: 'Europe/Berlin', city: 'Берлин' },
  { id: 'Europe/Paris', city: 'Париж' },
  { id: 'America/New_York', city: 'Нью-Йорк' },
  { id: 'America/Chicago', city: 'Чикаго' },
  { id: 'America/Los_Angeles', city: 'Лос-Анджелес' },
  { id: 'America/Sao_Paulo', city: 'Сан-Паулу' },
  { id: 'Asia/Dubai', city: 'Дубай' },
  { id: 'Asia/Kolkata', city: 'Дели' },
  { id: 'Asia/Shanghai', city: 'Шанхай' },
  { id: 'Asia/Tokyo', city: 'Токио' },
  { id: 'Australia/Sydney', city: 'Сидней' },
];

const DEFAULT_ZONES = ['Europe/Moscow', 'Europe/London', 'America/New_York', 'Asia/Tokyo'];

const timeFormatters = new Map();
const dateFormatters = new Map();

function getTimeFormatter(zone) {
  if (!timeFormatters.has(zone)) {
    timeFormatters.set(
      zone,
      new Intl.DateTimeFormat('ru-RU', {
        timeZone: zone,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hourCycle: 'h23',
      })
    );
  }
  return timeFormatters.get(zone);
}

function getDateFormatter(zone) {
  if (!dateFormatters.has(zone)) {
    dateFormatters.set(
      zone,
      new Intl.DateTimeFormat('ru-RU', {
        timeZone: zone,
        day: '2-digit',
        month: '2-digit',
      })
    );
  }
  return dateFormatters.get(zone);
}

function loadZones() {
  const saved = get(STORAGE_KEY, null);
  if (!Array.isArray(saved)) return [...DEFAULT_ZONES];
  return saved.filter((id) => ZONES.some((zone) => zone.id === id));
}

export default {
  id: 'world-clock',
  title: 'Мировые часы',

  init() {},

  render(container) {
    let zones = loadZones();

    const list = document.createElement('ul');
    list.className = 'world-clock-list';

    const form = document.createElement('div');
    form.className = 'world-clock-form';

    const select = document.createElement('select');
    select.className = 'world-clock-select';
    select.setAttribute('aria-label', 'Добавить часовой пояс');

    const addButton = document.createElement('button');
    addButton.type = 'button';
    addButton.textContent = 'Добавить';

    form.appendChild(select);
    form.appendChild(addButton);

    function saveZones() {
      set(STORAGE_KEY, zones);
    }

    function updateTimes() {
      const now = new Date();
      for (const row of list.querySelectorAll('.world-clock-item')) {
        const zone = row.dataset.zone;
        const timeEl = row.querySelector('.world-clock-time');
        const dateEl = row.querySelector('.world-clock-date');
        if (!zone || !timeEl || !dateEl) continue;
        timeEl.textContent = getTimeFormatter(zone).format(now);
        dateEl.textContent = getDateFormatter(zone).format(now);
      }
    }

    function createRow(zone) {
      const item = document.createElement('li');
      item.className = 'world-clock-item';
      item.dataset.zone = zone.id;

      const info = document.createElement('div');
      info.className = 'world-clock-info';

      const city = document.createElement('span');
      city.className = 'world-clock-city';
      city.textContent = zone.city;

      const date = document.createElement('span');
      date.className = 'world-clock-date';

      info.appendChild(city);
      info.appendChild(date);

      const time = document.createElement('span');
      time.className = 'world-clock-time';

      const remove = document.createElement('button');
      remove.type = 'button';
      remove.className = 'world-clock-remove';
      remove.textContent = '×';
      remove.title = `Удалить ${zone.city}`;
      remove.addEventListener('click', () => {
        zones = zones.filter((id) => id !== zone.id);
        saveZones();
        renderList();
      });

      item.appendChild(info);
      item.appendChild(time);
      item.appendChild(remove);
      return item;
    }

    function fillSelect() {
      select.replaceChildren();
      const available = ZONES.filter((zone) => !zones.includes(zone.id));

      if (!available.length) {
        const option = document.createElement('option');
        option.value = '';
        option.textContent = 'Все города добавлены';
        select.appendChild(option);
        select.disabled = true;
        addButton.disabled = true;
        return;
      }

      select.disabled = false;
      addButton.disabled = false;
      for (const zone of available) {
        const option = document.createElement('option');
        option.value = zone.id;
        option.textContent = zone.city;
        select.appendChild(option);
      }
    }

    function renderList() {
      list.replaceChildren();

      if (!zones.length) {
        const empty = document.createElement('li');
        empty.className = 'world-clock-empty';
        empty.textContent = 'Нет выбранных часовых поясов';
        list.appendChild(empty);
      } else {
        for (const id of zones) {
          const zone = ZONES.find((item) => item.id === id);
          if (zone) list.appendChild(createRow(zone));
        }
      }

      fillSelect();
      updateTimes();
    }

    addButton.addEventListener('click', () => {
      const id = select.value;
      if (!id || zones.includes(id)) return;
      zones.push(id);
      saveZones();
      renderList();
    });

    container.appendChild(list);
    container.appendChild(form);

    renderList();
    setInterval(updateTimes, 1000);
  },
};
