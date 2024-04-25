from fastapi.testclient import TestClient
from datetime import datetime
from modules import DateRange, Reservation
import pytest
from main import app, calendar

client = TestClient(app)

def test_get_reservations_by_customer_with_dates():
    # I am assuming there is a customer named "Nikola" with reservations in the date range
    start_date = "2024-01-01 11:00"
    end_date = "2024-12-31 11:00"
    response = client.get(f"/reservations/customers/Nikola?start={start_date}&end={end_date}")
    assert response.status_code == 200

    # Checking the response is not empty
    assert "reservations" in response.json()
    assert len(response.json()["reservations"]) > 0

def test_get_reservations_by_customer_with_dates_fail():
    with pytest.raises(AssertionError):
        # I am assuming there is no customer named "Jamal" with reservations in the date range
        start_date = "2024-01-01 11:00"
        end_date = "2024-12-31 11:00"
        response = client.get(f"/reservations/customers/Jamal?start={start_date}&end={end_date}")
        assert response.status_code == 200

        # Checking the response is not empty
        assert "reservations" in response.json()
        assert len(response.json()["reservations"]) > 0

def test_get_reservations_by_machine_with_dates():
    # I am assuming there is a machine named "Scanner" with reservations
    start_date = "2024-01-01 11:00"
    end_date = "2024-12-31 11:00"
    response = client.get(f"/reservations/machines/scanner?start={start_date}&end={end_date}")
    assert response.status_code == 200

    # Checking the response is not empty
    assert "reservations" in response.json()
    assert len(response.json()["reservations"]) > 0

def test_get_reservations_by_machine_with_dates_fail():
    with pytest.raises(AssertionError):
        # I am assuming there is no machine named "Blastinator" with reservations
        start_date = "2024-01-01 11:00"
        end_date = "2024-12-31 11:00"
        response = client.get(f"/reservations/machines/Blastinator?start={start_date}&end={end_date}")
        assert response.status_code == 200

        # Checking the response is not empty
        assert "reservations" in response.json()
        assert len(response.json()["reservations"]) > 0

def test_cancel_reservation():
 
    daterange = DateRange("2024-05-10 11:00", "2024-05-10 11:30")
    reservation = Reservation("testcustomer", "scanner", daterange)
    calendar.add_reservation(reservation)
    id = reservation.id
    response = client.delete(f"/reservations/{id}")

    assert response.status_code == 200
    assert 'refund' in response.json()
    assert 'message' in response.json()
    
def test_cancel_invalid_reservation():
    response = client.delete(f"/reservations/invalidID")
    assert response.status_code == 404
    assert 'detail' in response.json()
    assert response.json()['detail'] == "Reservation not found"

def test_get_reservations_by_date():
    start = "2024-01-01 11:00"
    end = "2024-12-31 14:00" 
    response = client.get(f"/reservations?start={start}&end={end}")
    assert response.status_code == 200
    assert 'reservations' in response.json()
    assert len(response.json()['reservations']) > 0

def test_get_no_reservations_by_date():
    start = "2010-01-01 11:00"
    end = "2010-12-31 14:00" 
    response = client.get(f"/reservations?start={start}&end={end}")
    assert response.status_code == 200
    assert 'reservations' not in response.json()
    assert 'message' in response.json()
    assert response.json()['message'] == "No reservations found in this date range"

def test_post_reservation():
    data = {
        "customer_name": "testcustomer",
        "machine_name": "scanner",
        "start_date": "2024-04-25 11:00",
        "end_date": "2024-04-25 11:30"
    }
    
    response = client.post("/reservations", json=data)
    assert response.status_code == 201
    assert 'message' in response.json()
    assert response.json()['message'] == "Reservation added successfully!"
