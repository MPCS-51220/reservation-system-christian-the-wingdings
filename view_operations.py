import sqlite3
from tabulate import tabulate

conn = sqlite3.connect('reservationDB.db')
cursor= conn.cursor()
cursor.execute("""
               SELECT Operation.operation_id, User.username, Operation.timestamp,
               Operation.type, Operation.description
               FROM Operation JOIN User
               ON Operation.user_id = User.user_id
               """
              )

res = cursor.fetchall()
headers = ["Operation ID","Username","Timestamp","Operation Type","Description"] 
print(tabulate(res, headers=headers))