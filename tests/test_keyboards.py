from dayratebot.handlers import _commands_keyboard, _day_keyboard
from dayratebot.i18n import translate


def _button_labels(keyboard) -> list[str]:
    return [button.text for row in keyboard.keyboard for button in row]


def test_main_keyboard_has_today_yesterday_and_commands() -> None:
    keyboard = _day_keyboard("en")
    assert _button_labels(keyboard) == [
        "Today",
        "Yesterday",
        "Other commands",
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
    assert _button_labels(keyboard) == [
        "History",
        "Chart",
        "Timezone",
        "Help",
        "Cancel comment",
        "Back",
    ]
