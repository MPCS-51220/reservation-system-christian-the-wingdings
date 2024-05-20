import sqlite3

with sqlite3.connect('reservationDB.db') as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Remote_Reservation")
    res=cursor.fetchall()
    print(res)

import requests

# try:
#     data={"username":"graham"}
#     response = requests.patch('http://localhost:8000/users/deactivate',params=data)
#     print(response)
# except Exception as e:
#     print(e)

# try:
#     data={
#             "start_time":"2024-05-28 12:00",
#             "end_time":"2024-05-28 13:00",
#             "client_name":"rishika",
#             "machine_name":"scooper",
#             "time_zone":"GMT-6",
#             "blocks":"Null"
#         }
#     headers={"API-Key":"b456e6d5ae43d16ce9d9e1fe2d5014258ccc73f12c237368400e6528a217af59"}
#     response = requests.post('http://localhost:8000/outside-requests',json=data, headers=headers)
#     print(response.json())

# except Exception as e:
#     print(e)

