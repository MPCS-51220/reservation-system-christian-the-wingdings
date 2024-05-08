import uuid
from datetime import datetime, date
import sqlite3

class Reservation:
    '''
    A class to manage information assiciated with a single reservation for a machine.

    This class provides a way to create a reservation object which includes details
    such as reservation ID, customer name, machine name, date range, cost, and down payment.

    Attributes:
        id (uuid.UUID): Unique identifier for the reservation.
        customer (str): Name of the customer making the reservation.
        machine (str): Name of the machine being reserved.
        daterange (DateRange): The range of dates for which the machine is reserved.
        cost (float): Total cost of the reservation.
        down_payment (float): Required down payment for the reservation.

    Methods:
        calculate_cost(): Calculates the total cost of the reservation.
        calculate_down_payment(): Calculates the required down payment.
        calculate_refund(): Calculates the refund for a cancelled reservation
    '''
    def __init__(self, customer_name, machine_name, daterange):
        self.id = str(uuid.uuid4())
        self.customer = customer_name
        self.machine = machine_name
        self.daterange = daterange
        self.cost = self.calculate_cost() - self.calculate_discount()
        self.down_payment = self.calculate_down_payment()

    def calculate_cost(self):

        if self.machine == "harvester":
            return 88000 # explicit cost for harvester as defined in the requirements
        if self.machine == "scooper": 
            return self.daterange.hours() * 1000 # cost per hour for scooper as defined in the requirements
        if self.machine == "scanner":    
            return self.daterange.hours() * 990 # cost per hour for scanner as defined in the requirements

    def calculate_discount(self):
        # Early bird discount of 25% if reservation is made more than 13 days in advance
        if (self.daterange.start_date - datetime.now()).days > 13:
            return self.calculate_cost()*0.25
        else:
            return 0
    
    def calculate_down_payment(self):
        return self.cost * 0.5


def calculate_refund(start_date, down_payment):
    # calculate refund based on number of advance days of cancellation
    start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
    advance_days = (start_date - datetime.now()).days
    if advance_days >= 7:
        refund = 0.75 * down_payment
    elif advance_days >= 2:
        refund = 0.5 * down_payment
    else:
        refund = 0
    return refund

class ReservationCalendar:
    '''
    A class to manage a collection of reservations.

    This class provides methods to load, retrieve, add, and remove reservations from a calendar.

    Attributes:
        reservations (dict of Reservation): A dict of reservations.

    Methods:
        load_reservations(): Loads reservations from a data source outside of backend folder at path: ../calendar.pkl.
        retrieve_by_date(daterange): Retrieves reservations by date range.
        retrieve_by_machine(daterange, machine): Retrieves reservations by machine within a date range.
        retrieve_by_customer(daterange, customer): Retrieves reservations by customer within a date range.
        add_reservation(reservation): Adds a new reservation to the calendar.
        remove_reservation(reservation_id): Removes a reservation from the calendar.
        save_reservations(): Saves current reservations to a data source.
    '''


    def get_db(self):
        """
        Connect to database
        """
        try:
            conn = sqlite3.connect('../reservationDB.db')
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            print("Error while connecting to database: ",str(e))
            raise
        
    def retrieve_by_date(self, daterange):

        try:

            start = daterange.start_date.strftime('%Y-%m-%d %H:%M')
            end = daterange.end_date.strftime('%Y-%m-%d %H:%M')
            
            query = "SELECT * FROM Reservation WHERE datetime(start_date) <= datetime(?) AND datetime(end_date) >= datetime(?)"
            conn = self.get_db()
            cursor = conn.cursor()
            cursor.execute(query, (end, start))
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]      

        except sqlite3.Error as e:
            print("Database error: ",str(e))
            raise

    
     
    def retrieve_by_machine(self, daterange, machine):

        try:

            start = daterange.start_date.strftime('%Y-%m-%d %H:%M')
            end = daterange.end_date.strftime('%Y-%m-%d %H:%M')
            query = """
            SELECT Reservation.* FROM Reservation
            JOIN Machine ON Reservation.machine_id = Machine.machine_id
            WHERE Machine.name = ?
            AND datetime(Reservation.start_date) <= datetime(?)
            AND datetime(Reservation.end_date) >= datetime(?)
            """ # join with Reservation and Machine table
            conn = self.get_db()
            cursor = conn.cursor()
            cursor.execute(query, (machine, end, start))
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]   
        
        except sqlite3.Error as e:
            print("Database error: ",str(e))
            raise
        
    
    def retrieve_by_customer(self, daterange, customer):

        try:
            start = daterange.start_date.strftime('%Y-%m-%d %H:%M')
            end = daterange.end_date.strftime('%Y-%m-%d %H:%M')
            query = """
            SELECT * FROM Reservation WHERE customer = ? 
            AND datetime(start_date) <= datetime(?)
            AND datetime(end_date) >= datetime(?)
            """
            conn = self.get_db()
            cursor = conn.cursor()
            cursor.execute(query, (customer, end, start))
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows] 
        
        except sqlite3.Error as e:
            print("Database error: ",str(e))
            raise
    
    
    def add_reservation(self, reservation):
        self._verify_business_hours(reservation)
        self._check_equipment_availability(reservation)

        try:
            conn = self.get_db()
            cursor = conn.cursor()
            # get machine id
            cursor.execute("SELECT machine_id from Machine WHERE name = ?", (reservation.machine,))
            machine_id = cursor.fetchone()
            if not machine_id:
                raise ValueError("Machine not found")

            query = """
            INSERT INTO Reservation (reservation_id, customer, machine_id, 
            start_date, end_date, total_cost, down_payment) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cursor.execute(query,(reservation.id, reservation.customer, machine_id[0],
                                    reservation.daterange.start_date, reservation.daterange.end_date,
                                    reservation.cost, reservation.down_payment))
            conn.commit()
            conn.close()

        except sqlite3.Error as e:
            print("Database error: ",str(e))
            raise
        

    
    def remove_reservation(self, reservation_id):

        try:
            query = "SELECT start_date, down_payment FROM Reservation WHERE reservation_id = ?"
            conn = self.get_db()
            cursor = conn.cursor()
            cursor.execute(query, (reservation_id,))
            row = cursor.fetchone()
            if row: # check if reservation exists
                start_date = row[0]
                down_payment = row[1]
                refund = calculate_refund(start_date, down_payment)
                query = "DELETE FROM Reservation WHERE reservation_id = ?"
                cursor.execute(query,(reservation_id,))
                conn.commit()
                return refund
            return False
        
        except sqlite3.Error as e:
            print("Database error: ",str(e))
            raise
    

    def _verify_business_hours(self, reservation):
        # Check if the reservation is on a Sunday
        if reservation.daterange.start_date.weekday() == 6:
            raise ValueError("Reservations cannot be made on Sundays.")

        # Check Saturday hours
        if reservation.daterange.start_date.weekday() == 5:
            if (reservation.daterange.start_date.time() > datetime.strptime("16:00", "%H:%M").time() or
                reservation.daterange.end_date.time() > datetime.strptime("16:00", "%H:%M").time() or
                reservation.daterange.start_date.time() < datetime.strptime("10:00", "%H:%M").time() or
                reservation.daterange.end_date.time() < datetime.strptime("10:00", "%H:%M").time()):
                raise ValueError("Reservations on Saturdays must be between 10:00 and 16:00.")

        # Check weekday hours
        if reservation.daterange.start_date.weekday() < 5:
            if (reservation.daterange.start_date.time() < datetime.strptime("9:00", "%H:%M").time() or
                reservation.daterange.end_date.time() > datetime.strptime("18:00", "%H:%M").time()):
                raise ValueError("Reservations on weekdays must be between 9:00 and 18:00.")

        # Check if the reservation is more than 30 days in advance
        if (reservation.daterange.start_date.date() - date.today()).days > 30:
            raise ValueError("Reservations cannot be made more than 30 days in advance.")
        
    def _check_equipment_availability(self, reservation):

        overlapping_reservations = self.retrieve_by_date(reservation.daterange)

        # Count how many scanners, harvesters, and scoopers are reserved in the overlapping period
        scanner_count = 0
        harvester_reserved = False
        scooper_count = 0

        for res in overlapping_reservations:
            if res['machine'] == "scanner":
                scanner_count += 1
            if res['machine'] == "harvester":
                harvester_reserved = True
            if res['machine'] == "scooper":
                scooper_count += 1

        # Check constraints for scanners
        if reservation.machine == "scanner":
            if scanner_count >= 3:
                raise ValueError("Maximum number of scanners already reserved for this time period.")
            if harvester_reserved:
                raise ValueError("Scanners cannot operate while the harvester is in use.")

        # Check if the reservation is for a harvester and if any scanner is reserved
        if reservation.machine == "harvester":
            if scanner_count > 0:
                raise ValueError("The harvester cannot operate while scanners are in use.")
            if harvester_reserved:
                raise ValueError("The harvester is already reserved for this time period.")

        # Check constraints for scoopers
        if reservation.machine == "scooper":
            if scooper_count >= 3:  # Since there are 4 scoopers, we can reserve up to 3 at the same time
                raise ValueError("Only one scooper must remain available; maximum number already reserved.")

        # General check for other machines (if more types are added in the future)
        if reservation.machine not in ["scanner", "harvester", "scooper"]:
            raise ValueError("Please select from one of our specified machines: scanner, harvester, scooper.")


class DateRange:
    '''
    A class to represent a range of dates and handle their formatting and comparison.

    Attributes:
        start_date (datetime): The start date of the range.
        end_date (datetime): The end date of the range.
    
    Methods:
        hours(): Calculate the number of hours between the start and end date.
        start(): Return the start date of the range.


    '''
    def __init__(self, start_date, end_date):
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M")

    def __eq__(self, other) -> bool:
        # two date ranges are equal if their is any overlap between them
        return (self.start_date <= other.end_date and self.end_date >= other.start_date) or \
        (other.start_date <= self.end_date and other.end_date >= self.start_date)
    
    def hours(self):
        return int((self.end_date - self.start_date).total_seconds() / 3600)
