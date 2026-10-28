from dayratebot.handlers import (
    _MENU_BUTTON_LABELS,
    _commands_keyboard,
    _comment_keyboard,
    _day_keyboard,
)
from dayratebot.i18n import translate


def _button_labels(keyboard) -> list[str]:
    return [button.text for row in keyboard.keyboard for button in row]


def test_main_keyboard_has_today_yesterday_and_commands() -> None:
    keyboard = _day_keyboard("en")
    assert _button_labels(keyboard) == [
        "📅 Today",
        "🗓 Yesterday",
        "☰ Other commands",
    ]


def test_main_keyboard_buttons_are_localized() -> None:
    keyboard = _day_keyboard("ru")
    assert _button_labels(keyboard) == [
        translate("ru", "day_today"),
        translate("ru", "day_yesterday"),
        translate("ru", "more_commands"),
    ]


def test_commands_keyboard_contains_secondary_actions_and_back() -> None:
    keyboard = _commands_keyboard("en")
    assert [
        [button.text for button in row]
        for row in keyboard.keyboard
    ] == [
        ["📚 History"],
        ["📈 Chart"],
        ["🌍 Timezone", "ℹ️ Help"],
        ["↩️ Back"],
    ]


def test_comment_action_button_has_icon() -> None:
    keyboard = _comment_keyboard(42, "ru")
    assert keyboard.inline_keyboard[0][0].text == "💬 Добавить комментарий"


def test_cancel_comment_button_is_not_in_menu() -> None:
    assert not any("Cancel comment" in label for label in _MENU_BUTTON_LABELS)
    assert not any("Отменить комментарий" in label for label in _MENU_BUTTON_LABELS)
