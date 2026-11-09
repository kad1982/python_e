let quoteEl;
let authorEl;
let statusEl;

async function loadQuote() {
  statusEl.textContent = 'Загрузка…';
  quoteEl.textContent = '';
  authorEl.textContent = '';

  try {
    const response = await fetch('https://dummyjson.com/quotes/random');
    if (!response.ok) throw new Error('Quote fetch failed');
    const data = await response.json();
    quoteEl.textContent = data.quote ?? '';
    authorEl.textContent = data.author ? `— ${data.author}` : '';
    statusEl.textContent = '';
  } catch {
    quoteEl.textContent = '';
    authorEl.textContent = '';
    statusEl.textContent = 'Сеть недоступна. Не удалось загрузить цитату.';
  }
}

export default {
  id: 'quotes',
  title: 'Цитаты',

  init() {},

  render(container) {
    quoteEl = document.createElement('blockquote');
    quoteEl.className = 'quotes-text';

    authorEl = document.createElement('p');
    authorEl.className = 'quotes-author';

    statusEl = document.createElement('p');
    statusEl.className = 'quotes-status';

    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = 'Новая цитата';
    button.addEventListener('click', () => {
      loadQuote();
    });

    container.appendChild(quoteEl);
    container.appendChild(authorEl);
    container.appendChild(statusEl);
    container.appendChild(button);

    loadQuote();
  },
};
