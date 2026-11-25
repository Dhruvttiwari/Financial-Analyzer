# Personal Finance & Transaction Analyzer

An interactive Python web application that ingests raw bank CSV statements, cleans and deduplicates transactions using SHA-256 hashing, auto-categorizes expenses with Regex rules, persists records in SQLite, and flags unusual spending spikes using statistical Z-scores.

**Live Demo:** [Add your Streamlit Cloud link here]

## Key Features
- **Duplicate-Proof CSV Ingestion:** Normalizes dates, strips currency symbols/commas, validates schemas, and uses SHA-256 transaction fingerprints (`txn_hash`) with SQLite `INSERT OR IGNORE` so overlapping uploads never double-count records.
- **Automated Categorization:** Classifies bank narrations into spending categories using modular Regex rules, with an interactive table editor to override and persist categories back to SQLite.
- **KPI & Visual Analytics:** Tracks Total Income, Total Expenses, Net Savings, and Savings Rate alongside interactive Plotly donut and monthly cash-flow bar charts.
- **Statistical Anomaly Detection:** Flags unusual spending spikes using category-level Z-scores with an interactive sensitivity slider.
- **Automated Testing:** Includes a `pytest` unit test suite covering deduplication, currency normalization, missing columns, and corrupted rows.

## Tech Stack
- **Language & Data:** Python, Pandas, Regex
- **Database:** SQLite (`sqlite3` with parameterized SQL queries)
- **Visualization & UI:** Streamlit, Plotly
- **Testing:** Pytest

## Project Structure
```text
finance-analyzer/
├── app.py                  # Streamlit dashboard & UI orchestration
├── src/
│   ├── cleaner.py          # Data normalization & SHA-256 deduplication
│   ├── categorizer.py      # Regex merchant classification rules
│   ├── database.py         # SQLite persistence & category updates
│   └── analytics.py        # KPI calculations & Z-score anomaly detector
├── data/
│   └── sample_statement.csv
├── tests/
│   └── test_cleaner.py     # Pytest unit tests
├── requirements.txt
└── .gitignore