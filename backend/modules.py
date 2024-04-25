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
        if (self.daterange.start_date - datetime.now()).days > 13:
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
        self.load_test_data([
                        {'start_date': '2024-04-29 10:00',
                                'end_date': '2024-04-29 12:00',
                                'customer_name': "Nikola",
                                'machine_name': "scanner"
                                },
                        {'start_date': "2024-04-29 10:00",
                                'end_date': "2024-04-29 12:00",
                                'customer_name': "testcustomer",
                                'machine_name': "scanner"
                                }
                                ])
        
        
    def load_reservations(self):
        try:
            with open("../calendar.pkl", "rb") as f:
                previous_calendar = pickle.load(f)
                calendar = previous_calendar.reservations
        except FileNotFoundError:
            calendar = {}
        return calendar
    
    def load_test_data(self, data):
        for data in data:
            daterange = DateRange(data["start_date"], data["end_date"])
            reservation = Reservation(data["customer_name"], data["machine_name"], daterange)
            self.add_reservation(reservation, True)
        
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
    
    def add_reservation(self, reservation, is_test=False):
        if not is_test:
            self._verify_business_hours(reservation)
            self._check_equipment_availability(reservation)
            self.reservations[reservation.id] = reservation
        else:
            self.reservations[reservation.id] = reservation
    
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
            if res.machine == "scanner":
                scanner_count += 1
            if res.machine == "harvester":
                harvester_reserved = True
            if res.machine == "scooper":
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
