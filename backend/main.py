from fastapi import FastAPI, HTTPException, status, Query, Depends, Header
from modules import Reservation, ReservationCalendar, DateRange, UserManager
from datetime import datetime
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from token_manager import create_access_token, decode_access_token
from permissions import role_required

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class ReservationRequest(BaseModel):
    customer_name: str
    machine_name: str
    start_date: str
    end_date: str

app = FastAPI() 

calendar = ReservationCalendar()


@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/add_user/")
async def add_user(username: str, password: str, role: str, salt: str, user_manager: UserManager = Depends()):
    try:
        user_manager.add_user(username, password, role, salt)
        return {"message": "User added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/login/")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), user_manager: UserManager = Depends(UserManager)):
    user = user_manager.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user['username'], "role": user['role']})
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return decode_access_token(token) or credentials_exception

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


# Condition for customers to only access their data
def is_customer_accessing_own_data(user_username, customer_name):
    return user_username == customer_name

get_reservation_permissions = {
    "admin": None,  # No additional checks needed for admin
    "scheduler": None,  # No additional checks needed for scheduler
    "customer": is_customer_accessing_own_data  # Customers can only access their own data
}

@app.get("/reservations/customers/{customer_name}", status_code=status.HTTP_200_OK)
@role_required(get_reservation_permissions)
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
            return {"reservations":[vars(reservation) for reservation in reservations]}
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
