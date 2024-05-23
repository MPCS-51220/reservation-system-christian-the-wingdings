import requests

API_KEY = "b456e6d5ae43d16ce9d9e1fe2d5014258ccc73f12c237368400e6528a217af59"

def main():
    print("Make your request for a remote reservation\n")
    try:
        start_date = input("Enter start date (YYYY-MM-DD HH:MM): ")
        end_date = input("Enter end date (YYYY-MM-DD HH:MM): ")
        client_name = input("Enter client's name: ")
        machine_name = input("Enter machine name: ")
        time_zone = input("Enter your time zone (example: GMT-5)")
        
        data={
                "start_time":start_date,
                "end_time":end_date,
                "client_name":client_name,
                "machine_name":machine_name,
                "time_zone":time_zone,
                "blocks":"Null"
            }
        
        headers={"API-Key":API_KEY}
        response = requests.post('http://linux1:51221/outside-requests',json=data, headers=headers)
        message = response.json()

        if message.get("reservation_made_success"): # reservation made
            # get cost and downpayment from response
            cost, down_payment = message['message'].split(",")
            cost=float(cost[1:])
            down_payment=float(down_payment[:-1])
            print("Reservation made successfully")
            print("Cost: ", cost)
            print("Down payment: ", down_payment)
        else:
            print(message) # print response message

    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()