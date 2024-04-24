from fastapi.testclient import TestClient
from datetime import datetime
from modules import DateRange, Reservation
import pytest
from main import app, calendar

client = TestClient(app)

def test_cancel_reservation():
    daterange = DateRange("2024-07-01 11:00", "2024-07-01 11:30")
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
    assert response.json()['reservations'] > 0

def test_get_no_reservations_by_date():
    start = "2010-01-01 11:00"
    end = "2010-12-31 14:00" 
    response = client.get(f"/reservations?start={start}&end={end}")
    assert response.status_code == 200
    assert 'reservations' not in response.json()
    assert 'message' in response.json()
    assert response.json()['message'] == "No reservations found in this date range"



