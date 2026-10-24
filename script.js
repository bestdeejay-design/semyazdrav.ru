(() => {
  const menuButton = document.querySelector('.menu-toggle');
  const navigation = document.querySelector('.main-nav');

  if (menuButton && navigation) {
    const setOpen = (open, { focusButton = false } = {}) => {
      menuButton.setAttribute('aria-expanded', String(open));
      menuButton.setAttribute('aria-label', open ? 'Закрыть меню' : 'Открыть меню');
      navigation.classList.toggle('is-open', open);
      if (focusButton) menuButton.focus();
    };
    const isOpen = () => menuButton.getAttribute('aria-expanded') === 'true';
    menuButton.addEventListener('click', () => setOpen(!isOpen()));
    navigation.querySelectorAll('a').forEach((link) =>
      link.addEventListener('click', () => setOpen(false)),
    );
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && isOpen()) setOpen(false, { focusButton: true });
    });
    document.addEventListener('click', (event) => {
      if (!isOpen()) return;
      if (navigation.contains(event.target) || menuButton.contains(event.target)) return;
      setOpen(false);
    });
    const desktopQuery = window.matchMedia?.('(min-width: 721px)');
    desktopQuery?.addEventListener?.('change', (event) => {
      if (event.matches) setOpen(false);
    });
  }

  const volumeInput = document.querySelector('#water-volume');
  const volumeRange = document.querySelector('#water-range');
  const doseResult = document.querySelector('#dose-result');
  const rangeOver = document.querySelector('#range-over');
  const presetButtons = [...document.querySelectorAll('[data-volume]')];
  const formatNumber = (number) =>
    new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 1 }).format(number);
  const RANGE_MAX = 20;

  function render(value) {
    const rangeValue = Math.min(RANGE_MAX, Math.max(Number(volumeRange.min), value));
    volumeRange.value = String(rangeValue);
    const progress =
      ((rangeValue - Number(volumeRange.min)) / (RANGE_MAX - Number(volumeRange.min))) * 100;
    volumeRange.style.background = `linear-gradient(to right, #80966d 0%, #80966d ${progress}%, #cad1bf ${progress}%, #cad1bf 100%)`;
    doseResult.textContent = `${formatNumber(value)} мл`;
    const over = value > RANGE_MAX;
    if (rangeOver) {
      rangeOver.hidden = !over;
      rangeOver.textContent = over
        ? `Сейчас введено ${formatNumber(value)} л — ползунок на максимуме, доза считается по полю.`
        : '';
    }
    volumeRange.setAttribute(
      'aria-valuetext',
      over ? `${formatNumber(value)} литров, ползунок на максимуме 20 литров` : `${formatNumber(value)} литров`,
    );
    presetButtons.forEach((button) => {
      const active = Number(button.dataset.volume) === value;
      button.classList.toggle('is-active', active);
      button.setAttribute('aria-pressed', String(active));
    });
  }

  function updateVolume(rawValue, { fromRange = false, normalizeInput = false } = {}) {
    if (!volumeInput || !volumeRange || !doseResult) return;
    const parsed = Number.parseFloat(String(rawValue).replace(',', '.'));
    if (!Number.isFinite(parsed)) {
      if (normalizeInput) {
        volumeInput.value = '0.1';
        render(0.1);
      } else {
        doseResult.textContent = '— мл';
      }
      return;
    }
    const clamped = Math.min(250, Math.max(0.1, parsed));
    const rounded = Math.round(clamped * 10) / 10;
    if (fromRange || normalizeInput) volumeInput.value = String(rounded);
    render(rounded);
  }

  volumeInput?.addEventListener('input', (event) => updateVolume(event.currentTarget.value));
  volumeInput?.addEventListener('change', (event) =>
    updateVolume(event.currentTarget.value, { normalizeInput: true }),
  );
  volumeRange?.addEventListener('input', (event) =>
    updateVolume(event.currentTarget.value, { fromRange: true }),
  );
  presetButtons.forEach((button) =>
    button.addEventListener('click', () =>
      updateVolume(button.dataset.volume, { fromRange: true, normalizeInput: true }),
    ),
  );
  updateVolume(volumeInput?.value || 5, { fromRange: true, normalizeInput: true });
})();
