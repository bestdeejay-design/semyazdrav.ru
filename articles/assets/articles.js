(() => {
  const cards = [...document.querySelectorAll('.article-card')];
  if (!cards.length) return;
  const searchInput = document.querySelector('#article-search');
  const filterButtons = [...document.querySelectorAll('[data-filter]')];
  const noResults = document.querySelector('#no-results');
  let currentCategory = 'all';
  let currentQuery = '';

  const filterCards = () => {
    let visible = 0;
    cards.forEach((card) => {
      const matchesCategory = currentCategory === 'all' || card.dataset.category === currentCategory;
      const matchesQuery = (card.dataset.search || '').includes(currentQuery);
      const show = matchesCategory && matchesQuery;
      card.hidden = !show;
      if (show) visible += 1;
    });
    if (noResults) noResults.hidden = visible !== 0;
  };

  searchInput?.addEventListener('input', (event) => {
    currentQuery = event.currentTarget.value.trim().toLocaleLowerCase('ru-RU');
    filterCards();
  });
  filterButtons.forEach((button) => button.addEventListener('click', () => {
    currentCategory = button.dataset.filter;
    filterButtons.forEach((item) => {
      const active = item === button;
      item.classList.toggle('is-active', active);
      item.setAttribute('aria-pressed', String(active));
    });
    filterCards();
  }));
})();
