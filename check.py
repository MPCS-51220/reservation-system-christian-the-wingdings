import sqlite3

with sqlite3.connect('reservationDB.db') as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM User")
    res=cursor.fetchall()
    print(res)

# import requests

# try:
#     data={"username":"graham"}
#     response = requests.patch('http://localhost:8000/users/deactivate',params=data)
#     print(response)
# except Exception as e:
#     print(e)