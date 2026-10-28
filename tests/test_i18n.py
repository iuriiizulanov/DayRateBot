from dayratebot.i18n import (
    _TRANSLATIONS,
    format_rating_count,
    get_locale,
    metric_name,
    translate,
)


def test_russian_telegram_language_uses_russian_catalog() -> None:
    assert get_locale("ru") == "ru"
    assert get_locale("ru-RU") == "ru"
    assert get_locale("ru_RU") == "ru"


def test_unsupported_and_missing_languages_use_english() -> None:
    assert get_locale("en") == "en"
    assert get_locale("fr") == "en"
    assert get_locale(None) == "en"
    assert translate(get_locale("fr"), "day_today") == "Today"


def test_default_metric_name_is_localized() -> None:
    metric = {"code": "day_rating", "name": "Оценка дня"}
    assert metric_name(metric, "en") == "Daily rating"
    assert metric_name(metric, "ru") == "Оценка дня"


def test_custom_metric_name_is_preserved() -> None:
    metric = {"code": "custom", "name": "Energy"}
    assert metric_name(metric, "ru") == "Energy"


def test_rating_counts_use_locale_plural_rules() -> None:
    assert format_rating_count("en", 1) == "1 rating"
    assert format_rating_count("en", 2) == "2 ratings"
    assert format_rating_count("ru", 1) == "1 оценка"
    assert format_rating_count("ru", 3) == "3 оценки"
    assert format_rating_count("ru", 5) == "5 оценок"
    assert format_rating_count("ru", 11) == "11 оценок"
    assert format_rating_count("ru", 21) == "21 оценка"


def test_language_catalogs_contain_the_same_translation_keys() -> None:
    assert set(_TRANSLATIONS["en"]) == set(_TRANSLATIONS["ru"])


def test_help_explains_rating_scale_in_both_languages() -> None:
    english_help = translate("en", "help_scale")
    russian_help = translate("ru", "help_scale")

    for score_range in ("1–2", "3–4", "5–6", "7–8", "9–10"):
        assert score_range in english_help
        assert score_range in russian_help

    assert "ответов нет" in russian_help
    assert "no right or wrong answers" in english_help


def test_welcome_lists_help_command() -> None:
    assert "/help" in translate("en", "welcome")
    assert "/help" in translate("ru", "welcome")
