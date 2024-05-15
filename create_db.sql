CREATE TABLE Machine (
    Machine_id INTEGER PRIMARY KEY,
    Name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    cooldown INTEGER NOT NULL,
    rate REAL NOT NULL
);


CREATE TABLE Reservation (
    reservation_id INTEGER PRIMARY KEY AUTO,
    customer TEXT NOT NULL,
    machine_id INTEGER NOT NULL,
    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,
    total_cost REAL NOT NULL,
    down_payment REAL NOT NULL,
    FOREIGN KEY(machine_id) REFERENCES Machine(Machine_id)
);

CREATE TABLE User (
    user_id INTEGER PRIMARY KEY AUTO,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    salt TEXT NOT NULL,
    is_active INTEGER NOT NULL CHECK (is_active IN (0, 1))
);

CREATE TABLE Operation (
    operation_id INTEGER PRIMARY KEY AUTO,
    user_id INTEGER NOT NULL,
    timestamp DATETIME NOT NULL,
    type TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY(user_id) REFERENCES User(user_id)
);


INSERT INTO Machine (machine_id, name, quantity, cooldown, rate) VALUES
(1, 'scanner', 4, 60, 990.0);

INSERT INTO Machine (machine_id, name, quantity, cooldown, rate) VALUES
(2, 'scooper', 4, 0, 1000.0);

INSERT INTO Machine (machine_id, name, quantity, cooldown, rate) VALUES
(3, 'harvester', 1, 360, 88000.0);
