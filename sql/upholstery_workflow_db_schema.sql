CREATE DATABASE upholstery_order_tracker;
USE upholstery_order_tracker;

-- 1. Customers
CREATE TABLE Customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    city TEXT,
    state TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Orders
CREATE TABLE Orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    due_date DATE,
    status VARCHAR(50),
    notes TEXT,
    barcode_value VARCHAR(225),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
);

-- 3. Products
CREATE TABLE Products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

-- 4. Order_Items
CREATE TABLE Order_Items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    barcode VARCHAR(50) UNIQUE,
    description TEXT,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
);

-- 5. Tasks
CREATE TABLE Tasks (
    task_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    sequence INT,
    estimated_time_minutes INT
);

-- 6. Item_Workflow
CREATE TABLE Item_Workflow (
    workflow_id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT,
    task_id INT,
    sequence INT,
    notes TEXT,
    FOREIGN KEY (item_id) REFERENCES Order_Items(item_id),
    FOREIGN KEY (task_id) REFERENCES Tasks(task_id)
);

-- 7. Employees
CREATE TABLE Employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    role VARCHAR(50)
);

-- 8. Scan_Events
CREATE TABLE Scan_Events (
    scan_id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT,
    task_id INT,
    employee_id INT,
    scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Started', 'Completed') NOT NULL,
    notes TEXT,
    FOREIGN KEY (item_id) REFERENCES Order_Items(item_id),
    FOREIGN KEY (task_id) REFERENCES Tasks(task_id),
    FOREIGN KEY (employee_id) REFERENCES Employees(employee_id)
);
