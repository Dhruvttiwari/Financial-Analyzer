import pandas as pd
import plotly.express as px
import streamlit as st

from src.analytics import compute_kpis, detect_anomalies
from src.categorizer import apply_categories
from src.cleaner import clean_transactions
from src.database import load_transactions, save_transactions, update_categories

# --- Page Setup ---
st.set_page_config(page_title="Personal Finance Analyzer", layout="wide")
st.title("Personal Finance & Transaction Analyzer")

# --- Sidebar: Upload or Load Sample Data ---
st.sidebar.header("Data Ingestion")
uploaded_file = st.sidebar.file_uploader("Upload Bank Statement (CSV)", type=["csv"])

if uploaded_file is not None:
    try:
        raw_df = pd.read_csv(uploaded_file)
        cleaned = apply_categories(clean_transactions(raw_df))
        inserted = save_transactions(cleaned)
        st.sidebar.success(f"Imported {inserted} new unique transaction(s).")
    except Exception as exc:
        st.sidebar.error(f"Upload failed: {exc}")

if st.sidebar.button("Load Sample Dataset"):
    sample_df = pd.read_csv("data/sample_statement.csv")
    cleaned = apply_categories(clean_transactions(sample_df))
    inserted = save_transactions(cleaned)
    st.sidebar.info(f"Loaded {inserted} new sample transaction(s).")

# --- Load Saved Data from SQLite ---
df = load_transactions()

if df.empty:
    st.info("Upload a CSV statement or click **Load Sample Dataset** in the sidebar to begin.")
    st.stop()

# --- Sidebar: Filters & Anomaly Controls ---
st.sidebar.divider()
st.sidebar.header("Filters & Settings")

df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)
months = sorted(df["month"].unique(), reverse=True)
selected_months = st.sidebar.multiselect("Filter by Month", months, default=months)
z_threshold = st.sidebar.slider(
    "Anomaly Sensitivity (Z-Score)",
    min_value=1.0,
    max_value=3.0,
    value=1.4,
    step=0.1,
    help="Lower values flag more transactions; higher values flag only extreme spikes.",
)

filtered_df = df[df["month"].isin(selected_months)]
if filtered_df.empty:
    st.warning("Select at least one month in the sidebar to view analytics.")
    st.stop()

# --- KPI Metric Cards ---
kpis = compute_kpis(filtered_df)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Income", f"₹{kpis['income']:,.0f}")
col2.metric("Total Expenses", f"₹{kpis['expenses']:,.0f}")
col3.metric("Net Savings", f"₹{kpis['net_savings']:,.0f}")
col4.metric("Savings Rate", f"{kpis['savings_rate']:.1f}%")

st.divider()

# --- Interactive Plotly Charts ---
chart_left, chart_right = st.columns(2)

with chart_left:
    st.subheader("Spending by Category")
    debits = filtered_df[filtered_df["type"] == "Debit"]
    if not debits.empty:
        cat_sum = debits.groupby("category", as_index=False)["amount"].sum()
        fig_pie = px.pie(cat_sum, names="category", values="amount", hole=0.45)
        st.plotly_chart(fig_pie, width="stretch")

with chart_right:
    st.subheader("Monthly Cash Flow")
    monthly = filtered_df.groupby(["month", "type"], as_index=False)["amount"].sum()
    fig_bar = px.bar(monthly, x="month", y="amount", color="type", barmode="group")
    st.plotly_chart(fig_bar, width="stretch")

# --- Anomaly Detection Section ---
st.subheader("Flagged Unusual Transactions")
anomalies = detect_anomalies(filtered_df, z_threshold=z_threshold)
if anomalies.empty:
    st.success("No unusual spending spikes detected at the current threshold.")
else:
    st.warning(f"{len(anomalies)} unusual transaction(s) detected based on spending variance.")
    st.dataframe(anomalies, width="stretch", hide_index=True)

# --- Interactive Category Editor ---
st.subheader("Transaction Ledger (Edit Categories)")
categories = [
    "Food & Dining",
    "Transport",
    "Housing & Rent",
    "Utilities & Bills",
    "Subscriptions",
    "Shopping",
    "Income",
    "Uncategorized",
]
edited_df = st.data_editor(
    filtered_df[["txn_hash", "date", "description", "amount", "type", "category"]],
    disabled=["txn_hash", "date", "description", "amount", "type"],
    column_config={
        "category": st.column_config.SelectboxColumn(
            "Category", options=categories, required=True
        )
    },
    hide_index=True,
    width="stretch",
)

if st.button("Save Category Changes"):
    updates = list(zip(edited_df["category"], edited_df["txn_hash"]))
    update_categories(updates)
    st.success("Categories updated in SQLite.")
    st.rerun()