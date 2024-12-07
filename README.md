
# Equipment Reservation System

## Overview
This is the final project for MPCS course 56612 Introduction to Software enginneering. The full assignment can be found here: https://canvas.uchicago.edu/courses/56612/assignments/663325?module_item_id=2406263


## Description

Welcome to the Equipment Reservation System! This system is designed to help users reserve various types of equipment through a web interface and a command-line interface (CLI), both developed using FastAPI. This comprehensive system aims to consolidate reservation processes across multiple facilities.


## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Running Tests](#running-tests)
- [Database Design](#database-system)
- [T-03 Security Discussion](#t-02-security-discussion)
- [T-03 Feature Points](#t-03-feature-points)
- [T-04 Feature Points](#t-04-feature-points)
- [T-04 Additional Features](#t-04-additional-features)
- [Contributing](#contributing)

## Installation

### Prerequisites

- Python 3.8 or higher
- SQLite

### Common Steps

1. Clone the repository:
   ```
   git clone https://github.com/MPCS-51220/reservation-system-christian-the-wingdings.git
   ```
2. Navigate to the project directory:
   ```
   cd reservation-system-christian-the-wingdings
   ```
3. Install required dependencies:
   ```
   pip install -r req.txt
   ```

### Starting the Backend Server

Navigate to the backend directory and run the following command to start the server:

```bash
uvicorn main:app --reload
```

## Usage

### Web Interface

1. Access the web interface through your browser by navigating to `http://localhost:8000`.
2. Follow the on-screen instructions to log in, make reservations, and manage equipment.

### CLI

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```
2. Run the CLI application:
   ```
   python app.py
   ```

### Logging-in

The administrator view can be accessed using the username `graham` and password `graham`

### Making a Reservation

   1. Select 'Make reservation' by entering 1 from the main menu of the CLI or click on the 'Make reservation' item in the tool-bar of the web-interface.

   2. Enter the required details:(Customer Name, Machine choice, Start Date and Time, End Date and Time)

   3. The system will confirm upon success.

*start/end is formated YYYY-MM-DD HH:MM*

### Cancelling a Reservation
    
   1. Select 'Cancel reservation' or enter 2 from the main menu of the CLI.

   2. Enter the ID of the reservation you wish to cancel.

   3. The system will confirm the cancellation and show any applicable refund.

### Listing Reservations

   1. Select 'List reservations' by entering 3 from the main menu.

   2. Choose the type of listing you need (by date, machine, or customer).

   3. Enter the required parameters based on your selection.

### Exiting the System

   Typing 'Exit' at any point will exit your current command in the CLI. If you are viewing the main menu this will close the system

   On the web-interface simply close the tab

### Making a New User

Per stipulations of the assignment, new users can only be created by an administrator. 

The new user will be given a temporary password assigned by the administrator for their first time accessing the portal. So if the admin assigns user1 the password `hello`, then to login user1 will use the password `_temphello`. user1 will then be prompted to change their password before continuing to make reservations. Upon successful reset user1 can reload the page and login using their new password.

## Running Tests

In a python environment, make sure pytest is installed with

```bash
pip install pytest
```

Then in the backend directory which contains the test_main.py file, run

```bash
pytest
```

## Database System

With the introduction of user data, we have adopted a relational database system to store user and machine data. Here is a breakdown of the tables in the system.

### Machine
    Machine_id (PK): unique id for the machine type
    Name: (scanner, scooper, harvester)
    quantity: number of machines of the type
    cooldown: cooldown time in minutes
    rate: rate per hour


### Reservation
    reservation_id (PK): unique reservation id
    customer: name of customer
    machine_id (FK): id of machine type reserved
    start_date: start date and time of reservation
    end_date: end date and time of reservation
    total_cost: total cost of reservation
    down_payment: down payment for reservation


### User
    user_id (PK): unique user id
    username: user’s name
    password_hash: hashed password
    role: (admin, customer, scheduler)
    salt: unique salt for password
    is_active: specifies if the user is activated or deactivated


### Operation
    operation_id (PK): unique id for the operation
    user_id (FK): id of the user who performed the operation
    timestamp: timestamp of the operation
    type: type of the operation (cancellation, making reservation, listing reservations, adding users)
    description: description of the operation performed


### Table Connections

one-to-many connection from Machine to Reservation

one-to-many connection from User to Operations

## T-03 Security Discussion

Our implementation has some security assumptions. The front end and server is not encrypted, but we are assuming that it would be in a more fleshed-out implementation. Therefore, we are currently passing the users password directly through a POST route. This is a security concern.

Authorization happens through a login route which creates a jwt with a life span set to 15 min. This is automatically applied to the header of any requests from the user after they log in.

Lastly, we are currently refactoring the program to push all the content displayed to the user, ie the main menu and command options, to the backend. We are currently using a dictionary in the cli file. Once we push this to the backend, we will serve only the menu options that a user has access to execute.

## T-03 Feature Points

### Login Feature through token (15 points)

Upon starting the application, the user will be provided first with a login prompt where they enter credentials. If they provide a proper username and password combination, they are logged in as a user and given functionality depending on their role in the system. This is instantiated through a jwt token which is automatically passed in the header of every api-call from the user and permissions are instantiated based on the user's 'role' which is encoded in the system. Each route other than log in checks for valid login through the '@validate_user' wrapper and makes sure that the authenticated user is inline with the permissions associated with the route through the @role_required wrapper'. 

Permissions are constructed through a dictionary to the '@role_required' wrapper with the key:value mapping being associated to the 'user_role': 'function with logic for additional constraints or None'. If a user_role is not allowed to access the route, then it is left out of the permissions dictionary.


### Configurable Business Rules (5 points)

We added an admin command on the frontend that allows the user to set particular values related to Reservations and logistics. Once the frontend rule and value are specified, an API request is made to the backend to change those values in the code. Then, the admin can set the following values in the code:

- harvester_price \
- scooper_price_per_hour \
- scanner_price_per_hour \
- number_of_scoopers \
- number_of_scanners \
- weekday_start \
- weekday_end \
- weekdend_start \
- weekend_end \
- week_refund \
- two_day_refund

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
