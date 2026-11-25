import hashlib
import pandas as pd


def _make_hash(row: pd.Series) -> str:
    raw = f"{row['date']}|{row['description']}|{row['amount']:.2f}|{row['type']}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [col.strip().lower() for col in df.columns]

    required = {"date", "description", "amount", "type"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["description"] = df["description"].astype(str).str.strip().str.upper()
    df["amount"] = (
        df["amount"]
        .astype(str)
        .str.replace(r"[₹$,\s]", "", regex=True)
        .pipe(pd.to_numeric, errors="coerce")
        .abs()
    )
    df["type"] = df["type"].astype(str).str.strip().str.title()

    df = df.dropna(subset=["date", "amount"])
    df["txn_hash"] = df.apply(_make_hash, axis=1)
    df = df.drop_duplicates(subset=["txn_hash"]).reset_index(drop=True)
    return df