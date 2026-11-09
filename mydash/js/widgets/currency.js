export default {
  id: 'currency',
  title: 'Курсы валют',

  init() {},

  render(container) {
    const statusEl = document.createElement('p');
    statusEl.className = 'currency-status';
    statusEl.textContent = 'Загрузка…';
    container.appendChild(statusEl);

    fetch('https://api.frankfurter.dev/v1/latest?base=USD&symbols=EUR,GBP')
      .then((response) => {
        if (!response.ok) throw new Error('Rates fetch failed');
        return response.json();
      })
      .then((data) => {
        container.replaceChildren();

        const baseEl = document.createElement('p');
        baseEl.className = 'currency-base';
        baseEl.textContent = `База: ${data.base} · ${data.date}`;

        const list = document.createElement('ul');
        list.className = 'currency-list';

        const rates = data.rates ?? {};
        for (const [code, value] of Object.entries(rates)) {
          const item = document.createElement('li');
          item.className = 'currency-item';
          item.textContent = `1 ${data.base} = ${value} ${code}`;
          list.appendChild(item);
        }

        container.appendChild(baseEl);
        container.appendChild(list);
      })
      .catch(() => {
        container.replaceChildren();
        const errorEl = document.createElement('p');
        errorEl.className = 'currency-status';
        errorEl.textContent = 'Не удалось загрузить курсы валют';
        container.appendChild(errorEl);
      });
  },
};
