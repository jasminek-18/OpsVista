"""
OpsVista – ETL Pipeline
Loads all clean CSVs into MySQL opsvista database.
Author: Jasmine
"""

import pandas as pd
import mysql.connector
import os

# ── CONFIG — ──────────────────────
DB = {
    "host":     "localhost",
    "user":     "root",
    "password": "jasmine2510",   
    "database": "opsvista"
}

CLEAN = "../data/clean"

def get_connection():
    return mysql.connector.connect(**DB)

def load_table(conn, table_name, df):
    cursor = conn.cursor()
    # clear existing rows before loading
    cursor.execute(f"SET FOREIGN_KEY_CHECKS=0")
    cursor.execute(f"TRUNCATE TABLE {table_name}")
    cursor.execute(f"SET FOREIGN_KEY_CHECKS=1")

    # build insert query
    cols        = ", ".join(df.columns)
    placeholders = ", ".join(["%s"] * len(df.columns))
    query       = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"

    # replace NaN with None so MySQL gets NULL
    data = [
        tuple(None if pd.isna(v) else v for v in row)
        for row in df.itertuples(index=False, name=None)
    ]

    cursor.executemany(query, data)
    conn.commit()
    cursor.close()
    print(f"  Loaded {table_name:<25} — {len(df):>6} rows")

def main():
    print("=" * 50)
    print("  OpsVista — ETL: Loading data into MySQL")
    print("=" * 50)

    conn = get_connection()
    print("  MySQL connection successful\n")

    # load order matters — parent tables first
    load_table(conn, "categories",           pd.read_csv(f"{CLEAN}/categories.csv"))
    load_table(conn, "products",             pd.read_csv(f"{CLEAN}/products.csv"))
    load_table(conn, "suppliers",            pd.read_csv(f"{CLEAN}/suppliers.csv"))
    load_table(conn, "warehouses",           pd.read_csv(f"{CLEAN}/warehouses.csv"))
    load_table(conn, "customers",            pd.read_csv(f"{CLEAN}/customers.csv"))
    load_table(conn, "purchase_orders",      pd.read_csv(f"{CLEAN}/purchase_orders.csv"))
    load_table(conn, "purchase_order_items", pd.read_csv(f"{CLEAN}/purchase_order_items.csv"))
    load_table(conn, "inventory",            pd.read_csv(f"{CLEAN}/inventory.csv"))
    load_table(conn, "sales_orders",         pd.read_csv(f"{CLEAN}/sales_orders.csv"))
    load_table(conn, "shipments",            pd.read_csv(f"{CLEAN}/shipments.csv"))
    load_table(conn, "returns",              pd.read_csv(f"{CLEAN}/returns.csv"))

    conn.close()
    print("\n" + "=" * 50)
    print("  ETL complete. All tables loaded.")
    print("=" * 50)

if __name__ == "__main__":
    main()