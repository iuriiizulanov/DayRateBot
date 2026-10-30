from datetime import date
from types import SimpleNamespace

import pytest

from dayratebot import handlers
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
async def test_rating_comment_appends_to_note_for_same_day(tmp_path) -> None:
    database = Database(tmp_path / "ratings.sqlite3")
    await database.open()
    try:
        user_id = 123
        rated_for = date(2026, 10, 28)
        await database.ensure_user(user_id)
        metric = (await database.list_metrics())[0]
        await database.save_daily_note(user_id, rated_for, "Старая заметка")
        assert await database.get_daily_note(user_id, rated_for) == "Старая заметка"
        await database.save_rating(user_id, metric["id"], rated_for, 8)
        rating = await database.get_rating(user_id, metric["id"], rated_for)

        assert await database.update_comment(
            int(rating["id"]), user_id, "Новый комментарий"
        )

        updated = await database.get_rating(user_id, metric["id"], rated_for)
        notes = await database.get_recent_daily_notes(user_id)
        combined_note = "Старая заметка\nНовый комментарий"
        assert updated["comment"] == combined_note
        assert [row["note"] for row in notes] == [combined_note]
        assert await database.get_daily_note(user_id, rated_for) == combined_note
    finally:
        await database.close()


@pytest.mark.asyncio
async def test_open_migrates_existing_rating_comments_to_daily_notes(tmp_path) -> None:
    path = tmp_path / "ratings.sqlite3"
    database = Database(path)
    await database.open()
    user_id = 123
    rated_for = date(2026, 10, 28)
    await database.ensure_user(user_id)
    metric = (await database.list_metrics())[0]
    await database.save_daily_note(user_id, rated_for, "Старая заметка")
    await database.save_rating(user_id, metric["id"], rated_for, 8)
    rating = await database.get_rating(user_id, metric["id"], rated_for)
    await database.connection.execute(
        "UPDATE ratings SET comment = ?, updated_at = ? WHERE id = ?",
        ("Комментарий к оценке", "2026-10-30 12:00:00", rating["id"]),
    )
    await database.connection.execute(
        "UPDATE daily_notes SET updated_at = ? WHERE user_id = ? AND note_for = ?",
        ("2026-10-30 11:00:00", user_id, rated_for.isoformat()),
    )
    await database.connection.commit()
    await database.close()

    await database.open()
    try:
        migrated_rating = await database.get_rating(user_id, metric["id"], rated_for)
        notes = await database.get_recent_daily_notes(user_id)
        assert migrated_rating["comment"] == "Комментарий к оценке"
        assert [row["note"] for row in notes] == ["Комментарий к оценке"]
        cursor = await database.connection.execute(
            "SELECT comment FROM ratings WHERE id = ?", (rating["id"],)
        )
        assert (await cursor.fetchone())["comment"] is None
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


@pytest.mark.asyncio
async def test_daily_notes_are_independent_of_ratings_and_replace_per_day(
    tmp_path,
) -> None:
    database = Database(tmp_path / "ratings.sqlite3")
    await database.open()
    try:
        user_id = 123
        note_for = date(2026, 10, 30)
        await database.ensure_user(user_id)

        await database.save_daily_note(user_id, note_for, "Сходил на прогулку")
        await database.save_daily_note(user_id, note_for, "Встретился с друзьями")

        cursor = await database.connection.execute(
            "SELECT note FROM daily_notes WHERE user_id = ? AND note_for = ?",
            (user_id, note_for.isoformat()),
        )
        rows = await cursor.fetchall()
        assert [row["note"] for row in rows] == ["Встретился с друзьями"]
        assert await database.get_rating(
            user_id, int((await database.list_metrics())[0]["id"]), note_for
        ) is None
    finally:
        await database.close()


@pytest.mark.asyncio
async def test_delete_daily_note_only_removes_selected_users_day(tmp_path) -> None:
    database = Database(tmp_path / "ratings.sqlite3")
    await database.open()
    try:
        note_for = date(2026, 10, 30)
        await database.ensure_user(123)
        await database.ensure_user(456)
        await database.save_daily_note(123, note_for, "Моя заметка")
        await database.save_daily_note(456, note_for, "Другая заметка")

        assert await database.delete_daily_note(123, note_for)
        assert not await database.delete_daily_note(123, note_for)
        assert await database.get_daily_note(123, note_for) is None
        assert await database.get_daily_note(456, note_for) == "Другая заметка"
    finally:
        await database.close()


@pytest.mark.asyncio
async def test_history_recent_rating_omits_maximum_score(tmp_path, monkeypatch) -> None:
    database = Database(tmp_path / "ratings.sqlite3")
    await database.open()
    try:
        user_id = 123
        today = date(2026, 10, 30)
        await database.ensure_user(user_id)
        metric = (await database.list_metrics())[0]
        await database.save_rating(user_id, metric["id"], today, 7)
        await database.save_daily_note(user_id, today, "Хорошо провёл день")

        async def local_today(_database, _user_id):
            return today

        monkeypatch.setattr(handlers, "_local_today", local_today)
        text = await handlers._history_text(database, user_id, metric, "ru")

        assert "30.10.2026: 7" in text
        assert "30.10.2026: 7/10" not in text
        assert "30.10.2026: 7 — Хорошо провёл день" in text
        assert text.count("Последние оценки:") == 1
        assert "Последние заметки:" not in text
    finally:
        await database.close()


@pytest.mark.asyncio
async def test_history_includes_notes_without_a_rating(tmp_path, monkeypatch) -> None:
    database = Database(tmp_path / "ratings.sqlite3")
    await database.open()
    try:
        user_id = 123
        today = date(2026, 10, 30)
        await database.ensure_user(user_id)
        metric = (await database.list_metrics())[0]
        await database.save_daily_note(user_id, today, "Прогулялся в парке")

        async def local_today(_database, _user_id):
            return today

        monkeypatch.setattr(handlers, "_local_today", local_today)
        text = await handlers._history_text(database, user_id, metric, "ru")

        assert "30.10.2026: Прогулялся в парке" in text
        assert text.count("Последние оценки:") == 1
        assert "Последние заметки:" not in text
    finally:
        await database.close()


@pytest.mark.asyncio
async def test_note_is_saved_for_local_day_when_note_is_submitted(
    tmp_path, monkeypatch
) -> None:
    database = Database(tmp_path / "ratings.sqlite3")
    await database.open()
    try:
        user_id = 123
        today = date(2026, 10, 30)
        await database.ensure_user(user_id)
        await database.save_daily_note(user_id, today, "Первый фрагмент")

        async def local_today(_database, _user_id):
            return today

        monkeypatch.setattr(handlers, "_local_today", local_today)

        class State:
            async def clear(self):
                pass

        async def answer(_text):
            pass

        message = SimpleNamespace(
            from_user=SimpleNamespace(id=user_id, language_code="ru"),
            text="Моя заметка",
            answer=answer,
        )
        await handlers.save_note(message, State(), database)

        notes = await database.get_recent_daily_notes(user_id)
        assert [(row["note_for"], row["note"]) for row in notes] == [
            (today.isoformat(), "Первый фрагмент\nМоя заметка")
        ]
    finally:
        await database.close()
