{{ config(
    materialized='table'
) }}

SELECT

    CUSTOMER_ID,

    INITCAP(TRIM(FIRST_NAME)) || ' ' ||
    INITCAP(TRIM(LAST_NAME))            AS CUSTOMER_NAME,

    LOWER(TRIM(EMAIL))                 AS EMAIL,

    COALESCE(CITY,'Unknown')           AS CITY,

    CASE
        WHEN COUNTRY='USA' THEN 'United States'
        ELSE COUNTRY
    END                                AS COUNTRY,

    COALESCE(CUSTOMER_SEGMENT,'Unknown')
                                      AS CUSTOMER_SEGMENT,

    SIGNUP_DATE

FROM {{ source('bronze','CUSTOMERS') }}