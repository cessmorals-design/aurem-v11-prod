import json

import pytest

import v11_max


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(v11_max, "DATA_FILE", str(tmp_path / "data.json"))
    return v11_max.app.test_client()


def test_public_conversion_signal_cannot_create_revenue(client):
    response = client.get("/track/conv?ref=affiliate&amount=999999")

    assert response.status_code == 202
    assert response.get_json() == {
        "ok": True,
        "status": "unverified_signal",
        "revenue_recorded": False,
    }
    data = json.loads((v11_max.Path(v11_max.DATA_FILE)).read_text())
    assert data["conversion_signals"][0]["status"] == "unverified"
    assert "amount" not in data["conversion_signals"][0]
    assert data.get("tx", []) == []
    assert "rev" not in data["users"].get("affiliate", {})


def test_admin_data_denies_requests_without_owner_token(client, monkeypatch):
    monkeypatch.delenv("AUREM_ADMIN_TOKEN", raising=False)

    response = client.get("/admin/data")

    assert response.status_code == 401
    assert response.get_json()["error"] == "admin_auth_required"


def test_admin_data_never_reports_client_supplied_revenue(client, monkeypatch):
    monkeypatch.setenv("AUREM_ADMIN_TOKEN", "test-owner-token")
    v11_max.Path(v11_max.DATA_FILE).write_text(json.dumps({
        "users": {"affiliate": {"clicks": 3, "rev": 999999}},
        "clicks": [],
        "conversions": [],
        "conversion_signals": [],
        "tx": [{"ref": "affiliate", "amount": 999999}],
    }))

    response = client.get(
        "/admin/data",
        headers={"Authorization": "Bearer test-owner-token"},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["totalRev"] is None
    assert body["revenueStatus"] == "not_connected_to_verified_owner_ledger"
    assert body["unverifiedConversionSignals"] == 1
    assert body["tx"] == []


def test_checkout_is_disabled_until_canonical_profit_engine_is_connected(client):
    response = client.get("/buy")

    assert response.status_code == 503
    assert response.get_json()["error"] == "checkout_not_connected"


def test_health_does_not_claim_payment_or_revenue_authority(client):
    body = client.get("/health").get_json()

    assert body["payment_state"] == "disabled"
    assert body["revenue_state"] == "unverified"
    assert body["execution_authority"] == "none"
