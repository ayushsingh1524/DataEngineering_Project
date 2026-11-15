from ingestion.sqlserver_incremental import INCREMENTAL_ORDERS_QUERY


def test_incremental_query_uses_parameterized_watermark():
    normalized = " ".join(INCREMENTAL_ORDERS_QUERY.split()).upper()

    assert "WHERE UPDATED_AT > ?" in normalized
    assert "ORDER BY UPDATED_AT" in normalized
    assert "SELECT" in normalized
    assert "OPERATIONS.ORDERS" in normalized
