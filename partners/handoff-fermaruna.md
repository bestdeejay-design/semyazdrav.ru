# Handoff: блок «Семяздрав» на fermaruna.ru

Инструкция для агента/разработчика, размещающего ответный партнёрский блок на fermaruna.ru (репозиторий `bestdeejay-design/fermaruna`, генератор `scripts/build.py`, шаблоны в `templates/`).

## Куда вставлять

На главной странице fermaruna.ru — отдельной спокойной секцией перед футером (аналогично блоку на semyazdrav.ru). Не в шапку, не рядом с формой заказа и не между карточками продукции: блок не должен конкурировать с собственными CTA фермы.

## Ассеты (уже лежат в этом пакете)

- Локап: `partners/logos/semyazdrav-logo.svg` (+ PNG 680/1360 на всякий случай). Скопировать в `assets/img/` репозитория fermaruna.
- Официальная карточка товара Wildberries целиком (не иллюстрация): `public/images/product/wb-card-516.jpg` из репозитория semyazdrav — или готовый баннер `partners/banners/fermaruna-to-semyazdrav-1200x300.png` как есть.
- Текст — нейтральный вариант из `partners/copy.md`.
- Ссылка: `https://semyazdrav.ru/?utm_source=fermaruna&utm_medium=partner&utm_campaign=crosspromo_2026q4` (`target="_blank" rel="noopener noreferrer"`).

## Готовый сниппет (не зависит от CSS semyazdrav)

Вставить разметку в шаблон главной (`templates/home.html`) перед футером, стили — в конец `assets/css/main.css`. Классы с префиксом `sz-partner`, чтобы не пересекаться со стилями фермы; цвета и шрифты берутся из переменных fermaruna.

```html
<section class="sz-partner" aria-labelledby="sz-partner-title">
  <img class="sz-partner__logo" src="assets/img/semyazdrav-logo.svg" width="340" height="64" alt="" loading="lazy">
  <div class="sz-partner__text">
    <h2 id="sz-partner-title">Дружественный проект — «Семяздрав»</h2>
    <p>Органический концентрат для комнатных растений, цветов и рассады и спокойная база знаний по уходу за домашним садом.</p>
    <a class="sz-partner__link" href="https://semyazdrav.ru/?utm_source=fermaruna&utm_medium=partner&utm_campaign=crosspromo_2026q4" target="_blank" rel="noopener noreferrer">Перейти на semyazdrav.ru ↗</a>
  </div>
  <img class="sz-partner__photo" src="assets/img/semyazdrav-card.jpg" width="516" height="688" alt="Карточка товара «Семяздрав» на Wildberries: флакон концентрата 250 мл" loading="lazy">
</section>
```

```css
.sz-partner{display:flex;align-items:center;gap:28px;flex-wrap:wrap;background:#f6f1e3;border:1px solid #ddd4bd;border-radius:16px;padding:28px clamp(20px,4vw,40px);margin:0 auto;max-width:1240px}
.sz-partner__logo{width:min(230px,70vw);height:auto}
.sz-partner__text{flex:1 1 300px;min-width:min(300px,100%)}
.sz-partner__text h2{font:700 clamp(1.4rem,3vw,1.9rem)/1.15 "Alegreya",Georgia,serif;color:#13291c;margin:0 0 8px}
.sz-partner__text p{margin:0 0 12px;color:#35433a;line-height:1.6}
.sz-partner__link{font-weight:700;color:#163c2b;text-decoration:underline;text-underline-offset:3px;display:inline-flex;align-items:center;min-height:40px}
.sz-partner__photo{width:110px;height:auto;aspect-ratio:3/4;object-fit:cover;border-radius:8px}
.sz-partner a:focus-visible{outline:3px solid #d97c06;outline-offset:2px}
@media (max-width:640px){.sz-partner{gap:16px}.sz-partner__photo{width:84px}}
```

Файл карточки для `assets/img/semyazdrav-card.jpg` — это `wb-card-516.jpg` (переименовать при копировании), локап — `semyazdrav-logo.svg`.

Альтернатива без вёрстки: поставить готовый баннер `fermaruna-to-semyazdrav-1200x300.png` картинкой-ссылкой (`alt="Семяздрав — пусть дома растёт больше. На semyazdrav.ru"`, `width/height` обязательны). Вёрстка предпочтительнее: текст индексируется и читается скринридерами.

## Требования и проверка

- Текст — только из `copy.md`; нельзя писать, что ферма использует или рекомендует продукт (см. `PERMISSIONS.md`).
- После правки шаблонов fermaruna: `python3 scripts/build.py` в её репозитории и коммит сгенерированного результата (по правилам того проекта).
- Скриншоты 390 и 1440 px: блок не ломает сетку, нет горизонтального скролла, ссылка открывается в новой вкладке, UTM сохраняется в адресной строке semyazdrav.ru.
- `alt` у карточки товара — информативный (как в сниппете), у локапа — пустой (рядом есть заголовок с названием).
- Не добавлять UTM к ссылкам на Wildberries и не вести с fermaruna напрямую на карточку товара: только на главную semyazdrav.ru с партнёрскими метками.
