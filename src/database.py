import sqlite3
import pandas as pd

DB_PATH = "finance.db"


def init_db(db_path: str = DB_PATH) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                txn_hash TEXT PRIMARY KEY,
                date TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                type TEXT NOT NULL,
                category TEXT NOT NULL
            )
            """
        )


def save_transactions(df: pd.DataFrame, db_path: str = DB_PATH) -> int:
    init_db(db_path)
    rows = df[["txn_hash", "date", "description", "amount", "type", "category"]].values.tolist()
    with sqlite3.connect(db_path) as conn:
        cursor = conn.executemany(
            """
            INSERT OR IGNORE INTO transactions
            (txn_hash, date, description, amount, type, category)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        return cursor.rowcount


def load_transactions(db_path: str = DB_PATH) -> pd.DataFrame:
    init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query("SELECT * FROM transactions ORDER BY date DESC", conn)


def update_categories(updates: list[tuple[str, str]], db_path: str = DB_PATH) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.executemany(
            "UPDATE transactions SET category = ? WHERE txn_hash = ?",
            updates,
        )