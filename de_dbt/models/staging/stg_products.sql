{{ config(materialized='table') }}

SELECT

    PRODUCT_ID,

    TRIM(PRODUCT_NAME) AS PRODUCT_NAME,

    COALESCE(NULLIF(TRIM(CATEGORY), ''), 'Unknown') AS CATEGORY,

    COALESCE(NULLIF(TRIM(SUBCATEGORY), ''), 'Unknown') AS SUBCATEGORY,

    SUPPLIER_ID,

    UNIT_PRICE,

    COST_PRICE

FROM {{ source('bronze', 'PRODUCTS') }}

