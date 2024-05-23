# T-04: Interoperate!

## Overview
MPCS, Inc. has decided that they are losing business by having each facility manage its own reservations. They'd like to consolidate their systems.  As a first step, they want all teams to implement a feature that lets any facility reserve a resource at another facility.   The full assignment can be found here: https://canvas.uchicago.edu/courses/56612/assignments/663325?module_item_id=2406263


# Equipment Reservation System Documentation

Welcome to the Equipment Reservation System! This system is designed to help users reserve various types of equipment through a simple command-line interface (CLI). Below you will find detailed instructions on how to install, configure, and use this system effectively.

## Table of Contents

- [Design](#design)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Running Tests](#running-tests)
- [Passwords for Sample Users](#passwords-for-sample-users)
- [T-03 Security Discussion](#t-02-security-discussion)
- [New Features](#new-features)
- [Database System](#database-system)
- [T-03 Feature Points](#t-03-feature-points)
- [T-04 Feature Points](#t-04-feature-points)
- [T-04 Additional Features](#t-04-additional-features)
- [Contributing](#contributing)


## Design

Our system is designed with both a frontend, a backend, and a database for persistent storage. The frotend consists of a user interface in the command line. This is where a user performs all actions, including login, reservation tasks, and user management. We use the backend for API calls, which select, update, or delete parts of the database. This helps us to separate distinct parts of the application.

### User Flow

When the user starts the frontend (more information on this below) they first are prompted to login. This requires a username and password. Once successfully logged in, they are given the list of commands they have access to depending on their role. From there, they can work on making, cancelling, or listing reservations until they wish to logout, which returns them to the original login page and resets the user. Otherwise, they can use the 'exit' option to exit the program entirely. Note: we assume the username that is used to login is the same as the name of the customer that we use throughout our backend, such as in the 'Reservation' table of the database.


## Installation

Before you can run the Equipment Reservation System, you need to ensure that SQLite, Python, FastAPI, Uvicorn, and the requests library are installed on your machine.

### Installing SQLite:

Run the following command for Linux:

```bash
sudo apt-get install sqlite3
```

MacOS has SQLite already installed, which can be accessed with

```bash
sqlite3
```

It is crucial for the system to have sqlite installed so data can be appropriately stored and used.

### Install Python and Libraries:

1. Download and install Python from [python.org](https://python.org).
2. Ensure Python is added to your system's PATH.
3. Install the required Python libraries using pip:

```bash
pip install fastapi uvicorn requests
pip install python-jose
```

### Setup the Backend Server:

Navigate to the backend directory and run the following command to start the server:

```bash
uvicorn main:app --reload
```

### Setup the Frontend CLI:

Navigate to the frontend directory and run the `app.py` file:

```bash
python app.py
```

## Configuration

The system interacts with a backend server via API calls. Ensure the `BASE_URL` in the `app.py` file is set to the URL of the backend server you are using. For local development, this might be:

```python
BASE_URL = "http://localhost:8000"
```

## Usage

The Equipment Reservation System is accessed through a command-line interface. Below are the commands and instructions on how to use them.

### Logging-in
    Select 'Log in' by entering 1 from the main menu.
    Enter the required details:(username, password)
    On successful login you will recieve a jwt which will be used to authenticate the routes you have access to


### Making a Reservation

    Select 'Make reservation' by entering 1 from the main menu.
    Enter the required details:(Customer Name, Machine choice, Start Date and Time, End Date and Time)
    The system will confirm upon success.
*NOTE start/end is formated YYYY-MM-DD HH:MM*

### Cancelling a Reservation
    
    Select 'Cancel reservation' by entering 2 from the main menu.
    Enter the ID of the reservation you wish to cancel.
    The system will confirm the cancellation and show any applicable refund.

### Listing Reservations

    Select 'List reservations' by entering 3 from the main menu.
    Choose the type of listing you need (by date, machine, or customer).
    Enter the required parameters based on your selection.

### Exiting the System

    Typing 'Exit' at any point will exit your current command. If you are viewing the main menu this will close the system


## Running Tests

In a python environment, make sure pytest is installed with

```bash
pip install pytest
```

Then in the backend directory which contains the test_main.py file, run

```bash
pytest
```

## Passwords for Sample Users

When loading the database from our repository, there starts some example in the tables of reservationDB. 

For the user, there is a user with username 'johndoe' and password 'hashed_password_example'. It is an admin user, so it can used to create new users for additional testing.


 Note: When a password is reset or a new user is created, their temporary password is set to 'temp'. When a user with this password tries to login, they will be prompted to change their password from 'temp', as that password is deemed unsecure with a specific salt I set in the system.

## T-03 Security Discussion

Our implementation has some security assumptions. The front end and server is not encrypted, but we are assuming that it would be in a more fleshed-out implementation. Therefore, we are currently passing the users password directly through a POST route. This is a security concern.

Authorization happens through a login route which creates a jwt with a life span set to 15 min. This is automatically applied to the header of any requests from the user after they log in.

Lastly, we are currently refactoring the program to push all the content displayed to the user, ie the main menu and command options, to the backend. We are currently using a dictionary in the cli file. Once we push this to the backend, we will serve only the menu options that a user has access to execute.


## New Features

The Equipment Reservation System is accessed through a command-line interface. Below are new features added in this assignment.

### Segregated Test

Test data is stored in a separate databse (reservationDB) so testing is separated from our frotend logic and other data.

### Error Handling
    
We use try-catch along with resetting users to previous inputs in the case of bad user input and bad endpoints.


## Database System

With the introduction of user data, we have adopted a relational database system to store user and machine data. Here is a breakdown of the tables in the system.

### Machine

Rows:

Machine_id (PK): unique id for the machine type

Name: (scanner, scooper, harvester)

quantity: number of machines of the type

cooldown: cooldown time in minutes

rate: rate per hour


### Reservation

Rows:

reservation_id (PK): unique reservation id

customer: name of customer

machine_id (FK): id of machine type reserved

start_date: start date and time of reservation

end_date: end date and time of reservation

total_cost: total cost of reservation

down_payment: down payment for reservation


### User

Rows:

user_id (PK): unique user id

username: user’s name

password_hash: hashed password

role: (admin, customer, scheduler)

salt: unique salt for password

is_active: specifies if the user is activated or deactivated


### Operation

Rows:


operation_id (PK): unique id for the operation

user_id (FK): id of the user who performed the operation

timestamp: timestamp of the operation

type: type of the operation (cancellation, making reservation, listing reservations, adding users)

description: description of the operation performed


### Table Connections

one-to-many connection from Machine to Reservation

one-to-many connection from User to Operations


## T-03 Feature Points

### Login Feature through token (15 points)

Upon starting the application, the user will be provided first with a login prompt where they enter credentials. If they provide a proper username and password combination, they are logged in as a user and given functionality depending on their role in the system. This is instantiated through a jwt token which is automatically passed in the header of every api-call from the user and permissions are instantiated based on the user's 'role' which is encoded in the system. Each route other than log in checks for valid login through the '@validate_user' wrapper and makes sure that the authenticated user is inline with the permissions associated with the route through the @role_required wrapper'. 

Permissions are constructed through a dictionary to the '@role_required' wrapper with the key:value mapping being associated to the 'user_role': 'function with logic for additional constraints or None'. If a user_role is not allowed to access the route, then it is left out of the permissions dictionary.


### Configurable Business Rules (5 points)

We added an admin command on the frontend that allows the user to set particular values related to Reservations and logistics. Once the frontend rule and value are specified, an API request is made to the backend to change those values in the code. Then, the admin can set the following values in the code:

harvester_price \
scooper_price_per_hour \
scanner_price_per_hour \
number_of_scoopers \
number_of_scanners \
weekday_start \
weekday_end \
weekdend_start \
weekend_end \
week_refund \
two_day_refund

Once these changes go through, these changes are generally updated for the entire system. Note that reservations created at certain prices will retain their original prices, but can get updated refund percentages based on their original down payment.


### Client activation management (5 points)

An admin can execute a command from the frontend that either deactivates a user, activates a user or lists all users with their activation state. An API endpoint has been specified to perform each of these tasks. The user's activation state is stored and modified in the database. A deactivated user cannot make a reservation or have a reservation made on their behalf.

## T-04 Feature Points

### Web Interface (15 points)

There is now a web interface containing core requirements of the reservation system.

## T-04 Additional Features

There is now an interoperability section designed to take in outside requests. It uses a shared endpoint in our backend between all the teams. It also has a separate client.

The configurable business rules were refactored in order to be more robust in the code.

We added additional tests and error handling for all features we have accumulated.


## Contributing

Contributors to this project include:

- Christian Urbanek
- Akshatha Ramkumar
- Graham Livingston
