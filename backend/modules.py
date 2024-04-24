import uuid
import pickle
from datetime import datetime, date

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
        self.id = uuid.uuid4()
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
        if (self.daterange.start_date - date.today()).days > 13:
            return self.calculate_cost()*0.25
        else:
            return 0
    
    def calculate_down_payment(self):
        return self.cost * 0.5


    def calculate_refund(self):
        # calculate refund based on number of advance days of cancellation
        advance_days = (self.daterange.start_date - datetime.now()).days
        if advance_days >= 7:
            refund = 0.75 * self.down_payment
        elif advance_days >= 2:
            refund = 0.5 * self.down_payment
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
    
    def remove_reservation(self, reservation_id):
        if reservation_id in self.reservations:
            reservation = self.reservations[reservation_id]
            refund = reservation.calculate_refund()
            del self.reservations[reservation_id]
            return refund
        return False
    
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
