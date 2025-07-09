--admin
CREATE TABLE admins (
  id int PRIMARY KEY AUTO_INCREMENT,
  name varchar(100) ,
  password_hash varchar(255) 
) 

--users
CREATE TABLE users (
  id int PRIMARY KEY AUTO_INCREMENT,
  username varchar(50),
  name varchar(100) ,
  email varchar(100) ,
  password_hash varchar(255) ,
  phone varchar(20) ,
  address text ,
  age int 
)

CREATE TABLE rooms (
  id int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT,
  room_type varchar(100) NOT NULL,
  floor varchar(100) NOT NULL,
  price decimal(10,2) NOT NULL,
  description text DEFAULT NULL,
  image varchar(255) DEFAULT NULL,
  status varchar(20) DEFAULT 'available',
  room_number varchar(50) NOT NULL,
  UNIQUE KEY room_number (`room_number`)
) 


--amenties
CREATE TABLE amenities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    amenity VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL
);

--booking
CREATE TABLE bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    room_id INT,
    check_in DATE,
    check_out DATE,
    guest INT,
    total_price DECIMAL(10, 2),
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'Pending',
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (room_id) REFERENCES rooms(id)
);

-- Booking-Amenities relation
CREATE TABLE booking_amenities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT,
    amenity_id INT,
    FOREIGN KEY (booking_id) REFERENCES bookings(id),
    FOREIGN KEY (amenity_id) REFERENCES amenities(id)
);

CREATE TABLE feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    status VARCHAR(20) DEFAULT 'pending',
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);




-- for 3rd normal form of data base 
/*
-- ADMIN TABLES (normalized name)
CREATE TABLE admins (
  id INT PRIMARY KEY AUTO_INCREMENT,
  first_name VARCHAR(50),
  last_name VARCHAR(50),
  password_hash VARCHAR(255)
);

-- USER TABLE (normalized name and atomic fields)
CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50) UNIQUE,
  first_name VARCHAR(50),
  middle_name VARCHAR(50),
  last_name VARCHAR(50),
  email VARCHAR(100) UNIQUE,
  password_hash VARCHAR(255),
  phone VARCHAR(20),
  address TEXT,
  age INT
);

-- FLOOR table (optional normalization if many repeated values)
CREATE TABLE floors (
  id INT PRIMARY KEY AUTO_INCREMENT,
  floor_name VARCHAR(50) UNIQUE
);

-- ROOM TYPES (normalizing repeated room types)
CREATE TABLE room_types (
  id INT PRIMARY KEY AUTO_INCREMENT,
  type_name VARCHAR(100) UNIQUE
);

-- ROOMS (normalized references to room_type and floor)
CREATE TABLE rooms (
  id INT PRIMARY KEY AUTO_INCREMENT,
  room_type_id INT,
  floor_id INT,
  price DECIMAL(10,2) NOT NULL,
  description TEXT,
  image VARCHAR(255),
  status VARCHAR(20) DEFAULT 'available',
  room_number VARCHAR(50) NOT NULL UNIQUE,
  FOREIGN KEY (room_type_id) REFERENCES room_types(id),
  FOREIGN KEY (floor_id) REFERENCES floors(id)
);

-- AMENITIES
CREATE TABLE amenities (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL UNIQUE,
  description TEXT,
  price DECIMAL(10,2) NOT NULL
);

-- BOOKINGS
CREATE TABLE bookings (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  room_id INT,
  check_in DATE,
  check_out DATE,
  guest INT,
  total_price DECIMAL(10,2),
  booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  status VARCHAR(50) DEFAULT 'Pending',
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (room_id) REFERENCES rooms(id)
);

-- BOOKING-AMENITY MAPPING
CREATE TABLE booking_amenities (
  id INT PRIMARY KEY AUTO_INCREMENT,
  booking_id INT,
  amenity_id INT,
  FOREIGN KEY (booking_id) REFERENCES bookings(id),
  FOREIGN KEY (amenity_id) REFERENCES amenities(id)
);

-- FEEDBACK STATUS TABLE
CREATE TABLE feedback_statuses (
  id INT PRIMARY KEY AUTO_INCREMENT,
  status_name VARCHAR(20) UNIQUE
);

-- FEEDBACK
CREATE TABLE feedback (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  message TEXT NOT NULL,
  rating INT CHECK (rating BETWEEN 1 AND 5),
  status_id INT,
  submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (status_id) REFERENCES feedback_statuses(id)
);
*/