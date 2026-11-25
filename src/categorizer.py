import re
import pandas as pd

CATEGORY_RULES = {
    "Food & Dining": [r"SWIGGY", r"ZOMATO", r"CAFE", r"RESTAURANT", r"DOMINOS", r"BLINKIT"],
    "Transport": [r"UBER", r"OLA", r"RAPIDO", r"METRO", r"PETROL", r"FUEL", r"IRCTC"],
    "Housing & Rent": [r"RENT", r"LANDLORD", r"MAINTENANCE", r"HOUSING"],
    "Utilities & Bills": [r"ELECTRICITY", r"WATER", r"JIO", r"AIRTEL", r"BROADBAND", r"RECHARGE"],
    "Subscriptions": [r"NETFLIX", r"SPOTIFY", r"APPLE MUSIC", r"PRIME", r"YOUTUBE"],
    "Shopping": [r"AMAZON", r"FLIPKART", r"MYNTRA", r"DECATHLON", r"ELECTRONICS"],
}


def classify_description(description: str, txn_type: str) -> str:
    if txn_type == "Credit":
        return "Income"
    for category, patterns in CATEGORY_RULES.items():
        if any(re.search(pattern, description, re.IGNORECASE) for pattern in patterns):
            return category
    return "Uncategorized"


def apply_categories(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["category"] = df.apply(
        lambda row: classify_description(row["description"], row["type"]), axis=1
    )
    return df