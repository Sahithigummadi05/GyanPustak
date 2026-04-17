-- GyanPustak Database Schema
-- Run this file in MySQL to create all tables and insert sample data

CREATE DATABASE IF NOT EXISTS gyanpustak;
USE gyanpustak;

-- ─────────────────────────────────────────────
-- EMPLOYEE (base for CS and Admin)
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS employee (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    fname VARCHAR(100) NOT NULL,
    lname VARCHAR(100) NOT NULL,
    gender ENUM('Male','Female','Other') NOT NULL,
    salary DECIMAL(10,2),
    aadhaar VARCHAR(12) UNIQUE,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(15),
    address TEXT,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS administrator (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL UNIQUE,
    is_super_admin TINYINT(1) DEFAULT 0,
    added_by INT,
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id),
    FOREIGN KEY (added_by) REFERENCES administrator(admin_id)
);

CREATE TABLE IF NOT EXISTS customer_support (
    cs_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL UNIQUE,
    added_by INT,
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id),
    FOREIGN KEY (added_by) REFERENCES administrator(admin_id)
);

-- ─────────────────────────────────────────────
-- UNIVERSITY / DEPARTMENT / INSTRUCTOR / COURSE
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS university (
    university_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    address TEXT,
    rep_fname VARCHAR(100),
    rep_lname VARCHAR(100),
    rep_email VARCHAR(150),
    rep_phone VARCHAR(15)
);

CREATE TABLE IF NOT EXISTS department (
    dept_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    university_id INT NOT NULL,
    FOREIGN KEY (university_id) REFERENCES university(university_id)
);

CREATE TABLE IF NOT EXISTS instructor (
    instructor_id INT AUTO_INCREMENT PRIMARY KEY,
    fname VARCHAR(100) NOT NULL,
    lname VARCHAR(100) NOT NULL,
    university_id INT NOT NULL,
    dept_id INT,
    FOREIGN KEY (university_id) REFERENCES university(university_id),
    FOREIGN KEY (dept_id) REFERENCES department(dept_id)
);

CREATE TABLE IF NOT EXISTS course (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    year INT,
    semester VARCHAR(20),
    university_id INT NOT NULL,
    FOREIGN KEY (university_id) REFERENCES university(university_id)
);

CREATE TABLE IF NOT EXISTS course_department (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    dept_id INT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES course(course_id),
    FOREIGN KEY (dept_id) REFERENCES department(dept_id)
);

CREATE TABLE IF NOT EXISTS course_instructor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    instructor_id INT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES course(course_id),
    FOREIGN KEY (instructor_id) REFERENCES instructor(instructor_id)
);

-- ─────────────────────────────────────────────
-- STUDENT
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS student (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    fname VARCHAR(100) NOT NULL,
    lname VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    address TEXT,
    phone VARCHAR(15),
    dob DATE,
    major VARCHAR(200),
    status ENUM('Graduate','Undergraduate') DEFAULT 'Undergraduate',
    year_of_study INT,
    university_id INT,
    password VARCHAR(255) NOT NULL,
    FOREIGN KEY (university_id) REFERENCES university(university_id)
);

-- ─────────────────────────────────────────────
-- BOOK-related
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS publisher (
    publisher_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL
);

CREATE TABLE IF NOT EXISTS category (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS subcategory (
    subcategory_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category_id INT,
    FOREIGN KEY (category_id) REFERENCES category(category_id)
);

CREATE TABLE IF NOT EXISTS author (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL
);

CREATE TABLE IF NOT EXISTS keyword (
    keyword_id INT AUTO_INCREMENT PRIMARY KEY,
    word VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS book (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    isbn VARCHAR(20) UNIQUE,
    type ENUM('New','Used') DEFAULT 'New',
    purchase_option ENUM('Rent','Buy','Both') DEFAULT 'Buy',
    price DECIMAL(10,2),
    quantity INT DEFAULT 0,
    language VARCHAR(50) DEFAULT 'English',
    format ENUM('Hardcover','Softcover','Electronic') DEFAULT 'Hardcover',
    edition INT DEFAULT 1,
    publication_date DATE,
    avg_rating DECIMAL(3,2) DEFAULT 0.00,
    publisher_id INT,
    category_id INT,
    last_updated_by INT,
    FOREIGN KEY (publisher_id) REFERENCES publisher(publisher_id),
    FOREIGN KEY (category_id) REFERENCES category(category_id),
    FOREIGN KEY (last_updated_by) REFERENCES administrator(admin_id)
);

CREATE TABLE IF NOT EXISTS book_author (
    book_id INT NOT NULL,
    author_id INT NOT NULL,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES book(book_id),
    FOREIGN KEY (author_id) REFERENCES author(author_id)
);

CREATE TABLE IF NOT EXISTS book_keyword (
    book_id INT NOT NULL,
    keyword_id INT NOT NULL,
    PRIMARY KEY (book_id, keyword_id),
    FOREIGN KEY (book_id) REFERENCES book(book_id),
    FOREIGN KEY (keyword_id) REFERENCES keyword(keyword_id)
);

CREATE TABLE IF NOT EXISTS book_subcategory (
    book_id INT NOT NULL,
    subcategory_id INT NOT NULL,
    PRIMARY KEY (book_id, subcategory_id),
    FOREIGN KEY (book_id) REFERENCES book(book_id),
    FOREIGN KEY (subcategory_id) REFERENCES subcategory(subcategory_id)
);

CREATE TABLE IF NOT EXISTS course_book (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    book_id INT NOT NULL,
    instructor_id INT,
    requirement_type ENUM('Required','Recommended') DEFAULT 'Required',
    added_by_admin INT,
    FOREIGN KEY (course_id) REFERENCES course(course_id),
    FOREIGN KEY (book_id) REFERENCES book(book_id),
    FOREIGN KEY (instructor_id) REFERENCES instructor(instructor_id),
    FOREIGN KEY (added_by_admin) REFERENCES administrator(admin_id)
);

-- ─────────────────────────────────────────────
-- REVIEW
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS review (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    book_id INT NOT NULL,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT,
    date_written DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (student_id) REFERENCES student(student_id),
    FOREIGN KEY (book_id) REFERENCES book(book_id)
);

-- ─────────────────────────────────────────────
-- CART & ORDER
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS cart (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL UNIQUE,
    date_created DATE DEFAULT (CURRENT_DATE),
    date_updated DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (student_id) REFERENCES student(student_id)
);

CREATE TABLE IF NOT EXISTS cart_item (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    cart_id INT NOT NULL,
    book_id INT NOT NULL,
    quantity INT DEFAULT 1,
    transaction_type ENUM('Buy','Rent') DEFAULT 'Buy',
    FOREIGN KEY (cart_id) REFERENCES cart(cart_id),
    FOREIGN KEY (book_id) REFERENCES book(book_id)
);

CREATE TABLE IF NOT EXISTS `order` (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    date_created DATE DEFAULT (CURRENT_DATE),
    date_fulfilled DATE,
    shipping_type ENUM('Standard','2-Day','1-Day') DEFAULT 'Standard',
    cc_number VARCHAR(20),
    cc_expiry VARCHAR(7),
    cc_holder VARCHAR(200),
    cc_type VARCHAR(30),
    status ENUM('New','Processed','Awaiting Shipping','Shipped','Canceled') DEFAULT 'New',
    cancelled_by_cs INT,
    FOREIGN KEY (student_id) REFERENCES student(student_id),
    FOREIGN KEY (cancelled_by_cs) REFERENCES customer_support(cs_id)
);

CREATE TABLE IF NOT EXISTS order_item (
    order_id INT NOT NULL,
    book_id INT NOT NULL,
    quantity INT DEFAULT 1,
    price DECIMAL(10,2),
    transaction_type ENUM('Buy','Rent') DEFAULT 'Buy',
    PRIMARY KEY (order_id, book_id),
    FOREIGN KEY (order_id) REFERENCES `order`(order_id),
    FOREIGN KEY (book_id) REFERENCES book(book_id)
);

-- ─────────────────────────────────────────────
-- TROUBLE TICKET
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS trouble_ticket (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    date_logged DATE DEFAULT (CURRENT_DATE),
    title VARCHAR(300),
    problem_desc TEXT,
    solution_desc TEXT,
    completion_date DATE,
    status ENUM('New','Assigned','In-Process','Completed') DEFAULT 'New',
    category ENUM('User Profile','Products','Cart','Orders','Other') DEFAULT 'Other',
    created_by_student INT,
    created_by_cs INT,
    resolved_by_admin INT,
    assigned_to_admin INT,
    FOREIGN KEY (created_by_student) REFERENCES student(student_id),
    FOREIGN KEY (created_by_cs) REFERENCES customer_support(cs_id),
    FOREIGN KEY (resolved_by_admin) REFERENCES administrator(admin_id),
    FOREIGN KEY (assigned_to_admin) REFERENCES administrator(admin_id)
);

CREATE TABLE IF NOT EXISTS ticket_status_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL,
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    changed_by_employee INT,
    FOREIGN KEY (ticket_id) REFERENCES trouble_ticket(ticket_id),
    FOREIGN KEY (changed_by_employee) REFERENCES employee(employee_id)
);

-- ─────────────────────────────────────────────
-- SAMPLE DATA
-- ─────────────────────────────────────────────

-- Universities
INSERT INTO university (name, address, rep_fname, rep_lname, rep_email, rep_phone) VALUES
('IIT Delhi', 'Hauz Khas, New Delhi 110016', 'Ramesh', 'Kumar', 'ramesh@iitd.ac.in', '9876543210'),
('NIT Trichy', 'Tanjore Main Road, Tiruchirappalli 620015', 'Priya', 'Sharma', 'priya@nitt.edu', '9123456780');

-- Departments
INSERT INTO department (name, university_id) VALUES
('Computer Science', 1),
('Mathematics', 1),
('Electronics', 2),
('Computer Science', 2);

-- Publishers
INSERT INTO publisher (name) VALUES
('Pearson'), ('McGraw-Hill'), ('O\'Reilly'), ('Wiley'), ('Springer');

-- Categories
INSERT INTO category (name) VALUES
('Computer Science'), ('Mathematics'), ('Physics'), ('Engineering'), ('Management');

-- Subcategories
INSERT INTO subcategory (name, category_id) VALUES
('Algorithms', 1), ('Databases', 1), ('Operating Systems', 1),
('Linear Algebra', 2), ('Calculus', 2);

-- Authors
INSERT INTO author (name) VALUES
('Thomas H. Cormen'), ('Abraham Silberschatz'), ('Andrew S. Tanenbaum'),
('Gilbert Strang'), ('Dennis Ritchie');

-- Keywords
INSERT INTO keyword (word) VALUES
('algorithms'), ('database'), ('networking'), ('operating-system'), ('data-structures');

-- Employees (passwords are stored as plain SHA2 here; app uses sha2 or bcrypt — for demo we store raw)
-- Super Admin
INSERT INTO employee (fname, lname, gender, salary, aadhaar, email, phone, address, password) VALUES
('Super', 'Admin', 'Male', 150000.00, '111122223333', 'superadmin@gyanpustak.com', '9000000001', 'HQ, New Delhi', 'superadmin123');

INSERT INTO administrator (employee_id, is_super_admin, added_by) VALUES (1, 1, NULL);

-- Regular Admin
INSERT INTO employee (fname, lname, gender, salary, aadhaar, email, phone, address, password) VALUES
('Arun', 'Verma', 'Male', 80000.00, '444455556666', 'arun.admin@gyanpustak.com', '9000000002', 'Connaught Place, Delhi', 'admin123');

INSERT INTO administrator (employee_id, is_super_admin, added_by) VALUES (2, 0, 1);

-- Customer Support
INSERT INTO employee (fname, lname, gender, salary, aadhaar, email, phone, address, password) VALUES
('Meena', 'Raj', 'Female', 50000.00, '777788889999', 'meena.cs@gyanpustak.com', '9000000003', 'Lajpat Nagar, Delhi', 'cs123');

INSERT INTO customer_support (employee_id, added_by) VALUES (3, 1);

-- Students
INSERT INTO student (fname, lname, email, address, phone, dob, major, status, year_of_study, university_id, password) VALUES
('Rohit', 'Singh', 'rohit@student.com', 'Delhi', '9111111111', '2002-05-10', 'Computer Science', 'Undergraduate', 3, 1, 'student123'),
('Anjali', 'Mehta', 'anjali@student.com', 'Mumbai', '9222222222', '2001-08-22', 'Mathematics', 'Undergraduate', 4, 1, 'student456');

-- Instructors
INSERT INTO instructor (fname, lname, university_id, dept_id) VALUES
('Dr. Patel', 'Suresh', 1, 1),
('Dr. Lakshmi', 'Nair', 2, 4);

-- Courses
INSERT INTO course (name, year, semester, university_id) VALUES
('Data Structures and Algorithms', 2025, 'Spring', 1),
('Database Management Systems', 2025, 'Spring', 1),
('Computer Networks', 2025, 'Fall', 2);

INSERT INTO course_department (course_id, dept_id) VALUES (1,1),(2,1),(3,4);
INSERT INTO course_instructor (course_id, instructor_id) VALUES (1,1),(2,1),(3,2);

-- Books
INSERT INTO book (title, isbn, type, purchase_option, price, quantity, language, format, edition, publication_date, avg_rating, publisher_id, category_id, last_updated_by) VALUES
('Introduction to Algorithms', '978-0262033848', 'New', 'Both', 899.00, 50, 'English', 'Hardcover', 4, '2022-04-05', 4.8, 1, 1, 1),
('Database System Concepts', '978-0078022159', 'New', 'Buy', 749.00, 30, 'English', 'Hardcover', 7, '2019-02-19', 4.6, 2, 1, 2),
('Computer Networks', '978-0132126953', 'Used', 'Rent', 299.00, 20, 'English', 'Softcover', 5, '2010-10-07', 4.3, 1, 4, 2),
('Linear Algebra and Its Applications', '978-0321982384', 'New', 'Both', 599.00, 40, 'English', 'Hardcover', 5, '2016-01-01', 4.5, 4, 2, 1),
('The C Programming Language', '978-0131103627', 'New', 'Buy', 399.00, 25, 'English', 'Softcover', 2, '1988-03-22', 4.9, 4, 1, 2);

INSERT INTO book_author (book_id, author_id) VALUES (1,1),(2,2),(3,3),(4,4),(5,5);
INSERT INTO book_keyword (book_id, keyword_id) VALUES (1,1),(1,5),(2,2),(3,2),(4,3),(5,1);
INSERT INTO book_subcategory (book_id, subcategory_id) VALUES (1,1),(2,2),(3,3),(4,4),(5,1);

INSERT INTO course_book (course_id, book_id, instructor_id, requirement_type, added_by_admin) VALUES
(1, 1, 1, 'Required', 1),
(2, 2, 1, 'Required', 1),
(3, 3, 2, 'Recommended', 2);

-- Carts for students
INSERT INTO cart (student_id, date_created, date_updated) VALUES (1, CURDATE(), CURDATE());

-- Reviews
INSERT INTO review (student_id, book_id, rating, review_text, date_written) VALUES
(1, 1, 5, 'Excellent book for algorithms! Very detailed and clear explanations.', '2024-12-01'),
(2, 2, 4, 'Great reference for database concepts. Comprehensive coverage.', '2025-01-15');

-- Tickets
INSERT INTO trouble_ticket (date_logged, title, problem_desc, status, category, created_by_student) VALUES
('2025-01-10', 'Book not available', 'The book Introduction to Algorithms shows out of stock but website still shows available.', 'New', 'Products', 1),
('2025-01-12', 'Cart issue', 'Cannot add books to cart, getting an error.', 'Assigned', 'Cart', 2);

UPDATE trouble_ticket SET assigned_to_admin=2 WHERE ticket_id=2;
UPDATE trouble_ticket SET status='Assigned' WHERE ticket_id=2;

-- Orders
INSERT INTO `order` (student_id, date_created, shipping_type, cc_number, cc_expiry, cc_holder, cc_type, status) VALUES
(1, '2025-01-05', 'Standard', '4111111111111111', '12/27', 'Rohit Singh', 'Visa', 'Shipped'),
(2, '2025-01-08', '2-Day', '5500005555555559', '06/26', 'Anjali Mehta', 'Mastercard', 'Processed');

INSERT INTO order_item (order_id, book_id, quantity, price, transaction_type) VALUES
(1, 1, 1, 899.00, 'Buy'),
(2, 2, 1, 749.00, 'Buy'),
(2, 4, 1, 599.00, 'Rent');
