import requests
import json

BASE_URL = "http://localhost:8000"

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
        print("Invalid choice. Back to the main menu")
        return
    return machine

def make_reservation():
    try:
        customer_name = input("\nEnter customer name: ")
        machine = get_machine_choice()
        if not machine:
            return    
        start_date = input("\nEnter start date (YYYY-MM-DD HH:MM): ")
        end_date = input("\nEnter end date (YYYY-MM-DD HH:MM): ")

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
            print(f"Error occurred while adding reservation: {error_detail}")
    except Exception as e:
        print(f"Error occurred while adding reservation: {str(e)}")

def cancel_reservation():
    try:
        reservation_id = input("\nEnter id of the reservation to cancel: ")
        response = requests.delete(f"{BASE_URL}/reservations/{reservation_id}")
        if response.status_code == 200:
            refund = response.json()['refund']
            print("\nReservation cancelled successfully\nRefund amount: ", refund)
        else:
            print(response.json()['detail'])
    except Exception as e:
        print("An error occurred ", str(e))


def list_reservations():
    print("\n\n1. List reservations for a given date range\n")
    print("2. List the reservations for a given machine for a given date range\n")
    print("3. List the reservations for a given customer for a given date range\n\n")
    choice = input("\nEnter your choice: ")
    start_date = input("\nEnter start date (YYYY-MM-DD HH:MM)  :")
    end_date = input("\nEnter end date (YYYY-MM-DD HH:MM)  :")
    params = {
        "start": start_date,
        "end": end_date
    } # url paramaters

    try: 
        if choice == '1':
            response = requests.get(f"{BASE_URL}/reservations", params=params)

        elif choice == '2':
            machine = get_machine_choice()
            if not machine:
                return    
            response = requests.get(f"{BASE_URL}/reservations/machines/{machine}", params=params)

        elif choice == '3':
            customer = input("\nEnter customer name: ")
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
        print("Error occurred in retrieving reservations ",str(e))


def main():
    while True:
        print("\nWelcome to the Reservation System!\n")
        print("\n\n1. Make reservation\n2. Cancel reservation\n3. List reservations\n4. Quit\n\n")
        choice = input("\nEnter your choice: ")
        if choice == '1':
            make_reservation()
        elif choice == '2':
            cancel_reservation()
        elif choice == '3':
            list_reservations()
        elif choice == '4':
            break
        else:
            print("Invalid choice, please try again")


if __name__ == "__main__":
    main()
