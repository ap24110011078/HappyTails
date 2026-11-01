CREATE DATABASE IF NOT EXISTS petpaglus_db;
USE petpaglus_db;

CREATE TABLE IF NOT EXISTS shelters (
    shelter_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(150),
    contact VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS pets (
    pet_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    age INT NOT NULL,
    status ENUM('available', 'adopted') DEFAULT 'available',
    shelter_id INT,
    FOREIGN KEY (shelter_id) REFERENCES shelters(shelter_id)
);

CREATE TABLE IF NOT EXISTS adopters (
    adopter_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS adoption (
    adoption_id INT AUTO_INCREMENT PRIMARY KEY,
    pet_id INT,
    adopter_id INT,
    adoption_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pet_id) REFERENCES pets(pet_id),
    FOREIGN KEY (adopter_id) REFERENCES adopters(adopter_id)
);

CREATE TABLE IF NOT EXISTS vaccinations (
    vaccination_id INT AUTO_INCREMENT PRIMARY KEY,
    pet_id INT,
    vaccine_name VARCHAR(100),
    vaccination_date DATE,
    FOREIGN KEY (pet_id) REFERENCES pets(pet_id)
);

CREATE TABLE IF NOT EXISTS staff (
    staff_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    role VARCHAR(50),
    shelter_id INT,
    FOREIGN KEY (shelter_id) REFERENCES shelters(shelter_id)
);

INSERT INTO shelters (name, location, contact) VALUES
('Happy Tails Shelter', 'Hyderabad', '9999999999'),
('Paws Care Center', 'Vijayawada', '8888888888');

INSERT INTO pets (name, type, age, status, shelter_id) VALUES
('Bella', 'Dog', 3, 'available', 1),
('Luna', 'Cat', 2, 'available', 1),
('Charlie', 'Dog', 5, 'available', 2),
('Milo', 'Cat', 1, 'adopted', 2);

INSERT INTO adopters (name, phone) VALUES
('John Doe', '555-1234');

INSERT INTO adoption (pet_id, adopter_id, adoption_date) VALUES
(4, 1, CURRENT_TIMESTAMP);

INSERT INTO vaccinations (pet_id, vaccine_name, vaccination_date) VALUES
(1, 'Rabies', '2024-01-10'),
(2, 'Feline Distemper', '2024-02-15');

INSERT INTO staff (name, role, shelter_id) VALUES
('Ravi Kumar', 'Manager', 1),
('Anita Sharma', 'Caretaker', 2);
