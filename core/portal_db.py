"""
Portal Database Manager.
Manages news articles, categories, views, and market insights for the web portal.
"""
import time
import json
import logging
from typing import Optional, List, Dict, Any
from core.aiosqlite_compat import aiosqlite
from config import settings

logger = logging.getLogger("sectors.portal_db")

class PortalDBManager:
    def __init__(self, db_path: str = settings.DATABASE_PATH):
        self.db_path = db_path

    async def init_db(self):
        """Create portal tables if not exists."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS portal_articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    slug TEXT UNIQUE NOT NULL,
                    summary TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT NOT NULL,
                    tickers_json TEXT DEFAULT '[]',
                    author TEXT NOT NULL,
                    sentiment TEXT DEFAULT 'NEUTRAL',
                    sectors_data_json TEXT,
                    views INTEGER DEFAULT 0,
                    published_at TEXT NOT NULL
                )
            """)
            await db.execute("CREATE INDEX IF NOT EXISTS idx_art_category ON portal_articles(category)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_art_slug ON portal_articles(slug)")
            await db.commit()
            logger.info("Portal database tables initialized at %s", self.db_path)

    async def save_article(
        self,
        title: str,
        slug: str,
        summary: str,
        content: str,
        category: str,
        tickers: List[str],
        author: str = "Wartawan AI Garda",
        sentiment: str = "NEUTRAL",
        sectors_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Insert or replace a published article."""
        published_at = time.strftime("%Y-%m-%d %H:%M:%S")
        tickers_str = json.dumps(tickers)
        sectors_str = json.dumps(sectors_data or {})

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO portal_articles (
                    title, slug, summary, content, category, tickers_json,
                    author, sentiment, sectors_data_json, views, published_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)
                ON CONFLICT(slug) DO UPDATE SET
                    title = excluded.title,
                    summary = excluded.summary,
                    content = excluded.content,
                    category = excluded.category,
                    tickers_json = excluded.tickers_json,
                    author = excluded.author,
                    sentiment = excluded.sentiment,
                    sectors_data_json = excluded.sectors_data_json,
                    published_at = excluded.published_at
            """, (title, slug, summary, content, category, tickers_str, author, sentiment, sectors_str, published_at))
            await db.commit()

        return {
            "title": title,
            "slug": slug,
            "category": category,
            "tickers": tickers,
            "author": author,
            "sentiment": sentiment,
            "published_at": published_at
        }

    async def list_articles(
        self,
        category: Optional[str] = None,
        ticker: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List articles with filtering and pagination."""
        query = "SELECT id, title, slug, summary, category, tickers_json, author, sentiment, views, published_at FROM portal_articles"
        clauses = []
        params = []

        if category:
            clauses.append("category = ?")
            params.append(category)

        if ticker:
            clauses.append("tickers_json LIKE ?")
            params.append(f"%{ticker.upper()}%")

        if clauses:
            query += " WHERE " + " AND ".join(clauses)

        query += " ORDER BY id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        articles = []
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(query, params) as cursor:
                async for row in cursor:
                    articles.append({
                        "id": row[0],
                        "title": row[1],
                        "slug": row[2],
                        "summary": row[3],
                        "category": row[4],
                        "tickers": json.loads(row[5] or "[]"),
                        "author": row[6],
                        "sentiment": row[7],
                        "views": row[8],
                        "published_at": row[9]
                    })
        return articles

    async def get_article(self, slug: str) -> Optional[Dict[str, Any]]:
        """Fetch a single article by slug and increment views."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT id, title, slug, summary, content, category, tickers_json, author, sentiment, sectors_data_json, views, published_at FROM portal_articles WHERE slug = ?",
                (slug,)
            ) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return None

                # Increment view count
                await db.execute("UPDATE portal_articles SET views = views + 1 WHERE slug = ?", (slug,))
                await db.commit()

                return {
                    "id": row[0],
                    "title": row[1],
                    "slug": row[2],
                    "summary": row[3],
                    "content": row[4],
                    "category": row[5],
                    "tickers": json.loads(row[6] or "[]"),
                    "author": row[7],
                    "sentiment": row[8],
                    "sectors_data": json.loads(row[9] or "{}"),
                    "views": row[10] + 1,
                    "published_at": row[11]
                }

portal_db = PortalDBManager()
