import pytest

from ingestion.sqlserver_incremental import build_sqlserver_connection_string


def test_sqlserver_connection_string_targets_local_docker_port(monkeypatch):
    monkeypatch.setenv("SQLSERVER_HOST", "localhost")
    monkeypatch.setenv("SQLSERVER_PORT", "1433")
    monkeypatch.setenv("SQLSERVER_DATABASE", "OrdersDb")
    monkeypatch.setenv("SQLSERVER_USER", "sa")
    monkeypatch.setenv("SQLSERVER_PASSWORD", "local-test-password")
    monkeypatch.setenv("SQLSERVER_DRIVER", "ODBC Driver 18 for SQL Server")

    connection_string = build_sqlserver_connection_string()

    assert "SERVER={tcp:localhost,1433};" in connection_string
    assert "DATABASE={OrdersDb};" in connection_string
    assert "UID={sa};" in connection_string
    assert "Encrypt=yes;" in connection_string
    assert "TrustServerCertificate=yes;" in connection_string


def test_sqlserver_connection_string_requires_credentials(monkeypatch):
    for key in (
        "SQLSERVER_DATABASE",
        "SQLSERVER_USER",
        "SQLSERVER_PASSWORD",
    ):
        monkeypatch.delenv(key, raising=False)

    with pytest.raises(ValueError, match="SQLSERVER_DATABASE"):
        build_sqlserver_connection_string()


def test_sqlserver_connection_string_escapes_odbc_values(monkeypatch):
    monkeypatch.setenv("SQLSERVER_HOST", "localhost")
    monkeypatch.setenv("SQLSERVER_PORT", "1433")
    monkeypatch.setenv("SQLSERVER_DATABASE", "Orders;Archive")
    monkeypatch.setenv("SQLSERVER_USER", "sa")
    monkeypatch.setenv("SQLSERVER_PASSWORD", "p}ass;word")

    connection_string = build_sqlserver_connection_string()

    assert "DATABASE={Orders;Archive};" in connection_string
    assert "PWD={p}}ass;word};" in connection_string
