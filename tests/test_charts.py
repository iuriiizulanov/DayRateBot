from datetime import date

from dayratebot.charts import make_rating_chart


def test_chart_is_a_png_image() -> None:
    image = make_rating_chart([(date(2026, 10, 28), 8)])
    assert image.read(8) == b"\x89PNG\r\n\x1a\n"
