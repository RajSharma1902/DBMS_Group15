-- Run in case of error
DROP DATABASE IF EXISTS hotel_db;
-- Create database
CREATE DATABASE IF NOT EXISTS hotel_db;
USE hotel_db;

-- Table: room_types
CREATE TABLE room_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(50),
    description TEXT
);

-- Table: roles
CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50)
);

-- Table: users
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    role_id INT,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE SET NULL
);

-- Table: rooms
CREATE TABLE rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room_number VARCHAR(10) UNIQUE,
    room_type_id INT,
    price_per_night DECIMAL(10, 2),
    status ENUM('available', 'booked') DEFAULT 'available',
    FOREIGN KEY (room_type_id) REFERENCES room_types(id)
);

-- Table: guests
CREATE TABLE guests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(15),
    address TEXT
);

-- Table: bookings
CREATE TABLE bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    guest_id INT,
    room_id INT,
    check_in DATE,
    check_out DATE,
    status VARCHAR(20) DEFAULT 'active',
    FOREIGN KEY (guest_id) REFERENCES guests(id),
    FOREIGN KEY (room_id) REFERENCES rooms(id)
);

-- Table: payments
CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT,
    amount DECIMAL(10, 2),
    payment_date DATE,
    payment_method VARCHAR(50),
    FOREIGN KEY (booking_id) REFERENCES bookings(id)
);

-- Table: staff
CREATE TABLE staff (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    role_id INT,
    email VARCHAR(100),
    phone VARCHAR(15),
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- Table: services
CREATE TABLE services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    service_name VARCHAR(100),
    price DECIMAL(10,2)
);

-- Table: booking_services
CREATE TABLE booking_services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT,
    service_id INT,
    FOREIGN KEY (booking_id) REFERENCES bookings(id),
    FOREIGN KEY (service_id) REFERENCES services(id)
);

-- Table: feedback
CREATE TABLE feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    guest_id INT,
    comments TEXT,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    FOREIGN KEY (guest_id) REFERENCES guests(id)
);
