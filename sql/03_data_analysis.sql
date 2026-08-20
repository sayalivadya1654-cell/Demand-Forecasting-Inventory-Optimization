-- ============================================================
-- DEMAND FORECASTING & INVENTORY OPTIMIZATION
-- 03_DATA_ANALYSIS.SQL
-- ============================================================

USE WAREHOUSE DEMAND_FORECAST_WH;
USE DATABASE DEMAND_FORECAST_DB;
USE SCHEMA SALES_SCHEMA;


-- ============================================================
-- 1. VIEW SAMPLE DATA
-- ============================================================

SELECT *
FROM RAW_SALES_DATA
LIMIT 20;


-- ============================================================
-- 2. TOTAL NUMBER OF RECORDS
-- ============================================================

SELECT
    COUNT(*) AS TOTAL_RECORDS
FROM RAW_SALES_DATA;


-- ============================================================
-- 3. CHECK DATE RANGE
-- ============================================================

SELECT
    MIN(SALE_DATE) AS START_DATE,
    MAX(SALE_DATE) AS END_DATE
FROM RAW_SALES_DATA;


-- ============================================================
-- 4. TOTAL UNITS SOLD
-- ============================================================

SELECT
    SUM(SALES) AS TOTAL_UNITS_SOLD
FROM RAW_SALES_DATA;


-- ============================================================
-- 5. TOTAL REVENUE
-- Price × Sales
-- ============================================================

SELECT
    ROUND(SUM(PRICE * SALES), 2) AS TOTAL_REVENUE
FROM RAW_SALES_DATA;


-- ============================================================
-- 6. AVERAGE SALES PER DAY/RECORD
-- ============================================================

SELECT
    ROUND(AVG(SALES), 2) AS AVERAGE_SALES
FROM RAW_SALES_DATA;


-- ============================================================
-- 7. AVERAGE INVENTORY
-- ============================================================

SELECT
    ROUND(AVG(INVENTORY), 2) AS AVERAGE_INVENTORY
FROM RAW_SALES_DATA;


-- ============================================================
-- 8. SALES BY PRODUCT
-- ============================================================

SELECT
    PRODUCT_ID,
    PRODUCT,
    SUM(SALES) AS TOTAL_SALES,
    ROUND(SUM(PRICE * SALES), 2) AS TOTAL_REVENUE
FROM RAW_SALES_DATA
GROUP BY
    PRODUCT_ID,
    PRODUCT
ORDER BY TOTAL_SALES DESC;


-- ============================================================
-- 9. SALES BY CATEGORY
-- ============================================================

SELECT
    CATEGORY,
    SUM(SALES) AS TOTAL_SALES,
    ROUND(SUM(PRICE * SALES), 2) AS TOTAL_REVENUE
FROM RAW_SALES_DATA
GROUP BY CATEGORY
ORDER BY TOTAL_REVENUE DESC;


-- ============================================================
-- 10. SALES BY CITY
-- ============================================================

SELECT
    CITY,
    SUM(SALES) AS TOTAL_SALES,
    ROUND(SUM(PRICE * SALES), 2) AS TOTAL_REVENUE
FROM RAW_SALES_DATA
GROUP BY CITY
ORDER BY TOTAL_REVENUE DESC;


-- ============================================================
-- 11. SALES BY STORE
-- ============================================================

SELECT
    STORE,
    CITY,
    SUM(SALES) AS TOTAL_SALES,
    ROUND(SUM(PRICE * SALES), 2) AS TOTAL_REVENUE
FROM RAW_SALES_DATA
GROUP BY
    STORE,
    CITY
ORDER BY TOTAL_REVENUE DESC;


-- ============================================================
-- 12. MONTHLY SALES
-- ============================================================

SELECT
    DATE_TRUNC('MONTH', SALE_DATE) AS SALES_MONTH,
    SUM(SALES) AS TOTAL_SALES,
    ROUND(SUM(PRICE * SALES), 2) AS TOTAL_REVENUE
FROM RAW_SALES_DATA
GROUP BY
    DATE_TRUNC('MONTH', SALE_DATE)
ORDER BY SALES_MONTH;


-- ============================================================
-- 13. DAILY SALES
-- ============================================================

SELECT
    SALE_DATE,
    SUM(SALES) AS DAILY_SALES,
    ROUND(SUM(PRICE * SALES), 2) AS DAILY_REVENUE
FROM RAW_SALES_DATA
GROUP BY SALE_DATE
ORDER BY SALE_DATE;


-- ============================================================
-- 14. PROMOTION ANALYSIS
-- ============================================================

SELECT
    PROMOTION,
    COUNT(*) AS NUMBER_OF_RECORDS,
    SUM(SALES) AS TOTAL_SALES,
    ROUND(AVG(SALES), 2) AS AVERAGE_SALES
FROM RAW_SALES_DATA
GROUP BY PROMOTION
ORDER BY PROMOTION;


-- ============================================================
-- 15. DISCOUNT ANALYSIS
-- ============================================================

SELECT
    DISCOUNT,
    COUNT(*) AS NUMBER_OF_RECORDS,
    SUM(SALES) AS TOTAL_SALES,
    ROUND(AVG(SALES), 2) AS AVERAGE_SALES
FROM RAW_SALES_DATA
GROUP BY DISCOUNT
ORDER BY DISCOUNT;


-- ============================================================
-- 16. LOW INVENTORY RECORDS
-- ============================================================

SELECT
    SALE_DATE,
    PRODUCT_ID,
    PRODUCT,
    STORE,
    CITY,
    INVENTORY,
    SALES
FROM RAW_SALES_DATA
WHERE INVENTORY <= 20
ORDER BY INVENTORY ASC;


-- ============================================================
-- 17. HIGH DEMAND PRODUCTS
-- ============================================================

SELECT
    PRODUCT_ID,
    PRODUCT,
    SUM(SALES) AS TOTAL_SALES
FROM RAW_SALES_DATA
GROUP BY
    PRODUCT_ID,
    PRODUCT
ORDER BY TOTAL_SALES DESC
LIMIT 10;


-- ============================================================
-- 18. PRODUCTS WITH HIGH SALES AND LOW INVENTORY
-- ============================================================

SELECT
    PRODUCT_ID,
    PRODUCT,
    SUM(SALES) AS TOTAL_SALES,
    ROUND(AVG(INVENTORY), 2) AS AVG_INVENTORY
FROM RAW_SALES_DATA
GROUP BY
    PRODUCT_ID,
    PRODUCT
HAVING
    SUM(SALES) > 100
    AND AVG(INVENTORY) < 50
ORDER BY TOTAL_SALES DESC; 

LIST @SALES_STAGE;
USE WAREHOUSE DEMAND_FORECAST_WH;
USE DATABASE DEMAND_FORECAST_DB;
USE SCHEMA SALES_SCHEMA;

COPY INTO RAW_SALES_DATA
FROM @SALES_STAGE
FILE_FORMAT = SALES_CSV_FORMAT
ON_ERROR = 'ABORT_STATEMENT';
SELECT COUNT(*) AS TOTAL_ROWS
FROM RAW_SALES_DATA;
SELECT *
FROM RAW_SALES_DATA
LIMIT 10;