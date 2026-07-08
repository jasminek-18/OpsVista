"""
OpsVista – Predictive Analytics
1. Vendor Risk Score (weighted formula)
2. Inventory Reorder Prediction (days of stock)
3. AI Recommendation Engine (business rules)
Author: Jasmine
"""

import pandas as pd
import numpy as np
import os

CLEAN  = "../data/clean"
OUTPUT = "../predictive"
os.makedirs(OUTPUT, exist_ok=True)

po   = pd.read_csv(f"{CLEAN}/purchase_orders.csv")
sup  = pd.read_csv(f"{CLEAN}/suppliers.csv")
inv  = pd.read_csv(f"{CLEAN}/inventory.csv")
prod = pd.read_csv(f"{CLEAN}/products.csv")
wh   = pd.read_csv(f"{CLEAN}/warehouses.csv")
ship = pd.read_csv(f"{CLEAN}/shipments.csv")

print("=" * 50)
print("  OpsVista — Predictive Analytics Engine")
print("=" * 50)

# ════════════════════════════════════════════
# MODEL 1 — VENDOR RISK SCORE
# Formula: 50% delay rate + 30% return rate + 20% lead time score
# Score range: 0 (safe) to 100 (very risky)
# ════════════════════════════════════════════

sup_stats = po.merge(
    sup[['supplier_id','supplier_name','delay_rate','return_rate',
         'avg_lead_time_days','profile','supplier_tier']],
    on='supplier_id'
)

vendor_risk = sup_stats.groupby(
    ['supplier_id','supplier_name','delay_rate','return_rate',
     'avg_lead_time_days','profile','supplier_tier']
).agg(
    total_orders=('po_id','count'),
    actual_delay_rate=('is_delayed','mean'),
    avg_actual_lead=('lead_days','mean'),
    total_spend=('total_amount','sum')
).reset_index()

# normalize lead time to 0–100 scale (max 30 days = 100)
vendor_risk['lead_score'] = (
    vendor_risk['avg_actual_lead'] / 30 * 100
).clip(0, 100)

# weighted risk score
vendor_risk['risk_score'] = (
    vendor_risk['actual_delay_rate'] * 50 +
    vendor_risk['return_rate']        * 30 +
    vendor_risk['lead_score']         * 0.20
).clip(0, 100).round(2)

# risk category
vendor_risk['risk_category'] = pd.cut(
    vendor_risk['risk_score'],
    bins=[-1, 30, 60, 100],
    labels=['Low Risk', 'Medium Risk', 'High Risk']
)

# recommended action
def vendor_action(row):
    if row['risk_score'] >= 60:
        return "Immediate SLA review. Identify backup supplier."
    elif row['risk_score'] >= 30:
        return "Monitor closely. Set delay penalty clauses."
    else:
        return "Continue. Preferred vendor for critical SKUs."

vendor_risk['recommended_action'] = vendor_risk.apply(vendor_action, axis=1)

vendor_risk = vendor_risk.sort_values('risk_score', ascending=False)
vendor_risk.to_csv(f"{OUTPUT}/vendor_risk_scores.csv", index=False)
print(f"\n  [Model 1] Vendor Risk Scores")
print(f"    High Risk  : {(vendor_risk.risk_category=='High Risk').sum()} vendors")
print(f"    Medium Risk: {(vendor_risk.risk_category=='Medium Risk').sum()} vendors")
print(f"    Low Risk   : {(vendor_risk.risk_category=='Low Risk').sum()} vendors")
print(f"    Saved      : vendor_risk_scores.csv")

# ════════════════════════════════════════════
# MODEL 2 — INVENTORY REORDER PREDICTION
# Logic: days_of_stock_left < supplier lead time → predict reorder needed
# ════════════════════════════════════════════

inv_pred = inv.merge(prod[['product_id','product_name','velocity','unit_price']], on='product_id')
inv_pred = inv_pred.merge(wh[['warehouse_id','warehouse_name']], on='warehouse_id')

# avg lead time across all suppliers
avg_lead = po['lead_days'].mean()

inv_pred['reorder_predicted'] = (
    inv_pred['days_of_stock_left'] < avg_lead
).astype(int)

inv_pred['urgency'] = np.where(
    inv_pred['quantity_on_hand'] == 0, 'Critical — Stock Out',
    np.where(inv_pred['days_of_stock_left'] < 7,  'High — &lt;7 days',
    np.where(inv_pred['days_of_stock_left'] < 20, 'Medium — &lt;20 days',
                                                   'Low'))
)

inv_pred['suggested_order_qty'] = np.where(
    inv_pred['reorder_predicted'] == 1,
    (inv_pred['reorder_point'] * 2).astype(int),
    0
)

reorder_output = inv_pred[[
    'product_id','product_name','warehouse_name','velocity',
    'quantity_on_hand','reorder_point','days_of_stock_left',
    'reorder_predicted','urgency','suggested_order_qty','unit_price'
]].sort_values('days_of_stock_left')

reorder_output.to_csv(f"{OUTPUT}/reorder_predictions.csv", index=False)
print(f"\n  [Model 2] Inventory Reorder Prediction")
print(f"    Items needing reorder : {reorder_output['reorder_predicted'].sum()}")
print(f"    Critical (stock-out)  : {(reorder_output['urgency']=='Critical — Stock Out').sum()}")
print(f"    Saved                 : reorder_predictions.csv")

# ════════════════════════════════════════════
# MODEL 3 — AI RECOMMENDATION ENGINE
# Pure business rules — generates action cards
# ════════════════════════════════════════════

recommendations = []

# Rule 1: high risk vendors
high_risk = vendor_risk[vendor_risk['risk_category'] == 'High Risk']
if len(high_risk) > 0:
    recommendations.append({
        "priority":    "HIGH",
        "area":        "Supplier Management",
        "finding":     f"{len(high_risk)} vendors have risk score > 60",
        "action":      "Initiate SLA review within 14 days. Apply penalty clauses.",
        "impact":      "Reduce procurement delays by estimated 15–20%"
    })

# Rule 2: stockout products
stockouts = inv_pred[inv_pred['quantity_on_hand'] == 0]
if len(stockouts) > 0:
    recommendations.append({
        "priority":    "CRITICAL",
        "area":        "Inventory Management",
        "finding":     f"{len(stockouts)} SKUs are completely out of stock",
        "action":      "Raise emergency purchase orders immediately.",
        "impact":      "Prevent production line stoppage"
    })

# Rule 3: overcrowded warehouses
wh_util = inv.groupby('warehouse_id')['quantity_on_hand'].sum().reset_index()
wh_util = wh_util.merge(wh[['warehouse_id','warehouse_name','capacity_units']], on='warehouse_id')
wh_util['util_pct'] = wh_util['quantity_on_hand'] / wh_util['capacity_units'] * 100
overcrowded = wh_util[wh_util['util_pct'] > 90]
if len(overcrowded) > 0:
    wh_names = ", ".join(overcrowded['warehouse_name'].tolist())
    recommendations.append({
        "priority":    "HIGH",
        "area":        "Warehouse Operations",
        "finding":     f"{len(overcrowded)} warehouses above 90% capacity: {wh_names}",
        "action":      "Redistribute inventory to low-utilization warehouses immediately.",
        "impact":      "Prevent receiving delays and warehouse congestion"
    })

# Rule 4: high shipment delay regions
region_delay = ship.groupby('destination_region')['is_delayed'].mean() * 100
high_delay_regions = region_delay[region_delay > 20].index.tolist()
if high_delay_regions:
    recommendations.append({
        "priority":    "MEDIUM",
        "area":        "Logistics",
        "finding":     f"Regions {high_delay_regions} have delay rate > 20%",
        "action":      "Migrate shipments to BlueDart/DHL. Renegotiate Ekart SLA.",
        "impact":      "Improve customer on-time delivery by 8–12%"
    })

# Rule 5: return rate check
total_delivered = len(pd.read_csv(f"{CLEAN}/sales_orders.csv").query("status=='Delivered'"))
total_returns   = len(pd.read_csv(f"{CLEAN}/returns.csv"))
ret_rate = total_returns / total_delivered * 100
if ret_rate > 5:
    recommendations.append({
        "priority":    "MEDIUM",
        "area":        "Quality Control",
        "finding":     f"Overall return rate is {ret_rate:.1f}% (threshold: 5%)",
        "action":      "Conduct supplier quality audit for top return-generating vendors.",
        "impact":      "Reduce refund costs and improve customer satisfaction"
    })

rec_df = pd.DataFrame(recommendations)
rec_df.to_csv(f"{OUTPUT}/ai_recommendations.csv", index=False)

print(f"\n  [Model 3] AI Recommendation Engine")
for _, row in rec_df.iterrows():
    print(f"    [{row['priority']}] {row['area']}: {row['finding']}")
print(f"    Saved: ai_recommendations.csv")

print("\n" + "=" * 50)
print("  Predictive analytics complete.")
print("  Check the predictive/ folder for output CSVs.")
print("=" * 50)