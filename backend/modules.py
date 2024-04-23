import uuid
import pickle

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
    '''
    def __init__(self, customer_name, machine_name, daterange):
        self.id = uuid.uuid4()
        self.customer = customer_name
        self.machine = machine_name
        self.daterange = daterange
        self.cost = self.calculate_cost()
        self.down_payment = self.calculate_down_payment()

    def calculate_cost(self):
        pass
    
    def calculate_down_payment(self):
        pass

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
        remove_reservation(reservation): Removes a reservation from the calendar.
        save_reservations(): Saves current reservations to a data source.
    '''
    def __init__(self):
        self.reservations = self.load_reservations()
        
    def load_reservations(self):
        try:
            with open("../calendar.pkl", "rb") as f:
                previous_calendar = pickle.load(f)
                calendar = previous_calendar.reservations
        except FileNotFoundError:
            calendar = {}
        return calendar
    
    def retrieve_by_date(self, daterange):
        final_reservations = []
    
        for reservation in self.reservations.values():
            if (reservation.daterange.start_date <= daterange.end_date and 
                reservation.daterange.end_date >= daterange.start_date):
                final_reservations.append(reservation)

        return final_reservations
    
    def retrieve_by_machine(self, daterange, machine):
        final_reservations = []
    
        for reservation in self.reservations.values():
            if (reservation.machine == machine and 
                reservation.daterange.start_date <= daterange.end_date and 
                reservation.daterange.end_date >= daterange.start_date):
                final_reservations.append(reservation)
        
        return final_reservations
    
    def retrieve_by_customer(self, daterange, customer):
        final_reservations = []
    
        for reservation in self.reservations.values():
            if (reservation.customer == customer and 
                reservation.daterange.start_date <= daterange.end_date and 
                reservation.daterange.end_date >= daterange.start_date):
                final_reservations.append(reservation)
        
        return final_reservations
    
    def add_reservation(self, reservation):
        pass
    
    def remove_reservation(self, reservation):
        pass
    
    def save_reservations(self):
        try:
            with open("../calendar.pkl", "wb") as f:
                pickle.dump(self, f)
                
        except (OSError, IOError) as e:
            raise Exception(f'Error saving reservations to file.\n{e}')
        
        except pickle.PicklingError as e:
            raise Exception(f'Error pickling reservations.\{e}')

        except Exception as e:
            raise Exception(f'An uncexpected error occurred saving reservations.\n{e}')
        
        else:
            return 'success'

class DateRange:
    '''
    A class to represent a range of dates and handle their formatting and comparison.

    Attributes:
        start_date (datetime.date): The start date of the range.
        end_date (datetime.date): The end date of the range.
    '''
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
