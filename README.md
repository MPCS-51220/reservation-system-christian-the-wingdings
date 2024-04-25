# T-01: API-ify the Reservation System

## Overview
For this assignment, your team will work together to create an API-enabled version of the reservation system that we've already worked on.  You can rewrite code or borrow from any that you've already written or refactored.  You'll be using FastAPI, which allows you to write API applications fairly easily. We've discussed FastAPI in class and will continue to do so.  The full assignment can be found here: https://canvas.uchicago.edu/courses/56612/assignments/661290


# Equipment Reservation System Documentation

Welcome to the Equipment Reservation System! This system is designed to help users reserve various types of equipment through a simple command-line interface (CLI). Below you will find detailed instructions on how to install, configure, and use this system effectively.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
    - [Making a Reservation](#make-reservation)
    - [Cancelling a Reservation](#cancelling-a-reservation)
    - [Listing Reservations](#listing-reservations)
    - [Exiting the System](#exiting-the-system)
- [API Reference](#api-reference)
    - [Post a Reservation](#post-/reservations)
    - [Delete a Reservation](#delete-/reservations)
    - [Listing Reservations](#get-/reservations)
        - [By Machine](#get-/reservations/machines)
        - [By Customer](#get-reservations/customers)
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

    Enter the required details:
        Customer name.
        Machine choice 1 - 3.
        Start and end date/time for the reservation. formated YYYY-MM-DD HH:mm

### Cancelling a Reservation

    Select 'Cancel reservation' from the main menu.
    Enter the ID of the reservation you wish to cancel.
        The system will confirm the cancellation and show any applicable refund.

### Listing Reservations

    Select 'List reservations' from the main menu.
    Choose the type of listing you need (by date, machine, or customer).
    Enter the required parameters based on your selection.

### Exiting the System

    Select 'Quit' from the main menu.
    Choose whether to save changes (if applicable).

## API Reference

This section details the available endpoints within the Equipment Reservation System, examples of successful responses, and errors that might occur during each operation.

### POST /reservations

Creates a new equipment reservation.

- **Request Body**:
  - `customer_name`: string (required)
  - `machine_type`: string (required)
  - `start_date`: datetime (required)
  - `end_date`: datetime (required)

- **Example of Successful Response**:
  ```json
  {
    "success": true,
    "id": 1,
    "message": "Reservation created successfully."
  }
  ```

- **Possible Errors**:
  - `ValidationError`: Occurs when there is missing or invalid data in the request.
  - `DatabaseError`: If there is an issue connecting to or querying the database.
  - `UnavailableEquipmentError`: If the requested equipment is not available for the specified date/time.

### DELETE /reservations

Cancels an existing reservation.

- **URL Parameters**:
  - `reservation_id`: int (required)

- **Example of Successful Response**:
  ```json
  {
    "success": true,
    "message": "Reservation cancelled successfully."
  }
  ```

- **Possible Errors**:
  - `ReservationNotFoundError`: If the reservation with the specified ID does not exist.
  - `DatabaseError`: If there is an issue connecting to or querying the database.

### GET /reservations

Lists all current reservations.

- **Example of Successful Response**:
  ```json
  [
    {
      "id": 1,
      "customer_name": "John Doe",
      "machine_type": "scanner",
      "start_date": "2024-01-01T09:00:00Z",
      "end_date": "2024-01-02T09:00:00Z"
    }
  ]
  ```

- **Possible Errors**:
  - `DatabaseError`: If there is an issue connecting to or querying the database.

### GET /reservations/machines

Lists all reservations for a specific machine.

- **URL Parameters**:
  - `machine_name`: string (required)

- **Example of Successful Response**:
  ```json
  [
    {
      "id": 1,
      "customer_name": "Jane Smith",
      "start_date": "2024-02-01T09:00:00Z",
      "end_date": "2024-02-02T09:00:00Z"
    }
  ]
  ```

- **Possible Errors**:
  - `MachineNotFoundError`: If no machine matches the given name.
  - `DatabaseError`: If there is an issue connecting to or querying the database.

### GET /reservations/customers

Lists all reservations for a specific customer.

- **URL Parameters**:
  - `customer_name`: string (required)

- **Example of Successful Response**:
  ```json
  [
    {
      "id": 3,
      "machine_type": "harvester",
      "start_date": "2024-03-01T09:00:00Z",
      "end_date": "2024-03-02T09:00:00Z"
    }
  ]
  ```

- **Possible Errors**:
  - `CustomerNotFoundError`: If no reservations exist for the specified customer.
  - `DatabaseError`: If there is an issue connecting to or querying the database.



## Contributing

Contributors to this project include:

- Christian Urbanek
- Akshatha Ramkumar
- Graham Livingston
