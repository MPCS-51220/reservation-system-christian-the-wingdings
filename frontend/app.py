import requests
import json
import hashlib
import os
import sqlite3
from getpass import getpass
from datetime import datetime

BASE_URL = "http://localhost:8000"

def validate_datetime(date):
    try:
        datetime.strptime(date, '%Y-%m-%d %H:%M')
        return True
    except ValueError:
        return False

def connect_db():
    return sqlite3.connect('../reservationDB.db')

def hash_password(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()

def login():
    login_username = input("Enter username: ")
    password = getpass("Enter password: ")
    
    try:
        response = requests.get(f"{BASE_URL}/login/{login_username}")
        user = None
        if response.status_code == 200:
            user_data = response.json()
            if 'user' in user_data:
                user = user_data['user']
        if user:
            hashed_password = hash_password(password, user['salt'])

            if hashed_password == user['password_hash'] == '4d997b5e8d99318eb2d0a062a8a7b5901e16afcc0db7c114ec5c8c9ad5d1b215':
                print("You currently are using a temp password and need to change it: ")
                global username, role
                username = login_username
                role = user['role']
                change_user_password()
                return login_username, user['role']
            elif hashed_password == user['password_hash']:
                return login_username, user['role']  # Return the role of the user
            else:
                print("Incorrect password")
        else:
            print("User not found")
    except Exception as e:
        print(f"Database error: {str(e)}")
    return None, None

def logout():
    global username, role
    username = None
    role = None
    print("Logged out successfully. Returning to login page.")

def get_machine_choice():
    """
    This function gets the user's choice of machine
    """
    print("\n\n1. Multi-phasic radiation scanner\n2. Ore scooper\n3. 1.21 gigawatt lightning harvester\n\n")
    choice = input("\nEnter your machine choice: ")
    if choice == '1':
        machine = "scanner"
    elif choice == '2':
        machine = "scooper"
    elif choice == '3':
        machine = "harvester"
    else:
        print("\nInvalid choice. Back to the main menu\n")
        return
    return machine

def make_reservation():
    if role not in ['admin', 'scheduler', 'customer']:
        print("You do not have permission to make reservations.")
        return

    try:
        if role == 'customer':
            customer_name = username  # Customers can only make reservations for themselves
        else:
            customer_name = input("\nEnter customer name: ")  # Schedulers can make reservations for anyone
        
        machine = get_machine_choice()
        if not machine:
            return    
        start_date = input("\nEnter start date (YYYY-MM-DD HH:MM): ")
        end_date = input("\nEnter end date (YYYY-MM-DD HH:MM): ")

        if not validate_datetime(start_date) or not validate_datetime(end_date):
            print("\nInvalid date. Please use the specified format.\n")
            return

        data ={
            "customer_name": customer_name,
            "machine_name": machine,
            "start_date": start_date,
            "end_date": end_date
        }
        
        response = requests.post(f"{BASE_URL}/reservations", json=data)
        if response.status_code == 201:
            print("\nReservation added successfully")
        else:
            error_detail = response.json().get('detail', 'Unknown error occurred')
            print(f"\nError occurred while adding reservation: {error_detail}")
    except Exception as e:
        print(f"\nError occurred while adding reservation: {str(e)}")

def cancel_reservation():
    if role not in ['admin', 'scheduler', 'customer']:
        print("You do not have permission to cancel reservations.")
        return

    try:
        reservation_id = input("\nEnter id of the reservation to cancel: ")
        if role == 'customer':
            # Verify that the reservation belongs to the logged-in customer
            
            response = requests.get(f"{BASE_URL}/reservations/id/{reservation_id}")
            reservation = None
            if response.status_code == 200:
                reserv_data = response.json()
                if 'reserv' in reserv_data:
                    reservation = reserv_data['reserv']
            if reservation is None:
                print("Reservation not found.")
                return
            elif reservation['customer'] != username: # assume customer in reservation is username of user
                print("You can only cancel your own reservations.")
                return

            response = requests.delete(f"{BASE_URL}/reservations/{reservation_id}")
        else:
            response = requests.delete(f"{BASE_URL}/reservations/{reservation_id}")
        if response.status_code == 200:
            refund = response.json()['refund']
            print("\nReservation cancelled successfully\nRefund amount: ", refund)
        else:
            print(response.json()['detail'])
    except Exception as e:
        print("\nAn error occurred ", str(e))

def list_reservations():
    if role not in ['admin', 'scheduler', 'customer']:
        print("You do not have permission to view reservations.")
        return

    if role in ['admin', 'scheduler']:
        print("\n\n1. List reservations for a given date range\n")
        print("2. List the reservations for a given machine for a given date range\n")
        print("3. List the reservations for a given customer for a given date range\n\n")
        choice = input("\nEnter your choice: ")
        start_date = input("\nEnter start date (YYYY-MM-DD HH:MM)  :")
        end_date = input("\nEnter end date (YYYY-MM-DD HH:MM)  :")
        params = {
            "start": start_date,
            "end": end_date
        } # url parameters

        try:
            if choice == '1':
                response = requests.get(f"{BASE_URL}/reservations", params=params)

            elif choice == '2':
                machine = get_machine_choice()
                if not machine:
                    return    
                response = requests.get(f"{BASE_URL}/reservations/machines/{machine}", params=params)

            elif choice == '3':
                customer = input("\nEnter customer name: ")  # Schedulers can make reservations for anyone
                response = requests.get(f"{BASE_URL}/reservations/customers/{customer}", params=params)

            else:
                print("Invalid choice. Back to the main menu")
                return

            if response.status_code == 200:
                reservations_data = response.json()
                if 'reservations' in reservations_data:
                    data = reservations_data['reservations']
                    print(json.dumps(data, indent=2))
                else: # no reservations found
                    print(response.json()['message'])

            else:
                print(response.json()['detail'])

        except Exception as e:
            print("Error occurred in retrieving reservations ", str(e))
    else:
        # in the customer case
        print("\n\n1. List reservations for a given date range\n")
        print("2. List the reservations for a given machine for a given date range\n")
        choice = input("\nEnter your choice: ")
        start_date = input("\nEnter start date (YYYY-MM-DD HH:MM)  :")
        end_date = input("\nEnter end date (YYYY-MM-DD HH:MM)  :")
        params = {
            "start": start_date,
            "end": end_date
        } # url parameters

        try:
            customer = username
            if choice == '1':
                response = requests.get(f"{BASE_URL}/reservations/customers/{customer}", params=params)

            elif choice == '2':
                machine = get_machine_choice()
                if not machine:
                    return    
                response = requests.get(f"{BASE_URL}/reservations/machines/{machine}/customers/{customer}", params=params)

            else:
                print("Invalid choice. Back to the main menu")
                return

            if response.status_code == 200:
                reservations_data = response.json()
                if 'reservations' in reservations_data:
                    data = reservations_data['reservations']
                    print(json.dumps(data, indent=2))
                else: # no reservations found
                    print(response.json()['message'])

            else:
                print(response.json()['detail'])

        except Exception as e:
            print("Error occurred in retrieving reservations ", str(e))

# admin management
def add_user():
    if role != 'admin':
        print("Unauthorized access. Only admins can add users.")
        return
    
    username = input("Enter new username: ")
    user_role = input("Enter user role (customer, scheduler, admin): ")
    password_hash = hash_password('temp', 'random_salt')

    data ={
            "username": username,
            "password_hash": password_hash,
            "salt": 'random_salt',
            "role": user_role
        }
        
    response = requests.post(f"{BASE_URL}/users", json=data)
    if response.status_code == 201:
        print("\nUser added successfully")
    else:
        error_detail = response.json().get('detail', 'Unknown error occurred')
        print(f"\nError occurred while adding user: {error_detail}")

def remove_user():
    if role != 'admin':
        print("Unauthorized access. Only admins can remove users.")
        return
    
    username_to_remove = input("Enter username of the user to remove: ")
    try:
        response = requests.get(f"{BASE_URL}/users/admincheck/{username_to_remove}")
        count, user_role = None, None
        if response.status_code == 200:
            data = response.json()
            count =  data['count']
            user_role =  data['user_role']
        if count is None or user_role is None:
            print("admincheck unsuccessful.")
            return
        if count <= 1 and user_role == 'admin':
            print("Cannot remove the last admin.")
            return
        
        response = requests.delete(f"{BASE_URL}/users/{username_to_remove}")
        print("User removed successfully.")
    except Exception as e:
        print("Failed to remove user: ", str(e))

def change_user_role():
    if role != 'admin':
        print("Unauthorized access. Only admins can change user roles.")
        return
    
    username_to_change = input("Enter username of the user to change role: ")
    new_role = input("Enter new role (customer, scheduler, admin): ")
    try:
        response = requests.get(f"{BASE_URL}/users/admincheck/{username_to_change}")
        count, user_role = None, None
        if response.status_code == 200:
            data = response.json()
            count =  data['count']
            user_role =  data['user_role']
        if count is None or user_role is None:
            print("admincheck unsuccessful.")
            return
        if count <= 1 and user_role == 'admin':
            print("Cannot change role of the last admin.")
            return

        response = requests.patch(f"{BASE_URL}/users/{username_to_change}/roles/{new_role}")
        print("User role updated successfully.")
    except Exception as e:
        print("Failed to change user role: ", str(e))

def change_user_password():
    try:
        # Enter new password
        new_password = getpass("Enter your new password: ")

        # Hash the new password
        new_salt = os.urandom(32).hex()  # Generate a new salt
        new_hashed_password = hash_password(new_password, new_salt)
        
        customer_name = username  # Customers can only make reservations for themselves

        data ={
            "username": customer_name,
            "password_hash": new_hashed_password,
            "salt": new_salt,
            "role": role
        }

        # Update the password in the database
        response = requests.patch(f"{BASE_URL}/password/update", json=data)
        print("Password changed successfully.")
        
    except Exception as e:
        print(f"Error while changing password: {str(e)}")


def reset_password():
    if role != 'admin':
        print("Unauthorized access. Only admins can change user roles.")
        return
    
    username_to_change = input("Enter username of the user to reset their password: ")
    try:

        data ={
            "username": username_to_change,
            "password_hash": '4d997b5e8d99318eb2d0a062a8a7b5901e16afcc0db7c114ec5c8c9ad5d1b215',
            "salt": 'random_salt',
            "role": role
        }

        # Update the password in the database
        response = requests.patch(f"{BASE_URL}/password/update", json=data)
        print("Password reset successfully.")
    except Exception as e:
        print("Failed to reset password: ", str(e))


# UI
def show_menu_by_role(role):
    actions = {
        'customer': ["1. Make reservation", "2. Cancel reservation", "3. List reservations", "4. Change My Password", "5. Logout", "6. Exit"],
        'scheduler': ["1. Make reservation", "2. Cancel reservation", "3. List reservations", "4. Change My Password", "5. Logout", "6. Exit"],
        'admin': ["1. Make reservation", "2. Cancel reservation", "3. List reservations", "4. Change My Password", "5. Logout", "6. Exit", "7. Add user", "8. Remove user", "9. Change user role", "10. Reset Password"]
    }
    if role in actions:
        return actions[role]
    return []

def main():
    print("\nWelcome to the Reservation System!\n")
    global username, role
    while True:
        username, role = login()
        print("\n")
        break_outer = False
        if username is not None:
            while True:
                options = show_menu_by_role(role)
                if not options:
                    print("No available actions for this role.")
                    return
                for option in options:
                    print(option)
                
                choice = input("\nEnter your choice: ")
                if choice == '1':
                    make_reservation()
                elif choice == '2':
                    cancel_reservation()
                elif choice == '3':
                    list_reservations()
                elif choice == '4':
                    change_user_password()
                elif choice == '5':
                    logout()
                    break
                elif choice == '6':
                    break_outer = True
                    break
                elif choice == '7' and role == 'admin':
                    add_user()
                elif choice == '8' and role == 'admin':
                    remove_user()
                elif choice == '9' and role == 'admin':
                    change_user_role()
                elif choice == '10' and role == 'admin':
                    reset_password()
                else:
                    print("Invalid choice, please try again")
        if break_outer:
            break
        

if __name__ == "__main__":
    main()
