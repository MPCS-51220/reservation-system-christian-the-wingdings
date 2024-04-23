from fastapi import FastAPI, HTTPException, status
from modules import Reservation, ReservationCalendar, DateRange

app = FastAPI()

# Create a new instance of ReservationCalendar
calendar = ReservationCalendar()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/exit/{persist_status}")
def exit_handler(persist_status: bool = False):
    try:
        if persist_status:
            calendar.save_reservations()
            return {"message": "Your changes have been saved. Goodbye!"}
        else: 
            return {"message": "Goodbye!"}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f'Failed to save changes due to {e}')
