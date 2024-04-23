from fastapi import FastAPI, HTTPException, status, Query
from modules import Reservation, ReservationCalendar, DateRange
from datetime import datetime

app = FastAPI()

# Create a new instance of ReservationCalendar
calendar = ReservationCalendar()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/exit/")
def exit_handler(persist_status: bool = False):
    try:
        if persist_status is True:
            calendar.save_reservations()
            return {"message": "Your changes have been saved. Goodbye!"}
        elif persist_status is False: 
            return {"message": "Goodbye!"}
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid value for persist_status. Please provide a boolean value.")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f'Failed to save changes due to {e}')
    
@app.delete("/reservations/{reservation_id}")
def cancel_reservation(reservation_id: str):

    refund = calendar.remove_reservation(reservation_id)
    if refund:
        return {"message": "Reservation deleted successfully", "refund": refund}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation not found") 
    
@app.get("/reservations")
def get_reservations_by_date(start: datetime = Query(None), end: datetime = Query(None)): 

    if not start or not end:
         raise HTTPException(status_code=400, detail="Start and end dates are required") 
    date_range = DateRange(start, end)
    reservations = calendar.retrieve_by_date(date_range)
    if reservations:
        return {"reservations":[vars(reservation) for reservation in reservations]}
    return {"message":"No reservations found in this date range"}

