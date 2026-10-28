from datetime import date

from dayratebot.analytics import (
    compare_periods,
    month_periods,
    summarize,
    week_periods,
)


def test_current_week_compares_equal_elapsed_days() -> None:
    current, previous = week_periods(date(2026, 10, 28))
    assert current == (date(2026, 10, 26), date(2026, 10, 28))
    assert previous == (date(2026, 10, 19), date(2026, 10, 21))


def test_month_comparison_clamps_to_previous_month_length() -> None:
    current, previous = month_periods(date(2025, 3, 31))
    assert current == (date(2025, 3, 1), date(2025, 3, 31))
    assert previous == (date(2025, 2, 1), date(2025, 2, 28))


def test_comparison_ignores_ratings_outside_period() -> None:
    result = compare_periods(
        [
            (date(2026, 10, 20), 6),
            (date(2026, 10, 21), 8),
            (date(2026, 10, 27), 10),
            (date(2026, 10, 28), 8),
            (date(2026, 10, 29), 1),
        ],
        (date(2026, 10, 26), date(2026, 10, 28)),
        (date(2026, 10, 19), date(2026, 10, 21)),
    )
    assert result.current.count == 2
    assert result.current.average == 9
    assert result.previous.count == 2
    assert result.previous.average == 7
    assert result.average_change == 2


def test_empty_period_has_no_average() -> None:
    summary = summarize([], date(2026, 1, 1), date(2026, 1, 7))
    assert summary.count == 0
    assert summary.average is None
