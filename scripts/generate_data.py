"""
OpsVista – Synthetic Data Generator
Generates 11 CSV files with realistic enterprise business patterns.
Author: Jasmine
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import os

fake = Faker('en_IN')
np.random.seed(42)
random.seed(42)

OUTPUT = "../data/raw"
os.makedirs(OUTPUT, exist_ok=True)

START_DATE = datetime(2022, 1, 1)
END_DATE   = datetime(2024, 12, 31)

REGIONS = ["North", "South", "East", "West", "Central"]

CATEGORIES = [
    "Raw Materials", "Packaging", "Electronics", "Chemicals",
    "Spare Parts", "Safety Equipment", "Office Supplies", "Machinery"
]

WAREHOUSE_NAMES = [
    "Delhi-WH1", "Mumbai-WH2", "Chennai-WH3", "Kolkata-WH4",
    "Hyderabad-WH5", "Pune-WH6", "Ahmedabad-WH7",
    "Bengaluru-WH8", "Jaipur-WH9", "Lucknow-WH10"
]

WAREHOUSE_REGIONS = [
    "North", "West", "South", "East", "South",
    "West", "West", "South", "North", "North"
]

SHIPMENT_PARTNERS = ["BlueDart", "DHL", "FedEx", "DTDC", "Delhivery", "Ekart"]

# ── HELPERS ───────────────────────────────────────────────────────────────────

def random_date(start, end):
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

def seasonal_multiplier(date):
    m = date.month
    if m in [10, 11, 12]: return 1.4
    if m in [7, 8, 9]:    return 1.1
    if m in [1, 2]:       return 0.85
    return 1.0

# ── 1. CATEGORIES ─────────────────────────────────────────────────────────────

def make_categories():
    rows = [{"category_id": i+1, "category_name": c} for i, c in enumerate(CATEGORIES)]
    df = pd.DataFrame(rows)
    df.to_csv(f"{OUTPUT}/categories.csv", index=False)
    print(f"  categories     : {len(df)} rows")
    return df

# ── 2. PRODUCTS ───────────────────────────────────────────────────────────────

PRODUCT_TEMPLATES = {
    "Raw Materials":    [("Steel Rods","KG"),("Aluminum Sheets","KG"),("Copper Wire","ROLL"),
                         ("Iron Ore","TON"),("Zinc Ingots","KG"),("Plastic Pellets","KG"),
                         ("Rubber Sheets","KG"),("Cotton Fabric","METER"),("Wood Planks","PIECE"),
                         ("Glass Panels","PIECE"),("Titanium Alloy","KG"),("Carbon Fiber","ROLL")],
    "Packaging":        [("Corrugated Boxes","PIECE"),("Bubble Wrap","ROLL"),("Stretch Film","ROLL"),
                         ("Packing Tape","ROLL"),("Foam Sheets","PIECE"),("Wooden Pallets","PIECE"),
                         ("HDPE Bags","PIECE"),("Kraft Paper","ROLL"),("Zip Lock Bags","PACK"),
                         ("Shrink Wrap","ROLL")],
    "Electronics":      [("Circuit Boards","PIECE"),("Resistors","PACK"),("Capacitors","PACK"),
                         ("LED Modules","PIECE"),("Sensors","PIECE"),("Microcontrollers","PIECE"),
                         ("Power Adapters","PIECE"),("Relay Switches","PIECE"),("Transformers","PIECE"),
                         ("Display Panels","PIECE")],
    "Chemicals":        [("Acetone","LITRE"),("Sulfuric Acid","LITRE"),("Isopropanol","LITRE"),
                         ("Sodium Hydroxide","KG"),("Ethanol","LITRE"),("Hydrochloric Acid","LITRE"),
                         ("Ammonia Solution","LITRE"),("Calcium Carbonate","KG")],
    "Spare Parts":      [("Bearings","PIECE"),("Drive Belts","PIECE"),("Hydraulic Seals","PIECE"),
                         ("Gear Sets","PIECE"),("Filter Elements","PIECE"),("O-Rings","PACK"),
                         ("Shaft Couplings","PIECE"),("Pump Impellers","PIECE")],
    "Safety Equipment": [("Safety Helmets","PIECE"),("Gloves","PAIR"),("Safety Goggles","PIECE"),
                         ("Ear Plugs","PACK"),("Safety Vests","PIECE"),("Fire Extinguishers","PIECE")],
    "Office Supplies":  [("Printer Paper","REAM"),("Pens","PACK"),("Notebooks","PIECE"),
                         ("Toner Cartridges","PIECE"),("Stapler","PIECE"),("Files","PACK")],
    "Machinery":        [("Industrial Pumps","PIECE"),("Conveyor Belts","METER"),("CNC Parts","SET"),
                         ("Welding Rods","KG"),("Lathe Tools","PIECE"),("Drill Bits","SET"),
                         ("Hydraulic Cylinders","PIECE"),("Pneumatic Valves","PIECE")]
}

VELOCITY = {
    "Raw Materials": "fast", "Packaging": "fast", "Electronics": "medium",
    "Chemicals": "medium", "Spare Parts": "medium", "Safety Equipment": "slow",
    "Office Supplies": "slow", "Machinery": "slow"
}

def make_products(cat_df):
    rows = []
    pid = 1
    for cat in CATEGORIES:
        templates = PRODUCT_TEMPLATES[cat]
        cid = cat_df[cat_df.category_name == cat].iloc[0].category_id
        velocity = VELOCITY[cat]
        for name, unit in templates:
            base_price = {
                "Raw Materials":    random.uniform(50, 500),
                "Packaging":        random.uniform(5, 100),
                "Electronics":      random.uniform(200, 5000),
                "Chemicals":        random.uniform(30, 300),
                "Spare Parts":      random.uniform(100, 2000),
                "Safety Equipment": random.uniform(50, 800),
                "Office Supplies":  random.uniform(10, 500),
                "Machinery":        random.uniform(5000, 80000)
            }[cat]
            reorder_point = {
                "fast":   random.randint(200, 500),
                "medium": random.randint(80, 200),
                "slow":   random.randint(20, 80)
            }[velocity]
            rows.append({
                "product_id":    pid,
                "product_name":  name,
                "category_id":   cid,
                "unit":          unit,
                "unit_price":    round(base_price, 2),
                "reorder_point": reorder_point,
                "velocity":      velocity,
                "is_active":     1
            })
            pid += 1
    df = pd.DataFrame(rows)
    df.to_csv(f"{OUTPUT}/products.csv", index=False)
    print(f"  products       : {len(df)} rows")
    return df

# ── 3. SUPPLIERS ──────────────────────────────────────────────────────────────

SUPPLIER_PROFILES = {
    "reliable": {"delay_rate": 0.05, "return_rate": 0.02, "lead_time_base": 7},
    "average":  {"delay_rate": 0.18, "return_rate": 0.06, "lead_time_base": 12},
    "poor":     {"delay_rate": 0.40, "return_rate": 0.12, "lead_time_base": 18}
}

SUPPLIER_NAMES = [
    "Tata Steel Supplies","Mahindra Materials","Infosys Components","HDFC Procurement",
    "Wipro Supplies","Reliance Raw Co","ONGC Industrials","Bajaj Components",
    "TVS Logistics","HUL Materials","ITC Supplies","Adani Resources",
    "Bharat Forge","Godrej Materials","L&T Components","Suzlon Parts",
    "JSW Supplies","Hindalco Metals","SAIL Distributors","GAIL Materials",
    "Motherson Parts","Bharat Electronics","HAL Components","BEL Supplies",
    "Siemens India","ABB Components","Bosch India Parts","Honeywell Supplies",
    "3M India","Cummins Components","Schneider Parts","Emerson India",
    "Eaton Components","Parker Hannifin India","SKF Bearings","Timken India",
    "Graco India","Atlas Copco Parts","Sandvik India","Kennametal India",
    "Dormer Tools","Seco Tools India","Iscar India","Walter India",
    "Mitsubishi Materials","Sumitomo India","Kyocera India","Nachi India",
    "OSG India","Tungaloy India","Mapal India","Guhring India",
    "YG-1 India","Korloy India","Taegutec India","Ingersoll India",
    "Stellram India","Vardex India","Carmex India","Vargus India",
    "Horn India","Pramet India","Ceratizit India","Sintercast India",
    "Palbit India","Promax India","Sherwood India","Omega Supplies",
    "Sigma Materials","Delta Components","Apex Industrials","Prime Parts",
    "Global Supplies","National Materials","United Components","Metro Parts",
    "City Supplies","Fast Track Materials","Swift Components","Eagle Parts"
]

def make_suppliers():
    rows = []
    profile_choices = ["reliable"]*28 + ["average"]*32 + ["poor"]*20
    random.shuffle(profile_choices)
    for i, name in enumerate(SUPPLIER_NAMES):
        pk = profile_choices[i]
        p  = SUPPLIER_PROFILES[pk]
        rows.append({
            "supplier_id":        i + 1,
            "supplier_name":      name,
            "contact_email":      fake.email(),
            "phone":              fake.phone_number(),
            "city":               fake.city(),
            "region":             random.choice(REGIONS),
            "profile":            pk,
            "avg_lead_time_days": p["lead_time_base"] + random.randint(-2, 5),
            "delay_rate":         round(p["delay_rate"] + random.uniform(-0.02, 0.04), 3),
            "return_rate":        round(p["return_rate"] + random.uniform(-0.01, 0.03), 3),
            "is_active":          1
        })
    df = pd.DataFrame(rows)
    df.to_csv(f"{OUTPUT}/suppliers.csv", index=False)
    print(f"  suppliers      : {len(df)} rows")
    return df

# ── 4. WAREHOUSES ─────────────────────────────────────────────────────────────

def make_warehouses():
    rows = []
    for i, name in enumerate(WAREHOUSE_NAMES):
        capacity = random.choice([5000, 8000, 10000, 12000, 15000])
        rows.append({
            "warehouse_id":   i + 1,
            "warehouse_name": name,
            "region":         WAREHOUSE_REGIONS[i],
            "city":           name.split("-")[0],
            "capacity_units": capacity,
            "manager":        fake.name(),
            "is_active":      1
        })
    df = pd.DataFrame(rows)
    df.to_csv(f"{OUTPUT}/warehouses.csv", index=False)
    print(f"  warehouses     : {len(df)} rows")
    return df

# ── 5. CUSTOMERS ──────────────────────────────────────────────────────────────

def make_customers():
    rows = []
    for i in range(600):
        rows.append({
            "customer_id":     i + 1,
            "customer_name":   fake.company(),
            "contact_person":  fake.name(),
            "email":           fake.email(),
            "phone":           fake.phone_number(),
            "city":            fake.city(),
            "region":          random.choice(REGIONS),
            "customer_type":   random.choice(["Distributor","Retailer","Manufacturer","Direct"])
        })
    df = pd.DataFrame(rows)
    df.to_csv(f"{OUTPUT}/customers.csv", index=False)
    print(f"  customers      : {len(df)} rows")
    return df

# ── 6. PURCHASE ORDERS ────────────────────────────────────────────────────────

def make_purchase_orders(supplier_df, product_df, warehouse_df):
    po_rows  = []
    poi_rows = []
    po_id  = 1
    poi_id = 1

    for _ in range(6000):
        supplier  = supplier_df.sample(1).iloc[0]
        warehouse = warehouse_df.sample(1).iloc[0]
        order_date = random_date(START_DATE, END_DATE)

        lead_days = int(supplier.avg_lead_time_days * random.uniform(0.7, 1.8))
        if supplier.profile == "poor" and random.random() < 0.35:
            lead_days = int(lead_days * random.uniform(1.5, 2.5))

        expected_date = order_date + timedelta(days=lead_days)
        is_delayed    = random.random() < supplier.delay_rate
        actual_days   = lead_days + (random.randint(3,15) if is_delayed else random.randint(-1,2))
        actual_date   = order_date + timedelta(days=max(actual_days, 1))
        status        = "Delivered" if actual_date <= END_DATE else "Pending"

        cost_factor  = seasonal_multiplier(order_date) * random.uniform(0.95, 1.10)
        num_items    = random.randint(1, 5)
        total_amount = 0.0

        for _ in range(num_items):
            prod      = product_df.sample(1).iloc[0]
            qty       = random.randint(50, 1000)
            unit_cost = round(prod.unit_price * cost_factor, 2)
            line_total = round(qty * unit_cost, 2)
            total_amount += line_total
            poi_rows.append({
                "poi_id":           poi_id,
                "po_id":            po_id,
                "product_id":       int(prod.product_id),
                "quantity_ordered": qty,
                "unit_cost":        unit_cost,
                "line_total":       line_total
            })
            poi_id += 1

        po_rows.append({
            "po_id":                  po_id,
            "supplier_id":            int(supplier.supplier_id),
            "warehouse_id":           int(warehouse.warehouse_id),
            "order_date":             order_date.date(),
            "expected_delivery_date": expected_date.date(),
            "actual_delivery_date":   actual_date.date() if status == "Delivered" else None,
            "status":                 status,
            "is_delayed":             int(is_delayed),
            "total_amount":           round(total_amount, 2),
            "payment_terms":          random.choice(["Net30","Net60","Net90","Immediate"])
        })
        po_id += 1

    po_df  = pd.DataFrame(po_rows)
    poi_df = pd.DataFrame(poi_rows)
    po_df.to_csv(f"{OUTPUT}/purchase_orders.csv",      index=False)
    poi_df.to_csv(f"{OUTPUT}/purchase_order_items.csv", index=False)
    print(f"  purchase_orders      : {len(po_df)} rows")
    print(f"  purchase_order_items : {len(poi_df)} rows")
    return po_df, poi_df

# ── 7. INVENTORY ──────────────────────────────────────────────────────────────

def make_inventory(product_df, warehouse_df):
    rows = []
    inv_id = 1
    for _, wh in warehouse_df.iterrows():
        sampled = product_df.sample(frac=0.6, random_state=int(wh.warehouse_id))
        for _, prod in sampled.iterrows():
            qty = {
                "fast":   random.randint(500, 3000),
                "medium": random.randint(100, 800),
                "slow":   random.randint(10, 200)
            }[prod.velocity]
            if random.random() < 0.05:  qty = 0           # stockout
            if random.random() < 0.10:  qty = qty * random.randint(3, 6)  # overstock

            last_updated = random_date(datetime(2024, 1, 1), END_DATE)
            rows.append({
                "inventory_id":    inv_id,
                "product_id":      int(prod.product_id),
                "warehouse_id":    int(wh.warehouse_id),
                "quantity_on_hand": qty,
                "reorder_point":   int(prod.reorder_point),
                "last_updated":    last_updated.date(),
                "inventory_age_days": (END_DATE - last_updated).days
            })
            inv_id += 1
    df = pd.DataFrame(rows)
    df.to_csv(f"{OUTPUT}/inventory.csv", index=False)
    print(f"  inventory      : {len(df)} rows")
    return df

# ── 8. SALES ORDERS ───────────────────────────────────────────────────────────

def make_sales_orders(customer_df, product_df, warehouse_df):
    rows = []
    oid = 1
    fast   = product_df[product_df.velocity == "fast"]
    medium = product_df[product_df.velocity == "medium"]
    slow   = product_df[product_df.velocity == "slow"]

    for _ in range(12000):
        cust       = customer_df.sample(1).iloc[0]
        order_date = random_date(START_DATE, END_DATE)
        wh         = warehouse_df.sample(1).iloc[0]

        r = random.random()
        if r < 0.60:   prod = fast.sample(1).iloc[0]
        elif r < 0.85: prod = medium.sample(1).iloc[0]
        else:          prod = slow.sample(1).iloc[0]

        qty        = int(random.randint(10, 200) * seasonal_multiplier(order_date))
        unit_price = round(prod.unit_price * random.uniform(1.10, 1.30), 2)
        status     = random.choices(["Delivered","Processing","Cancelled"], [0.80, 0.15, 0.05])[0]

        rows.append({
            "order_id":     oid,
            "customer_id":  int(cust.customer_id),
            "product_id":   int(prod.product_id),
            "warehouse_id": int(wh.warehouse_id),
            "order_date":   order_date.date(),
            "quantity":     qty,
            "unit_price":   unit_price,
            "total_amount": round(qty * unit_price, 2),
            "status":       status,
            "region":       cust.region
        })
        oid += 1

    df = pd.DataFrame(rows)
    df.to_csv(f"{OUTPUT}/sales_orders.csv", index=False)
    print(f"  sales_orders   : {len(df)} rows")
    return df

# ── 9. SHIPMENTS ──────────────────────────────────────────────────────────────

def make_shipments(sales_df, warehouse_df):
    rows = []
    sid = 1
    delivered = sales_df[sales_df.status == "Delivered"]

    REGION_DELAY = {
        "North": 0.15, "South": 0.12, "East": 0.25,
        "West": 0.13,  "Central": 0.20
    }

    for _, order in delivered.iterrows():
        delay_prob = REGION_DELAY.get(order.region, 0.15)
        is_delayed = random.random() < delay_prob
        ship_date  = pd.to_datetime(order.order_date) + timedelta(days=random.randint(1, 3))
        transit    = random.randint(3, 12) + (random.randint(3, 10) if is_delayed else 0)

        rows.append({
            "shipment_id":            sid,
            "order_id":               int(order.order_id),
            "warehouse_id":           int(order.warehouse_id),
            "shipment_partner":       random.choice(SHIPMENT_PARTNERS),
            "ship_date":              ship_date.date(),
            "expected_delivery_date": (ship_date + timedelta(days=random.randint(3,10))).date(),
            "actual_delivery_date":   (ship_date + timedelta(days=transit)).date(),
            "is_delayed":             int(is_delayed),
            "transit_days":           transit,
            "destination_region":     order.region,
            "shipment_status":        "Delivered",
            "vehicle_type":           random.choice(["Truck","Van","Air","Rail"])
        })
        sid += 1

    df = pd.DataFrame(rows)
    df.to_csv(f"{OUTPUT}/shipments.csv", index=False)
    print(f"  shipments      : {len(df)} rows")
    return df

# ── 10. RETURNS ───────────────────────────────────────────────────────────────

def make_returns(sales_df):
    rows = []
    rid = 1
    delivered    = sales_df[sales_df.status == "Delivered"]
    return_sample = delivered.sample(frac=0.07, random_state=42)

    REASONS = [
        "Defective Product", "Wrong Item", "Damaged in Transit",
        "Quality Issue", "Overstock Return", "Expired Product"
    ]

    for _, order in return_sample.iterrows():
        return_date = pd.to_datetime(order.order_date) + timedelta(days=random.randint(10, 45))
        qty = random.randint(1, max(1, int(order.quantity * 0.5)))
        rows.append({
            "return_id":        rid,
            "order_id":         int(order.order_id),
            "product_id":       int(order.product_id),
            "return_date":      return_date.date(),
            "quantity_returned": qty,
            "return_reason":    random.choice(REASONS),
            "refund_amount":    round(qty * order.unit_price, 2),
            "status":           random.choice(["Processed","Pending","Rejected"])
        })
        rid += 1

    df = pd.DataFrame(rows)
    df.to_csv(f"{OUTPUT}/returns.csv", index=False)
    print(f"  returns        : {len(df)} rows")
    return df

# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 45)
    print("  OpsVista — Synthetic Data Generator")
    print("=" * 45)

    cat_df          = make_categories()
    prod_df         = make_products(cat_df)
    sup_df          = make_suppliers()
    wh_df           = make_warehouses()
    cust_df         = make_customers()
    po_df, poi_df   = make_purchase_orders(sup_df, prod_df, wh_df)
    inv_df          = make_inventory(prod_df, wh_df)
    sales_df        = make_sales_orders(cust_df, prod_df, wh_df)
    ship_df         = make_shipments(sales_df, wh_df)
    ret_df          = make_returns(sales_df)

    total = sum([len(cat_df), len(prod_df), len(sup_df), len(wh_df),
                 len(cust_df), len(po_df), len(poi_df), len(inv_df),
                 len(sales_df), len(ship_df), len(ret_df)])

    print("=" * 45)
    print(f"  Total rows generated : {total:,}")
    print(f"  Files saved to       : {OUTPUT}")
    print("=" * 45)

if __name__ == "__main__":
    main()