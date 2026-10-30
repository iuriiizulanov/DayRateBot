from datetime import date

import pytest

from dayratebot import handlers
from dayratebot.database import Database
from dayratebot.handlers import (
    _MENU_BUTTON_LABELS,
    _commands_keyboard,
    _comment_keyboard,
    _delete_note_keyboard,
    _day_keyboard,
)
from dayratebot.i18n import translate


def _button_labels(keyboard) -> list[str]:
    return [button.text for row in keyboard.keyboard for button in row]


def test_main_keyboard_has_today_yesterday_and_commands() -> None:
    keyboard = _day_keyboard("en")
    assert _button_labels(keyboard) == [
        "🗓 Yesterday",
        "📅 Today",
        "📝 Notes",
        "☰ More",
    ]
    assert [
        [button.text for button in row]
        for row in keyboard.keyboard
    ] == [
        ["🗓 Yesterday", "📅 Today"],
        ["📝 Notes", "☰ More"],
    ]


def test_main_keyboard_buttons_are_localized() -> None:
    keyboard = _day_keyboard("ru")
    assert _button_labels(keyboard) == [
        translate("ru", "day_yesterday"),
        translate("ru", "day_today"),
        translate("ru", "note_today"),
        translate("ru", "more_commands"),
    ]


def test_main_keyboard_shows_scores_with_traffic_light_colors() -> None:
    keyboard = _day_keyboard("ru", today_score=8, yesterday_score=4)
    assert _button_labels(keyboard) == [
        "🗓 Вчера - 🔴 4",
        "📅 Сегодня - 🟢 8",
        translate("ru", "note_today"),
        translate("ru", "more_commands"),
    ]


@pytest.mark.asyncio
async def test_user_keyboard_loads_today_and_yesterday_scores(
    tmp_path, monkeypatch
) -> None:
    database = Database(tmp_path / "ratings.sqlite3")
    await database.open()
    try:
        user_id = 123
        await database.ensure_user(user_id)
        metric = (await database.list_metrics())[0]
        today = date(2026, 10, 30)
        await database.save_rating(user_id, metric["id"], today, 8)
        await database.save_rating(user_id, metric["id"], today.replace(day=29), 5)

        async def local_today(_database, _user_id):
            return today

        monkeypatch.setattr(handlers, "_local_today", local_today)
        keyboard = await handlers._day_keyboard_for_user(database, user_id, "en")

        assert _button_labels(keyboard) == [
            "🗓 Yesterday - 🟡 5",
            "📅 Today - 🟢 8",
            translate("en", "note_today"),
            translate("en", "more_commands"),
        ]
    finally:
        await database.close()


def test_commands_keyboard_contains_secondary_actions_and_back() -> None:
    keyboard = _commands_keyboard("en")
    assert [
        [button.text for button in row]
        for row in keyboard.keyboard
    ] == [
        ["📚 History", "📈 Chart"],
        ["🗑 Delete note"],
        ["🌍 Timezone", "ℹ️ Help"],
        ["↩️ Back"],
    ]


def test_delete_note_keyboard_lists_dates_for_selection() -> None:
    keyboard = _delete_note_keyboard(
        [
            {"note_for": "2026-10-30"},
            {"note_for": "2026-10-29"},
            {"note_for": "2026-10-28"},
        ],
        "ru",
    )

    assert [
        [(button.text, button.callback_data) for button in row]
        for row in keyboard.inline_keyboard
    ] == [
        [
            ("🗑 30.10.2026", "delete_note:2026-10-30"),
            ("🗑 29.10.2026", "delete_note:2026-10-29"),
        ],
        [("🗑 28.10.2026", "delete_note:2026-10-28")],
    ]


def test_comment_action_button_has_icon() -> None:
    keyboard = _comment_keyboard(42, "ru")
    assert keyboard.inline_keyboard[0][0].text == "💬 Добавить комментарий"


def test_cancel_comment_button_is_not_in_menu() -> None:
    assert not any("Cancel comment" in label for label in _MENU_BUTTON_LABELS)
    assert not any("Отменить комментарий" in label for label in _MENU_BUTTON_LABELS)


def test_renamed_menu_buttons_and_previous_labels_are_routed() -> None:
    assert {
        "📝 Заметки",
        "📝 Заметка сегодня",
        "📝 Notes",
        "📝 Note today",
        "☰ Еще",
        "☰ Другие команды",
        "☰ More",
        "☰ Other commands",
    } <= _MENU_BUTTON_LABELS
