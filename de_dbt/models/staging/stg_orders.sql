{{ config(materialized='table') }}

WITH ranked_orders AS (

    SELECT

        ORDER_ID,
        CUSTOMER_ID,
        ORDER_DATE,
        ORDER_STATUS,
        TOTAL_AMOUNT,
        CREATED_AT,
        UPDATED_AT,

        ROW_NUMBER() OVER (
            PARTITION BY ORDER_ID
            ORDER BY UPDATED_AT DESC
        ) AS RN

    FROM {{ source('bronze','ORDERS') }}

)

SELECT

    ORDER_ID,
    CUSTOMER_ID,
    ORDER_DATE,
    ORDER_STATUS,
    TOTAL_AMOUNT,
    CREATED_AT,
    UPDATED_AT

FROM ranked_orders

WHERE RN = 1