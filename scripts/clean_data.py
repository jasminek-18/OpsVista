"""
OpsVista – Data Cleaning Pipeline
Reads raw CSVs, cleans them, engineers new columns, saves to data/clean/
Author: Jasmine
"""

import pandas as pd
import numpy as np
import os

RAW   = "../data/raw"
CLEAN = "../data/clean"
os.makedirs(CLEAN, exist_ok=True)

# ── HELPER ────────────────────────────────────────────────────────────────────

def report(name, before, after, nulls_fixed, dups_removed):
    print(f"\n  [{name}]")
    print(f"    Rows        : {before} → {after}")
    print(f"    Nulls fixed : {nulls_fixed}")
    print(f"    Dups removed: {dups_removed}")

# ── 1. CATEGORIES ─────────────────────────────────────────────────────────────

def clean_categories():
    df = pd.read_csv(f"{RAW}/categories.csv")
    before = len(df)
    dups   = df.duplicated().sum()
    df     = df.drop_duplicates()
    df['category_name'] = df['category_name'].str.strip().str.title()
    df.to_csv(f"{CLEAN}/categories.csv", index=False)
    report("categories", before, len(df), 0, dups)
    return df

# ── 2. PRODUCTS ───────────────────────────────────────────────────────────────

def clean_products():
    df     = pd.read_csv(f"{RAW}/products.csv")
    before = len(df)
    dups   = df.duplicated(subset='product_id').sum()
    df     = df.drop_duplicates(subset='product_id')

    # fix nulls
    nulls = df.isnull().sum().sum()
    df['unit_price']    = df['unit_price'].fillna(df['unit_price'].median())
    df['reorder_point'] = df['reorder_point'].fillna(100)
    df['is_active']     = df['is_active'].fillna(1)

    # clean text
    df['product_name'] = df['product_name'].str.strip().str.title()
    df['unit']         = df['unit'].str.strip().str.upper()
    df['velocity']     = df['velocity'].str.strip().str.lower()

    # feature: price band
    df['price_band'] = pd.cut(
        df['unit_price'],
        bins=[0, 100, 500, 2000, 10000, float('inf')],
        labels=['Very Low', 'Low', 'Medium', 'High', 'Very High']
    )

    df.to_csv(f"{CLEAN}/products.csv", index=False)
    report("products", before, len(df), nulls, dups)
    return df

# ── 3. SUPPLIERS ──────────────────────────────────────────────────────────────

def clean_suppliers():
    df     = pd.read_csv(f"{RAW}/suppliers.csv")
    before = len(df)
    dups   = df.duplicated(subset='supplier_id').sum()
    df     = df.drop_duplicates(subset='supplier_id')

    nulls = df.isnull().sum().sum()
    df['avg_lead_time_days'] = df['avg_lead_time_days'].fillna(df['avg_lead_time_days'].median())
    df['delay_rate']         = df['delay_rate'].fillna(0.20)
    df['return_rate']        = df['return_rate'].fillna(0.05)

    df['supplier_name'] = df['supplier_name'].str.strip()
    df['region']        = df['region'].str.strip().str.title()
    df['profile']       = df['profile'].str.strip().str.lower()

    # feature: supplier tier label
    df['supplier_tier'] = df['profile'].map({
        'reliable': 'Tier 1',
        'average':  'Tier 2',
        'poor':     'Tier 3'
    })

    # feature: risk flag
    df['high_risk_flag'] = (
        (df['delay_rate'] > 0.30) | (df['return_rate'] > 0.10)
    ).astype(int)

    df.to_csv(f"{CLEAN}/suppliers.csv", index=False)
    report("suppliers", before, len(df), nulls, dups)
    return df

# ── 4. WAREHOUSES ─────────────────────────────────────────────────────────────

def clean_warehouses():
    df     = pd.read_csv(f"{RAW}/warehouses.csv")
    before = len(df)
    dups   = df.duplicated(subset='warehouse_id').sum()
    df     = df.drop_duplicates(subset='warehouse_id')

    nulls = df.isnull().sum().sum()
    df['warehouse_name'] = df['warehouse_name'].str.strip()
    df['region']         = df['region'].str.strip().str.title()

    df.to_csv(f"{CLEAN}/warehouses.csv", index=False)
    report("warehouses", before, len(df), nulls, dups)
    return df

# ── 5. CUSTOMERS ──────────────────────────────────────────────────────────────

def clean_customers():
    df     = pd.read_csv(f"{RAW}/customers.csv")
    before = len(df)
    dups   = df.duplicated(subset='customer_id').sum()
    df     = df.drop_duplicates(subset='customer_id')

    nulls = df.isnull().sum().sum()
    df['customer_name']   = df['customer_name'].str.strip()
    df['region']          = df['region'].str.strip().str.title()
    df['customer_type']   = df['customer_type'].str.strip().str.title()

    df.to_csv(f"{CLEAN}/customers.csv", index=False)
    report("customers", before, len(df), nulls, dups)
    return df

# ── 6. PURCHASE ORDERS ────────────────────────────────────────────────────────

def clean_purchase_orders():
    df     = pd.read_csv(f"{RAW}/purchase_orders.csv")
    before = len(df)
    dups   = df.duplicated(subset='po_id').sum()
    df     = df.drop_duplicates(subset='po_id')

    # date parsing
    df['order_date']             = pd.to_datetime(df['order_date'])
    df['expected_delivery_date'] = pd.to_datetime(df['expected_delivery_date'])
    df['actual_delivery_date']   = pd.to_datetime(df['actual_delivery_date'])

    nulls = df['actual_delivery_date'].isnull().sum()

    # feature engineering
    df['lead_days'] = (
        df['actual_delivery_date'] - df['order_date']
    ).dt.days

    df['delay_days'] = (
        df['actual_delivery_date'] - df['expected_delivery_date']
    ).dt.days.clip(lower=0)

    # for pending orders fill lead_days with expected
    df['lead_days'] = df['lead_days'].fillna(
        (df['expected_delivery_date'] - df['order_date']).dt.days
    )
    df['delay_days'] = df['delay_days'].fillna(0)

    df['order_month'] = df['order_date'].dt.to_period('M').astype(str)
    df['order_year']  = df['order_date'].dt.year
    df['order_quarter'] = df['order_date'].dt.quarter.apply(lambda q: f"Q{q}")

    df['delay_band'] = pd.cut(
        df['delay_days'],
        bins=[-1, 0, 3, 7, 15, float('inf')],
        labels=['No Delay', '1–3 Days', '4–7 Days', '8–15 Days', '15+ Days']
    )

    df['payment_terms'] = df['payment_terms'].fillna('Net30')
    df['status']        = df['status'].str.strip().str.title()

    df.to_csv(f"{CLEAN}/purchase_orders.csv", index=False)
    report("purchase_orders", before, len(df), nulls, dups)
    return df

# ── 7. PURCHASE ORDER ITEMS ───────────────────────────────────────────────────

def clean_purchase_order_items():
    df     = pd.read_csv(f"{RAW}/purchase_order_items.csv")
    before = len(df)
    dups   = df.duplicated(subset='poi_id').sum()
    df     = df.drop_duplicates(subset='poi_id')

    nulls = df.isnull().sum().sum()
    df['unit_cost']       = df['unit_cost'].fillna(df['unit_cost'].median())
    df['quantity_ordered'] = df['quantity_ordered'].fillna(1).astype(int)
    df['line_total']      = df['unit_cost'] * df['quantity_ordered']

    df.to_csv(f"{CLEAN}/purchase_order_items.csv", index=False)
    report("purchase_order_items", before, len(df), nulls, dups)
    return df

# ── 8. INVENTORY ──────────────────────────────────────────────────────────────

def clean_inventory():
    df     = pd.read_csv(f"{RAW}/inventory.csv")
    before = len(df)
    dups   = df.duplicated(subset=['product_id','warehouse_id']).sum()
    df     = df.drop_duplicates(subset=['product_id','warehouse_id'])

    nulls = df.isnull().sum().sum()
    df['quantity_on_hand'] = df['quantity_on_hand'].fillna(0).astype(int)
    df['reorder_point']    = df['reorder_point'].fillna(100).astype(int)
    df['last_updated']     = pd.to_datetime(df['last_updated'])

    # feature: stock status
    df['stock_status'] = np.where(
        df['quantity_on_hand'] == 0, 'Stock-Out',
        np.where(
            df['quantity_on_hand'] < df['reorder_point'], 'Low Stock',
            np.where(
                df['quantity_on_hand'] > df['reorder_point'] * 5, 'Overstock',
                'Healthy'
            )
        )
    )

    # feature: days of stock remaining (assume avg daily usage = reorder_point / 30)
    df['avg_daily_usage']     = (df['reorder_point'] / 30).clip(lower=1)
    df['days_of_stock_left']  = (df['quantity_on_hand'] / df['avg_daily_usage']).round(0).astype(int)

    # feature: reorder flag
    df['reorder_flag'] = (df['quantity_on_hand'] <= df['reorder_point']).astype(int)

    df.to_csv(f"{CLEAN}/inventory.csv", index=False)
    report("inventory", before, len(df), nulls, dups)
    return df

# ── 9. SALES ORDERS ───────────────────────────────────────────────────────────

def clean_sales_orders():
    df     = pd.read_csv(f"{RAW}/sales_orders.csv")
    before = len(df)
    dups   = df.duplicated(subset='order_id').sum()
    df     = df.drop_duplicates(subset='order_id')

    nulls = df.isnull().sum().sum()
    df['order_date']   = pd.to_datetime(df['order_date'])
    df['total_amount'] = df['total_amount'].fillna(0)
    df['status']       = df['status'].str.strip().str.title()
    df['region']       = df['region'].str.strip().str.title()

    df['order_month']   = df['order_date'].dt.to_period('M').astype(str)
    df['order_year']    = df['order_date'].dt.year
    df['order_quarter'] = df['order_date'].dt.quarter.apply(lambda q: f"Q{q}")

    # feature: revenue band
    df['revenue_band'] = pd.cut(
        df['total_amount'],
        bins=[0, 5000, 25000, 100000, float('inf')],
        labels=['Small', 'Medium', 'Large', 'Enterprise']
    )

    df.to_csv(f"{CLEAN}/sales_orders.csv", index=False)
    report("sales_orders", before, len(df), nulls, dups)
    return df

# ── 10. SHIPMENTS ─────────────────────────────────────────────────────────────

def clean_shipments():
    df     = pd.read_csv(f"{RAW}/shipments.csv")
    before = len(df)
    dups   = df.duplicated(subset='shipment_id').sum()
    df     = df.drop_duplicates(subset='shipment_id')

    nulls = df.isnull().sum().sum()
    df['ship_date']              = pd.to_datetime(df['ship_date'])
    df['expected_delivery_date'] = pd.to_datetime(df['expected_delivery_date'])
    df['actual_delivery_date']   = pd.to_datetime(df['actual_delivery_date'])

    df['delay_days'] = (
        df['actual_delivery_date'] - df['expected_delivery_date']
    ).dt.days.clip(lower=0)

    df['shipment_partner']   = df['shipment_partner'].str.strip()
    df['destination_region'] = df['destination_region'].str.strip().str.title()
    df['vehicle_type']       = df['vehicle_type'].str.strip().str.title()

    # feature: delay severity
    df['delay_severity'] = np.where(
        df['delay_days'] == 0,  'On Time',
        np.where(df['delay_days'] <= 3,  'Minor Delay',
        np.where(df['delay_days'] <= 7,  'Moderate Delay',
                                         'Severe Delay'))
    )

    df.to_csv(f"{CLEAN}/shipments.csv", index=False)
    report("shipments", before, len(df), nulls, dups)
    return df

# ── 11. RETURNS ───────────────────────────────────────────────────────────────

def clean_returns():
    df     = pd.read_csv(f"{RAW}/returns.csv")
    before = len(df)
    dups   = df.duplicated(subset='return_id').sum()
    df     = df.drop_duplicates(subset='return_id')

    nulls = df.isnull().sum().sum()
    df['return_date']    = pd.to_datetime(df['return_date'])
    df['return_reason']  = df['return_reason'].str.strip().str.title()
    df['status']         = df['status'].str.strip().str.title()
    df['refund_amount']  = df['refund_amount'].fillna(0)

    df['return_month'] = df['return_date'].dt.to_period('M').astype(str)
    df['return_year']  = df['return_date'].dt.year

    df.to_csv(f"{CLEAN}/returns.csv", index=False)
    report("returns", before, len(df), nulls, dups)
    return df

# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 45)
    print("  OpsVista — Data Cleaning Pipeline")
    print("=" * 45)

    clean_categories()
    clean_products()
    clean_suppliers()
    clean_warehouses()
    clean_customers()
    clean_purchase_orders()
    clean_purchase_order_items()
    clean_inventory()
    clean_sales_orders()
    clean_shipments()
    clean_returns()

    print("\n" + "=" * 45)
    print("  All files saved to : ../data/clean/")
    print("  Cleaning complete.")
    print("=" * 45)

if __name__ == "__main__":
    main()