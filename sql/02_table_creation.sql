-- =====================================================
-- TABLE CREATION
-- DEMAND FORECASTING & INVENTORY OPTIMIZATION
-- =====================================================

USE WAREHOUSE DEMAND_FORECAST_WH;
USE DATABASE DEMAND_FORECAST_DB;
USE SCHEMA SALES_SCHEMA;


-- =====================================================
-- CREATE RAW SALES TABLE
-- =====================================================

CREATE OR REPLACE TABLE RAW_SALES_DATA
(
    SALE_DATE       DATE,
    PRODUCT_ID      VARCHAR(20),
    PRODUCT         VARCHAR(100),
    CATEGORY        VARCHAR(100),
    STORE           VARCHAR(20),
    CITY            VARCHAR(100),
    PRICE           NUMBER(12,2),
    DISCOUNT        NUMBER(5,2),
    PROMOTION       NUMBER(1,0),
    INVENTORY       NUMBER(12,2),
    SALES           NUMBER(12,2)
);


-- =====================================================
-- CHECK TABLE STRUCTURE
-- =====================================================

DESC TABLE RAW_SALES_DATA;


-- =====================================================
-- CREATE FILE FORMAT
-- =====================================================

CREATE OR REPLACE FILE FORMAT SALES_CSV_FORMAT
TYPE = CSV
SKIP_HEADER = 1
FIELD_OPTIONALLY_ENCLOSED_BY = '"'
DATE_FORMAT = 'YYYY-MM-DD';


-- =====================================================
-- CREATE INTERNAL STAGE
-- =====================================================

CREATE OR REPLACE STAGE SALES_STAGE
FILE_FORMAT = SALES_CSV_FORMAT;


-- =====================================================
-- CHECK TABLE
-- =====================================================

SHOW TABLES;

-- Check that table is currently empty
SELECT COUNT(*) AS TOTAL_ROWS
FROM RAW_SALES_DATA; 

CREATE OR REPLACE STAGE SALES_STAGE
FILE_FORMAT = SALES_CSV_FORMAT;

SHOW STAGES; 