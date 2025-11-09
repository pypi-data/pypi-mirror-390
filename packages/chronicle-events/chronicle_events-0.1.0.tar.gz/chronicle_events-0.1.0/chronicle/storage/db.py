from __future__ import annotations
import sqlite3, os, time
from typing import List, Dict, Any

DB_PATH = os.environ.get("CHRONICLE_DB", "data/chronicle.db")


def _ensure_schema(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS docs ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "source TEXT,"
        "external_id TEXT,"
        "title TEXT,"
        "url TEXT,"
        "text TEXT,"
        "ts INTEGER"
        ");"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS vectors ("
        "doc_id INTEGER,"
        "dim INTEGER,"
        "vec BLOB,"
        "FOREIGN KEY(doc_id) REFERENCES docs(id)"
        ");"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS clusters ("
        "doc_id INTEGER,"
        "cluster_id TEXT,"
        "score REAL,"
        "ts INTEGER"
        ");"
    )
    conn.commit()


def connect() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    _ensure_schema(conn)
    return conn


def insert_doc(conn: sqlite3.Connection, doc: Dict[str, Any]) -> int:
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO docs(source, external_id, title, url, text, ts) VALUES(?,?,?,?,?,?)",
        (
            doc.get("source"),
            doc.get("external_id"),
            doc.get("title"),
            doc.get("url"),
            doc.get("text"),
            int(doc.get("ts", time.time())),
        ),
    )
    conn.commit()
    return cur.lastrowid


def get_recent_docs(conn: sqlite3.Connection, limit: int = 500) -> List[Dict[str, Any]]:
    cur = conn.cursor()
    cur.execute(
        "SELECT id, source, external_id, title, url, text, ts FROM docs ORDER BY ts DESC LIMIT ?",
        (limit,),
    )
    rows = cur.fetchall()
    keys = ["id", "source", "external_id", "title", "url", "text", "ts"]
    return [dict(zip(keys, r)) for r in rows]


def upsert_cluster(
    conn: sqlite3.Connection, doc_id: int, cluster_id: str, score: float
):
    ts = int(time.time())
    cur = conn.cursor()
    cur.execute("DELETE FROM clusters WHERE doc_id=?", (doc_id,))
    cur.execute(
        "INSERT INTO clusters(doc_id, cluster_id, score, ts) VALUES(?,?,?,?)",
        (doc_id, cluster_id, score, ts),
    )
    conn.commit()


def get_clusters(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute(
        "SELECT c.cluster_id, d.id, d.title, d.url, d.text, d.ts, c.score "
        "FROM clusters c JOIN docs d ON d.id = c.doc_id "
        "ORDER BY d.ts DESC"
    )
    out = {}
    for cid, did, title, url, text, ts, score in cur.fetchall():
        out.setdefault(cid, {"docs": [], "score_sum": 0.0, "n": 0})
        out[cid]["docs"].append(
            {
                "id": did,
                "title": title,
                "url": url,
                "text": text,
                "ts": ts,
                "score": score,
            }
        )
        out[cid]["score_sum"] += score
        out[cid]["n"] += 1
    for cid, v in out.items():
        v["score"] = v["score_sum"] / max(1, v["n"])
        del v["score_sum"]
        del v["n"]
    return out


def get_cluster_docs(conn: sqlite3.Connection, cluster_id: str):
    cur = conn.cursor()
    cur.execute(
        "SELECT d.id, d.title, d.url, d.text, d.ts, c.score "
        "FROM clusters c JOIN docs d ON d.id = c.doc_id "
        "WHERE c.cluster_id=? ORDER BY d.ts DESC",
        (cluster_id,),
    )
    keys = ["id", "title", "url", "text", "ts", "score"]
    return [dict(zip(keys, r)) for r in cur.fetchall()]
