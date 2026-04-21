# GyanPustak – Online Textbook Platform

GyanPustak is a web-based platform designed for college students to buy, rent, and explore textbooks. The system supports new books, used books, and electronic books. It provides role-based access for students and employees to manage different functionalities of the platform.

The application is built using Flask, Jinja2, and MySQL.

Demo Video Link:https://drive.google.com/file/d/1cFmM0UOc-_vbf6tMJrXLwQ3ak0o2UzsV/view?usp=sharing
---

## Overview

The system consists of two main user groups:

- Students: Use the platform to browse, purchase, rent, and review books  
- Employees: Manage operations such as support tickets, book inventory, and user management  

Employees are further divided into:
- Customer Support  
- Administrator  
- Super Administrator  

---

## Features

### Student
- Browse and search books by title, author, or category  
- Add books to cart (buy or rent)  
- Checkout and place orders  
- View order history  
- Write and update reviews  
- Submit support tickets  
- Edit profile  

### Customer Support
- View all support tickets  
- Assign new tickets to administrators  
- Create tickets  
- Cancel orders (if not shipped)  

### Administrator
- Manage books (add, edit, delete)  
- Handle assigned tickets  
- Link books to courses  

### Super Administrator
- Add and remove employees  
- Manage administrators and support staff  

---

## Tech Stack

- Frontend: HTML, CSS, JavaScript, Jinja2  
- Backend: Python (Flask)  
- Database: MySQL  
- Connector: MySQL Connector for Python  

---

## Project Structure

gyanpustak/
│── app.py
│── schema.sql
│── requirements.txt
│── README.md
│
├── templates/
├── static/
│   ├── css/
│   └── js/

---

## Setup Instructions

### 1. Setup Database

Run the following command:

mysql -u root -p < schema.sql

This will create the database, tables, and insert sample data.

---

### 2. Install Dependencies

pip install -r requirements.txt

---

### 3. Configure Database (Optional)

If your MySQL credentials are different, set environment variables:

Windows:
set DB_HOST=localhost
set DB_USER=root
set DB_PASSWORD=yourpassword

Mac/Linux:
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=yourpassword

---

### 4. Run the Application

python app.py

Open in browser:
http://localhost:5000

---

## Login Credentials

### Student Login
- URL: /student/login  
- Example:
  - Student ID: 1  
  - Name: Rohit Singh  

Register new student:
/student/register

---

### Employee Login

Role              Email                      Password        
-----------------------------------------------------------
Super Admin      superadmin@gyanpustak.com   superadmin123   
Administrator    arun.admin@gyanpustak.com   admin123        
Customer Support meena.cs@gyanpustak.com     cs123           

---

## Key Functionalities

- Role-based authentication and access control  
- Book catalog with search and filtering  
- Shopping cart and order management  
- Review and rating system  
- Support ticket system with status tracking  

---

## Assumptions

- Users have access to a web browser (Chrome or similar)  
- MySQL server is installed and running  
- Python 3.8 or higher is installed  

---

## Future Enhancements

- Payment gateway integration  
- Email notifications  
- Improved UI and responsiveness  
- Recommendation system  

---

## License

This project is developed for academic purposes.
