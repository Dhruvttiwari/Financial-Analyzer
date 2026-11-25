import pandas as pd


def compute_kpis(df: pd.DataFrame) -> dict:
    income = df.loc[df["type"] == "Credit", "amount"].sum()
    expenses = df.loc[df["type"] == "Debit", "amount"].sum()
    net_savings = income - expenses
    savings_rate = (net_savings / income * 100) if income > 0 else 0.0
    return {
        "income": round(float(income), 2),
        "expenses": round(float(expenses), 2),
        "net_savings": round(float(net_savings), 2),
        "savings_rate": round(float(savings_rate), 2),
    }


def detect_anomalies(df: pd.DataFrame, z_threshold: float = 1.4) -> pd.DataFrame:
    debits = df[df["type"] == "Debit"].copy()
    if len(debits) < 4:
        return pd.DataFrame()

    overall_mean = debits["amount"].mean()
    overall_std = debits["amount"].std()

    cat_stats = (
        debits.groupby("category")["amount"]
        .agg(["count", "mean", "std"])
        .reset_index()
    )
    debits = debits.merge(cat_stats, on="category", how="left")

    def _calc_z(row):
        if row["count"] >= 3 and pd.notna(row["std"]) and row["std"] > 0:
            return (row["amount"] - row["mean"]) / row["std"]
        if pd.notna(overall_std) and overall_std > 0:
            return (row["amount"] - overall_mean) / overall_std
        return 0.0

    debits["z_score"] = debits.apply(_calc_z, axis=1).round(2)
    anomalies = debits[debits["z_score"] >= z_threshold].sort_values(
        "z_score", ascending=False
    )
    return anomalies[["date", "description", "category", "amount", "z_score"]]