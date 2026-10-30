# DayRateBot

*English | [Русский](#русский)*

A Telegram bot for rating today or yesterday on a 1–10 scale, adding daily notes
and rating comments, and reviewing personal statistics.

## Features

- Rate or re-rate a day; a new rating replaces the previous one.
- Append text to a day's note from the main keyboard or after rating; both
  update the same note for that date.
- Review current weekly and monthly statistics, compared with the same elapsed
  part of the previous week or month.
- View a chart of ratings for the last 30 days.
- Set a personal timezone. The default is UTC.
- The interface follows the Telegram language: Russian for `ru`; English for
  all other languages or when no language is set.
- Get guidance on the rating scale using the **Help** button or `/help`.

## Getting started

Python 3.10 or newer is required.

1. Create a bot with [@BotFather](https://t.me/BotFather) and get its token.
2. Copy `.env.example` to `.env` and set `BOT_TOKEN`.
3. Install the project: `python -m pip install -e .`
4. Start the bot: `python -m dayratebot.main` or `day-rate-bot`

Set a timezone with, for example, `/timezone Europe/London`.

## Commands and menu

- `/start` — show the welcome message and main menu.
- `/rate` — rate today or yesterday.
- `/history` — view weekly and monthly statistics.
- `/chart` — view the recent ratings chart.
- Use **Delete note** in the additional menu to choose a date and delete its note.
- `/help` — read the rating-scale guide.
- `/timezone` — view or set your timezone.
- `/cancel` — cancel comment or note entry.

The main keyboard has **Yesterday** and **Today** on the first row, and **Notes**
and **More** on the second row.
The additional menu puts History and Chart on the same row, followed by Delete
note, Timezone, Help, and Back. Use
`/cancel` to cancel note entry. New text is appended to the existing note for
that date. The note is dated when submitted, using the user's
local timezone. History shows ratings and their daily notes together.

## Architecture

- `handlers.py` — Telegram commands and conversation flows.
- `database.py` — persistence for users, metrics, ratings, and daily notes.
- `analytics.py` — period calculations and comparisons.
- `charts.py` — rating chart generation.
- `i18n.py` — interface translations and language selection. Add another
  language by adding its translation catalog.

Ratings are stored separately from the `metrics` catalog. A new metric can be
added as a database record with its own score range. A rating is unique per
user, metric, and date, so re-rating updates the existing record. A day's note
is stored once and shared by the main-menu note button and the rating comment.

The SQLite database is created automatically on first start. It is stored in
`data/` by default; change the location with `DATABASE_PATH`.

---

## Русский

Telegram-бот для оценки сегодняшнего или вчерашнего дня по шкале от 1 до 10,
добавления заметок и комментариев к оценкам, а также просмотра личной статистики.

### Возможности

- Оценка и переоценка дня: новая оценка заменяет предыдущую.
- Текст можно дописать к заметке за день с главной клавиатуры или после
  выставления оценки; в обоих случаях обновляется одна и та же заметка.
- Статистика за текущую неделю и месяц со сравнением с прошедшей частью
  предыдущей недели или месяца.
- График оценок за последние 30 дней.
- Персональный часовой пояс. По умолчанию используется UTC.
- Язык интерфейса определяется по настройке Telegram: русский для `ru`,
  английский — для остальных языков или если язык не задан.
- Подсказка о шкале оценок доступна по кнопке **«Помощь»** или команде `/help`.

### Запуск

Требуется Python 3.10 или новее.

1. Создайте бота через [@BotFather](https://t.me/BotFather) и получите токен.
2. Скопируйте `.env.example` в `.env` и задайте `BOT_TOKEN`.
3. Установите проект: `python -m pip install -e .`
4. Запустите: `python -m dayratebot.main` или `day-rate-bot`

Чтобы установить часовой пояс, отправьте, например, `/timezone Europe/Moscow`.

### Команды и меню

- `/start` — приветствие и главное меню.
- `/rate` — оценить сегодня или вчера.
- `/history` — посмотреть статистику за неделю и месяц.
- `/chart` — посмотреть график недавних оценок.
- Кнопка **«Удалить заметку»** в дополнительном меню позволяет выбрать дату
  и удалить заметку за этот день.
- `/help` — открыть подсказку по шкале оценок.
- `/timezone` — посмотреть или изменить часовой пояс.
- `/cancel` — отменить ввод комментария или заметки.

В основной клавиатуре кнопки **«Вчера»** и **«Сегодня»** находятся в первой
строке, а **«Заметки»** и **«Еще»** — во второй. В дополнительном меню история
и график находятся в одной строке; ниже доступны удаление заметки, часовой пояс,
помощь и возврат назад. Команда `/cancel` отменяет ввод заметки. Новый текст дописывается к
предыдущему за эту дату и получает дату отправки по часовому
поясу пользователя. Заметка из кнопки и комментарий к оценке за тот же день
добавляются в одну запись. В истории оценки и заметки показываются вместе.

### Архитектура

- `handlers.py` — команды Telegram и сценарии взаимодействия.
- `database.py` — хранение пользователей, метрик, оценок и заметок за день.
- `analytics.py` — расчёт периодов и сравнений.
- `charts.py` — построение графиков оценок.
- `i18n.py` — переводы интерфейса и выбор языка. Чтобы добавить язык, достаточно
  добавить каталог переводов.

Оценки хранятся отдельно от справочника `metrics`. Новую метрику можно добавить
записью в таблицу и указать для неё собственный диапазон баллов. Для каждой
пары «пользователь, метрика, дата» хранится одна оценка: повторная оценка
обновляет существующую запись. Заметка за день хранится в одном экземпляре и
общая для кнопки заметок и комментария к оценке; новый текст дописывается к
уже сохранённому.

База SQLite создаётся автоматически при первом запуске. По умолчанию она
располагается в каталоге `data/`; путь можно изменить переменной
`DATABASE_PATH`.
