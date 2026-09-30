(() => {
  const menuButton = document.querySelector('.menu-toggle');
  const navigation = document.querySelector('.main-nav');

  if (menuButton && navigation) {
    menuButton.addEventListener('click', () => {
      const isOpen = menuButton.getAttribute('aria-expanded') === 'true';
      menuButton.setAttribute('aria-expanded', String(!isOpen));
      menuButton.setAttribute('aria-label', isOpen ? 'Открыть меню' : 'Закрыть меню');
      navigation.classList.toggle('is-open', !isOpen);
    });
    navigation.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => {
      menuButton.setAttribute('aria-expanded', 'false');
      menuButton.setAttribute('aria-label', 'Открыть меню');
      navigation.classList.remove('is-open');
    }));
  }

  const volumeInput = document.querySelector('#water-volume');
  const volumeRange = document.querySelector('#water-range');
  const doseResult = document.querySelector('#dose-result');
  const presetButtons = [...document.querySelectorAll('[data-volume]')];
  const formatNumber = (number) => new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 1 }).format(number);

  function updateVolume(rawValue, fromRange = false) {
    if (!volumeInput || !volumeRange || !doseResult) return;
    const parsed = Number.parseFloat(rawValue);
    const safeValue = Number.isFinite(parsed) ? Math.min(250, Math.max(0.1, parsed)) : 0.1;
    const rounded = Math.round(safeValue * 10) / 10;
    if (fromRange) volumeInput.value = String(rounded);
    else if (Number.isFinite(parsed)) volumeInput.value = String(rounded);
    const rangeValue = Math.min(Number(volumeRange.max), Math.max(Number(volumeRange.min), rounded));
    volumeRange.value = String(rangeValue);
    const progress = ((rangeValue - Number(volumeRange.min)) / (Number(volumeRange.max) - Number(volumeRange.min))) * 100;
    volumeRange.style.background = `linear-gradient(to right, #80966d 0%, #80966d ${progress}%, #cad1bf ${progress}%, #cad1bf 100%)`;
    doseResult.textContent = `${formatNumber(rounded)} мл`;
    presetButtons.forEach((button) => button.classList.toggle('is-active', Number(button.dataset.volume) === rounded));
  }

  volumeInput?.addEventListener('input', (event) => updateVolume(event.currentTarget.value));
  volumeRange?.addEventListener('input', (event) => updateVolume(event.currentTarget.value, true));
  presetButtons.forEach((button) => button.addEventListener('click', () => updateVolume(button.dataset.volume, true)));
  updateVolume(volumeInput?.value || 5, true);
})();
