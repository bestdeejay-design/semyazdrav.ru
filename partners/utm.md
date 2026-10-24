# UTM-правила кросс-промо

Единый формат на обе стороны, кампания `crosspromo_2026q4`:

| Направление | Ссылка |
|---|---|
| semyazdrav → fermaruna | `https://fermaruna.ru/?utm_source=semyazdrav&utm_medium=partner&utm_campaign=crosspromo_2026q4` |
| fermaruna → semyazdrav | `https://semyazdrav.ru/?utm_source=fermaruna&utm_medium=partner&utm_campaign=crosspromo_2026q4` |

Правила:

1. Метки — только в ссылках между двумя сайтами партнёров. К продуктовым ссылкам на Wildberries UTM **не добавляются**: чекер `scripts/check_site.py` требует, чтобы все ссылки на wildberries.ru были строго равны карточке товара.
2. Если с fermaruna нужно вести на товар, ссылка идёт на `https://semyazdrav.ru/` с UTM выше, а дальше посетитель уходит обычным CTA сайта.
3. Для отдельных размещений (баннер в статье, пост) допускается `utm_content` латиницей в нижнем регистре, например `utm_content=article_kartofel`. Значения `utm_source` и `utm_campaign` не менять.
4. Все партнёрские ссылки: `target="_blank" rel="noopener noreferrer"`.
