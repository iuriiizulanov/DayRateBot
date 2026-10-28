import calendar
from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class PeriodSummary:
    start: date
    end: date
    count: int
    average: float | None


@dataclass(frozen=True)
class Comparison:
    current: PeriodSummary
    previous: PeriodSummary
    average_change: float | None


def week_periods(today: date) -> tuple[tuple[date, date], tuple[date, date]]:
    current_start = today - timedelta(days=today.weekday())
    elapsed_days = today.weekday()
    previous_start = current_start - timedelta(days=7)
    return (
        (current_start, today),
        (previous_start, previous_start + timedelta(days=elapsed_days)),
    )


def month_periods(today: date) -> tuple[tuple[date, date], tuple[date, date]]:
    current_start = today.replace(day=1)
    previous_end = current_start - timedelta(days=1)
    previous_start = previous_end.replace(day=1)
    comparable_day = min(today.day, calendar.monthrange(previous_end.year, previous_end.month)[1])
    return (
        (current_start, today),
        (previous_start, previous_start.replace(day=comparable_day)),
    )


def summarize(
    ratings: list[tuple[date, int]], start: date, end: date
) -> PeriodSummary:
    scores = [score for rated_for, score in ratings if start <= rated_for <= end]
    return PeriodSummary(
        start=start,
        end=end,
        count=len(scores),
        average=sum(scores) / len(scores) if scores else None,
    )


def compare_periods(
    ratings: list[tuple[date, int]],
    current_period: tuple[date, date],
    previous_period: tuple[date, date],
) -> Comparison:
    current = summarize(ratings, *current_period)
    previous = summarize(ratings, *previous_period)
    change = (
        current.average - previous.average
        if current.average is not None and previous.average is not None
        else None
    )
    return Comparison(current, previous, change)
