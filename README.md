# T-01: API-ify the Reservation System

## Overview
For this assignment, your team will work together to create an API-enabled version of the reservation system that we've already worked on.  You can rewrite code or borrow from any that you've already written or refactored.  You'll be using FastAPI, which allows you to write API applications fairly easily. We've discussed FastAPI in class and will continue to do so.  The full assignment can be found here: https://canvas.uchicago.edu/courses/56612/assignments/661290


# Equipment Reservation System Documentation

Welcome to the Equipment Reservation System! This system is designed to help users reserve various types of equipment through a simple command-line interface (CLI). Below you will find detailed instructions on how to install, configure, and use this system effectively.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
    - [Making a Reservation](#making-a-reservation)
    - [Cancelling a Reservation](#cancelling-a-reservation)
    - [Listing Reservations](#listing-reservations)
    - [Exiting the System](#exiting-the-system)
- [API Reference](#api-reference)
    - [Post Reservation](#post-reservations)
    - [Delete Reservation](#delete-reservations)
    - [GET Reservations](#get-reservations)
    - [GET Reservations By Machine](#get-reservations/machines)
    - [GET Reservations By Customer](#get-reservations/customers)
    <!-- - [Exiting the System](#exiting-the-system) -->
- [Contributing](#contributing)


## Installation

Before you can run the Equipment Reservation System, you need to ensure that Python, FastAPI, Uvicorn, and the requests library are installed on your machine.

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

## API Reference

This section details the available endpoints within the Equipment Reservation System, examples of successful responses, and errors that might occur during each operation.

### POST Reservations

Creates a new equipment reservation.

- **Parameters**:
  - `customer_name`: string (required)
  - `machine_type`: string (required)
  - `start_date`: datetime (required)
  - `end_date`: datetime (required)

### DELETE Reservations

Cancels an existing reservation.

- **Parameters**:
  - `reservation_id`: int (required)

### GET /reservations

Lists all current reservations in a date range.
- **Parameters**:
  - `start_date`: str (required)
  - `end_date`: str (required)

### GET Reservations/Machines

Lists all reservations for a specific machine.

- **Parameters**:
  - `machine_name`: string (required)
  - `start_date`: str (required)
  - `end_date`: str (required)

### GET Reservations/Customers

Lists all reservations for a specific customer.

- **Parameters**:
  - `customer_name`: string (required)
  - `start_date`: str (required)
  - `end_date`: str (required)

## Contributing

Contributors to this project include:

- Christian Urbanek
- Akshatha Ramkumar
- Graham Livingston
