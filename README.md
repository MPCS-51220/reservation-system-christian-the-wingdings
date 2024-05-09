# T-02: Pay Off Debt, Strengthen the Foundation, Persist Data, Track Users

## Overview
For this assignment, your team will work together to improve last week's iteration.  The work in this iteration is focussed on making your design and tests more robust, implementing a robust (well, at least somewhat robust) persistence layer, and setting up user roles and passwords. The full assignment can be found here: https://canvas.uchicago.edu/courses/56612/assignments/663327


# Equipment Reservation System Documentation

Welcome to the Equipment Reservation System! This system is designed to help users reserve various types of equipment through a simple command-line interface (CLI). Below you will find detailed instructions on how to install, configure, and use this system effectively.

## Table of Contents

- [Design](#design)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Running Tests](#running-tests)
- [Passwords for Sample Users](#passwords-for-sample-users)
- [T-02 Security Discussion](#t-02-security-discussion)
- [New Features](#new-features)
- [Database System](#database-system)
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

    Select 'Quit' by entering 4 from the main menu.
    Choose whether to save changes (if applicable).
*NOTE: calendar object will be saved as calendar.pkl in the main repo directory*


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

## T-02 Security Discussion

Our implementation has some security assumptions. We pass hashes between the backend and frontend pretty easily, and it definitely is not the most secure method. The front end and server are not encrypted, but we are assuming that it would be in a more fleshed-out implementation. Additionally, the role is a pretty easy variable to set in the code, and there is no protection to make sure it does not change (unless an admin changes it). This can be problematic because there are definitely ways to exploit our global variables in a way to give users too much permission.

Lastly, we were working on but did not fully complete a version with tokens for extra security on the user. Currently, we trust that when a user logs in that they are who they say they are when working with the backend. We do think there are additional security measures we could use.


## New Features

The Equipment Reservation System is accessed through a command-line interface. Below are new features added in this assignment.

### Segregated Test

Test data is stored in a separate databse (reservationDB) so testing is separated from our frotend logic and other data.

### Error Handling
    
We use try-catch along with resetting users to previous inputs in the case of bad user input and bad endpoints.

### Login Feature

Upon starting the application, the user will be provided first with a login prompt where they enter credentials. If they provide a proper username and password combination, they are logged in as a user and given functionality depending on their role in the system. Customers have basic functionality for scheduling, cancelling, and viewing equiptment, but only for their own data. Schedulers have customer functionality for all data. Admin have total access to users and can change their roles and reset passwords.

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


## Contributing

Contributors to this project include:

- Christian Urbanek
- Akshatha Ramkumar
- Graham Livingston
