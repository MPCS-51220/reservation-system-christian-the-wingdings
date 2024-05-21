from fastapi import FastAPI, HTTPException, status, Request, Query, Depends, Security
import urllib.parse
import sqlite3
from datetime import datetime
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from webbuilder import WebBuilder

from fastapi.security.api_key import APIKeyHeader
import requests
from dateutil import parser, tz

from permissions import validate_user, role_required
from modules import Reservation, ReservationCalendar, UserManager, BusinessManager, DateRange, DatabaseManager
from token_manager import create_access_token

from schema import Reservation_Req, User, UserRole, UserLogin, Activation, BusinessRule, RemoteRequest

API_KEY_NAME = "API-Key"
API_KEY = "b456e6d5ae43d16ce9d9e1fe2d5014258ccc73f12c237368400e6528a217af59" 

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

TIMEZONE = "GMT-5"

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def convert_timezone(date_string, from_timezone, to_timezone):
    """
    Converts a datetime string from one timezone to another ."""

    # dateutil uses opposite sign conventions
    if "+" in from_timezone:
        from_timezone = from_timezone.replace("+","-")
    else:
        from_timezone = from_timezone.replace("-","+")
    
    datetime_obj = parser.parse(date_string + ' ' + from_timezone)

    to_timezone = tz.gettz(to_timezone)

    # Convert the datetime object to the target timezone
    datetime_obj = datetime_obj.astimezone(to_timezone)

    # Format the datetime object back to string
    return datetime_obj.strftime('%Y-%m-%d %H:%M')

def get_db_manager():
    return DatabaseManager('../reservationDB.db')

def get_business_manager(db_manager: DatabaseManager = Depends(get_db_manager)):
    return BusinessManager(db_manager)

def get_user_manager(db_manager: DatabaseManager = Depends(get_db_manager)):
    return UserManager(db_manager)

def get_calendar(db_manager: DatabaseManager = Depends(get_db_manager)):
    return ReservationCalendar(db_manager)



# async def log_operation(username, type, description, timestamp, db_manager: DatabaseManager = Depends(get_db_manager)):
def log_operation(username, type, description, timestamp):
    """
    Logs user operations to the database
    """
    try:
        timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        # print(f'25, username: {username}, type: {type}, description: {description}, timestamp: {timestamp}')
        # print(f'27, db: {db_manager}')
        # id_query = f"SELECT user_id FROM USER WHERE username = ?"
        # id = db_manager.execute_query(id_query, (username,))
        # insert_query = """INSERT INTO Operation (user_id, type, description, timestamp)
        #                 VALUES (?, ?, ?, ?)"""
        # print(f'32, id: {id}, id[0]: {id[0]} insert_query: {insert_query}')
        # db_manager.execute_query(insert_query, (id[0], type, description, timestamp))
        
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
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login-form", response_class=JSONResponse)
async def get_login_form():
    menu = WebBuilder()
    menuJson = menu.build_menu()
    if menuJson is not None:
        return JSONResponse(content=menuJson)
 
    return JSONResponse(content={"error": "Login form not found"}, status_code=404)


@app.post("/login")
async def login(userlog: UserLogin,
                user_manager: UserManager = Depends(get_user_manager)):
    try:
        user = user_manager.authenticate_user(userlog.username, userlog.password)
        if not user:
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        access_token = create_access_token(data={"sub": user['username'],
                                                    "role": user['role']
                                                    })
        print(f"user: {user['username']}, role: {user['role']} logged in")
        log_operation(user['username'],"login", f"{user['username']} logged in", datetime.now())
        
        menu = WebBuilder(user['role'])
        menuJson = menu.build_menu()
        
        return {"access_token": access_token, "token_type": "bearer", "interface": menuJson}
    
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
                   user_request: User,
                   user_manager: UserManager = Depends(get_user_manager)):

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
                             bizRule: BusinessRule,
                             bizManager = Depends(get_business_manager)):

    rule = bizRule.rule
    value = bizRule.value
    
    update_data = {rule: value}
    origVal = update_data[rule]
    
    try:
        float_value = float(value)

        if float_value.is_integer():
            #update_data[rule] = int(float_value)
            value = int(float_value)
        else:
            #update_data[rule] = float_value
            value = float_value
    except ValueError:
        #update_data[rule] = origVal
        value = origVal

    try:

        bizManager.update_rule(rule, value) 
        #calendar.update_settings(**update_data)  
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


# def attempt_remote_reservation(reservation):
#     try:
#         data={
#             "start_time":reservation.daterange.start_date,
#             "end_time":reservation.daterange.end_date,
#             "client_name":reservation.customer,
#             "machine_name":reservation.machine,
#             "time_zone":"GMT-5",
#             "blocks":"Null"
#         }

#         remote_endpoints = [] # store urls for the 3 teams' endpoints here
#         headers={"API-Key":API_KEY}
#         for url in remote_endpoints:
#             response = requests.post(url, headers=headers,json=data)
#             if response.json()['reservation_made_success']:
#                 return {"message": "Reservation added successfully at a remote facility!"}
    
#         return {"message":"Reservation was not made due to unavailable resources"}
    
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                              detail=f'Failed to add reservation due to {e}')


@app.post("/reservations", status_code=status.HTTP_201_CREATED)
@validate_user
@role_required(add_reservation_permissions)
async def add_reservation(request: Request,
                            reservation_request: Reservation_Req,
                            user_manager: UserManager = Depends(get_user_manager),
                            calendar: ReservationCalendar = Depends(get_calendar),
                            business_manager: BusinessManager = Depends(get_business_manager)):
    """
    This endpoints attempts to add a reservation with a particular
    customer name, machine, start date and end date. It returns a
    status code of 201 if the reservation was made successfully or
    a status code of 500 if there was an error
    """
    try:      
        if not user_manager.is_user_active(reservation_request.customer) or not user_manager.is_user_active(request.state.user): #Need to come back to. 
            # reservation cannot be made by/for deactivated users
            raise HTTPException(status_code=400, 
                                detail="This user is deactivated and cannot make reservations.")
        reservation_date = DateRange(reservation_request.start_date, reservation_request.end_date)
        reservation = Reservation(reservation_request.customer, reservation_request.machine, reservation_date, business_manager)

        calendar.add_reservation(reservation)
        log_operation(request.state.user, 
                      "add reservation", 
                      f"reservation added for machine {reservation_request.machine}", 
                      datetime.now())
        return {"message": "Reservation added successfully!"}
   
    except Exception as e:
        # attempt_remote_reservation(reservation) # change this to catch specific error of no availability
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'Failed to add reservation due to {e}')


get_reservations_prmissions = {
    "admin": None,
    "scheduler": None,
    "customer": is_customer_accessing_own_data
}

@app.get("/reservations", status_code=status.HTTP_200_OK)
@validate_user
@role_required(get_reservations_prmissions)
async def get_reservations(request: Request,
                           customer: str = Query(None, description="Customer name"),
                           machine: str = Query(None, description="Machine to get records for"),
                           start_date: str = Query(..., description="Start date of the reservation period"),
                           end_date: str = Query(..., description="End date of the reservation period"),
                           calendar: ReservationCalendar = Depends(get_calendar)):
    try:
        if request.state.role == "customer":
            if customer and customer != request.state.user:
                raise HTTPException(status_code=403, detail="Customers can only access their own data.")
            customer = request.state.user

        if not start_date or not end_date:
            raise HTTPException(status_code=400, detail="Both start and end dates are required")

        start = urllib.parse.unquote(start_date)
        end = urllib.parse.unquote(end_date)
        daterange = DateRange(start, end)

        if customer and machine:
            reservations = calendar.retrieve_by_machine_and_customer(daterange, machine, customer)
            logstring = f'Listed reservations for customer: {customer}, machine: {machine}'
        elif customer:
            reservations = calendar.retrieve_by_customer(daterange, customer)
            logstring = f'Listed reservations for customer: {customer} in daterange: {daterange}'
        elif machine:
            reservations = calendar.retrieve_by_machine(daterange, machine)
            logstring = f'Listed reservations for machine: {machine} in daterange: {daterange}'
        else:
            reservations = calendar.retrieve_by_date(daterange)
            logstring = f'Listed reservations in daterange: {daterange}'

        log_operation(request.state.user,
                      "list reservations",
                      logstring,
                      datetime.now())

        if reservations:
            return {"reservations": reservations}
        else:
            return {"message": "No reservations found for the given criteria."}

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
                             reservation_id: str = Query(..., description="Reservation ID"),
                             calendar: ReservationCalendar = Depends(get_calendar)):
    """
    This endpoint attempts to cancel a reservation. If no
    such reservation is found, a status code 404 is returned.
    """
    try:
        print('cancel reservation try block')
        refund = calendar.remove_reservation(reservation_id)
        print(f'refund: {refund} in cancel_reservation')
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
    "admin": None
}
@app.delete("/users", status_code=status.HTTP_200_OK)
@validate_user
@role_required(del_user_permissions)
async def remove_user(request: Request,
                      username: str = Query(..., description="Username of the user to delete"),
                      user_manager: UserManager = Depends(get_user_manager)):
    try:
        user_manager.remove_user(username)
        log_operation(request.state.user,
                      "remove user", 
                      f"{username} user removed", 
                      datetime.now())
        return {"message": f"{username} deleted successfully"}


    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f'Failed to delete user due to {e}')


patch_user_role_permissions = {
    "admin": None,
    "scheduler": None
    }
@app.patch("/users/role", status_code=status.HTTP_200_OK)
@validate_user
@role_required(patch_user_role_permissions)
async def update_user_role(request: Request,
                           role_request: UserRole,
                           user_manager: UserManager = Depends(get_user_manager)):
    try:
        user_manager.update_user_role(role_request.role, role_request.username)
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
                         user_request: User,
                         user_manager: UserManager = Depends(get_user_manager)):
    try:
        if request.state.role == "customer":
            user_request.username = request.state.user

        user_manager.update_password(user_request.username, user_request.password, user_request.salt)
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
async def deactivate_user(request: Request,
                          user_request: Activation,
                          user_manager: UserManager = Depends(get_user_manager)):
    try:
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
async def activate_user(request: Request,
                        user_request: Activation,
                        user_manager: UserManager = Depends(get_user_manager)):
    
    try:
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
async def list_users(request: Request,
                     user_manager: UserManager = Depends(get_user_manager)):


    try:
        users_status = user_manager.list_users()
        print(f'users_status: {users_status}')
        log_operation(request.state.user,
                      "list users' status", 
                      f"Listed all users with status", 
                      datetime.now())
        return {'users': users_status}
   
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f'Failed to list users due to {e}')
    

def api_key_auth(api_key: str = Security(api_key_header)):
    if api_key == API_KEY:
        return api_key
    else:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )


@app.post("/outside-requests")
async def handle_requests(request:Request, remote_request: RemoteRequest, 
                          calendar: ReservationCalendar = Depends(get_calendar),
                          api_key: str = Depends(api_key_auth),
                          business_manager: BusinessManager = Depends(get_business_manager)
                          ):
    try:
        # convert start_time and end_time to correct timezone
        start_time = convert_timezone(remote_request.start_time, 
                                      remote_request.time_zone,
                                      TIMEZONE)
        end_time = convert_timezone(remote_request.end_time, 
                                    remote_request.time_zone,
                                    TIMEZONE)
        
        reservation_date = DateRange(start_time, end_time)
        reservation = Reservation(remote_request.client_name, 
                                  remote_request.machine_name, 
                                  reservation_date,
                                  business_manager)
        
        calendar.add_reservation(reservation, True)
        return {"reservation_made_success":True,
                "message":f"({reservation.cost},{reservation.down_payment})"} 
    
    except Exception as e:
        return {"reservation_made_success":False,
                "message":f"{e}"}
    



   
del_remote_reservation_permissions = {
    "admin": None,
    "scheduler": None,
}


@app.delete("/reservations/remote", status_code=status.HTTP_200_OK)
@validate_user
@role_required(del_remote_reservation_permissions)
async def cancel_remote_reservation(request: Request,
                             reservation_id: str = Query(..., description="Reservation ID"),
                             calendar: ReservationCalendar = Depends(get_calendar)):

   
    try:
        refund = calendar.remove_remote_reservation(reservation_id)
        print(f'refund: {refund} in cancel_reservation')
        if refund is not False: # reservation was removed and refund amount returned
            return {"message": "Reservation cancelled successfully", "refund": refund}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail="Reservation not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f'Failed to cancel reservation due to {e}')
    

list_remote_reservations_permissions = {
    "admin":None,
    "scheduler":None
}

@app.get("/reservations/remote", status_code=status.HTTP_200_OK)
@validate_user
@role_required(list_remote_reservations_permissions)
async def list_remote(request: Request,
                     calendar: ReservationCalendar = Depends(get_calendar)):


    try:
        reservations = calendar.list_remote_reservations()
        if reservations:
            return {"reservations":reservations}
        else:
            return {"message": "No remote reservations"}
   
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f'Failed to list reservations due to {e}')
