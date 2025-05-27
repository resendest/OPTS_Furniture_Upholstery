DROP TABLE IF EXISTS scan_events;
DROP TABLE IF EXISTS item_workflow;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS customers;

-- 1. customers
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    city TEXT,
    state TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. products
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

-- 3. tasks
CREATE TABLE tasks (
    task_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    sequence INT,
    estimated_time_minutes INT
);

-- 4. employees
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    role VARCHAR(50)
);

-- 5. orders
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    order_date DATE,
    due_date DATE,
    status VARCHAR(50),
    notes TEXT,
    barcode_value VARCHAR(225),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. order_items
CREATE TABLE order_items (
    item_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(order_id),
    product_id INT REFERENCES products(product_id),
    barcode VARCHAR(50) UNIQUE,
    description TEXT,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. item_workflow
CREATE TABLE item_workflow (
    workflow_id SERIAL PRIMARY KEY,
    item_id INT REFERENCES order_items(item_id),
    task_id INT REFERENCES tasks(task_id),
    sequence INT,
    notes TEXT
);

-- 8. scan_events
CREATE TABLE scan_events (
    scan_id SERIAL PRIMARY KEY,
    item_id INT REFERENCES order_items(item_id),
    task_id INT REFERENCES tasks(task_id),
    employee_id INT REFERENCES employees(employee_id),
    scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL CHECK (status IN ('Started', 'Completed')),
    notes TEXT
);