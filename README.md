# DayRateBot

*English | [Русский](#русский)*

A Telegram bot for rating today or yesterday on a 1–10 scale, adding comments,
and reviewing personal statistics.

## Features

- Rate or re-rate a day; a new rating replaces the previous one.
- Add an optional comment to each rating.
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
- `/help` — read the rating-scale guide.
- `/timezone` — view or set your timezone.
- `/cancel` — cancel comment entry.

The main keyboard has **Today**, **Yesterday**, and **Other commands** buttons.
The additional menu contains History, Chart, Timezone, Help, and Back. Use
`/cancel` to cancel comment entry.

## Architecture

- `handlers.py` — Telegram commands and conversation flows.
- `database.py` — persistence for users, metrics, and ratings.
- `analytics.py` — period calculations and comparisons.
- `charts.py` — rating chart generation.
- `i18n.py` — interface translations and language selection. Add another
  language by adding its translation catalog.

Ratings are stored separately from the `metrics` catalog. A new metric can be
added as a database record with its own score range. A rating is unique per
user, metric, and date, so re-rating updates the existing record and preserves
its comment.

The SQLite database is created automatically on first start. It is stored in
`data/` by default; change the location with `DATABASE_PATH`.

---

## Русский

Telegram-бот для оценки сегодняшнего или вчерашнего дня по шкале от 1 до 10,
комментариев к оценкам и просмотра личной статистики.

### Возможности

- Оценка и переоценка дня: новая оценка заменяет предыдущую.
- Необязательный комментарий к каждой оценке.
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
- `/help` — открыть подсказку по шкале оценок.
- `/timezone` — посмотреть или изменить часовой пояс.
- `/cancel` — отменить ввод комментария.

В основной клавиатуре есть кнопки **«Сегодня»**, **«Вчера»** и
**«Другие команды»**. В дополнительном меню доступны история, график, часовой
пояс, помощь, отмена ввода комментария и возврат назад.

### Архитектура

- `handlers.py` — команды Telegram и сценарии взаимодействия.
- `database.py` — хранение пользователей, метрик и оценок.
- `analytics.py` — расчёт периодов и сравнений.
- `charts.py` — построение графиков оценок.
- `i18n.py` — переводы интерфейса и выбор языка. Чтобы добавить язык, достаточно
  добавить каталог переводов.

Оценки хранятся отдельно от справочника `metrics`. Новую метрику можно добавить
записью в таблицу и указать для неё собственный диапазон баллов. Для каждой
пары «пользователь, метрика, дата» хранится одна оценка: повторная оценка
обновляет существующую запись и сохраняет комментарий.

База SQLite создаётся автоматически при первом запуске. По умолчанию она
располагается в каталоге `data/`; путь можно изменить переменной
`DATABASE_PATH`.
