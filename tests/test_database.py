from datetime import date

import pytest

from dayratebot.database import Database


@pytest.mark.asyncio
async def test_resaving_rating_updates_score_and_preserves_comment(tmp_path) -> None:
    database = Database(tmp_path / "ratings.sqlite3")
    await database.open()
    try:
        user_id = 123
        await database.ensure_user(user_id)
        metric = (await database.list_metrics())[0]
        rated_for = date(2026, 10, 28)

        await database.save_rating(user_id, metric["id"], rated_for, 6, "Хороший день")
        previous = await database.get_rating(user_id, metric["id"], rated_for)
        await database.save_rating(user_id, metric["id"], rated_for, 8)
        updated = await database.get_rating(user_id, metric["id"], rated_for)

        assert updated["id"] == previous["id"]
        assert updated["score"] == 8
        assert updated["comment"] == "Хороший день"
    finally:
        await database.close()


@pytest.mark.asyncio
async def test_users_have_independent_timezones_and_ratings(tmp_path) -> None:
    database = Database(tmp_path / "ratings.sqlite3")
    await database.open()
    try:
        metric = (await database.list_metrics())[0]
        rated_for = date(2026, 10, 28)
        await database.set_timezone(123, "Europe/Moscow")
        await database.set_timezone(456, "America/New_York")
        await database.save_rating(123, metric["id"], rated_for, 9)

        assert await database.get_timezone(123) == "Europe/Moscow"
        assert await database.get_timezone(456) == "America/New_York"
        assert await database.get_rating(456, metric["id"], rated_for) is None
    finally:
        await database.close()
