import pandas as pd
import pytest
from src.cleaner import clean_transactions


def test_deduplication_and_currency_cleaning():
    raw = pd.DataFrame(
        {
            " Date ": ["2026-10-05", "2026-10-05"],
            "Description": ["upi-zomato", "UPI-ZOMATO "],
            "Amount": ["₹1,200.50", "1200.50"],
            "Type": ["debit", "Debit"],
        }
    )
    cleaned = clean_transactions(raw)

    assert len(cleaned) == 1
    assert cleaned.loc[0, "amount"] == 1200.50
    assert cleaned.loc[0, "description"] == "UPI-ZOMATO"
    assert cleaned.loc[0, "type"] == "Debit"


def test_missing_required_columns_raises_error():
    bad_df = pd.DataFrame({"Date": ["2026-10-01"], "Amount": [500]})

    with pytest.raises(ValueError, match="Missing required columns"):
        clean_transactions(bad_df)


def test_invalid_rows_are_dropped():
    raw = pd.DataFrame(
        {
            "Date": ["2026-10-01", "not-a-date", "2026-10-03"],
            "Description": ["Valid Row", "Broken Date", "Broken Amount"],
            "Amount": [500, 200, "abc"],
            "Type": ["Debit", "Debit", "Debit"],
        }
    )
    cleaned = clean_transactions(raw)

    assert len(cleaned) == 1
    assert cleaned.loc[0, "description"] == "VALID ROW"