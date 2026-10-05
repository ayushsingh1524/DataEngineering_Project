{{ config(materialized='table') }}

SELECT
    USER_ID,
    NAME,
    USERNAME,
    EMAIL,
    PHONE,
    WEBSITE,
    CITY,
    ZIPCODE,
    COMPANY

FROM {{ ref('stg_api_users') }}