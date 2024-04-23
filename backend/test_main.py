from fastapi.testclient import TestClient
from datetime import datetime
import pytest
from main import app

client = TestClient(app)

def test_get_reservations_by_customer_with_dates():
    # I am assuming there is a customer named "Nikola" with reservations in the date range
    start_date = datetime(2024, 1, 1).isoformat()
    end_date = datetime(2024, 1, 31).isoformat()
    response = client.get(f"/reservations/customers/Nikola?start={start_date}&end={end_date}")
    assert response.status_code == 200

    # Checking the response is not empty
    assert "reservations" in response.json()
    assert len(response.json()["reservations"]) > 0

def test_get_reservations_by_customer_with_dates_fail():
    with pytest.raises(AssertionError):
        # I am assuming there is no customer named "Jamal" with reservations in the date range
        start_date = datetime(2024, 1, 1).isoformat()
        end_date = datetime(2024, 1, 31).isoformat()
        response = client.get(f"/reservations/customers/Jamal?start={start_date}&end={end_date}")
        assert response.status_code == 200

        # Checking the response is not empty
        assert "reservations" in response.json()
        assert len(response.json()["reservations"]) > 0

def test_get_reservations_by_machine_with_dates():
    # I am assuming there is a machine named "Scanner" with reservations
    start_date = datetime(2024, 1, 1).isoformat()
    end_date = datetime(2024, 1, 31).isoformat()
    response = client.get(f"/reservations/machines/Scanner?start={start_date}&end={end_date}")
    assert response.status_code == 200

    # Checking the response is not empty
    assert "reservations" in response.json()
    assert len(response.json()["reservations"]) > 0

def test_get_reservations_by_machine_with_dates_fail():
    with pytest.raises(AssertionError):
        # I am assuming there is no machine named "Blastinator" with reservations
        start_date = datetime(2024, 1, 1).isoformat()
        end_date = datetime(2024, 1, 31).isoformat()
        response = client.get(f"/reservations/machines/Blastinator?start={start_date}&end={end_date}")
        assert response.status_code == 200

        # Checking the response is not empty
        assert "reservations" in response.json()
        assert len(response.json()["reservations"]) > 0
