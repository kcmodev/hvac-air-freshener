from unittest.mock import MagicMock

import pytest

import app as web
from pi_logic.config import ConfigError
from pi_logic.motor_logic import SprayerBusyError
from pi_logic.spray_log import record_spray
from pi_logic.thermostat_logic import ThermostatError


@pytest.fixture
def client():
    return web.app.test_client()


@pytest.fixture
def thermostat(monkeypatch):
    fake = MagicMock()
    monkeypatch.setattr(web, "get_thermostat", lambda: fake)
    return fake


@pytest.fixture
def sprayer(monkeypatch):
    fake = MagicMock(side_effect=record_spray)
    monkeypatch.setattr(web, "cycle_sprayer_manually", fake)
    return fake


def test_routes_are_only_served_under_api(client):
    assert client.get("/").status_code == 404
    assert client.get("/timestamp").status_code == 404


def test_spray_runs_a_cycle_and_returns_its_time(client, sprayer):
    response = client.post("/api/spray")

    assert response.status_code == 200
    assert set(response.json) == {"date", "time"}
    sprayer.assert_called_once_with()


def test_spray_rejects_get(client, sprayer):
    assert client.get("/api/spray").status_code == 405
    sprayer.assert_not_called()


def test_spray_reports_busy_as_conflict(client, sprayer):
    sprayer.side_effect = SprayerBusyError("The sprayer is already running")

    response = client.post("/api/spray")

    assert response.status_code == 409
    assert response.json == {"error": "The sprayer is already running"}


def test_spray_reports_fan_failure_as_bad_gateway(client, sprayer):
    sprayer.side_effect = ThermostatError("unreachable")

    assert client.post("/api/spray").status_code == 502


def test_timestamp_is_not_found_before_any_spray(client):
    assert client.get("/api/timestamp").status_code == 404


def test_timestamp_returns_the_latest_spray(client):
    entry = record_spray()

    response = client.get("/api/timestamp")

    assert response.status_code == 200
    assert response.json == entry


def test_timestamp_cannot_be_written_by_clients(client):
    assert client.post("/api/timestamp", json={"date": "x", "time": "y"}).status_code == 405


def test_status_returns_the_live_hvac_state(client, thermostat):
    thermostat.get_hvac_status.return_value = "COOLING"

    assert client.get("/api/status").json == {"status": "COOLING"}


def test_status_hides_failure_details_from_the_client(client, thermostat):
    thermostat.get_hvac_status.side_effect = ThermostatError("https://secret-device-url")

    response = client.get("/api/status")

    assert response.status_code == 502
    assert b"secret-device-url" not in response.data


def test_missing_credentials_are_reported_as_unavailable(client, monkeypatch):
    monkeypatch.setattr(web, "get_thermostat", MagicMock(side_effect=ConfigError("Missing")))

    assert client.get("/api/status").status_code == 503
