{{ config(materialized='table') }}

SELECT
    CUSTOMER_ID,
    CUSTOMER_NAME,
    EMAIL,
    COUNTRY,
    CITY,
    CUSTOMER_SEGMENT,
    SIGNUP_DATE,

    YEAR(SIGNUP_DATE) AS SIGNUP_YEAR

FROM {{ ref('stg_customers') }}