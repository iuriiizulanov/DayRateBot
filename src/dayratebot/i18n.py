from typing import Any


_TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "day_today": "📅 Today",
        "day_yesterday": "🗓 Yesterday",
        "note_today": "📝 Notes",
        "more_commands": "☰ More",
        "menu_prompt": "Choose a command:",
        "menu_history": "📚 History",
        "menu_chart": "📈 Chart",
        "menu_delete_note": "🗑 Delete note",
        "menu_timezone": "🌍 Timezone",
        "menu_help": "ℹ️ Help",
        "menu_back": "↩️ Back",
        "help_scale": (
            "How to rate your day (1–10):\n"
            "🔴 1–2 — very difficult day\n"
            "🔴 3–4 — a rather bad day\n"
            "🟡 5–6 — mixed or okay day\n"
            "🟢 7–8 — a good day\n"
            "🟢 9–10 — an excellent day\n\n"
            "Use the score that best reflects how you personally feel. "
            "There are no right or wrong answers."
        ),
        "add_comment": "💬 Add a comment",
        "welcome": (
            "Hi! This bot helps you:\n"
            "• rate today or yesterday from 1 to 10\n"
            "• add a comment to each rating\n"
            "• review weekly and monthly analytics\n"
            "• compare current periods with previous ones\n"
            "• view charts for your ratings\n\n"
            "Commands:\n"
            "/start — welcome message\n"
            "/rate — rate today or yesterday\n"
            "/history — weekly/monthly analytics\n"
            "/chart — chart of recent ratings\n"
            "/help — rating scale and help\n"
            "/timezone — set your timezone\n"
            "/cancel — cancel comment input\n\n"
            "Your timezone is UTC by default; change it with /timezone."
        ),
        "rate_prompt": "Which day would you like to rate?",
        "invalid_day": "You can only rate today or yesterday.",
        "no_metrics": "There are no rating types available right now.",
        "choose_rating_for": "Choose a rating for {date}:",
        "metric_unavailable": "This rating type is no longer available.",
        "metric_for_date": "{metric} for {date}.",
        "current_rating": (
            " Current rating: {score}/{maximum}. Choose a new value to update it."
        ),
        "invalid_score": "Invalid rating. Please choose a value again.",
        "rating_updated": "Rating updated.",
        "rating_saved": "Rating saved.",
        "saved_rating": "{status} {metric} for {date}: {score}/{maximum}.",
        "rating_not_found": "Rating not found.",
        "current_note": "Current note:\n{note}",
        "comment_prompt": (
            "Send the text to append to the current note (up to {limit} characters). "
            "Use /cancel to cancel."
        ),
        "comment_empty": "The comment cannot be empty. Send text or /cancel.",
        "comment_too_long": (
            "The comment is too long ({length} characters). Maximum: {limit}."
        ),
        "comment_saved": "Comment saved.",
        "comment_cancelled": "Adding a comment was cancelled.",
        "note_prompt": (
            "Send text to append to today's note (up to {limit} characters). "
            "Use /cancel to cancel."
        ),
        "note_saved": "Today's note saved.",
        "note_cancelled": "Adding a note was cancelled.",
        "choose_note_to_delete": "Choose the day whose note you want to delete:",
        "delete_note_date": "🗑 {date}",
        "note_deleted": "The note was deleted.",
        "note_not_found": "There is no note for that day.",
        "no_notes_to_delete": "There are no notes to delete.",
        "timezone_current": "Your current timezone is {timezone}.",
        "timezone_prompt": (
            "Enter an IANA timezone, for example: /timezone Europe/London"
        ),
        "timezone_invalid": (
            "Timezone not recognized. For example, use Europe/London."
        ),
        "timezone_set": "Timezone set to {timezone}.",
        "choose_history_metric": "Which rating would you like statistics for?",
        "choose_chart_metric": "Which rating would you like a chart for?",
        "history_period_note": (
            "Each period is compared with the same elapsed part of the previous "
            "period (from the start of the week/month through today)."
        ),
        "this_week_vs_last": "This week vs the same period last week",
        "this_month_vs_last": "This month vs the same period last month",
        "current": "Current",
        "previous": "Previous",
        "average_change": "Change in average",
        "no_ratings": "no ratings",
        "not_enough_data": "not enough data to compare",
        "rating_count_one": "{count} rating",
        "rating_count_few": "{count} ratings",
        "rating_count_many": "{count} ratings",
        "rating_count_other": "{count} ratings",
        "recent_ratings": "Recent ratings:",
        "chart_title": "Daily rating",
        "chart_last_30_days": "last 30 days",
        "chart_score_axis": "Score",
        "chart_no_ratings": "No ratings yet",
    },
    "ru": {
        "day_today": "📅 Сегодня",
        "day_yesterday": "🗓 Вчера",
        "note_today": "📝 Заметки",
        "more_commands": "☰ Еще",
        "menu_prompt": "Выберите команду:",
        "menu_history": "📚 История",
        "menu_chart": "📈 График",
        "menu_delete_note": "🗑 Удалить заметку",
        "menu_timezone": "🌍 Часовой пояс",
        "menu_help": "ℹ️ Помощь",
        "menu_back": "↩️ Назад",
        "help_scale": (
            "Как оценить свой день по шкале от 1 до 10:\n"
            "🔴 1–2 — очень тяжёлый день\n"
            "🔴 3–4 — скорее плохой день\n"
            "🟡 5–6 — неоднозначный или обычный день\n"
            "🟢 7–8 — хороший день\n"
            "🟢 9–10 — отличный день\n\n"
            "Выбирайте оценку по своим ощущениям. Правильных или неправильных "
            "ответов нет."
        ),
        "add_comment": "💬 Добавить комментарий",
        "welcome": (
            "Привет! Этот бот поможет тебе:\n"
            "• оценить сегодня или вчера по 10-балльной шкале\n"
            "• добавить комментарий к каждой оценке\n"
            "• посмотреть аналитику за неделю и месяц\n"
            "• сравнить текущий период с предыдущим\n"
            "• открыть график по оценкам\n\n"
            "Команды:\n"
            "/start — приветствие и список команд\n"
            "/rate — оценить сегодня или вчера\n"
            "/history — статистика за неделю и месяц\n"
            "/chart — график оценок\n"
            "/help — помощь и шкала оценок\n"
            "/timezone — задать часовой пояс\n"
            "/cancel — отменить ввод комментария\n\n"
            "Часовой пояс по умолчанию — UTC; изменить его можно командой /timezone."
        ),
        "rate_prompt": "Какой день оценим?",
        "invalid_day": "Можно выбрать только сегодня или вчера.",
        "no_metrics": "Сейчас нет доступных типов оценки.",
        "choose_rating_for": "Выберите оценку для {date}:",
        "metric_unavailable": "Этот тип оценки больше недоступен.",
        "metric_for_date": "{metric} за {date}.",
        "current_rating": (
            " Текущая оценка: {score}/{maximum}. Выберите новое значение, "
            "чтобы переоценить день."
        ),
        "invalid_score": "Некорректная оценка. Попробуйте выбрать значение ещё раз.",
        "rating_updated": "Оценка обновлена.",
        "rating_saved": "Оценка сохранена.",
        "saved_rating": "{status} {metric} за {date}: {score}/{maximum}.",
        "rating_not_found": "Оценка не найдена.",
        "current_note": "Текущая заметка:\n{note}",
        "comment_prompt": (
            "Отправьте текст, который нужно добавить к текущей заметке "
            "(до {limit} символов). Для отмены используйте /cancel."
        ),
        "comment_empty": "Комментарий не должен быть пустым. Отправьте текст или /cancel.",
        "comment_too_long": (
            "Слишком длинный комментарий ({length} символов). Максимум — {limit}."
        ),
        "comment_saved": "Комментарий сохранён.",
        "comment_cancelled": "Добавление комментария отменено.",
        "note_prompt": (
            "Отправьте текст, который нужно дописать к заметке за сегодня "
            "(до {limit} символов). Для отмены используйте /cancel."
        ),
        "note_saved": "Заметка за сегодня сохранена.",
        "note_cancelled": "Добавление заметки отменено.",
        "choose_note_to_delete": "Выберите день, заметку за который нужно удалить:",
        "delete_note_date": "🗑 {date}",
        "note_deleted": "Заметка удалена.",
        "note_not_found": "За этот день заметки нет.",
        "no_notes_to_delete": "Нет заметок для удаления.",
        "timezone_current": "Текущий часовой пояс: {timezone}.",
        "timezone_prompt": (
            "Укажите IANA-имя, например: /timezone Europe/Moscow"
        ),
        "timezone_invalid": (
            "Не удалось распознать часовой пояс. Пример корректного значения: "
            "Europe/Moscow."
        ),
        "timezone_set": "Часовой пояс установлен: {timezone}.",
        "choose_history_metric": "Для какой оценки показать статистику?",
        "choose_chart_metric": "Для какой оценки построить график?",
        "history_period_note": (
            "В статистике сравниваются равные части текущего периода и предыдущего "
            "(с начала недели/месяца по сегодняшний день)."
        ),
        "this_week_vs_last": "Эта неделя vs аналогичный период прошлой недели",
        "this_month_vs_last": "Этот месяц vs аналогичный период прошлого месяца",
        "current": "Сейчас",
        "previous": "До этого",
        "average_change": "Изменение среднего",
        "no_ratings": "нет оценок",
        "not_enough_data": "недостаточно данных для сравнения",
        "rating_count_one": "{count} оценка",
        "rating_count_few": "{count} оценки",
        "rating_count_many": "{count} оценок",
        "rating_count_other": "{count} оценки",
        "recent_ratings": "Последние оценки:",
        "chart_title": "Оценка дня",
        "chart_last_30_days": "последние 30 дней",
        "chart_score_axis": "Баллы",
        "chart_no_ratings": "Оценок пока нет",
    },
}


def get_locale(language_code: str | None) -> str:
    if language_code:
        primary_language = language_code.replace("_", "-").split("-", maxsplit=1)[0]
        if primary_language.lower() == "ru":
            return "ru"
    return "en"


def translate(locale: str, key: str, **values: Any) -> str:
    template = _TRANSLATIONS.get(locale, _TRANSLATIONS["en"]).get(
        key, _TRANSLATIONS["en"][key]
    )
    return template.format(**values)


def format_rating_count(locale: str, count: int) -> str:
    if locale == "ru":
        last_two_digits = count % 100
        last_digit = count % 10
        if 11 <= last_two_digits <= 14:
            plural_form = "many"
        elif last_digit == 1:
            plural_form = "one"
        elif 2 <= last_digit <= 4:
            plural_form = "few"
        else:
            plural_form = "many"
    else:
        plural_form = "one" if count == 1 else "other"

    return translate(locale, f"rating_count_{plural_form}", count=count)


def metric_name(metric: Any, locale: str) -> str:
    if metric["code"] == "day_rating":
        return translate(locale, "chart_title")
    return str(metric["name"])
