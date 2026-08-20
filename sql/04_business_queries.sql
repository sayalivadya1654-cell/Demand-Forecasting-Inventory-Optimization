-- ============================================================
-- DEMAND FORECASTING & INVENTORY OPTIMIZATION
-- 04_BUSINESS_QUERIES.SQL
-- ============================================================

USE WAREHOUSE DEMAND_FORECAST_WH;
USE DATABASE DEMAND_FORECAST_DB;
USE SCHEMA SALES_SCHEMA;


-- ============================================================
-- 1. TOP 10 BEST-SELLING PRODUCTS
-- ============================================================

SELECT
    PRODUCT_ID,
    PRODUCT,
    SUM(SALES) AS TOTAL_UNITS_SOLD,
    ROUND(SUM(PRICE * SALES), 2) AS TOTAL_REVENUE
FROM RAW_SALES_DATA
GROUP BY
    PRODUCT_ID,
    PRODUCT
ORDER BY TOTAL_UNITS_SOLD DESC
LIMIT 10;


-- ============================================================
-- 2. STOCK STATUS
-- ============================================================

SELECT
    PRODUCT_ID,
    PRODUCT,
    STORE,
    CITY,
    INVENTORY,

    CASE
        WHEN INVENTORY <= 10 THEN 'CRITICAL'
        WHEN INVENTORY <= 25 THEN 'LOW'
        WHEN INVENTORY <= 50 THEN 'MEDIUM'
        ELSE 'HEALTHY'
    END AS STOCK_STATUS

FROM RAW_SALES_DATA
ORDER BY INVENTORY ASC;


-- ============================================================
-- 3. INVENTORY RISK BY PRODUCT
-- ============================================================

SELECT
    PRODUCT_ID,
    PRODUCT,

    ROUND(AVG(SALES), 2) AS AVG_DAILY_DEMAND,

    ROUND(AVG(INVENTORY), 2) AS AVG_INVENTORY,

    CASE
        WHEN AVG(INVENTORY) < AVG(SALES) * 3
            THEN 'HIGH RISK'

        WHEN AVG(INVENTORY) < AVG(SALES) * 7
            THEN 'MEDIUM RISK'

        ELSE 'LOW RISK'
    END AS INVENTORY_RISK

FROM RAW_SALES_DATA

GROUP BY
    PRODUCT_ID,
    PRODUCT

ORDER BY AVG_INVENTORY ASC;


-- ============================================================
-- 4. MONTHLY REVENUE
-- ============================================================

SELECT
    DATE_TRUNC('MONTH', SALE_DATE) AS SALES_MONTH,
    ROUND(SUM(PRICE * SALES), 2) AS MONTHLY_REVENUE
FROM RAW_SALES_DATA
GROUP BY
    DATE_TRUNC('MONTH', SALE_DATE)
ORDER BY SALES_MONTH;


-- ============================================================
-- 5. MONTH-OVER-MONTH REVENUE GROWTH
-- ============================================================

WITH MONTHLY_REVENUE AS
(
    SELECT
        DATE_TRUNC('MONTH', SALE_DATE) AS SALES_MONTH,
        SUM(PRICE * SALES) AS REVENUE

    FROM RAW_SALES_DATA

    GROUP BY
        DATE_TRUNC('MONTH', SALE_DATE)
)

SELECT
    SALES_MONTH,

    ROUND(REVENUE, 2) AS REVENUE,

    ROUND(
        LAG(REVENUE) OVER (
            ORDER BY SALES_MONTH
        ),
        2
    ) AS PREVIOUS_MONTH_REVENUE,

    ROUND(
        (
            REVENUE -
            LAG(REVENUE) OVER (
                ORDER BY SALES_MONTH
            )
        )
        /
        NULLIF(
            LAG(REVENUE) OVER (
                ORDER BY SALES_MONTH
            ),
            0
        ) * 100,
        2
    ) AS MOM_GROWTH_PERCENT

FROM MONTHLY_REVENUE
ORDER BY SALES_MONTH;


-- ============================================================
-- 6. PRODUCT REVENUE RANKING
-- ============================================================

SELECT
    PRODUCT_ID,
    PRODUCT,

    ROUND(SUM(PRICE * SALES), 2) AS TOTAL_REVENUE,

    RANK() OVER (
        ORDER BY SUM(PRICE * SALES) DESC
    ) AS REVENUE_RANK

FROM RAW_SALES_DATA

GROUP BY
    PRODUCT_ID,
    PRODUCT

ORDER BY REVENUE_RANK;


-- ============================================================
-- 7. STORE PERFORMANCE
-- ============================================================

SELECT
    STORE,
    CITY,

    SUM(SALES) AS TOTAL_UNITS_SOLD,

    ROUND(SUM(PRICE * SALES), 2) AS TOTAL_REVENUE,

    ROUND(AVG(SALES), 2) AS AVERAGE_SALES

FROM RAW_SALES_DATA

GROUP BY
    STORE,
    CITY

ORDER BY TOTAL_REVENUE DESC;


-- ============================================================
-- 8. PROMOTION EFFECTIVENESS
-- ============================================================

SELECT
    PROMOTION,

    COUNT(*) AS NUMBER_OF_RECORDS,

    ROUND(AVG(SALES), 2) AS AVERAGE_SALES,

    SUM(SALES) AS TOTAL_SALES

FROM RAW_SALES_DATA

GROUP BY PROMOTION

ORDER BY AVERAGE_SALES DESC;


-- ============================================================
-- 9. DISCOUNT EFFECTIVENESS
-- ============================================================

SELECT
    DISCOUNT,

    COUNT(*) AS NUMBER_OF_RECORDS,

    ROUND(AVG(SALES), 2) AS AVERAGE_SALES,

    SUM(SALES) AS TOTAL_SALES

FROM RAW_SALES_DATA

GROUP BY DISCOUNT

ORDER BY DISCOUNT;


-- ============================================================
-- 10. DEMAND BY DAY OF WEEK
-- ============================================================

SELECT
    DAYNAME(SALE_DATE) AS DAY_OF_WEEK,

    SUM(SALES) AS TOTAL_SALES,

    ROUND(AVG(SALES), 2) AS AVERAGE_SALES

FROM RAW_SALES_DATA

GROUP BY DAYNAME(SALE_DATE)
ORDER BY TOTAL_SALES DESC;


-- ============================================================
-- 11. REORDER RECOMMENDATION
-- 7-DAY DEMAND BASED
-- ============================================================

WITH PRODUCT_METRICS AS
(
    SELECT
        PRODUCT_ID,
        PRODUCT,

        AVG(SALES) AS AVG_DAILY_DEMAND,

        AVG(INVENTORY) AS CURRENT_INVENTORY

    FROM RAW_SALES_DATA

    GROUP BY
        PRODUCT_ID,
        PRODUCT
)

SELECT
    PRODUCT_ID,
    PRODUCT,

    ROUND(AVG_DAILY_DEMAND, 2)
        AS AVG_DAILY_DEMAND,

    ROUND(CURRENT_INVENTORY, 2)
        AS CURRENT_INVENTORY,

    ROUND(
        AVG_DAILY_DEMAND * 7,
        2
    ) AS EXPECTED_7_DAY_DEMAND,

    ROUND(
        GREATEST(
            AVG_DAILY_DEMAND * 7
            - CURRENT_INVENTORY,
            0
        ),
        2
    ) AS RECOMMENDED_REORDER_QTY,

    CASE
        WHEN CURRENT_INVENTORY <
             AVG_DAILY_DEMAND * 7
        THEN 'REORDER NOW'

        ELSE 'NO REORDER'
    END AS REORDER_STATUS

FROM PRODUCT_METRICS

ORDER BY CURRENT_INVENTORY ASC;


-- ============================================================
-- 12. BUSINESS PRIORITY
-- HIGH DEMAND + LOW INVENTORY
-- ============================================================

WITH PRODUCT_METRICS AS
(
    SELECT
        PRODUCT_ID,
        PRODUCT,

        SUM(SALES) AS TOTAL_SALES,

        AVG(SALES) AS AVG_DAILY_DEMAND,

        AVG(INVENTORY) AS AVG_INVENTORY

    FROM RAW_SALES_DATA

    GROUP BY
        PRODUCT_ID,
        PRODUCT
)

SELECT
    PRODUCT_ID,
    PRODUCT,

    TOTAL_SALES,

    ROUND(AVG_DAILY_DEMAND, 2)
        AS AVG_DAILY_DEMAND,

    ROUND(AVG_INVENTORY, 2)
        AS AVG_INVENTORY,

    CASE
        WHEN AVG_INVENTORY < AVG_DAILY_DEMAND * 3
             AND TOTAL_SALES > 100
        THEN 'URGENT REORDER'

        WHEN AVG_INVENTORY < AVG_DAILY_DEMAND * 7
             AND TOTAL_SALES > 100
        THEN 'HIGH PRIORITY'

        ELSE 'NORMAL'
    END AS BUSINESS_PRIORITY

FROM PRODUCT_METRICS

ORDER BY
    BUSINESS_PRIORITY,
    TOTAL_SALES DESC;