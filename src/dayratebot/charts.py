from datetime import date
from io import BytesIO

import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.pyplot as plt


def make_rating_chart(
    ratings: list[tuple[date, int]],
    title: str = "Daily rating",
    minimum: int = 1,
    maximum: int = 10,
    period_label: str = "last 30 days",
    score_label: str = "Score",
    empty_label: str = "No ratings yet",
) -> BytesIO:
    image = BytesIO()
    figure, axis = plt.subplots(figsize=(9, 4.5))
    try:
        if ratings:
            days = [rated_for for rated_for, _ in ratings]
            scores = [score for _, score in ratings]
            axis.plot(
                mdates.date2num(days),
                scores,
                marker="o",
                linewidth=2,
                color="#3b82f6",
            )
        else:
            axis.text(
                0.5,
                0.5,
                empty_label,
                horizontalalignment="center",
                verticalalignment="center",
                transform=axis.transAxes,
            )

        axis.set_title(f"{title} — {period_label}")
        axis.set_ylabel(score_label)
        axis.set_ylim(minimum - 0.5, maximum + 0.5)
        axis.set_yticks(range(minimum, maximum + 1))
        axis.grid(axis="y", alpha=0.25)
        axis.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m"))
        figure.autofmt_xdate()
        figure.tight_layout()
        figure.savefig(image, format="png", dpi=150)
    finally:
        plt.close(figure)
    image.seek(0)
    return image
