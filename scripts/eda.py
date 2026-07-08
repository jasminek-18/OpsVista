"""
OpsVista – Exploratory Data Analysis
Generates 10 business charts saved as PNG files.
Author: Jasmine
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

CLEAN  = "../data/clean"
OUTPUT = "../eda_charts"
os.makedirs(OUTPUT, exist_ok=True)

# ── STYLE ─────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor":  "#0d1117",
    "axes.facecolor":    "#161b22",
    "axes.edgecolor":    "#30363d",
    "axes.labelcolor":   "#8b949e",
    "xtick.color":       "#8b949e",
    "ytick.color":       "#8b949e",
    "text.color":        "#e6edf3",
    "grid.color":        "#21262d",
    "grid.linestyle":    "--",
    "grid.alpha":        0.6,
    "font.family":       "sans-serif",
    "axes.titlesize":    13,
    "axes.labelsize":    11,
    "xtick.labelsize":   9,
    "ytick.labelsize":   9,
})

COLORS = ["#388bfd","#3fb950","#d29922","#f85149","#a371f7","#fb8f44","#39d3f2","#ff7b72"]

def save(name):
    plt.tight_layout()
    plt.savefig(f"{OUTPUT}/{name}.png", dpi=150, bbox_inches='tight',
                facecolor="#0d1117")
    plt.close()
    print(f"  Saved: {name}.png")

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
po   = pd.read_csv(f"{CLEAN}/purchase_orders.csv")
sup  = pd.read_csv(f"{CLEAN}/suppliers.csv")
inv  = pd.read_csv(f"{CLEAN}/inventory.csv")
wh   = pd.read_csv(f"{CLEAN}/warehouses.csv")
prod = pd.read_csv(f"{CLEAN}/products.csv")
cat  = pd.read_csv(f"{CLEAN}/categories.csv")
so   = pd.read_csv(f"{CLEAN}/sales_orders.csv")
ship = pd.read_csv(f"{CLEAN}/shipments.csv")
ret  = pd.read_csv(f"{CLEAN}/returns.csv")

print("=" * 45)
print("  OpsVista — EDA Chart Generation")
print("=" * 45)

# ── CHART 1: Monthly Procurement Cost ─────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 4))
monthly = po.groupby('order_month')['total_amount'].sum() / 1e7
monthly.plot(ax=ax, color=COLORS[0], linewidth=2, marker='o', markersize=3)
ax.set_title("Monthly Procurement Cost (₹ Cr)")
ax.set_xlabel("Month")
ax.set_ylabel("Cost (₹ Cr)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"₹{x:.0f}Cr"))
ax.grid(True)
save("01_monthly_procurement")

# ── CHART 2: Supplier Delay Rate by Profile ───────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 4))
sup_delay = po.merge(sup[['supplier_id','profile']], on='supplier_id')
delay_by_profile = sup_delay.groupby('profile')['is_delayed'].mean() * 100
bars = ax.bar(delay_by_profile.index, delay_by_profile.values,
              color=[COLORS[1], COLORS[2], COLORS[3]], width=0.5, edgecolor='none')
ax.bar_label(bars, fmt='%.1f%%', color='#e6edf3', padding=4, fontsize=10)
ax.set_title("Avg Delay Rate by Supplier Profile (%)")
ax.set_ylabel("Delay Rate (%)")
ax.grid(True, axis='y')
save("02_supplier_delay_profile")

# ── CHART 3: Warehouse Utilization ────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 4))
wh_stock = inv.groupby('warehouse_id')['quantity_on_hand'].sum().reset_index()
wh_merged = wh_stock.merge(wh[['warehouse_id','warehouse_name','capacity_units']], on='warehouse_id')
wh_merged['util'] = (wh_merged['quantity_on_hand'] / wh_merged['capacity_units'] * 100).clip(0,100)
wh_merged = wh_merged.sort_values('util', ascending=True)
colors = [COLORS[3] if u > 90 else COLORS[2] if u > 75 else COLORS[1] for u in wh_merged['util']]
bars = ax.barh(wh_merged['warehouse_name'], wh_merged['util'], color=colors, edgecolor='none')
ax.bar_label(bars, fmt='%.1f%%', color='#e6edf3', padding=4, fontsize=9)
ax.set_title("Warehouse Capacity Utilization (%)")
ax.set_xlabel("Utilization (%)")
ax.set_xlim(0, 115)
ax.grid(True, axis='x')
save("03_warehouse_utilization")

# ── CHART 4: Category Spend (Pie) ─────────────────────────────────────────────
poi  = pd.read_csv(f"{CLEAN}/purchase_order_items.csv")
poi_cat = poi.merge(prod[['product_id','category_id']], on='product_id')
poi_cat = poi_cat.merge(cat, on='category_id')
cat_spend = poi_cat.groupby('category_name')['line_total'].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(7, 5))
wedges, texts, autotexts = ax.pie(
    cat_spend.values, labels=cat_spend.index,
    autopct='%1.1f%%', colors=COLORS,
    startangle=140, pctdistance=0.75,
    wedgeprops=dict(edgecolor='#0d1117', linewidth=1.5)
)
for t in autotexts: t.set_color('#e6edf3'); t.set_fontsize(8)
for t in texts:     t.set_color('#8b949e'); t.set_fontsize(8)
ax.set_title("Procurement Spend by Category")
save("04_category_spend")

# ── CHART 5: Stock Status Distribution ────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 4))
stock_counts = inv['stock_status'].value_counts()
bar_colors = {'Healthy':COLORS[1],'Low Stock':COLORS[2],'Stock-Out':COLORS[3],'Overstock':COLORS[4]}
colors_list = [bar_colors.get(s, COLORS[0]) for s in stock_counts.index]
bars = ax.bar(stock_counts.index, stock_counts.values, color=colors_list, edgecolor='none', width=0.5)
ax.bar_label(bars, color='#e6edf3', padding=4, fontsize=10)
ax.set_title("Inventory Stock Status Distribution")
ax.set_ylabel("Number of SKUs")
ax.grid(True, axis='y')
save("05_stock_status")

# ── CHART 6: Shipment Delay by Region ─────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 4))
region_delay = ship.groupby('destination_region')['is_delayed'].mean() * 100
region_delay = region_delay.sort_values(ascending=False)
bar_cols = [COLORS[3] if v >= 22 else COLORS[2] if v >= 16 else COLORS[1] for v in region_delay.values]
bars = ax.bar(region_delay.index, region_delay.values, color=bar_cols, edgecolor='none', width=0.5)
ax.bar_label(bars, fmt='%.1f%%', color='#e6edf3', padding=4, fontsize=10)
ax.set_title("Shipment Delay Rate by Region (%)")
ax.set_ylabel("Delay Rate (%)")
ax.set_ylim(0, 32)
ax.grid(True, axis='y')
save("06_shipment_delay_region")

# ── CHART 7: Monthly Sales Revenue ────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 4))
delivered = so[so['status'] == 'Delivered']
monthly_sales = delivered.groupby('order_month')['total_amount'].sum() / 1e7
monthly_sales.plot(ax=ax, color=COLORS[1], linewidth=2, marker='o', markersize=3)
ax.set_title("Monthly Sales Revenue (₹ Cr)")
ax.set_xlabel("Month")
ax.set_ylabel("Revenue (₹ Cr)")
ax.grid(True)
save("07_monthly_sales")

# ── CHART 8: Top 10 Suppliers by Spend ────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
sup_spend = po.merge(sup[['supplier_id','supplier_name']], on='supplier_id')
top_sup = sup_spend.groupby('supplier_name')['total_amount'].sum().sort_values(ascending=True).tail(10) / 1e7
bars = ax.barh(top_sup.index, top_sup.values, color=COLORS[0], edgecolor='none')
ax.bar_label(bars, fmt='₹%.1fCr', color='#e6edf3', padding=4, fontsize=9)
ax.set_title("Top 10 Suppliers by Procurement Spend")
ax.set_xlabel("Spend (₹ Cr)")
ax.grid(True, axis='x')
save("08_top_suppliers_spend")

# ── CHART 9: Return Reasons ────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 4))
ret_reasons = ret['return_reason'].value_counts()
bars = ax.barh(ret_reasons.index, ret_reasons.values, color=COLORS[4], edgecolor='none')
ax.bar_label(bars, color='#e6edf3', padding=4, fontsize=9)
ax.set_title("Returns by Reason")
ax.set_xlabel("Return Count")
ax.grid(True, axis='x')
save("09_return_reasons")

# ── CHART 10: Delay Severity Distribution ─────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 4))
sev = ship['delay_severity'].value_counts()
sev_colors = {'On Time':COLORS[1],'Minor Delay':COLORS[2],'Moderate Delay':COLORS[2],'Severe Delay':COLORS[3]}
colors_list = [sev_colors.get(s, COLORS[0]) for s in sev.index]
bars = ax.bar(sev.index, sev.values, color=colors_list, edgecolor='none', width=0.5)
ax.bar_label(bars, color='#e6edf3', padding=4, fontsize=10)
ax.set_title("Shipment Delay Severity Distribution")
ax.set_ylabel("Number of Shipments")
ax.grid(True, axis='y')
save("10_delay_severity")

print("=" * 45)
print(f"  All 10 charts saved to: {OUTPUT}")
print("=" * 45)