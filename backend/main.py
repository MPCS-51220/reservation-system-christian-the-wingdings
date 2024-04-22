from fastapi import FastAPI
from modules import Reservation, ReservationCalendar, DateRange

app = FastAPI()

# Create a new instance of ReservationCalendar
calendar = ReservationCalendar()

@app.get("/")
def root():
    return {"message": "Hello World"}


