from datetime import date
from pathlib import Path
from typing import Any

import aiosqlite


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.connection: aiosqlite.Connection | None = None

    async def open(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = await aiosqlite.connect(self.path)
        self.connection.row_factory = aiosqlite.Row
        await self.connection.execute("PRAGMA foreign_keys = ON")
        await self.connection.execute("PRAGMA journal_mode = WAL")
        await self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                timezone TEXT NOT NULL DEFAULT 'UTC',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                min_score INTEGER NOT NULL,
                max_score INTEGER NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                CHECK (min_score <= max_score)
            );

            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
                metric_id INTEGER NOT NULL REFERENCES metrics(id),
                rated_for TEXT NOT NULL,
                score INTEGER NOT NULL,
                comment TEXT,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (user_id, metric_id, rated_for)
            );

            CREATE INDEX IF NOT EXISTS ratings_user_date_idx
                ON ratings (user_id, rated_for);

            INSERT OR IGNORE INTO metrics (code, name, min_score, max_score)
            VALUES ('day_rating', 'Оценка дня', 1, 10);
            """
        )
        await self.connection.commit()

    async def close(self) -> None:
        if self.connection is not None:
            await self.connection.close()
            self.connection = None

    def _db(self) -> aiosqlite.Connection:
        if self.connection is None:
            raise RuntimeError("Database is not open")
        return self.connection

    async def ensure_user(self, telegram_id: int) -> None:
        await self._db().execute(
            "INSERT OR IGNORE INTO users (telegram_id) VALUES (?)", (telegram_id,)
        )
        await self._db().commit()

    async def get_timezone(self, telegram_id: int) -> str:
        cursor = await self._db().execute(
            "SELECT timezone FROM users WHERE telegram_id = ?", (telegram_id,)
        )
        row = await cursor.fetchone()
        if row is None:
            await self.ensure_user(telegram_id)
            return "UTC"
        return str(row["timezone"])

    async def set_timezone(self, telegram_id: int, timezone: str) -> None:
        await self._db().execute(
            "INSERT INTO users (telegram_id, timezone) VALUES (?, ?) "
            "ON CONFLICT (telegram_id) DO UPDATE SET timezone = excluded.timezone",
            (telegram_id, timezone),
        )
        await self._db().commit()

    async def list_metrics(self) -> list[aiosqlite.Row]:
        cursor = await self._db().execute(
            "SELECT id, code, name, min_score, max_score FROM metrics "
            "WHERE is_active = 1 ORDER BY id"
        )
        return list(await cursor.fetchall())

    async def get_rating(
        self, user_id: int, metric_id: int, rated_for: date
    ) -> aiosqlite.Row | None:
        cursor = await self._db().execute(
            "SELECT id, score, comment FROM ratings "
            "WHERE user_id = ? AND metric_id = ? AND rated_for = ?",
            (user_id, metric_id, rated_for.isoformat()),
        )
        return await cursor.fetchone()

    async def save_rating(
        self,
        user_id: int,
        metric_id: int,
        rated_for: date,
        score: int,
        comment: str | None = None,
    ) -> None:
        await self._db().execute(
            """
            INSERT INTO ratings (user_id, metric_id, rated_for, score, comment)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT (user_id, metric_id, rated_for) DO UPDATE SET
                score = excluded.score,
                comment = COALESCE(excluded.comment, ratings.comment),
                updated_at = CURRENT_TIMESTAMP
            """,
            (user_id, metric_id, rated_for.isoformat(), score, comment),
        )
        await self._db().commit()

    async def update_comment(self, rating_id: int, user_id: int, comment: str) -> bool:
        cursor = await self._db().execute(
            "UPDATE ratings SET comment = ?, updated_at = CURRENT_TIMESTAMP "
            "WHERE id = ? AND user_id = ?",
            (comment, rating_id, user_id),
        )
        await self._db().commit()
        return cursor.rowcount == 1

    async def get_rating_owner(self, rating_id: int, user_id: int) -> Any | None:
        cursor = await self._db().execute(
            "SELECT id FROM ratings WHERE id = ? AND user_id = ?",
            (rating_id, user_id),
        )
        return await cursor.fetchone()

    async def get_ratings(
        self, user_id: int, metric_id: int, start: date, end: date
    ) -> list[tuple[date, int]]:
        cursor = await self._db().execute(
            """
            SELECT rated_for, score FROM ratings
            WHERE user_id = ? AND metric_id = ? AND rated_for >= ? AND rated_for <= ?
            ORDER BY rated_for
            """,
            (user_id, metric_id, start.isoformat(), end.isoformat()),
        )
        rows = await cursor.fetchall()
        return [(date.fromisoformat(row["rated_for"]), int(row["score"])) for row in rows]

    async def get_recent_ratings(
        self, user_id: int, metric_id: int, limit: int = 5
    ) -> list[aiosqlite.Row]:
        cursor = await self._db().execute(
            """
            SELECT rated_for, score, comment FROM ratings
            WHERE user_id = ? AND metric_id = ?
            ORDER BY rated_for DESC LIMIT ?
            """,
            (user_id, metric_id, limit),
        )
        return list(await cursor.fetchall())
