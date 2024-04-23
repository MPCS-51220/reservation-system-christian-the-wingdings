from fastapi import FastAPI, HTTPException, status
from modules import Reservation, ReservationCalendar, DateRange

app = FastAPI()

# Create a new instance of ReservationCalendar
calendar = ReservationCalendar()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/reservations/")
def add_reservation(customer_name: str, machine_name: str, start_date: str, end_date: str):
    
    try:
        reservation_date = DateRange(start_date, end_date)
        reservation = Reservation(customer_name, machine_name, reservation_date)
        calendar.add_reservation(reservation)
        return {"message": "Reservation added successfully!"}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f'Failed to add reservation due to {e}')

@app.get("/exit/")
def exit_handler(persist_status: bool = False):
    try:
        if persist_status is True:
            calendar.save_reservations()
            return {"message": "Your changes have been saved. Goodbye!"} # return a successful status code
        elif persist_status is False: 
            return {"message": "Goodbye!"}
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid value for persist_status. Please provide a boolean value.")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f'Failed to save changes due to {e}')
