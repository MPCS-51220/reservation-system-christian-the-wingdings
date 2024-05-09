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
    """
    This endpoints attempts to add a reservation with a particular
    customer name, machine, start date and end date. It returns a 
    status code of 201 if the reservation was made successfully or
    a status code of 500 if there was an error
    """
    
    try:
        reservation_date = DateRange(reservation_request.start_date, reservation_request.end_date)
        reservation = Reservation(reservation_request.customer_name, reservation_request.machine_name, reservation_date)
        calendar.add_reservation(reservation)
        return {"message": "Reservation added successfully!"}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'Failed to add reservation due to {e}')



@app.get("/reservations/customers/{customer_name}", status_code=status.HTTP_200_OK)
def get_reservations_by_customer(customer_name: str, 
                                  start: str = Query(..., description="Start date of the reservation period"),
                                  end: str = Query(..., description="End date of the reservation period")):
    
    """
    This endpoint retrieves the reservations made by a customer
    in a particular date range. It returns an appropriate message
    if no such reservations are found.
    """
    try:
        if start and end:
            daterange = DateRange(start, end)
            reservations = calendar.retrieve_by_customer(daterange, customer_name)
        else:
            raise HTTPException(status_code=400, detail="Both start and end dates are required")
        
        if reservations:
            return {"reservations":reservations}
        else:
            return {"message": "No reservations found for this customer."}
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f'Failed to get reservations due to {e}')
    
@app.get("/reservations/machines/{machine_name}", status_code=status.HTTP_200_OK)
def get_reservations_by_machine(machine_name: str, 
                                  start: str = Query(..., description="Start date of the reservation period"),
                                  end: str = Query(..., description="End date of the reservation period")):
    """
    This endpoint retrieves the reservations made for a machine
    in a particular date range. It returns an appropriate message
    if no such reservations are found.
    """
    try:
        if start and end:
            daterange = DateRange(start, end)
            reservations = calendar.retrieve_by_machine(daterange, machine_name)
        else:
            raise HTTPException(status_code=400, detail="Both start and end dates are required")
        
        if reservations:
            return {"reservations":reservations}
        else:
            return {"message": "No reservations found for this machine."}
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f'Failed to get reservations due to {e}')
    

@app.get("/reservations/machines/{machine_name}/customers/{customer_name}", status_code=status.HTTP_200_OK)
def get_reservations_by_machine(machine_name: str, 
                                customer_name: str,
                                  start: str = Query(..., description="Start date of the reservation period"),
                                  end: str = Query(..., description="End date of the reservation period")):
    """
    This endpoint retrieves the reservations made for a machine
    in a particular date range. It returns an appropriate message
    if no such reservations are found.
    """
    try:
        if start and end:
            daterange = DateRange(start, end)
            reservations = calendar.retrieve_by_machine_and_customer(daterange, machine_name, customer_name)
        else:
            raise HTTPException(status_code=400, detail="Both start and end dates are required")
        
        if reservations:
            return {"reservations":reservations}
        else:
            return {"message": "No reservations found for this machine."}
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f'Failed to get reservations due to {e}')

    
@app.delete("/reservations/{reservation_id}", status_code=status.HTTP_200_OK)
def cancel_reservation(reservation_id: str):
    """
    This endpoint attempts to cancel a reservation. If no 
    such reservation is found, a status code 404 is returned.
    """
    try:
        refund = calendar.remove_reservation(reservation_id)
        if refund is not False: # reservation was removed and refund amount returned
            return {"message": "Reservation cancelled successfully", "refund": refund}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail="Reservation not found") 
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f'Failed to cancel reservation due to {e}')
    
    
@app.get("/reservations", status_code=status.HTTP_200_OK)
def get_reservations_by_date(start: str = Query(None), end: str = Query(None)): 
    """
    This endpoint retrieves the reservations in a particular
    date range. It returns an appropriate message if no such 
    reservations are found.
    """
    
    if not start or not end: # url parameters missing
        raise HTTPException(status_code=400, detail="Start and end dates are required") 
    
    try:
        date_range = DateRange(start, end)
        reservations = calendar.retrieve_by_date(date_range)
        if reservations:
            # convert Reservation objects to dictionaries
            return {"reservations":reservations}
        return {"message":"No reservations found in this date range"}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f'Failed to get reservations due to {e}')
