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

@app.get("/reservations/customers/{customer_name}")
def get_reservations_by_customer(customer_name: str, 
                                  start: datetime = Query(..., description="Start date of the reservation period"),
                                  end: datetime = Query(..., description="End date of the reservation period")):
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
    
@app.get("/reservations/machines/{machine_name}")
def get_reservations_by_machine(machine_name: str, 
                                  start: datetime = Query(..., description="Start date of the reservation period"),
                                  end: datetime = Query(..., description="End date of the reservation period")):
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