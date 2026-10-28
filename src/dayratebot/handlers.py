from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)

from dayratebot.analytics import compare_periods, month_periods, week_periods
from dayratebot.charts import make_rating_chart
from dayratebot.database import Database
from dayratebot.i18n import format_rating_count, get_locale, metric_name, translate

router = Router()
COMMENT_LIMIT = 1000


class CommentForm(StatesGroup):
    waiting_for_comment = State()


def _day_keyboard(locale: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=translate(locale, "day_today")),
                KeyboardButton(text=translate(locale, "day_yesterday")),
            ],
            [KeyboardButton(text=translate(locale, "more_commands"))],
        ],
        resize_keyboard=True,
    )


def _commands_keyboard(locale: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=translate(locale, "menu_history"))],
            [KeyboardButton(text=translate(locale, "menu_chart"))],
            [
                KeyboardButton(text=translate(locale, "menu_timezone")),
                KeyboardButton(text=translate(locale, "menu_help")),
            ],
            [KeyboardButton(text=translate(locale, "menu_back"))],
        ],
        resize_keyboard=True,
    )


_MENU_BUTTON_KEYS = (
    "day_today",
    "day_yesterday",
    "more_commands",
    "menu_history",
    "menu_chart",
    "menu_timezone",
    "menu_help",
    "menu_back",
)
_MENU_BUTTON_LABELS = {
    translate(locale, key) for locale in ("en", "ru") for key in _MENU_BUTTON_KEYS
}


def _metric_keyboard(metrics: list, rated_for: date, locale: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"⭐ {metric_name(metric, locale)}",
                    callback_data=f"metric:{metric['id']}:{rated_for.isoformat()}",
                )
            ]
            for metric in metrics
        ]
    )


def _metric_action_keyboard(
    metrics: list, action: str, locale: str
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"⭐ {metric_name(metric, locale)}",
                    callback_data=f"{action}:{metric['id']}",
                )
            ]
            for metric in metrics
        ]
    )


def _score_keyboard(
    metric_id: int, rated_for: date, minimum: int, maximum: int
) -> InlineKeyboardMarkup:
    scores = [
        InlineKeyboardButton(
            text=str(score),
            callback_data=f"score:{metric_id}:{rated_for.isoformat()}:{score}",
        )
        for score in range(minimum, maximum + 1)
    ]
    rows = [scores[index : index + 5] for index in range(0, len(scores), 5)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _comment_keyboard(rating_id: int, locale: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=translate(locale, "add_comment"),
                    callback_data=f"comment:{rating_id}",
                )
            ]
        ]
    )


async def _local_today(database: Database, user_id: int) -> date:
    timezone = await database.get_timezone(user_id)
    return datetime.now(ZoneInfo(timezone)).date()


@router.message(CommandStart())
async def start(message: Message, database: Database) -> None:
    await database.ensure_user(message.from_user.id)
    locale = get_locale(message.from_user.language_code)
    await message.answer(
        translate(locale, "welcome"),
        reply_markup=_day_keyboard(locale),
    )


@router.message(Command("rate"))
async def rate(message: Message, database: Database) -> None:
    await database.ensure_user(message.from_user.id)
    locale = get_locale(message.from_user.language_code)
    await message.answer(
        translate(locale, "rate_prompt"),
        reply_markup=_day_keyboard(locale),
    )


async def _send_rating_for_date(
    message: Message,
    database: Database,
    user_id: int,
    rated_for: date,
    locale: str,
) -> None:
    metrics = await database.list_metrics()
    if not metrics:
        await message.answer(translate(locale, "no_metrics"))
        return
    if len(metrics) > 1:
        await message.answer(
            translate(locale, "choose_rating_for", date=f"{rated_for:%d.%m.%Y}"),
            reply_markup=_metric_keyboard(metrics, rated_for, locale),
        )
        return

    metric = metrics[0]
    previous = await database.get_rating(user_id, int(metric["id"]), rated_for)
    current = (
        translate(
            locale,
            "current_rating",
            score=previous["score"],
            maximum=metric["max_score"],
        )
        if previous is not None
        else ""
    )
    await message.answer(
        translate(
            locale,
            "metric_for_date",
            metric=metric_name(metric, locale),
            date=f"{rated_for:%d.%m.%Y}",
        )
        + current,
        reply_markup=_score_keyboard(
            int(metric["id"]),
            rated_for,
            int(metric["min_score"]),
            int(metric["max_score"]),
        ),
    )


@router.callback_query(F.data.startswith("day:"))
async def choose_day(callback: CallbackQuery, database: Database) -> None:
    await callback.answer()
    locale = get_locale(callback.from_user.language_code)
    offset = int(callback.data.split(":")[1])
    if offset not in (0, 1):
        await callback.message.answer(translate(locale, "invalid_day"))
        return
    user_id = callback.from_user.id
    rated_for = await _local_today(database, user_id) - timedelta(days=offset)
    if not isinstance(callback.message, Message):
        return
    await _send_rating_for_date(
        callback.message, database, user_id, rated_for, locale
    )


@router.callback_query(F.data.startswith("metric:"))
async def choose_metric(callback: CallbackQuery, database: Database) -> None:
    await callback.answer()
    locale = get_locale(callback.from_user.language_code)
    _, metric_id_text, date_text = callback.data.split(":")
    metric_id = int(metric_id_text)
    rated_for = date.fromisoformat(date_text)
    metric = next(
        (item for item in await database.list_metrics() if item["id"] == metric_id),
        None,
    )
    if metric is None:
        await callback.message.answer(translate(locale, "metric_unavailable"))
        return

    previous = await database.get_rating(callback.from_user.id, metric_id, rated_for)
    current = (
        translate(
            locale,
            "current_rating",
            score=previous["score"],
            maximum=metric["max_score"],
        )
        if previous is not None
        else ""
    )
    await callback.message.answer(
        translate(
            locale,
            "metric_for_date",
            metric=metric_name(metric, locale),
            date=f"{rated_for:%d.%m.%Y}",
        )
        + current,
        reply_markup=_score_keyboard(
            metric_id, rated_for, int(metric["min_score"]), int(metric["max_score"])
        ),
    )


@router.callback_query(F.data.startswith("score:"))
async def save_score(callback: CallbackQuery, database: Database) -> None:
    await callback.answer()
    locale = get_locale(callback.from_user.language_code)
    _, metric_id_text, date_text, score_text = callback.data.split(":")
    metric_id = int(metric_id_text)
    rated_for = date.fromisoformat(date_text)
    score = int(score_text)
    metrics = {item["id"]: item for item in await database.list_metrics()}
    metric = metrics.get(metric_id)
    if metric is None or not int(metric["min_score"]) <= score <= int(metric["max_score"]):
        await callback.message.answer(translate(locale, "invalid_score"))
        return

    old_rating = await database.get_rating(callback.from_user.id, metric_id, rated_for)
    await database.save_rating(
        callback.from_user.id,
        metric_id,
        rated_for,
        score,
    )
    saved_rating = await database.get_rating(callback.from_user.id, metric_id, rated_for)
    status = (
        translate(locale, "rating_updated")
        if old_rating is not None
        else translate(locale, "rating_saved")
    )
    await callback.message.answer(
        translate(
            locale,
            "saved_rating",
            status=status,
            metric=metric_name(metric, locale),
            date=f"{rated_for:%d.%m.%Y}",
            score=score,
            maximum=metric["max_score"],
        ),
        reply_markup=_comment_keyboard(int(saved_rating["id"]), locale),
    )


@router.callback_query(F.data.startswith("comment:"))
async def request_comment(
    callback: CallbackQuery, database: Database, state: FSMContext
) -> None:
    await callback.answer()
    locale = get_locale(callback.from_user.language_code)
    rating_id = int(callback.data.split(":")[1])
    if await database.get_rating_owner(rating_id, callback.from_user.id) is None:
        await callback.message.answer(translate(locale, "rating_not_found"))
        return
    await state.update_data(rating_id=rating_id)
    await state.set_state(CommentForm.waiting_for_comment)
    await callback.message.answer(
        translate(locale, "comment_prompt", limit=COMMENT_LIMIT)
    )


@router.message(Command("cancel"))
async def cancel_comment(message: Message, state: FSMContext) -> None:
    await state.clear()
    locale = get_locale(message.from_user.language_code)
    await message.answer(translate(locale, "comment_cancelled"))


@router.message(
    CommentForm.waiting_for_comment,
    F.text & ~F.text.startswith("/") & ~F.text.in_(_MENU_BUTTON_LABELS),
)
async def save_comment(message: Message, state: FSMContext, database: Database) -> None:
    locale = get_locale(message.from_user.language_code)
    comment = (message.text or "").strip()
    if not comment:
        await message.answer(translate(locale, "comment_empty"))
        return
    if len(comment) > COMMENT_LIMIT:
        await message.answer(
            translate(
                locale,
                "comment_too_long",
                length=len(comment),
                limit=COMMENT_LIMIT,
            )
        )
        return
    data = await state.get_data()
    updated = await database.update_comment(
        int(data["rating_id"]), message.from_user.id, comment
    )
    await state.clear()
    await message.answer(
        translate(locale, "comment_saved" if updated else "rating_not_found")
    )


@router.message(Command("timezone"))
async def set_timezone(message: Message, database: Database) -> None:
    locale = get_locale(message.from_user.language_code)
    timezone = (message.text or "").partition(" ")[2].strip()
    if not timezone:
        await _show_timezone_prompt(message, database, locale)
        return
    try:
        ZoneInfo(timezone)
    except (ZoneInfoNotFoundError, ValueError):
        await message.answer(translate(locale, "timezone_invalid"))
        return
    await database.set_timezone(message.from_user.id, timezone)
    await message.answer(translate(locale, "timezone_set", timezone=timezone))


async def _show_timezone_prompt(
    message: Message, database: Database, locale: str
) -> None:
    current_timezone = await database.get_timezone(message.from_user.id)
    await message.answer(
        translate(locale, "timezone_current", timezone=current_timezone)
        + "\n"
        + translate(locale, "timezone_prompt"),
        reply_markup=_commands_keyboard(locale),
    )


def _comparison_line(title: str, comparison, locale: str) -> str:
    current = comparison.current
    previous = comparison.previous
    current_average = (
        f"{current.average:.2f}"
        if current.average is not None
        else translate(locale, "no_ratings")
    )
    previous_average = (
        f"{previous.average:.2f}"
        if previous.average is not None
        else translate(locale, "no_ratings")
    )
    delta = (
        f"{comparison.average_change:+.2f}"
        if comparison.average_change is not None
        else translate(locale, "not_enough_data")
    )
    return (
        f"{title}\n"
        f"  {translate(locale, 'current')}: {current_average} "
        f"({format_rating_count(locale, current.count)})\n"
        f"  {translate(locale, 'previous')}: {previous_average} "
        f"({format_rating_count(locale, previous.count)})\n"
        f"  {translate(locale, 'average_change')}: {delta}"
    )


async def _history_text(
    database: Database, user_id: int, metric, locale: str
) -> str:
    today = await _local_today(database, user_id)
    earliest = min(week_periods(today)[1][0], month_periods(today)[1][0])
    ratings = await database.get_ratings(user_id, int(metric["id"]), earliest, today)
    weekly = compare_periods(ratings, *week_periods(today))
    monthly = compare_periods(ratings, *month_periods(today))
    text = (
        f"{translate(locale, 'history_period_note')}\n\n"
        f"{_comparison_line(translate(locale, 'this_week_vs_last'), weekly, locale)}\n\n"
        f"{_comparison_line(translate(locale, 'this_month_vs_last'), monthly, locale)}"
    )
    recent = await database.get_recent_ratings(user_id, int(metric["id"]))
    if recent:
        entries = [
            f"  {date.fromisoformat(row['rated_for']):%d.%m.%Y}: "
            f"{row['score']}/{metric['max_score']}"
            + (f" — {row['comment']}" if row["comment"] else "")
            for row in recent
        ]
        text += f"\n\n{translate(locale, 'recent_ratings')}\n" + "\n".join(entries)
    return f"{metric_name(metric, locale)}\n\n{text}"


@router.message(Command("history"))
async def history(message: Message, database: Database) -> None:
    locale = get_locale(message.from_user.language_code)
    metrics = await database.list_metrics()
    if not metrics:
        await message.answer(translate(locale, "no_metrics"))
    elif len(metrics) > 1:
        await message.answer(
            translate(locale, "choose_history_metric"),
            reply_markup=_metric_action_keyboard(metrics, "history", locale),
        )
    else:
        await message.answer(
            await _history_text(database, message.from_user.id, metrics[0], locale)
        )


@router.callback_query(F.data.startswith("history:"))
async def history_for_metric(callback: CallbackQuery, database: Database) -> None:
    await callback.answer()
    locale = get_locale(callback.from_user.language_code)
    metric_id = int(callback.data.split(":")[1])
    metric = next(
        (item for item in await database.list_metrics() if item["id"] == metric_id),
        None,
    )
    if metric is None:
        await callback.message.answer(translate(locale, "metric_unavailable"))
        return
    await callback.message.answer(
        await _history_text(database, callback.from_user.id, metric, locale)
    )


async def _send_chart(
    message: Message, database: Database, user_id: int, metric, locale: str
) -> None:
    today = await _local_today(database, user_id)
    start = today - timedelta(days=29)
    ratings = await database.get_ratings(user_id, int(metric["id"]), start, today)
    chart = make_rating_chart(
        ratings,
        title=metric_name(metric, locale),
        minimum=int(metric["min_score"]),
        maximum=int(metric["max_score"]),
        period_label=translate(locale, "chart_last_30_days"),
        score_label=translate(locale, "chart_score_axis"),
        empty_label=translate(locale, "chart_no_ratings"),
    )
    await message.answer_photo(
        BufferedInputFile(chart.getvalue(), filename="day-ratings.png")
    )


@router.message(Command("chart"))
async def chart(message: Message, database: Database) -> None:
    locale = get_locale(message.from_user.language_code)
    metrics = await database.list_metrics()
    if not metrics:
        await message.answer(translate(locale, "no_metrics"))
    elif len(metrics) > 1:
        await message.answer(
            translate(locale, "choose_chart_metric"),
            reply_markup=_metric_action_keyboard(metrics, "chart", locale),
        )
    else:
        await _send_chart(
            message, database, message.from_user.id, metrics[0], locale
        )


@router.message(Command("help"))
async def show_help(message: Message) -> None:
    locale = get_locale(message.from_user.language_code)
    await message.answer(
        translate(locale, "help_scale"),
        reply_markup=_commands_keyboard(locale),
    )


@router.callback_query(F.data.startswith("chart:"))
async def chart_for_metric(callback: CallbackQuery, database: Database) -> None:
    await callback.answer()
    locale = get_locale(callback.from_user.language_code)
    metric_id = int(callback.data.split(":")[1])
    metric = next(
        (item for item in await database.list_metrics() if item["id"] == metric_id),
        None,
    )
    if metric is None:
        await callback.message.answer(translate(locale, "metric_unavailable"))
        return
    await _send_chart(
        callback.message, database, callback.from_user.id, metric, locale
    )


@router.message(F.text.in_(_MENU_BUTTON_LABELS))
async def handle_menu_button(
    message: Message, database: Database
) -> None:
    locale = get_locale(message.from_user.language_code)
    text = message.text

    if text == translate(locale, "day_today") or text == translate(
        locale, "day_yesterday"
    ):
        await database.ensure_user(message.from_user.id)
        offset = 0 if text == translate(locale, "day_today") else 1
        rated_for = await _local_today(database, message.from_user.id) - timedelta(
            days=offset
        )
        await _send_rating_for_date(
            message, database, message.from_user.id, rated_for, locale
        )
    elif text == translate(locale, "more_commands"):
        await message.answer(
            translate(locale, "menu_prompt"),
            reply_markup=_commands_keyboard(locale),
        )
    elif text == translate(locale, "menu_history"):
        await history(message, database)
    elif text == translate(locale, "menu_chart"):
        await chart(message, database)
    elif text == translate(locale, "menu_timezone"):
        await _show_timezone_prompt(message, database, locale)
    elif text == translate(locale, "menu_help"):
        await show_help(message)
    elif text == translate(locale, "menu_back"):
        await message.answer(
            translate(locale, "rate_prompt"),
            reply_markup=_day_keyboard(locale),
        )
