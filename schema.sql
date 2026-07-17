DROP TABLE IF EXISTS expense_reports;
DROP TABLE IF EXISTS travel_logs;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS users;

CREATE TABLE users(
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(10) NOT NULL
);

CREATE TABLE employees(
    employee_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(50) UNIQUE NOT NULL,
    job_title VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
	ON DELETE CASCADE
	ON UPDATE CASCADE
);

CREATE TABLE travel_logs(
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT NOT NULL,
    start_time DATETIME,
    end_time DATETIME,
    miles_traveled INT, 
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
	ON DELETE CASCADE
	ON UPDATE CASCADE
);

CREATE TABLE expense_reports(
    report_id INT PRIMARY KEY AUTO_INCREMENT,
    log_id INT NOT NULL,
    description VARCHAR(100) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    category VARCHAR(20) NOT NULL,
    FOREIGN KEY (log_id) REFERENCES travel_logs(log_id)
	ON DELETE CASCADE
	ON UPDATE CASCADE
);

