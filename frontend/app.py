import requests
import json

BASE_URL = "http://localhost:8000/"

def get_machine_choice():
    print("\n1. Multi-phasic radiation scanner\n2. Ore scooper\n3. 1.21 gigawatt lightning harvester")
    choice = input("\nEnter your machine choice: ")
    if choice == '1':
        machine = "scanner"
    elif choice == '2':
        machine = "scooper"
    elif choice == '3':
        machine = "harvester"
    else:
        print("Invalid choice. Back to the main menu")
        return
    return machine

def make_reservation():
    try:
        customer_name = input("Enter customer name")
        machine = get_machine_choice()
        if not machine:
            return    
        start_date = input("Enter start date (YYYY-MM-DD): ")
        data ={
            "customer": customer_name,
            "machine": machine,
            "start_date": start_date
        }
        
        response = requests.post(f"{BASE_URL}/reservations", json=data)
        if response.status_code == 201:
            print("Reservation added successfully")
        else:
            print("Failed to add reservation")
    except Exception as e:
        print("Error while adding reservation ", str(e))

def cancel_reservation():
    try:
        reservation_id = input("Enter id of the reservation to cancel")
        response = requests.delete(f"{BASE_URL}/reservations/{reservation_id}")
        if response.status_code == 200:
            refund = response.json()['refund']
            print("Reservation cancelled successfully\nRefund amount: ", refund)
    except Exception as e:
        print("Reservation not found")


def list_reservations():
    print("1. List reservations for a given date range\n\
          2. List the reservations for a given machine for a given date range\n\
          3. List the reservations for a given customer for a given date range")
    choice = input("\nEnter your choice: ")
    start_date = input("\nEnter start date (YYYY-MM-DD)  :")
    end_date = input("\nEnter end date (YYYY-MM-DD)  :")
    params = {
        "start": start_date,
        "end": end_date
    }

    try: 
        if choice == '1':
            response = requests.get(f"{BASE_URL}/reservations", params=params)

        elif choice == '2':
            machine = get_machine_choice()
            if not machine:
                return    
            response = requests.get(f"{BASE_URL}/reservations/machines/{machine}", params=params)

        elif choice == '3':
            customer = input("Enter customer name: ")
            response = requests.get(f"{BASE_URL}/reservations/customers/{customer}", params=params)

        else:
            print("Invalid choice. Back to the main menu")
            return
        
        if 'reservations' in response:
            print(response['reservations'])
        else:
            print(response['message'])

    except Exception as e:
        print("Error occurred in retrieving reservations ",str(e))

def exit_system():
    try:
        choice = input("Do you want to save your changes? Y/N")
        if choice.lower() == 'y':
            params={'persist_status':True}
        else:
            params={'persist_status':False}
        requests.get(f"{BASE_URL}/exit",params=params)
    except Exception as e:
        print("Error while saving changes ",str(e))

def main():
    while True:
        print("Welcome to the Reservation System!")
        print("\n1. Make reservation\n\
              2. Cancel reservation\n\
              3. List reservations\n\
              4. Quit")
        choice = input("Enter your choice")
        if choice == '1':
            make_reservation()
        elif choice == '2':
            cancel_reservation()
        elif choice == '3':
            list_reservations()
        elif choice == '4':
            exit_system()
            break
        else:
            print("Invalid choice, please try again")


if __name__ == "__main__":
    main()
