import uuid
from datetime import datetime, date
import sqlite3
import hashlib
from contextlib import contextmanager

class UserManager:
    '''
    A class to manage funtions that need to effect a user.

    This class provides a way to add a user, get a user, 
    verify a password, authenticate a user, and update their password.

    Attributes:
        db_path (str): Path to the database file.
        db_manager (DatabaseManager): An instance of the DatabaseManager class.
        
        
    Methods:
        add_user(username, password, role, salt): Adds a new user to the database.
        hash_password(password, salt): Hashes a password using PBKDF2.
        get_user(username): Retrieves a user from the database.
        verify_password(plain_password, password_hash, salt): Verifies a password against a hash.
        authenticate_user(username, password): Authenticates a user using a username and password.
        update_password(username, password, salt): Updates a user's password in the database.
    '''

    def __init__(self, DatabaseManager, db_connection=None):
        self.db_manager = DatabaseManager
        # self.db_connection = db_connection or sqlite3.connect('../reservationDB.db', check_same_thread=False)
        # print(f"Database connection established at: {self.db_connection}")

    def add_user(self, username, password, role, salt):
        try:
            password_hash = self.hash_password(password, salt)
            query = "INSERT INTO User (username, password_hash, role, salt) VALUES (?, ?, ?, ?)"
            self.db_manager.execute_statement(query, (username, password_hash, role, salt))
            return True
        except sqlite3.Error as e:
            print("Database error: ",str(e))
            raise e
        except Exception as e:
            print(f"Error: {e}")
            raise e

    def hash_password(self, password, salt):
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()

    def get_user(self, username):
        """Retrieve user details from the database."""
        # with self.db_connection as conn:
        #     cursor = conn.cursor()
        #     cursor.execute("SELECT username, password_hash, role, salt FROM User WHERE username = ?", (username,))
        #     row = cursor.fetchone()
        #     if row:
        #         return {"username": row[0], "password_hash": row[1], "role": row[2], "salt": row[3]}
        #     return None
        query = "SELECT username, password_hash, role, salt FROM User WHERE username = ?"
        try:
            result = self.db_manager.execute_query(query, (username,))
            if result:
                return result[0]
        except sqlite3.Error as e:
            print("Database error: ",str(e))
            raise e

    def verify_password(self, plain_password, password_hash, salt):
        """Verify a plaintext password against the hashed version."""
        if password_hash == self.hash_password(plain_password, salt):
            return True
        else:
            return False

    def authenticate_user(self, username: str, password: str):
        """Authenticate a user using username and password."""
        user = self.get_user(username)
        if user and self.verify_password(password, user['password_hash'], user['salt']):
            return user
        return False

    def update_password(self, username, password, salt):
        """Update a user's password in the database."""
        password_hash = self.hash_password(password, salt)
        try:
            password_hash = self.hash_password(password, salt)
            query = "UPDATE User SET password_hash = ?, salt = ? WHERE username = ?"
            self.db_manager.execute_statement(query, (password_hash, salt, username))
            return True
        except sqlite3.Error as e:
            print("Database error: ",str(e))
            raise e
    
    
    def update_user_role(self, new_role, username):
        try:
            query = "UPDATE User SET role = ? WHERE username = ?"
            params = (new_role, username)
            self.db_manager.execute_statement(query, params)
            
        except sqlite3.Error as e:
            print("Database error: ", str(e))
            raise
    
    def remove_user(self, username):

        try:
            query = "DELETE FROM User WHERE username = ?"
            params = (username,)
            self.db_manager.execute_statement(query, params)
               
        except sqlite3.Error as e:
            print("Database error: ",str(e))
            raise

    
    def deactivate_user(self, username):
        """Deactivate a user"""
        try:
            query = "UPDATE User SET is_active = ? WHERE username = ?"
            params = (0, username)
            self.db_manager.execute_statement(query, params)
            
        except sqlite3.Error as e:
            print("Database error: ",str(e))
            raise e
        
    def activate_user(self, username):
        """Activate a user"""
        try:
            query = "UPDATE User SET is_active = ? WHERE username = ?"
            params = (1, username)
            self.db_manager.execute_statement(query, params)
        except sqlite3.Error as e:
            print("Database error: ",str(e))
            raise e
        
    def list_users(self):
        """List users with activation state"""
        try:
            query = "SELECT username, is_active FROM User"
            rows = self.db_manager.execute_query(query)
            return rows
        
        except sqlite3.Error as e:
            print("Database error: ",str(e))
            raise e
        

    def is_user_active(self, username):
        """Check if a user is active"""
        try:
            print(f"Checking if {username} is active")
            query = "SELECT is_active FROM User WHERE username = ?"
            user = self.db_manager.execute_query(query, (username,))
            print(f"User: {user}")
            # if user:
            # and user['is_active']:
            return True
            # return False
        
        except sqlite3.Error as e:
            print("Database error: ",str(e))
            raise e
        except Exception as e:
            print(f"Error: {e}")
            raise e

class DatabaseManager:
    '''
    A class to manage database operations and connections.

    Need to get back to this!

    Raises:
        AttributeError: _description_
        ValueError: _description_

    Returns:
        _type_: _description_
    '''
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path='../reservationDB.db'):
        if not hasattr(self, 'initialized'):
            self.db_path = db_path
            self.initialized = True
            print(f"Database Manager initialized at path: {self.db_path}")

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def execute_query(self, query, params=None):
        """
        Execute a query with optional parameters.
        
        Args:
            query (str): The SQL query to execute.
            params (tuple): The parameters to bind to the query.
        
        Returns:
            list: The result of the query as a list of dictionaries.
        """
        with self.get_connection() as conn:
                cursor = conn.cursor()
                try:
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    conn.commit()
                    rows = cursor.fetchall()
                    print(f'Rows: {rows}')
                    if rows:
                        print(f'Get Connection returned: {[dict(zip([column[0] for column in cursor.description], row)) for row in rows]}')
                        return [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
                    return []
                except sqlite3.Error as e:
                    print(f"Failed to execute query: {e}")
                    raise

    def execute_statement(self, query, params=None):
        """
        Execute a non-query (INSERT, UPDATE, DELETE) with optional parameters.
        
        Args:
            query (str): The SQL query to execute.
            params (tuple): The parameters to bind to the query.
        
        Returns:
            int: The number of rows affected.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                conn.commit()
                return cursor.rowcount
            except sqlite3.Error as e:
                print(f"Failed to execute non-query: {e}")
                raise


class BusinessManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.load_business_rules()

    def load_business_rules(self):
        # Get the column names from the BusinessRules table
        query = "PRAGMA table_info(BusinessRules)"
        column_info = self.db_manager.execute_query(query)
        column_names = [col['name'] for col in column_info]

        # Select the first row from the BusinessRules table
        query = "SELECT * FROM BusinessRules LIMIT 1"
        row = self.db_manager.execute_query(query)
        
        if row:
            row = row[0]  # Get the first row
            print(f'Row: {row} for load_business_rules')
            # Create instance attributes for each column
            for column_name in column_names:
                setattr(self, column_name, row[column_name])

    def get_rule(self, field_name):
        return getattr(self, field_name, None)

    def update_rule(self, field_name, value):
        setattr(self, field_name, value)
        query = f"UPDATE BusinessRules SET {field_name} = ? WHERE rowid = 1"
        self.db_manager.execute_statement(query, (value,))




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
    def __init__(self, customer_name, machine_name, daterange, business_manager):
        self.id = str(uuid.uuid4()) 
        self.biz_manager = business_manager

        self.customer = customer_name
        self.machine = machine_name
        self.daterange = daterange
        self.cost = self.calculate_cost() - self.calculate_discount()
        self.down_payment = self.calculate_down_payment()


    def calculate_cost(self):
        if self.machine == "harvester":
            return self.biz_manager.harvester_price
        if self.machine == "scooper": 
            return self.daterange.hours() * self.biz_manager.scooper_price_per_hour
        if self.machine == "scanner":    
            return self.daterange.hours() * self.biz_manager.scanner_price_per_hour
        
    def calculate_discount(self):
        # Early bird discount of 25% if reservation is made more than 13 days in advance
        if (self.daterange.start_date - datetime.now()).days > 13:
            return self.calculate_cost()*0.25
        else:
            return 0
    
    def calculate_down_payment(self):
        return self.cost * 0.5


    def calculate_refund(self):
        # calculate refund based on number of advance days of cancellation
        start_date = self.daterange.start_date
        
        advance_days = (start_date - datetime.now()).days
        if advance_days >= 7:
            refund = self.biz_manager.week_refund * self.down_payment # 0.75 * down_payment
        elif advance_days >= 2:
            refund = self.biz_manager.two_day_refund * self.down_payment # 0.5 * down_payment
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

    def __init__(self, DatabaseManager):
        
        self.db_manager = DatabaseManager
        self.biz_manager = BusinessManager(DatabaseManager)

    '''def update_settings(self, **kwargs): 
        """
        Updates the settings of the reservation calendar dynamically.
        Accepted kwargs: harvester_price, scooper_price_per_hour, scanner_price_per_hour,
                         number_of_scoopers, number_of_scanners, weekday_hours, weekend_hours.
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"'ReservationCalendar' object has no attribute '{key}'")''' # This is not needed anymore its just a block quote

    # def get_db(self):
    #     """
    #     Connect to database
    #     """
    #     try:
    #         conn = sqlite3.connect('../reservationDB.db')
    #         conn.row_factory = sqlite3.Row
    #         return conn
    #     except sqlite3.Error as e:
    #         print("Error while connecting to database: ",str(e))
    #         raise

    # def login(self, login_username):

    #     try:
    #         conn = self.get_db()
    #         cursor = conn.cursor()
    #         cursor.execute("SELECT password_hash, salt, role FROM User WHERE username = ?", (login_username,))
    #         user = cursor.fetchone()
    #         conn.close()
    #         return user
               
    #     except sqlite3.Error as e:
    #         print("Database error: ",str(e))
    #         raise

    # def retrieve_admin_check(self, username):

    #     try:
    #         conn = self.get_db()
    #         cursor = conn.cursor()
    #         cursor.execute("SELECT COUNT(*) FROM User WHERE role = 'admin'")
    #         count = cursor.fetchone()[0]
    #         cursor.execute("SELECT role FROM User WHERE username = ?", (username,))
    #         user_role = cursor.fetchone()[0]
    #         conn.close()
    #         return count, user_role
               
    #     except sqlite3.Error as e:
    #         print("Database error: ",str(e))
    #         raise

    # def retrieve_by_id(self, reservation_id):

    #     try:
    #         conn = self.get_db()
    #         cursor = conn.cursor()
    #         cursor.execute("SELECT customer FROM Reservation WHERE reservation_id = ?", (reservation_id,))
    #         reserv = cursor.fetchone()
    #         conn.close()
    #         return reserv
               
    #     except sqlite3.Error as e:
    #         print("Database error: ",str(e))
    #         raise

    def retrieve_by_date(self, daterange):

        try:
            start = daterange.start_date.strftime('%Y-%m-%d %H:%M')
            end = daterange.end_date.strftime('%Y-%m-%d %H:%M')
            
            query = """
                SELECT 
                    Reservation.*, 
                    Machine.Name AS machine_name
                FROM Reservation
                JOIN Machine ON Reservation.machine_id = Machine.machine_id
                WHERE datetime(Reservation.start_date) <= datetime(?) 
                    AND datetime(Reservation.end_date) >= datetime(?)
                """
            params = (end, start) # why is this reversed?
            
            result = self.db_manager.execute_query(query, params)
            return result

        except sqlite3.Error as e:
            print("Database error: ", str(e))
            raise
        except Exception as e:
            print(f"Error: {e}")
            raise
    
     
    def retrieve_by_machine(self, daterange, machine):
        try:
            start = daterange.start_date.strftime('%Y-%m-%d %H:%M')
            end = daterange.end_date.strftime('%Y-%m-%d %H:%M')
            
            query = """
            SELECT
                Reservation.*,
                Machine.name AS machine_name
            FROM Reservation
            JOIN Machine ON Reservation.machine_id = Machine.machine_id
            WHERE Machine.name = ?
            AND datetime(Reservation.start_date) <= datetime(?)
            AND datetime(Reservation.end_date) >= datetime(?)
            """
            
            params = (machine, end, start)
            
            result = self.db_manager.execute_query(query, params)
            return result
        
        except sqlite3.Error as e:
            print("Database error: ",str(e))
            raise
        
    
    def retrieve_by_customer(self, daterange, customer):
        try:
            start = daterange.start_date.strftime('%Y-%m-%d %H:%M')
            end = daterange.end_date.strftime('%Y-%m-%d %H:%M')
            
            query = """
            SELECT 
                Reservation.*, 
                Machine.name AS machine_name
            FROM Reservation
            JOIN Machine ON Reservation.machine_id = Machine.machine_id
            WHERE customer = ? 
            AND datetime(Reservation.start_date) <= datetime(?)
            AND datetime(Reservation.end_date) >= datetime(?)
            """
            params = (customer, end, start)
            
            result = self.db_manager.execute_query(query, params)
            print(f"Result: {result}")
            return result

        except sqlite3.Error as e:
            print("Database error: ", str(e))
            raise
        except Exception as e:
            print(f"Error: {e}")
            raise

    
    def retrieve_by_machine_and_customer(self, daterange, machine, customer):
        final_reservations = []
    
        for reservation in self.reservations.values():
            if (reservation.machine == machine and 
                reservation.customer == customer and 
                reservation.daterange.start_date <= daterange.end_date and 
                reservation.daterange.end_date >= daterange.start_date):
                final_reservations.append(reservation)
        
        return final_reservations
    
    
    def add_reservation(self, reservation):
        try:
            machine_id = self._get_Machine_id(reservation)
            self._verify_business_hours(reservation)
            self._check_equipment_availability(reservation)
            self._save_reservation(reservation, machine_id)
        except ValueError as e:
            print(f"Error: {e}")
            raise
        
    # def add_user(self, username, password_hash, salt, user_role):

    #     try:
    #         conn = self.get_db()
    #         cursor = conn.cursor()
    #         cursor.execute("INSERT INTO User (username, password_hash, salt, role) VALUES (?, ?, ?, ?)", 
    #                    (username, password_hash, salt, user_role))
    #         conn.commit()
    #         conn.close()
               
    #     except sqlite3.Error as e:
    #         print("Database error: ",str(e))
    #         raise

    # def update_user_password(self, new_hashed_password, new_salt, username):
    #     try:
    #         conn = self.get_db()
    #         cursor = conn.cursor()
    #         cursor.execute("UPDATE User SET password_hash = ?, salt = ? WHERE username = ?", 
    #                    (new_hashed_password, new_salt, username))
    #         conn.commit()
    #         conn.close()
               
    #     except sqlite3.Error as e:
    #         print("Database error: ",str(e))
    #         raise
    
    def remove_reservation(self, reservation_id):
        try:
            # Query to get the reservation details for the given reservation_id
            query = """
                SELECT 
                    Reservation.start_date, 
                    Reservation.end_date,
                    Reservation.down_payment,
                    Machine.name AS machine_name
                FROM Reservation
                JOIN Machine ON Reservation.machine_id = Machine.machine_id
                WHERE Reservation.reservation_id = ?
            """
            
            # Execute the query using the DatabaseManager
            result = self.db_manager.execute_query(query, (reservation_id,))
            if result:  # Check if reservation exists
                start_date = result[0]['start_date']
                end_date = result[0]['end_date']
                machine_name = result[0]['machine_name']
                # Create a Reservation instance
                start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M')
                end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M')
                daterange = DateRange(start_date, end_date)  # Corrected order of arguments

                reservation = Reservation(
                    customer_name="", # Not needed for refund calculation
                    machine_name=machine_name,
                    daterange=daterange,
                    business_manager=self.biz_manager
                    )
                # Calculate the refund using the Reservation class method
                refund = reservation.calculate_refund()
                # Query to delete the reservation
                delete_query = "DELETE FROM Reservation WHERE reservation_id = ?"
                self.db_manager.execute_statement(delete_query, (reservation_id,))
                return refund
            
            return False

        except sqlite3.Error as e:
            print("Database error: ", str(e))
            
    def _get_Machine_id(self, reservation):
        try:
            machine_query = "SELECT machine_id FROM Machine WHERE name = ?"
            machine_id_result = self.db_manager.execute_query(machine_query, (reservation.machine,))
            if not machine_id_result:
                raise ValueError("Machine not found")
            machine_id = machine_id_result[0]['Machine_id']
            return machine_id
        except sqlite3.Error as e:
            print("Database error: ", str(e))
            raise

    def _save_reservation(self, reservation, machine_id):
        try:
            reservation_query = """
                INSERT INTO Reservation (customer, machine_id, 
                start_date, end_date, total_cost, down_payment) 
                VALUES (?, ?, ?, ?, ?, ?)
                """
            self.db_manager.execute_statement(reservation_query, (
                reservation.customer, machine_id,
                reservation.daterange.start_date,
                reservation.daterange.end_date,
                reservation.cost, reservation.down_payment
            ))
        except sqlite3.Error as e:
            print("Database error: ", str(e))
            raise

    def _verify_business_hours(self, reservation):
        # Check if the reservation is on a Sunday
        if reservation.daterange.start_date.weekday() == 6:
            raise ValueError("Reservations cannot be made on Sundays.")

        # Check Saturday hours
        weekday_start = self.biz_manager.weekday_start
        weekday_end = self.biz_manager.weekday_end
        weekend_start = self.biz_manager.weekend_start
        weekend_end = self.biz_manager.weekend_end

        if reservation.daterange.start_date.weekday() == 5:
            if (reservation.daterange.start_date.time() > datetime.strptime(weekend_end, "%H:%M").time() or #"16:00"
                reservation.daterange.end_date.time() > datetime.strptime(weekend_end, "%H:%M").time() or #"16:00"
                reservation.daterange.start_date.time() < datetime.strptime(weekend_start, "%H:%M").time() or #"10:00"
                reservation.daterange.end_date.time() < datetime.strptime(weekend_start, "%H:%M").time()): #"10:00"
                raise ValueError("Reservations on Saturdays must be between 10:00 and 16:00.")
        # Check weekday hours
        if reservation.daterange.start_date.weekday() < 5:
            if (reservation.daterange.start_date.time() < datetime.strptime(weekday_start, "%H:%M").time() or #"9:00"
                reservation.daterange.end_date.time() > datetime.strptime(weekday_end, "%H:%M").time()): #"18:00"
                raise ValueError("Reservations on weekdays must be between 9:00 and 18:00.")

        # Check if the reservation is more than 30 days in advance
        if (reservation.daterange.start_date.date() - date.today()).days > 30:
            raise ValueError("Reservations cannot be made more than 30 days in advance.")
        
    def _check_equipment_availability(self, reservation):
        
        try:
            overlapping_reservations = self.retrieve_by_date(reservation.daterange)
            # Count how many scanners, harvesters, and scoopers are reserved in the overlapping period
            scanner_count = 0
            harvester_reserved = False
            scooper_count = 0

            for res in overlapping_reservations:
                if res['machine_name'] == "scanner":
                    scanner_count += 1
                if res['machine_name'] == "harvester":
                    harvester_reserved = True
                if res['machine_name'] == "scooper":
                    scooper_count += 1

            # Check constraints for scanners
            if reservation.machine == "scanner":
                if scanner_count >= self.biz_manager.number_of_scanners: #3
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
                if scooper_count >= self.biz_manager.number_of_scoopers:  #3 # Since there are 4 scoopers, we can reserve up to 3 at the same time
                    raise ValueError("Only one scooper must remain available; maximum number already reserved.")

                # General check for other machines (if more types are added in the future)
                if reservation.machine not in ["scanner", "harvester", "scooper"]:
                    raise ValueError("Please select from one of our specified machines: scanner, harvester, scooper.")
        
        except sqlite3.Error as e:
            print("Database error: ",str(e))
            raise
        except Exception as e:
            print(f"Error: {e}")
            raise

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
        try:
            self.start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
            self.end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
        except ValueError as e:
            print(f"Error parsing dates: {e}")
            raise ValueError(f"Invalid date format: {e}")

    def __eq__(self, other) -> bool:
        # two date ranges are equal if their is any overlap between them
        return (self.start_date <= other.end_date and self.end_date >= other.start_date) or \
        (other.start_date <= self.end_date and other.end_date >= self.start_date)
    
    def hours(self):
        return int((self.end_date - self.start_date).total_seconds() / 3600)
