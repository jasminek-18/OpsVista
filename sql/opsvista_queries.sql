USE opsvista;

-- ════════════════════════════════════════════
-- SECTION A — PROCUREMENT ANALYSIS
-- ════════════════════════════════════════════

-- Q1. Total procurement cost per year
SELECT
    order_year,
    COUNT(po_id)              AS total_orders,
    ROUND(SUM(total_amount)/1e7, 2) AS total_cost_cr
FROM purchase_orders
GROUP BY order_year
ORDER BY order_year;

-- Q2. Monthly procurement trend
SELECT
    order_month,
    COUNT(po_id)                    AS orders,
    ROUND(SUM(total_amount)/1e7, 2) AS cost_cr
FROM purchase_orders
GROUP BY order_month
ORDER BY order_month;

-- Q3. Top 10 most expensive purchase orders
SELECT
    po_id,
    supplier_id,
    order_date,
    ROUND(total_amount/1e7, 2) AS cost_cr,
    status
FROM purchase_orders
ORDER BY total_amount DESC
LIMIT 10;

-- Q4. Procurement cost by payment terms
SELECT
    payment_terms,
    COUNT(po_id)                    AS orders,
    ROUND(SUM(total_amount)/1e7, 2) AS total_cost_cr
FROM purchase_orders
GROUP BY payment_terms
ORDER BY total_cost_cr DESC;

-- Q5. Running total of procurement cost by month
SELECT
    order_month,
    ROUND(SUM(total_amount)/1e7, 2) AS monthly_cost_cr,
    ROUND(SUM(SUM(total_amount)) OVER (ORDER BY order_month)/1e7, 2) AS running_total_cr
FROM purchase_orders
GROUP BY order_month
ORDER BY order_month;

-- ════════════════════════════════════════════
-- SECTION B — SUPPLIER PERFORMANCE
-- ════════════════════════════════════════════

-- Q6. Supplier delay rate ranking
SELECT
    s.supplier_id,
    s.supplier_name,
    s.profile,
    COUNT(po.po_id)                              AS total_orders,
    SUM(po.is_delayed)                           AS delayed_orders,
    ROUND(SUM(po.is_delayed)/COUNT(po.po_id)*100, 1) AS delay_pct,
    ROUND(AVG(po.lead_days), 1)                  AS avg_lead_days
FROM suppliers s
JOIN purchase_orders po ON s.supplier_id = po.supplier_id
GROUP BY s.supplier_id, s.supplier_name, s.profile
ORDER BY delay_pct DESC;

-- Q7. Top 10 suppliers by total spend
SELECT
    s.supplier_name,
    s.profile,
    COUNT(po.po_id)                    AS orders,
    ROUND(SUM(po.total_amount)/1e7, 2) AS spend_cr
FROM suppliers s
JOIN purchase_orders po ON s.supplier_id = po.supplier_id
GROUP BY s.supplier_id, s.supplier_name, s.profile
ORDER BY spend_cr DESC
LIMIT 10;

-- Q8. Supplier performance score (weighted)
SELECT
    s.supplier_name,
    s.profile,
    ROUND(AVG(po.lead_days), 1) AS avg_lead,
    ROUND(SUM(po.is_delayed)/COUNT(*)*100, 1) AS delay_pct,
    ROUND(
        100
        - (SUM(po.is_delayed)/COUNT(*)*100 * 1.5)
        - ((AVG(po.lead_days) - 7) * 0.5)
    , 1) AS performance_score
FROM suppliers s
JOIN purchase_orders po ON s.supplier_id = po.supplier_id
GROUP BY s.supplier_id, s.supplier_name, s.profile
ORDER BY performance_score DESC;

-- Q9. Suppliers with delay rate above 30% (high risk)
SELECT
    s.supplier_name,
    s.region,
    ROUND(SUM(po.is_delayed)/COUNT(*)*100, 1) AS delay_pct,
    COUNT(*) AS total_orders
FROM suppliers s
JOIN purchase_orders po ON s.supplier_id = po.supplier_id
GROUP BY s.supplier_id, s.supplier_name, s.region
HAVING delay_pct > 30
ORDER BY delay_pct DESC;

-- Q10. Supplier rank by delay using RANK()
SELECT
    supplier_name,
    delay_pct,
    RANK() OVER (ORDER BY delay_pct DESC) AS delay_rank
FROM (
    SELECT
        s.supplier_name,
        ROUND(SUM(po.is_delayed)/COUNT(*)*100, 1) AS delay_pct
    FROM suppliers s
    JOIN purchase_orders po ON s.supplier_id = po.supplier_id
    GROUP BY s.supplier_id, s.supplier_name
) ranked;

-- Q11. Month-over-month procurement change per supplier
SELECT
    s.supplier_name,
    po.order_month,
    ROUND(SUM(po.total_amount)/1e7, 2) AS monthly_spend_cr,
    ROUND(LAG(SUM(po.total_amount)) OVER (
        PARTITION BY s.supplier_name ORDER BY po.order_month
    )/1e7, 2) AS prev_month_cr
FROM suppliers s
JOIN purchase_orders po ON s.supplier_id = po.supplier_id
GROUP BY s.supplier_name, po.order_month
ORDER BY s.supplier_name, po.order_month;

-- Q12. Average delay days by supplier profile
SELECT
    profile,
    ROUND(AVG(delay_days), 1) AS avg_delay_days,
    ROUND(AVG(lead_days), 1)  AS avg_lead_days,
    COUNT(*)                  AS total_orders
FROM purchase_orders po
JOIN suppliers s ON po.supplier_id = s.supplier_id
GROUP BY profile;

-- ════════════════════════════════════════════
-- SECTION C — INVENTORY ANALYSIS
-- ════════════════════════════════════════════

-- Q13. Current stock status summary
SELECT
    stock_status,
    COUNT(*) AS sku_count
FROM inventory
GROUP BY stock_status
ORDER BY sku_count DESC;

-- Q14. Products with zero stock (stock-outs)
SELECT
    p.product_name,
    p.velocity,
    w.warehouse_name,
    i.quantity_on_hand,
    i.reorder_point
FROM inventory i
JOIN products  p ON i.product_id   = p.product_id
JOIN warehouses w ON i.warehouse_id = w.warehouse_id
WHERE i.quantity_on_hand = 0
ORDER BY p.velocity DESC;

-- Q15. Products below reorder point
SELECT
    p.product_name,
    p.velocity,
    i.quantity_on_hand,
    i.reorder_point,
    i.days_of_stock_left,
    w.warehouse_name
FROM inventory i
JOIN products   p ON i.product_id   = p.product_id
JOIN warehouses w ON i.warehouse_id = w.warehouse_id
WHERE i.reorder_flag = 1
ORDER BY i.days_of_stock_left ASC;

-- Q16. Warehouse utilization
SELECT
    w.warehouse_name,
    w.region,
    w.capacity_units,
    SUM(i.quantity_on_hand)                              AS stock_on_hand,
    ROUND(SUM(i.quantity_on_hand)/w.capacity_units*100, 1) AS utilization_pct
FROM inventory  i
JOIN warehouses w ON i.warehouse_id = w.warehouse_id
GROUP BY w.warehouse_id, w.warehouse_name, w.region, w.capacity_units
ORDER BY utilization_pct DESC;

-- Q17. Inventory value by warehouse
SELECT
    w.warehouse_name,
    ROUND(SUM(i.quantity_on_hand * p.unit_price)/1e6, 2) AS inventory_value_lakhs
FROM inventory  i
JOIN products   p ON i.product_id   = p.product_id
JOIN warehouses w ON i.warehouse_id = w.warehouse_id
GROUP BY w.warehouse_id, w.warehouse_name
ORDER BY inventory_value_lakhs DESC;

-- Q18. Inventory value by category
SELECT
    c.category_name,
    ROUND(SUM(i.quantity_on_hand * p.unit_price)/1e6, 2) AS value_lakhs
FROM inventory  i
JOIN products   p ON i.product_id  = p.product_id
JOIN categories c ON p.category_id = c.category_id
GROUP BY c.category_name
ORDER BY value_lakhs DESC;

-- Q19. Overstocked products
SELECT
    p.product_name,
    p.velocity,
    i.quantity_on_hand,
    i.reorder_point,
    ROUND(i.quantity_on_hand / i.reorder_point, 1) AS overstock_ratio
FROM inventory i
JOIN products  p ON i.product_id = p.product_id
WHERE i.stock_status = 'Overstock'
ORDER BY overstock_ratio DESC
LIMIT 15;

-- Q20. ABC classification by inventory value
SELECT
    p.product_name,
    ROUND(SUM(i.quantity_on_hand * p.unit_price)/1e6, 2) AS value_lakhs,
    ROUND(SUM(i.quantity_on_hand * p.unit_price) /
        SUM(SUM(i.quantity_on_hand * p.unit_price)) OVER () * 100, 2) AS pct_of_total,
    CASE
        WHEN SUM(i.quantity_on_hand * p.unit_price) /
             SUM(SUM(i.quantity_on_hand * p.unit_price)) OVER () * 100 >= 70
        THEN 'A'
        WHEN SUM(i.quantity_on_hand * p.unit_price) /
             SUM(SUM(i.quantity_on_hand * p.unit_price)) OVER () * 100 >= 20
        THEN 'B'
        ELSE 'C'
    END AS abc_class
FROM inventory  i
JOIN products   p ON i.product_id = p.product_id
GROUP BY p.product_id, p.product_name
ORDER BY value_lakhs DESC;

-- ════════════════════════════════════════════
-- SECTION D — SALES ANALYSIS
-- ════════════════════════════════════════════

-- Q21. Monthly sales revenue trend
SELECT
    order_month,
    COUNT(order_id)                    AS orders,
    ROUND(SUM(total_amount)/1e7, 2)    AS revenue_cr
FROM sales_orders
WHERE status = 'Delivered'
GROUP BY order_month
ORDER BY order_month;

-- Q22. Revenue by region
SELECT
    region,
    COUNT(order_id)                 AS orders,
    ROUND(SUM(total_amount)/1e7, 2) AS revenue_cr
FROM sales_orders
WHERE status = 'Delivered'
GROUP BY region
ORDER BY revenue_cr DESC;

-- Q23. Top 10 products by revenue
SELECT
    p.product_name,
    p.velocity,
    COUNT(so.order_id)              AS orders,
    ROUND(SUM(so.total_amount)/1e7, 2) AS revenue_cr
FROM sales_orders so
JOIN products     p ON so.product_id = p.product_id
WHERE so.status = 'Delivered'
GROUP BY p.product_id, p.product_name, p.velocity
ORDER BY revenue_cr DESC
LIMIT 10;

-- Q24. Sales by customer type
SELECT
    c.customer_type,
    COUNT(so.order_id)              AS orders,
    ROUND(SUM(so.total_amount)/1e7, 2) AS revenue_cr
FROM sales_orders so
JOIN customers    c ON so.customer_id = c.customer_id
GROUP BY c.customer_type
ORDER BY revenue_cr DESC;

-- Q25. Running total of sales revenue
SELECT
    order_month,
    ROUND(SUM(total_amount)/1e7, 2) AS monthly_revenue_cr,
    ROUND(SUM(SUM(total_amount)) OVER (ORDER BY order_month)/1e7, 2) AS cumulative_revenue_cr
FROM sales_orders
WHERE status = 'Delivered'
GROUP BY order_month
ORDER BY order_month;

-- Q26. Year-over-year revenue comparison
SELECT
    order_year,
    ROUND(SUM(total_amount)/1e7, 2) AS revenue_cr,
    ROUND(SUM(total_amount) - LAG(SUM(total_amount)) OVER (ORDER BY order_year), 2) AS yoy_change
FROM sales_orders
WHERE status = 'Delivered'
GROUP BY order_year;

-- Q27. Top 10 customers by revenue
SELECT
    c.customer_name,
    c.customer_type,
    c.region,
    COUNT(so.order_id)                 AS orders,
    ROUND(SUM(so.total_amount)/1e7, 2) AS revenue_cr
FROM sales_orders so
JOIN customers    c ON so.customer_id = c.customer_id
WHERE so.status = 'Delivered'
GROUP BY c.customer_id, c.customer_name, c.customer_type, c.region
ORDER BY revenue_cr DESC
LIMIT 10;

-- ════════════════════════════════════════════
-- SECTION E — SHIPMENT ANALYSIS
-- ════════════════════════════════════════════

-- Q28. Overall shipment delay summary
SELECT
    COUNT(*)                              AS total_shipments,
    SUM(is_delayed)                       AS delayed,
    ROUND(SUM(is_delayed)/COUNT(*)*100,1) AS delay_pct,
    ROUND(AVG(transit_days), 1)           AS avg_transit_days
FROM shipments;

-- Q29. Delay rate by shipment partner
SELECT
    shipment_partner,
    COUNT(*)                              AS total,
    SUM(is_delayed)                       AS delayed,
    ROUND(SUM(is_delayed)/COUNT(*)*100,1) AS delay_pct,
    ROUND(AVG(transit_days), 1)           AS avg_transit_days
FROM shipments
GROUP BY shipment_partner
ORDER BY delay_pct DESC;

-- Q30. Delay rate by destination region
SELECT
    destination_region,
    COUNT(*)                              AS total,
    SUM(is_delayed)                       AS delayed,
    ROUND(SUM(is_delayed)/COUNT(*)*100,1) AS delay_pct
FROM shipments
GROUP BY destination_region
ORDER BY delay_pct DESC;

-- Q31. Delay severity distribution
SELECT
    delay_severity,
    COUNT(*) AS shipments,
    ROUND(COUNT(*)/SUM(COUNT(*)) OVER()*100, 1) AS pct
FROM shipments
GROUP BY delay_severity
ORDER BY shipments DESC;

-- Q32. Monthly shipment volume and delay trend
SELECT
    DATE_FORMAT(ship_date, '%Y-%m')       AS ship_month,
    COUNT(*)                              AS total_shipments,
    SUM(is_delayed)                       AS delayed,
    ROUND(SUM(is_delayed)/COUNT(*)*100,1) AS delay_pct
FROM shipments
GROUP BY ship_month
ORDER BY ship_month;

-- Q33. Delay by vehicle type
SELECT
    vehicle_type,
    COUNT(*)                              AS total,
    ROUND(SUM(is_delayed)/COUNT(*)*100,1) AS delay_pct,
    ROUND(AVG(transit_days), 1)           AS avg_transit
FROM shipments
GROUP BY vehicle_type
ORDER BY delay_pct DESC;

-- Q34. Shipment partner ranking using DENSE_RANK
SELECT
    shipment_partner,
    ROUND(SUM(is_delayed)/COUNT(*)*100,1) AS delay_pct,
    DENSE_RANK() OVER (
        ORDER BY SUM(is_delayed)/COUNT(*) DESC
    ) AS delay_rank
FROM shipments
GROUP BY shipment_partner;

-- ════════════════════════════════════════════
-- SECTION F — RETURNS ANALYSIS
-- ════════════════════════════════════════════

-- Q35. Overall return rate
SELECT
    COUNT(r.return_id)                              AS total_returns,
    COUNT(so.order_id)                              AS total_orders,
    ROUND(COUNT(r.return_id)/COUNT(so.order_id)*100,2) AS return_rate_pct
FROM sales_orders so
LEFT JOIN returns  r ON so.order_id = r.order_id
WHERE so.status = 'Delivered';

-- Q36. Returns by reason
SELECT
    return_reason,
    COUNT(*)                              AS count,
    ROUND(SUM(refund_amount)/1e6, 2)      AS refund_lakhs,
    ROUND(COUNT(*)/SUM(COUNT(*)) OVER()*100,1) AS pct
FROM returns
GROUP BY return_reason
ORDER BY count DESC;

-- Q37. Products with highest return count
SELECT
    p.product_name,
    p.velocity,
    COUNT(r.return_id)               AS return_count,
    ROUND(SUM(r.refund_amount)/1e6,2) AS refund_lakhs
FROM returns  r
JOIN products p ON r.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.velocity
ORDER BY return_count DESC
LIMIT 10;

-- Q38. Monthly return trend
SELECT
    return_month,
    COUNT(return_id)                  AS returns,
    ROUND(SUM(refund_amount)/1e6, 2)  AS refund_lakhs
FROM returns
GROUP BY return_month
ORDER BY return_month;

-- ════════════════════════════════════════════
-- SECTION G — ADVANCED / COMBINED QUERIES
-- ════════════════════════════════════════════

-- Q39. CTE — Supplier summary with performance tier
WITH supplier_summary AS (
    SELECT
        s.supplier_id,
        s.supplier_name,
        s.profile,
        COUNT(po.po_id)              AS total_orders,
        ROUND(SUM(po.total_amount)/1e7, 2) AS spend_cr,
        ROUND(SUM(po.is_delayed)/COUNT(*)*100, 1) AS delay_pct,
        ROUND(AVG(po.lead_days), 1)  AS avg_lead
    FROM suppliers s
    JOIN purchase_orders po ON s.supplier_id = po.supplier_id
    GROUP BY s.supplier_id, s.supplier_name, s.profile
)
SELECT *,
    CASE
        WHEN delay_pct < 10  THEN 'Green — Low Risk'
        WHEN delay_pct < 30  THEN 'Yellow — Medium Risk'
        ELSE                      'Red — High Risk'
    END AS risk_flag
FROM supplier_summary
ORDER BY delay_pct DESC;

-- Q40. CTE — Warehouse stock health with utilization
WITH warehouse_stock AS (
    SELECT
        w.warehouse_id,
        w.warehouse_name,
        w.region,
        w.capacity_units,
        SUM(i.quantity_on_hand) AS total_stock,
        SUM(i.reorder_flag)     AS low_stock_skus,
        COUNT(i.inventory_id)   AS total_skus
    FROM warehouses w
    JOIN inventory  i ON w.warehouse_id = i.warehouse_id
    GROUP BY w.warehouse_id, w.warehouse_name, w.region, w.capacity_units
)
SELECT *,
    ROUND(total_stock/capacity_units*100, 1) AS utilization_pct,
    CASE
        WHEN total_stock/capacity_units > 0.90 THEN 'Critical — Overcrowded'
        WHEN total_stock/capacity_units > 0.75 THEN 'Warning — High Utilization'
        ELSE                                        'Healthy'
    END AS warehouse_status
FROM warehouse_stock
ORDER BY utilization_pct DESC;

-- Q41. Window function — rank products by revenue within each category
SELECT
    c.category_name,
    p.product_name,
    ROUND(SUM(so.total_amount)/1e6, 2) AS revenue_lakhs,
    RANK() OVER (
        PARTITION BY c.category_name
        ORDER BY SUM(so.total_amount) DESC
    ) AS rank_in_category
FROM sales_orders so
JOIN products     p ON so.product_id  = p.product_id
JOIN categories   c ON p.category_id  = c.category_id
WHERE so.status = 'Delivered'
GROUP BY c.category_name, p.product_id, p.product_name;

-- Q42. Lead/Lag — month over month sales growth
SELECT
    order_month,
    ROUND(SUM(total_amount)/1e7, 2) AS revenue_cr,
    ROUND(LAG(SUM(total_amount)) OVER (ORDER BY order_month)/1e7, 2) AS prev_month_cr,
    ROUND(
        (SUM(total_amount) - LAG(SUM(total_amount)) OVER (ORDER BY order_month))
        / LAG(SUM(total_amount)) OVER (ORDER BY order_month) * 100
    , 1) AS mom_growth_pct
FROM sales_orders
WHERE status = 'Delivered'
GROUP BY order_month
ORDER BY order_month;

-- Q43. NTILE — segment customers into quartiles by revenue
SELECT
    c.customer_name,
    ROUND(SUM(so.total_amount)/1e6, 2) AS revenue_lakhs,
    NTILE(4) OVER (ORDER BY SUM(so.total_amount) DESC) AS customer_quartile
FROM sales_orders so
JOIN customers    c ON so.customer_id = c.customer_id
WHERE so.status = 'Delivered'
GROUP BY c.customer_id, c.customer_name
ORDER BY revenue_lakhs DESC;

-- Q44. Subquery — suppliers whose avg lead time is above company average
SELECT
    supplier_name,
    ROUND(AVG(po.lead_days), 1) AS avg_lead_days
FROM suppliers s
JOIN purchase_orders po ON s.supplier_id = po.supplier_id
GROUP BY s.supplier_id, s.supplier_name
HAVING AVG(po.lead_days) > (
    SELECT AVG(lead_days) FROM purchase_orders
)
ORDER BY avg_lead_days DESC;

-- Q45. Combined — procurement vs sales by warehouse
SELECT
    w.warehouse_name,
    ROUND(SUM(po.total_amount)/1e7, 2)  AS procurement_cr,
    ROUND(SUM(so.total_amount)/1e7, 2)  AS sales_cr
FROM warehouses w
LEFT JOIN purchase_orders po ON w.warehouse_id = po.warehouse_id
LEFT JOIN sales_orders    so ON w.warehouse_id = so.warehouse_id
GROUP BY w.warehouse_id, w.warehouse_name
ORDER BY procurement_cr DESC;