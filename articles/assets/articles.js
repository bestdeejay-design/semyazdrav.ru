(() => {
  const cards = [...document.querySelectorAll('.article-card')];
  if (!cards.length) return;
  const searchInput = document.querySelector('#article-search');
  const filterButtons = [...document.querySelectorAll('[data-filter]')];
  const noResults = document.querySelector('#no-results');
  const searchStatus = document.querySelector('#search-status');
  let currentCategory = 'all';
  let currentQuery = '';

  // Russian word forms differ by ending («орхидеи» vs «орхидей»):
  // match whole words first, then fall back to a trimmed stem.
  const matchesToken = (haystack, token) => {
    if (!token) return true;
    if (haystack.includes(token)) return true;
    if (token.length >= 5) return haystack.includes(token.slice(0, token.length - 2));
    return false;
  };

  const filterCards = () => {
    let visible = 0;
    const tokens = currentQuery.split(/\s+/).filter(Boolean);
    cards.forEach((card) => {
      const matchesCategory = currentCategory === 'all' || card.dataset.category === currentCategory;
      const haystack = card.dataset.search || '';
      const matchesQuery = tokens.every((token) => matchesToken(haystack, token));
      const show = matchesCategory && matchesQuery;
      card.hidden = !show;
      if (show) visible += 1;
    });
    if (noResults) noResults.hidden = visible !== 0;
    if (searchStatus) searchStatus.textContent = `Показано статей: ${visible}`;
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
