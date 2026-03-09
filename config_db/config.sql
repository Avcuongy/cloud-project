CREATE DATABASE IF NOT EXISTS `customer_manager` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `customer_manager`;

CREATE TABLE CUSTOMERS (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    address TEXT,
    phone_number VARCHAR(20),
    email_address VARCHAR(150),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE = InnoDB;

CREATE TABLE COMMUNICATION_LOGS (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    type ENUM('SMS', 'EMAIL') NOT NULL,
    status ENUM('Pending', 'Success', 'Failed') DEFAULT 'Pending',
    message_id VARCHAR(255) COMMENT 'AWS Tracking ID',
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_customer_log FOREIGN KEY (customer_id) REFERENCES CUSTOMERS(customer_id) ON DELETE CASCADE
) ENGINE = InnoDB;