# T-01: API-ify the Reservation System

## Overview
For this assignment, your team will work together to improve last week's iteration.  The work in this iteration is focussed on making your design and tests more robust, implementing a robust (well, at least somewhat robust) persistence layer, and setting up user roles and passwords. The full assignment can be found here: https://canvas.uchicago.edu/courses/56612/assignments/663327


# Equipment Reservation System Documentation

Welcome to the Equipment Reservation System! This system is designed to help users reserve various types of equipment through a simple command-line interface (CLI). Below you will find detailed instructions on how to install, configure, and use this system effectively.

## Table of Contents

- [Installation](#installation)
    - [Installing SQLite](#installing-sqlite)
- [New Features](#new-features)
    - [Segregated Testing](#segregated-test)
    - [Robust Error Handling](#error-handling)
    - [Login System](#login-feature)
- [Database System](#database-system)
    - [Machine](#machine)
    - [Reservation](#reservation)
    - [User](#user)
    - [Operation](#operation)
    - [Table Connections](#table-connections)
- [Contributing](#contributing)


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

## New Features

The Equipment Reservation System is accessed through a command-line interface. Below are new features added in this assignment.

### Segregated Test

Test data is stored in a separate pickle file so testing is separated from production data.

### Error Handling
    
We use try-catch along with resetting users to previous inputs in the case of bad user input and bad endpoints.

### Login Feature

Upon starting the application, the user will be provided first with a login prompt where they enter credentials. If they provide a proper username and password combination, they are logged in as a user and given functionality depending on their role in the system. Customers have basic functionality for scheduling, cancelling, and viewing equiptment, but only for their own data. Schedulers have customer functionality for all data. Admin have total access to users and can change their roles.

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
