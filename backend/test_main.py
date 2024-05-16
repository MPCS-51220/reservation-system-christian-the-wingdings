from fastapi.testclient import TestClient
import sqlite3
from datetime import datetime
from modules import DateRange, Reservation, ReservationCalendar, UserManager
import pytest
from main import app, calendar
import hashlib


# The in memory copy ensures the original database won't be corrupted, 
# if the database grows large in production, revisit this approach
@pytest.fixture(scope="session")
def db():

    disk_connection = sqlite3.connect('../reservationDB.db')
    memory_connection = sqlite3.connect(':memory:', check_same_thread=False)

    disk_connection.backup(memory_connection)
    disk_connection.close()

    yield memory_connection

    memory_connection.close()

@pytest.fixture # Roll back changes after each test
def transaction(db):
    cursor = db.cursor()
    yield cursor
    db.rollback()
    
@pytest.fixture(scope="session")
def setup_db(db):
    username = "adminTest"
    password = "adminpass"
    role = "admin"
    salt = "admin_salt"
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO User (username, password_hash, role, salt) 
        VALUES (?, ?, ?, ?)
    """, (username, hashed_password, role, salt))
    db.commit()

# Fixture to create a test client for FastAPI
@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[UserManager] = lambda: UserManager(db)
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


############ Database Tests ############


############ API ROUTES Tests ############
@pytest.mark.parametrize("username, password, expected_status, expected_detail", [
    ("adminTest", "adminpass", 200, None),  # Successful login
    ("adminTest", "wrongpass", 401, "Incorrect username or password"),  # Incorrect password
    (None, "adminpass", 422, None),  # Missing username
    ("adminTest", None, 422, None),  # Missing password
    (None, None, 422, None)  # Empty payload
])
def test_login(client, setup_db, transaction, username, password, expected_status, expected_detail):
    payload = {}
    if username is not None:
        payload["username"] = username
    if password is not None:
        payload["password"] = password

    response = client.post("/login", json=payload)
    assert response.status_code == expected_status
    if expected_detail:
        assert response.json()["detail"] == expected_detail
    elif expected_status == 200:
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"


############ Permissions AUTH Tests ############


######

# def test_user_roles(client, transaction, username, password, expected_role):
#     # Assuming there is an endpoint `/login` that accepts JSON credentials
#     response = client.post("/login", json={"username": username, "password_hash": password, "role": expected_role})
#     assert response.status_code == 200
#     assert response.json()['role'] == expected_role

# def test_get_reservations_by_customer_with_dates(client):
#     # I am assuming there is a customer named "Nikola" with reservations in the date range
#     start_date = "2024-01-01 11:00"
#     end_date = "2024-12-31 11:00"
#     response = client.get(f"/reservations/customers/Nikola?start={start_date}&end={end_date}")
#     assert response.status_code == 200

#     # Checking the response is not empty
#     assert "reservations" in response.json()
#     assert len(response.json()["reservations"]) > 0

# def test_get_reservations_by_customer_with_dates_fail(client):
#     with pytest.raises(AssertionError):
#         # I am assuming there is no customer named "Jamal" with reservations in the date range
#         start_date = "2024-01-01 11:00"
#         end_date = "2024-12-31 11:00"
#         response = client.get(f"/reservations/customers/Jamal?start={start_date}&end={end_date}")
#         assert response.status_code == 200

#         # Checking the response is not empty
#         assert "reservations" in response.json()
#         assert len(response.json()["reservations"]) > 0

# def test_get_reservations_by_machine_with_dates(client):
#     # I am assuming there is a machine named "Scanner" with reservations
#     start_date = "2024-01-01 11:00"
#     end_date = "2024-12-31 11:00"
#     response = client.get(f"/reservations/machines/scanner?start={start_date}&end={end_date}")
#     assert response.status_code == 200

#     # Checking the response is not empty
#     assert "reservations" in response.json()
#     assert len(response.json()["reservations"]) > 0

# def test_get_reservations_by_machine_with_dates_fail(client):
#     with pytest.raises(AssertionError):
#         # I am assuming there is no machine named "Blastinator" with reservations
#         start_date = "2024-01-01 11:00"
#         end_date = "2024-12-31 11:00"
#         response = client.get(f"/reservations/machines/Blastinator?start={start_date}&end={end_date}")
#         assert response.status_code == 200

#         # Checking the response is not empty
#         assert "reservations" in response.json()
#         assert len(response.json()["reservations"]) > 0

# def test_cancel_reservation(client):
 
#     daterange = DateRange("2024-05-10 11:00", "2024-05-10 11:30")
#     reservation = Reservation("testcustomer", "scanner", daterange)
#     calendar.add_reservation(reservation)
#     id = reservation.id
#     response = client.delete(f"/reservations/{id}")

#     assert response.status_code == 200
#     assert 'refund' in response.json()
#     assert 'message' in response.json()
    
# def test_cancel_invalid_reservation(client):
#     response = client.delete(f"/reservations/invalidID")
#     assert response.status_code == 404
#     assert 'detail' in response.json()
#     assert response.json()['detail'] == "Reservation not found"

# def test_get_reservations_by_date(client):
#     start = "2024-01-01 11:00"
#     end = "2024-12-31 14:00" 
#     response = client.get(f"/reservations?start={start}&end={end}")
#     assert response.status_code == 200
#     assert 'reservations' in response.json()
#     assert len(response.json()['reservations']) > 0

# def test_get_no_reservations_by_date(client):
#     start = "2010-01-01 11:00"
#     end = "2010-12-31 14:00" 
#     response = client.get(f"/reservations?start={start}&end={end}")
#     assert response.status_code == 200
#     assert 'reservations' not in response.json()
#     assert 'message' in response.json()
#     assert response.json()['message'] == "No reservations found in this date range"

# def test_post_reservation(client):
#     data = {
#         "customer_name": "testcustomer",
#         "machine_name": "scanner",
#         "start_date": "2024-04-25 11:00",
#         "end_date": "2024-04-25 11:30"
#     }
    
#     response = client.post("/reservations", json=data)
#     assert response.status_code == 201
#     assert 'message' in response.json()
#     assert response.json()['message'] == "Reservation added successfully!"
