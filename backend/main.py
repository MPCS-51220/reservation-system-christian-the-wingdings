from fastapi import FastAPI, HTTPException, status, Query
from modules import Reservation, ReservationCalendar, DateRange
from datetime import datetime
from pydantic import BaseModel

class ReservationRequest(BaseModel):
    customer_name: str
    machine_name: str
    start_date: str
    end_date: str

app = FastAPI()

# Create a new instance of ReservationCalendar
calendar = ReservationCalendar()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/reservations", status_code=status.HTTP_201_CREATED)
def add_reservation(reservation_request: ReservationRequest):
    
    try:
        reservation_date = DateRange(reservation_request.start_date, reservation_request.end_date)
        reservation = Reservation(reservation_request.customer_name, reservation_request.machine_name, reservation_date)
        calendar.add_reservation(reservation)
        return {"message": "Reservation added successfully!"}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'Failed to add reservation due to {e}')


@app.get("/exit", status_code=status.HTTP_200_OK)
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


@app.get("/reservations/customers/{customer_name}", status_code=status.HTTP_200_OK)
def get_reservations_by_customer(customer_name: str, 
                                  start: str = Query(..., description="Start date of the reservation period"),
                                  end: str = Query(..., description="End date of the reservation period")):
    try:
        if start and end:
            daterange = DateRange(start, end)
            reservations = calendar.retrieve_by_customer(daterange, customer_name)
        else:
            raise HTTPException(status_code=400, detail="Both start and end dates are required")
        
        if reservations:
            return {"reservations":[vars(reservation) for reservation in reservations]}
        else:
            return {"message": "No reservations found for this customer."}
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f'Failed to get reservations due to {e}')
    
@app.get("/reservations/machines/{machine_name}", status_code=status.HTTP_200_OK)
def get_reservations_by_machine(machine_name: str, 
                                  start: str = Query(..., description="Start date of the reservation period"),
                                  end: str = Query(..., description="End date of the reservation period")):
    try:
        if start and end:
            daterange = DateRange(start, end)
            reservations = calendar.retrieve_by_machine(daterange, machine_name)
        else:
            raise HTTPException(status_code=400, detail="Both start and end dates are required")
        
        if reservations:
            return {"reservations":[vars(reservation) for reservation in reservations]}
        else:
            return {"message": "No reservations found for this machine."}
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f'Failed to get reservations due to {e}')

    
@app.delete("/reservations/{reservation_id}", status_code=status.HTTP_200_OK)
def cancel_reservation(reservation_id: str):

    refund = calendar.remove_reservation(reservation_id)
    if refund: # reservation was removed and refund amount returned
        return {"message": "Reservation cancelled successfully", "refund": refund}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation not found") 
    
@app.get("/reservations")
def get_reservations_by_date(start: str = Query(None), end: str = Query(None)): 

    if not start or not end: # url parameters missing
         raise HTTPException(status_code=400, detail="Start and end dates are required") 
    date_range = DateRange(start, end)
    reservations = calendar.retrieve_by_date(date_range)
    if reservations:
        # convert Reservation objects to dictionaries
        return {"reservations":[reservation.__dict__ for reservation in reservations]}
    return {"message":"No reservations found in this date range"}
