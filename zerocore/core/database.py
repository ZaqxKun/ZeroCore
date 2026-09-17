from __future__ import annotations
import json, hashlib
from datetime import datetime, timedelta, timezone
import aiosqlite
from .config import DATABASE_PATH

class Database:
    async def init(self):
        DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.executescript("""
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS messages(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              discord_message_id TEXT UNIQUE NOT NULL,
              channel_id TEXT NOT NULL,
              channel_name TEXT NOT NULL,
              author_hash TEXT NOT NULL,
              content TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS actions(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              action_type TEXT NOT NULL,
              target TEXT,
              reason TEXT NOT NULL,
              metadata_json TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS trials(
              channel_id TEXT PRIMARY KEY,
              channel_name TEXT NOT NULL,
              topic_key TEXT NOT NULL,
              created_at TEXT NOT NULL,
              review_at TEXT NOT NULL,
              state TEXT NOT NULL DEFAULT 'trial'
            );
            CREATE TABLE IF NOT EXISTS topic_cooldowns(
              topic_key TEXT PRIMARY KEY,
              last_action_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS heartbeats(
              id INTEGER PRIMARY KEY CHECK(id=1),
              last_seen_at TEXT NOT NULL,
              source TEXT NOT NULL
            );
            """)
            await db.commit()

    @staticmethod
    def _author_hash(user_id: int) -> str:
        return hashlib.sha256(str(user_id).encode()).hexdigest()[:16]

    async def add_message(self, message):
        content = (message.content or "").strip()
        if not content:
            return
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute("""
              INSERT OR IGNORE INTO messages
              (discord_message_id,channel_id,channel_name,author_hash,content,created_at)
              VALUES(?,?,?,?,?,?)
            """, (
              str(message.id), str(message.channel.id),
              getattr(message.channel, "name", "unknown"),
              self._author_hash(message.author.id), content[:3000],
              message.created_at.astimezone(timezone.utc).isoformat()
            ))
            await db.commit()

    async def recent_messages(self, days: int, limit: int, excluded_channels=None):
        since = (datetime.now(timezone.utc)-timedelta(days=days)).isoformat()
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute("""
              SELECT channel_name,author_hash,content,created_at
              FROM messages WHERE created_at>=?
              ORDER BY created_at DESC LIMIT ?
            """, (since, limit*2))
            rows = [dict(x) for x in await cur.fetchall()]
        rows.reverse()
        if excluded_channels:
            rows = [r for r in rows if r["channel_name"] not in excluded_channels]
        return rows[-limit:]

    async def log_action(self, action_type, target, reason, metadata=None):
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute("""
              INSERT INTO actions(action_type,target,reason,metadata_json,created_at)
              VALUES(?,?,?,?,?)
            """, (
              action_type, target, reason,
              json.dumps(metadata or {}, ensure_ascii=False),
              datetime.now(timezone.utc).isoformat()
            ))
            await db.commit()

    async def topic_last_action(self, key):
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cur = await db.execute("SELECT last_action_at FROM topic_cooldowns WHERE topic_key=?", (key,))
            row = await cur.fetchone()
        return datetime.fromisoformat(row[0]) if row else None

    async def touch_topic(self, key):
        now = datetime.now(timezone.utc).isoformat()
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute("""
              INSERT INTO topic_cooldowns(topic_key,last_action_at) VALUES(?,?)
              ON CONFLICT(topic_key) DO UPDATE SET last_action_at=excluded.last_action_at
            """, (key,now))
            await db.commit()

    async def add_trial(self, channel_id, channel_name, topic_key, review_at):
        now = datetime.now(timezone.utc).isoformat()
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute("""
              INSERT OR REPLACE INTO trials(channel_id,channel_name,topic_key,created_at,review_at,state)
              VALUES(?,?,?,?,?,'trial')
            """, (str(channel_id),channel_name,topic_key,now,review_at.isoformat()))
            await db.commit()

    async def due_trials(self):
        now = datetime.now(timezone.utc).isoformat()
        async with aiosqlite.connect(DATABASE_PATH) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute("SELECT * FROM trials WHERE state='trial' AND review_at<=?", (now,))
            return [dict(x) for x in await cur.fetchall()]

    async def set_trial_state(self, channel_id, state):
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute("UPDATE trials SET state=? WHERE channel_id=?", (state,str(channel_id)))
            await db.commit()

    async def set_heartbeat(self, source="manual"):
        now = datetime.now(timezone.utc).isoformat()
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute("""
              INSERT INTO heartbeats(id,last_seen_at,source) VALUES(1,?,?)
              ON CONFLICT(id) DO UPDATE SET last_seen_at=excluded.last_seen_at,source=excluded.source
            """, (now,source))
            await db.commit()

    async def get_heartbeat(self):
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cur = await db.execute("SELECT last_seen_at,source FROM heartbeats WHERE id=1")
            row = await cur.fetchone()
        return (datetime.fromisoformat(row[0]), row[1]) if row else None

    async def purge_old_messages(self, retention_days):
        cutoff = (datetime.now(timezone.utc)-timedelta(days=retention_days)).isoformat()
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cur = await db.execute("DELETE FROM messages WHERE created_at<?", (cutoff,))
            await db.commit()
            return cur.rowcount
