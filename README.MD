# Ishant's Finance Manager 💰

A lightweight, terminal-based personal finance manager built in Python. This tool allows you to track daily expenses, manage investments, handle lending/borrowing, and calculate your exact net worth—all offline. Data is persistently stored locally in a JSON file.

## Features

* **Wallet Tracking:** Log daily income and expenses.
* **Investment Portfolio:** Buy and sell funds, and track your total invested assets.
* **Debt Manager:** Record money you have lent out (assets) and money you have borrowed (liabilities).
* **Pending Income Tracker:** Log expected payments and clear them via full or partial receipts.
* **Net Worth Calculator:** Automatically calculates your real wealth using the formula: `Wallet + Investments + Lent - Borrowed`.
* **CSV Export:** Export your complete transaction history to a `.csv` file for use in Excel or Google Sheets.
* **Safe Reset:** Wipe monthly transaction data while keeping your investment portfolio intact.

## Prerequisites

This script runs entirely on Python's standard library. No external installations (like `pip install`) are required.
* Python 3.x

## How to Run

1. Clone this repository to your local machine.
2. Open your terminal or command prompt in the project directory.
3. Execute the script:
   ```bash
   python manager.py