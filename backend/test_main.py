from fastapi.testclient import TestClient
from fastapi import Request, HTTPException, status
import time
from permissions import role_required, validate_user, validate_user_token, check_role_permissions, RoleNotFoundError, PermissionDeniedError
from token_manager import create_access_token, decode_access_token, SECRET_KEY, ALGORITHM, ExpiredTokenError, InvalidTokenError, TokenCreationError
import sqlite3
from datetime import datetime, timedelta, timezone
from jose import jwt, ExpiredSignatureError, JWTError
from modules import DateRange, Reservation, ReservationCalendar, UserManager, DatabaseManager, BusinessManager
import pytest
from main import app
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
    
@pytest.fixture(scope="session", autouse=True)
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


@pytest.fixture(scope="session")
def db_manager(db):
    # Instantiate DatabaseManager with the in-memory database connection
    return DatabaseManager(connection=db)


@pytest.fixture
def user_manager(db_manager):
    return UserManager(db_manager)

@pytest.fixture
def biz_manager(db_manager):
    return BusinessManager(db_manager)

@pytest.fixture
def calendar(db_manager):
    return ReservationCalendar(db_manager)

############ Database Tests ############


############ API ROUTES Tests ############
# @pytest.mark.parametrize("username, password, expected_status, expected_detail", [
#     ("adminTest", "adminpass", 200, None),  # Successful login
#     ("adminTest", "wrongpass", 401, "Incorrect username or password"),  # Incorrect password
#     (None, "adminpass", 422, None),  # Missing username
#     ("adminTest", None, 422, None),  # Missing password
#     (None, None, 422, None)  # Empty payload
# ])
# def test_login(client, setup_db, transaction, username, password, expected_status, expected_detail):
#     payload = {}
#     if username is not None:
#         payload["username"] = username
#     if password is not None:
#         payload["password"] = password

#     response = client.post("/login", json=payload)
#     assert response.status_code == expected_status
#     if expected_detail:
#         assert response.json()["detail"] == expected_detail
#     elif expected_status == 200:
#         assert "access_token" in response.json()
#         assert response.json()["token_type"] == "bearer"



############ Modules Tests ############





def test_get_user(setup_db, user_manager):
    result = user_manager.get_user("adminTest")
    assert result is not None
    assert result['username'] == 'adminTest'
    assert result['role'] == "admin"

def test_get_user_fail(setup_db, user_manager):
    result = user_manager.get_user("fakeuser")
    assert result is None

def test_add_user(setup_db, user_manager, transaction):
    username = "Testuser"
    password = "testuser"
    role = "customer"
    salt= "test_salt"
    res = user_manager.add_user(username, password, role, salt)
    assert res is not None
    assert res == True
    user = user_manager.get_user(username)
    assert user is not None
    assert user['username'] == username

def test_authenticate_user(setup_db, user_manager):
    result = user_manager.authenticate_user("adminTest", "adminpass")
    assert result is not None
    assert result != False
    assert result['username'] == "adminTest"

def test_authenticate_user_fail(setup_db, user_manager):
    result = user_manager.authenticate_user("fake", "adminpass")
    assert result == False

def test_update_role(setup_db, user_manager):
    user_manager.update_user_role("scheduler","adminTest")
    user = user_manager.get_user("adminTest")
    assert user is not None
    assert user['role'] == "scheduler"

def test_list_users(setup_db, user_manager):
    result = user_manager.list_users()
    assert result is not None

def test_deactivate(setup_db, user_manager):
    user_manager.deactivate_user("adminTest")
    result = user_manager.is_user_active("adminTest")
    assert result == False

def test_activate(setup_db, user_manager):
    user_manager.activate_user("adminTest")
    result = user_manager.is_user_active("adminTest")
    assert result == True


def test_retrieve_by_date(setup_db, calendar):
    daterange = DateRange("2024-01-01 10:00","2025-01-01 10:00")
    result = calendar.retrieve_by_date(daterange)
    assert result is not None    
    assert len(result) > 0

def test_retrieve_by_date_empty(setup_db, calendar):
    daterange = DateRange("2010-01-01 10:00","2011-01-01 10:00")
    result = calendar.retrieve_by_date(daterange)
    assert result is not None    
    assert len(result) == 0


def test_retrieve_by_machine(setup_db, calendar):
    daterange = DateRange("2024-01-01 10:00","2025-01-01 10:00")
    result = calendar.retrieve_by_machine(daterange, "scanner")
    assert result is not None    
    assert len(result) > 0

def test_retrieve_by_machine_empty(setup_db, calendar):
    daterange = DateRange("2024-01-01 10:00","2025-01-01 10:00")
    result = calendar.retrieve_by_machine(daterange, "fakemachine")
    assert result is not None    
    assert len(result) == 0

def test_retrieve_by_customer(setup_db, calendar):
    daterange = DateRange("2024-01-01 10:00","2025-01-01 10:00")
    result = calendar.retrieve_by_customer(daterange, "akshatha")
    assert result is not None    
    assert len(result) > 0


def test_retrieve_by_customer_empty(setup_db, calendar):
    daterange = DateRange("2024-01-01 10:00","2025-01-01 10:00")
    result = calendar.retrieve_by_customer(daterange, "fakecustomer")
    assert result is not None    
    assert len(result) == 0

def test_add_reservation(setup_db, transaction, calendar, biz_manager):
    daterange = DateRange("2024-06-20 11:00","2025-06-20 12:00")
    reservation = Reservation("akshatha", "scooper", daterange, biz_manager)
    calendar.add_reservation(reservation)
    result = calendar.retrieve_by_customer(daterange, "akshatha") # reservation should be present
    assert result is not None
    assert len(result) == 1

def test_add_reservation_sunday(setup_db, transaction, calendar, biz_manager):
    daterange = DateRange("2024-06-16 11:00","2025-06-16 12:00")
    reservation = Reservation("fakecustomer", "scooper", daterange, biz_manager)
    with pytest.raises(ValueError):
        calendar.add_reservation(reservation)

def test_add_reservation_future(setup_db, transaction, calendar, biz_manager):
    daterange = DateRange("2024-10-16 11:00","2025-10-16 12:00")
    reservation = Reservation("fakecustomer", "scooper", daterange, biz_manager)
    with pytest.raises(ValueError):
        calendar.add_reservation(reservation)

def test_add_reservation_outside_working_hours(setup_db, transaction, calendar, biz_manager):
    daterange = DateRange("2024-06-10 04:00","2025-06-10 05:00")
    reservation = Reservation("fakecustomer", "scooper", daterange, biz_manager)
    with pytest.raises(ValueError):
        calendar.add_reservation(reservation)


def test_remove_reservation(setup_db, transaction, calendar):
    result = calendar.remove_reservation(3)
    assert result is not None
    assert result != False

def test_remove_reservation_fail(setup_db, transaction, calendar):
    result = calendar.remove_reservation(9000)
    assert result is not None
    assert result == False

def test_get_rule(setup_db, biz_manager):
    value = biz_manager.get_rule("week_refund")
    assert value is not None
    assert isinstance(value, float)

def test_get_rule_fale(setup_db, biz_manager):
    with pytest.raises(AssertionError):
        value = biz_manager.get_rule("harvester_price")
        assert value is not None
        assert isinstance(value, str)












############ Permissions AUTH Tests ############
def test_create_access_token():
    data = {"sub": "testuser", "role": "customer"}
    token = create_access_token(data)
    
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    exp_timestamp = decoded_token["exp"]
    exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    
    assert decoded_token["sub"] == "testuser"
    assert decoded_token["role"] == "customer"
    assert "exp" in decoded_token
    assert exp_datetime <= datetime.now(timezone.utc) + timedelta(minutes=15)
    assert exp_datetime > datetime.now(timezone.utc) + timedelta(minutes=14)

def test_create_access_token_with_expiration():
    data = {"sub": "testuser", "role": "customer"}
    expires_delta = timedelta(minutes=5)
    token = create_access_token(data, expires_delta)
    
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    exp_timestamp = decoded_token["exp"]
    exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    
    assert exp_datetime <= datetime.now(timezone.utc) + timedelta(minutes=5)
    assert exp_datetime > datetime.now(timezone.utc) + timedelta(minutes=4)
    assert decoded_token["sub"] == "testuser"
    assert decoded_token["role"] == "customer"
    assert "exp" in decoded_token

def test_create_access_token_error():
    with pytest.raises(TokenCreationError):
        create_access_token(None)

def test_decode_access_token():
    data = {"sub": "testuser", "role": "customer"}
    token = create_access_token(data)
    
    decoded_token = decode_access_token(token)
    
    assert decoded_token["sub"] == "testuser"
    assert decoded_token["role"] == "customer"

def test_decode_access_token_expired():
    data = {"sub": "testuser", "role": "customer"}
    token = create_access_token(data, timedelta(seconds=1))
    
    # Wait for the token to expire
    import time
    time.sleep(2)
    
    with pytest.raises(ExpiredTokenError) as excinfo:
        decode_access_token(token)
    
    assert "Token has expired" in str(excinfo.value)

def test_decode_access_token_invalid():
    invalid_token = "invalid_token"
    
    with pytest.raises(InvalidTokenError) as excinfo:
        decode_access_token(invalid_token)
    
    assert "Invalid token" in str(excinfo.value)
    
def test_validate_user_token_valid():
    user_data = {"sub": "testuser", "role": "customer"}
    token = create_access_token(user_data)
    auth_header = f"Bearer {token}"
    user, role = validate_user_token(auth_header)
    assert user == "testuser"
    assert role == "customer"

def test_validate_user_token_invalid():
    invalid_token = "invalid_token"
    auth_header = f"Bearer {invalid_token}"
    with pytest.raises(HTTPException) as excinfo:
        validate_user_token(auth_header)
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Invalid token: Invalid token during decoding"

def test_validate_user_token_expired():
    user_data = {"sub": "testuser", "role": "customer"}
    token = create_access_token(user_data, timedelta(seconds=1))
    auth_header = f"Bearer {token}"
    
    # Wait for the token to expire
    import time
    time.sleep(2)
    
    with pytest.raises(HTTPException) as excinfo:
        validate_user_token(auth_header)
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Token has expired: Token has expired"

def test_validate_user_token_no_user_or_role():
    payload = {"sub": 'testuser'}
    token = create_access_token(payload)
    auth_header = f"Bearer {token}"
    with pytest.raises(HTTPException) as excinfo:
        validate_user_token(auth_header)
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Invalid token: no user or role"


def is_customer_accessing_own_data(user_username, **kwargs):
    customer_name = kwargs.get('customer')
    return user_username == customer_name

def test_check_role_permissions_valid():
    roles_permissions = {
        "admin": None,
        "scheduler": None,
        "customer": is_customer_accessing_own_data
    }
    
    # Test valid admin role
    assert check_role_permissions("admin", roles_permissions, "testuser")
    
    # Test valid scheduler role
    assert check_role_permissions("scheduler", roles_permissions, "testuser")
    
    # Test valid customer role accessing own data
    kwargs = {'customer': 'testuser'}
    assert check_role_permissions("customer", roles_permissions, "testuser", **kwargs)
    
    # Test valid customer role when customer name is None
    kwargs = {'customer': None}
    assert check_role_permissions("customer", roles_permissions, "testuser", **kwargs)
    
    # Test invalid role
    with pytest.raises(RoleNotFoundError) as excinfo:
        check_role_permissions("nonexistent_role", roles_permissions, "testuser")
    assert str(excinfo.value) == "Role 'nonexistent_role' not found in permissions."
    
    # Test invalid customer role accessing other user's data
    kwargs = {'customer': 'otheruser'}
    with pytest.raises(PermissionDeniedError) as excinfo:
        check_role_permissions("customer", roles_permissions, "testuser", **kwargs)
    assert str(excinfo.value) == "permissions.PermissionDeniedError: Permission denied for user 'testuser' with role 'customer'."

# def is_customer(user, **kwargs):
#     return user == "customer"

# roles_permissions = {
#     "admin": None,
#     "customer": is_customer,
# }

# @role_required(roles_permissions)
# async def sample_role_endpoint(request: Request):
#     return {"message": "success"}

# def test_role_required_decorator_valid_role(client):
#     user_data = {"sub": "customer", "role": "customer"}
#     token = create_access_token(user_data)

#     request = client.build_request("GET", "/", headers={"Authorization": f"Bearer {token}"})
#     response = client.request("GET", "/", headers={"Authorization": f"Bearer {token}"})
#     assert response.status_code == 200
#     assert response.json() == {"message": "success"}


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
