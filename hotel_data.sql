-- Use the database
USE hotel_db;

-- Insert into roles
INSERT INTO roles (role_name) VALUES 
('Admin'), 
('Staff');

-- Insert into users (simple plain text passwords)
INSERT INTO users (username, password, role_id) VALUES 
('admin', 'admin123', 1),
('staff', 'staff123', 2);

-- Insert room types
INSERT INTO room_types (type_name, description) VALUES
('Single', 'One single bed with basic facilities'),
('Double', 'Two beds or one double bed'),
('Suite', 'Luxury room with all amenities');

-- Insert rooms
INSERT INTO rooms (room_number, room_type_id, price_per_night, status) VALUES
('101', 1, 1200.00, 'available'),
('102', 1, 1200.00, 'available'),
('201', 2, 1800.00, 'available'),
('301', 3, 3000.00, 'booked');

-- Insert guests
INSERT INTO guests (name, email, phone, address) VALUES
('Ravi Kumar', 'ravi@example.com', '9876543210', 'Delhi'),
('Anjali Singh', 'anjali@example.com', '9876512345', 'Mumbai');

-- Insert bookings
INSERT INTO bookings (guest_id, room_id, check_in, check_out, status) VALUES
(1, 1, '2025-04-08', '2025-04-10', 'active'),
(2, 3, '2025-04-07', '2025-04-11', 'active');

-- Insert payments
INSERT INTO payments (booking_id, amount, payment_date, payment_method) VALUES
(1, 2400.00, '2025-04-08', 'Credit Card'),
(2, 7200.00, '2025-04-07', 'Cash');

-- Insert services
INSERT INTO services (service_name, price) VALUES
('Room Service', 300.00),
('Laundry', 150.00),
('Airport Pickup', 500.00);

-- Insert booking_services
INSERT INTO booking_services (booking_id, service_id) VALUES
(1, 1),
(1, 2),
(2, 3);

-- Insert feedback
INSERT INTO feedback (guest_id, comments, rating) VALUES
(1, 'Great service!', 5),
(2, 'WiFi could be better.', 3);
