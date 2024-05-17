from fastapi import FastAPI, HTTPException, status, Request, Query, Depends
import urllib.parse
import sqlite3
from datetime import datetime


from permissions import validate_user, role_required
from modules import Reservation, ReservationCalendar, UserManager, DateRange
from token_manager import create_access_token

from schema import Reservation_Req, User, UserRole, UserLogin, Activation, BusinessRule


app = FastAPI()
calendar = ReservationCalendar(88000, 1000, 990, 3, 3, "9:00", "18:00", "10:00", "16:00", 0.75, 0.5)




def log_operation(username, type, description, timestamp):
    """
    Logs user operations to the database
    """
    try:
        timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        with sqlite3.connect('../reservationDB.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM USER WHERE username = ?",(username,))
            user_id = cursor.fetchone()[0]
            query = """
                    INSERT INTO Operation (user_id, type, description, timestamp)
                    VALUES (?, ?, ?, ?)
                    """
            cursor.execute(query, (user_id, type, description, timestamp))
            conn.commit()


    except sqlite3.Error as e:
        print("Failed to log operation: ", str(e))


@app.get("/")
def root():
    return {"message": "Hello World"}



@app.post("/login")
async def login(userlog: UserLogin, user_manager: UserManager = Depends()):
    try:
        user = user_manager.authenticate_user(userlog.username, userlog.password)
        if not user:
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        access_token = create_access_token(data={"sub": user['username'],
                                                    "role": user['role']
                                                    })
        print(f"user: {user['username']}, role: {user['role']} logged in")
        log_operation(user['username'],"login", f"{user['username']} logged in", datetime.now())
        return {"access_token": access_token, "token_type": "bearer"}
    
    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
        # Log the exception details for debugging purposes
        print(f"An unexpected error occurred: {str(e)}")
        
        # Raise a generic HTTPException with status code 500
        raise HTTPException(status_code=500, detail="Internal Server Error")
        


add_user_permissions = {
    "admin": None
}
@app.post("/users")
@validate_user
@role_required(add_user_permissions)
async def add_user(request: Request,
                   user_request: User):


    user_manager = UserManager()
    try:
        user_manager.add_user(user_request.username, user_request.password, user_request.role, user_request.salt)  
        log_operation(request.state.user, "add user", f"{user_request.username} user added", datetime.now())
        return {"message": f'{user_request.username} added successfully'}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'Failed to add user due to {e}')




configure_biz_rules_permissions = {
    "admin": None
}
@app.post("/business-rules")
@validate_user
@role_required(configure_biz_rules_permissions)
async def configure_business_rules(request: Request,
                             bizRule: BusinessRule):
    rule = bizRule.rule
    value = bizRule.value
    update_data = {rule: value}
    origVal = update_data[rule]
    
    try:
        float_value = float(value)

        if float_value.is_integer():
            update_data[rule] = int(float_value)
        else:
            update_data[rule] = float_value
    except ValueError:
        update_data[rule] = origVal

    try:


        calendar.update_settings(**update_data)    
        return {"message": f'business rules updated successfully'}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'Failed to update business rules due to {e}')


def is_customer_accessing_own_data(user_username, customer_name):
    return user_username == customer_name

add_reservation_permissions = {
    "admin": None,  # No additional checks needed for admin
    "scheduler": None,  # No additional checks needed for scheduler
    "customer": is_customer_accessing_own_data  # Customers can only access their own data
}

@app.post("/reservations", status_code=status.HTTP_201_CREATED)
@validate_user
@role_required(add_reservation_permissions)
async def add_reservation(request: Request,
                    reservation_request: Reservation_Req):
    """
    This endpoints attempts to add a reservation with a particular
    customer name, machine, start date and end date. It returns a
    status code of 201 if the reservation was made successfully or
    a status code of 500 if there was an error
    """
   
    try:
      
        user_manager = UserManager()
        if not user_manager.is_user_active(reservation_request.customer) or not user_manager.is_user_active(request.state.user):
            # reservation cannot be made by/for deactivated users
            raise HTTPException(status_code=400, 
                                detail="This user is deactivated and cannot make reservations.")

        reservation_date = DateRange(reservation_request.start_date, reservation_request.end_date)
        reservation = Reservation(reservation_request.customer, reservation_request.machine, reservation_date)

        calendar.add_reservation(reservation)
        log_operation(request.state.user, 
                      "add reservation", 
                      f"reservation added for machine {reservation_request.machine}", 
                      datetime.now())
        return {"message": "Reservation added successfully!"}
   
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'Failed to add reservation due to {e}')




get_reservation_permissions = {
    "admin": None,
    "scheduler": None,
    "customer": is_customer_accessing_own_data
}


@app.get("/reservations/customers", status_code=status.HTTP_200_OK)
@validate_user
@role_required(get_reservation_permissions)
async def get_reservations_by_customer(request: Request,
                                      customer: str = None,
                                      start_date: str = Query(..., description="Start date of the reservation period"),
                                      end_date: str = Query(..., description="End date of the reservation period")):
    """
    This endpoint retrieves the reservations made by a customer
    in a particular date range. It returns an appropriate message
    if no such reservations are found.
    """
    if customer is None:
        customer = request.state.user

    try:
        if start_date and end_date:
           
            start = urllib.parse.unquote(start_date)
            end = urllib.parse.unquote(end_date)


            daterange = DateRange(start, end)
            reservations = calendar.retrieve_by_customer(daterange, customer)
        else:
            raise HTTPException(status_code=400, detail="Both start and end dates are required")
        log_operation(request.state.user,
                      "list reservations", 
                      f"Listed reservations for {customer}", 
                      datetime.now())
        
        if reservations:
            return {"reservations":reservations}
        else:
            return {"message": "No reservations found for this customer."}
       
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'Failed to get reservations due to {e}')










get_reservation_by_machine_permissions = {
    "admin": None,
    "scheduler": None,
    "customer": is_customer_accessing_own_data
}


@app.get("/reservations/machines", status_code=status.HTTP_200_OK)
@validate_user
@role_required(get_reservation_by_machine_permissions)
async def get_reservations_by_machine(request: Request,
                                machine: str,
                                start_date: str = Query(..., description="Start date of the reservation period"),
                                end_date: str = Query(..., description="End date of the reservation period")):
    """
    This endpoint retrieves the reservations made for a machine
    in a particular date range. It returns an appropriate message
    if no such reservations are found.
    """
    try:
        if start_date and end_date:
            start = urllib.parse.unquote(start_date)
            end = urllib.parse.unquote(end_date)


            daterange = DateRange(start, end)
            reservations = calendar.retrieve_by_machine(daterange, machine)
        else:
            raise HTTPException(status_code=400, detail="Both start and end dates are required")
        
        log_operation(request.state.user,
                      "list reservations", 
                      f"Listed reservations for machine {machine}", 
                      datetime.now())
        
        if reservations:
            return {"reservations":reservations}
        else:
            return {"message": "No reservations found for this machine."}
       
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f'Failed to get reservations due to {e}')










del_reservation_permissions = {
    "admin": None,
    "scheduler": None,
    "customer": is_customer_accessing_own_data
}


@app.delete("/reservations", status_code=status.HTTP_200_OK)
@validate_user
@role_required(del_reservation_permissions)
async def cancel_reservation(request: Request,
                             reservation_id: str):
    """
    This endpoint attempts to cancel a reservation. If no
    such reservation is found, a status code 404 is returned.
    """
    try:
        refund = calendar.remove_reservation(reservation_id)
        if refund is not False: # reservation was removed and refund amount returned
            log_operation(request.state.user,
                      "cancel reservation", 
                      f"Cancelled reservation with ID {reservation_id}", 
                      datetime.now())
            return {"message": "Reservation cancelled successfully", "refund": refund}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail="Reservation not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f'Failed to cancel reservation due to {e}')






del_user_permissions = {
    "admin": None  # No additional checks needed for admin
}
@app.delete("/users", status_code=status.HTTP_200_OK)
@validate_user
@role_required(del_user_permissions)
async def remove_user(request: Request,
                      username: str):
    try:
        calendar.remove_user(username)
        log_operation(request.state.user,
                      "remove user", 
                      f"{username} user removed", 
                      datetime.now())
        return {"message": f"{username} deleted successfully"}


    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f'Failed to delete user due to {e}')










patch_user_role_permissions = {
    "admin": None
    }
@app.patch("/users/role", status_code=status.HTTP_200_OK)
@validate_user
@role_required(patch_user_role_permissions)
async def update_user_role(request: Request,
                           role_request: UserRole):
    try:
        calendar.update_user_role(role_request.role, role_request.username)
        log_operation(request.state.user,
                      "change user role", 
                      f"{role_request.username} role changed to {role_request.role}", 
                      datetime.now())
        
        return {"message": f"{role_request.username} role changed to {role_request.role} successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f'Failed to update user role due to {e}')








patch_user_password_permissions = {
    "admin": None,
    "customer": is_customer_accessing_own_data
}

@app.patch("/users/password", status_code=status.HTTP_200_OK)
@validate_user
@role_required(patch_user_password_permissions)
async def update_user_password(request: Request,
                         user_request: User):
    try:
        if request.state.role == "customer":
            user_request.username = request.state.user

        UserManager.update_password(user_request.username, user_request.password, user_request.salt)
        log_operation(request.state.user,
                      "change user password", 
                      f"Password changed for {user_request.username}", 
                      datetime.now())
        return {"message": f"password for {user_request.username} was changed successfully"}


    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f'Failed to update password due to {e}')




deactivate_activate_permissions={
    "admin":None
}


@app.patch("/users/deactivate", status_code=status.HTTP_200_OK)
@validate_user
@role_required(deactivate_activate_permissions)
async def deactivate_user(request: Request, user_request: Activation):


    try:
        user_manager = UserManager()
        user_manager.deactivate_user(user_request.username)
        log_operation(request.state.user,
                      "deactivate user", 
                      f"Deactivated user {user_request.username}", 
                      datetime.now())
        return {"message": f"User {user_request.username} has been deactivated."}
   
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f'Failed to deactivate user due to {e}')
   


@app.patch("/users/activate", status_code=status.HTTP_200_OK)
@validate_user
@role_required(deactivate_activate_permissions)
async def activate_user(request: Request, user_request: Activation):


    try:
        user_manager = UserManager()
        user_manager.activate_user(user_request.username)
        log_operation(request.state.user,
                      "activate user", 
                      f"Activated user {user_request.username}", 
                      datetime.now())
        return {"message": f"User {user_request.username} has been activated."}
   
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f'Failed to activate user due to {e}')




@app.get("/users", status_code=status.HTTP_200_OK)
@validate_user
@role_required(deactivate_activate_permissions)
async def list_users(request: Request):


    try:
        user_manager = UserManager()
        users = user_manager.list_users()
        log_operation(request.state.user,
                      "list users' status", 
                      f"Listed all users with status", 
                      datetime.now())
        return {"users": users}
   
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f'Failed to list users due to {e}')
   
