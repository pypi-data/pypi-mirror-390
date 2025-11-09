# storage/db.py
import sqlite3, json, time
from pathlib import Path
from typing import Iterable, Optional, Any

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS pages(
  id INTEGER PRIMARY KEY,
  url TEXT UNIQUE,
  canonical TEXT,
  status INTEGER,
  fetched_at INTEGER,
  title TEXT,
  visible_text TEXT
);

CREATE TABLE IF NOT EXISTS links(
  id INTEGER PRIMARY KEY,
  from_url TEXT,
  to_url TEXT,
  anchor_text TEXT,
  rel TEXT,
  llm_score_est REAL DEFAULT 0.0,
  llm_score_final REAL DEFAULT 0.0,
  UNIQUE(from_url, to_url)
);

CREATE TABLE IF NOT EXISTS chunks(
  id INTEGER PRIMARY KEY,
  page_url TEXT,
  chunk_id INTEGER,
  text TEXT,
  token_count INTEGER,
  UNIQUE(page_url, chunk_id)
);

-- Simple vector storage (float32 array as JSON; small, portable)
CREATE TABLE IF NOT EXISTS embeddings(
  id INTEGER PRIMARY KEY,
  page_url TEXT,
  chunk_id INTEGER,
  vector TEXT,             -- json.dumps(list of floats)
  model TEXT,
  dim INTEGER,
  created_at INTEGER,
  UNIQUE(page_url, chunk_id, model)
);

CREATE TABLE IF NOT EXISTS crawl_log(
  id INTEGER PRIMARY KEY,
  url TEXT,
  action TEXT,             -- queued, fetched, skipped, failed
  reason TEXT,
  ts INTEGER
);

CREATE INDEX IF NOT EXISTS idx_pages_url ON pages(url);
CREATE INDEX IF NOT EXISTS idx_links_to ON links(to_url);
CREATE INDEX IF NOT EXISTS idx_chunks_page ON chunks(page_url);
CREATE INDEX IF NOT EXISTS idx_embeds_page ON embeddings(page_url);
"""

class DB:
    def __init__(self, path: str = "spider_core.db"):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def upsert_page(self, url: str, canonical: Optional[str], status: int, title: Optional[str], visible_text: str):
        self.conn.execute(
            """INSERT INTO pages(url, canonical, status, fetched_at, title, visible_text)
               VALUES(?,?,?,?,?,?)
               ON CONFLICT(url) DO UPDATE SET
                 canonical=excluded.canonical,
                 status=excluded.status,
                 fetched_at=excluded.fetched_at,
                 title=excluded.title,
                 visible_text=excluded.visible_text
            """,
            (url, canonical, status, int(time.time()), title, visible_text),
        )
        self.conn.commit()

    def upsert_links(self, from_url: str, links: Iterable[dict]):
        rows = []
        for l in links:
            rows.append((
                from_url, l["href"], l.get("text"), json.dumps(l.get("rel", [])),
                float(l.get("llm_score", 0.0))
            ))
        self.conn.executemany(
            """INSERT INTO links(from_url, to_url, anchor_text, rel, llm_score_est)
               VALUES(?,?,?,?,?)
               ON CONFLICT(from_url,to_url) DO UPDATE SET
                 anchor_text=excluded.anchor_text,
                 rel=excluded.rel,
                 llm_score_est=excluded.llm_score_est
            """,
            rows
        )
        self.conn.commit()

    def set_final_link_score(self, from_url: str, to_url: str, score: float):
        self.conn.execute(
            "UPDATE links SET llm_score_final=? WHERE from_url=? AND to_url=?",
            (float(score), from_url, to_url)
        )
        self.conn.commit()

    def upsert_chunks(self, page_url: str, chunks: Iterable[dict]):
        rows = []
        for c in chunks:
            rows.append((page_url, int(c["chunk_id"]), c["text"], int(c["token_count"])))
        self.conn.executemany(
            """INSERT INTO chunks(page_url, chunk_id, text, token_count)
               VALUES(?,?,?,?)
               ON CONFLICT(page_url,chunk_id) DO UPDATE SET
                 text=excluded.text,
                 token_count=excluded.token_count
            """, rows
        )
        self.conn.commit()

    def upsert_embedding(self, page_url: str, chunk_id: int, vec: list[float], model: str, dim: int):
        self.conn.execute(
            """INSERT INTO embeddings(page_url,chunk_id,vector,model,dim,created_at)
               VALUES(?,?,?,?,?,?)
               ON CONFLICT(page_url,chunk_id,model) DO UPDATE SET
                 vector=excluded.vector,
                 dim=excluded.dim,
                 created_at=excluded.created_at
            """,
            (page_url, chunk_id, json.dumps(vec), model, dim, int(time.time()))
        )
        self.conn.commit()

    def already_fetched(self, url: str) -> bool:
        r = self.conn.execute("SELECT 1 FROM pages WHERE url=? LIMIT 1", (url,)).fetchone()
        return r is not None

    def log(self, url: str, action: str, reason: Optional[str] = None):
        self.conn.execute(
            "INSERT INTO crawl_log(url,action,reason,ts) VALUES(?,?,?,?)",
            (url, action, reason, int(time.time()))
        )
        self.conn.commit()

    def close(self):
        self.conn.close()
