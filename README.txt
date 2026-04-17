============================================================
  GyanPustak – Online Textbook Platform
  Flask + Jinja2 + MySQL
============================================================

REQUIREMENTS
------------
- Python 3.8+
- MySQL 5.7+ or 8.0+
- pip

SETUP STEPS
-----------

STEP 1: Set up the MySQL database
-----------------------------------
Open MySQL Workbench or the MySQL command line and run:

    mysql -u root -p < schema.sql

Or open schema.sql in MySQL Workbench and execute it.
This creates the database, all tables, and inserts sample data.

STEP 2: Install Python dependencies
--------------------------------------
Open a terminal in this folder and run:

    pip install -r requirements.txt

STEP 3: Configure database connection (if needed)
--------------------------------------------------
If your MySQL username/password/host differs from defaults,
set these environment variables before running:

    Windows (Command Prompt):
        set DB_HOST=localhost
        set DB_USER=root
        set DB_PASSWORD=yourpassword

    Mac/Linux (Terminal):
        export DB_HOST=localhost
        export DB_USER=root
        export DB_PASSWORD=yourpassword

Default values: host=localhost, user=root, password=(empty)

STEP 4: Run the Flask app
--------------------------
    python app.py

Then open your browser and go to:
    http://localhost:5000

============================================================
LOGIN CREDENTIALS
============================================================

STUDENT LOGIN  (URL: /student/login)
  Enter Student ID (number) + Full Name
  Sample: Student ID = 1, Name = Rohit Singh
  Sample: Student ID = 2, Name = Anjali Mehta

  To register a new student: http://localhost:5000/student/register

EMPLOYEE LOGIN  (URL: /employee/login)
  Used for: Customer Support, Admin, Super Admin

  Role              Email                           Password
  ----------------------------------------------------------------
  Super Admin       superadmin@gyanpustak.com       superadmin123
  Administrator     arun.admin@gyanpustak.com       admin123
  Customer Support  meena.cs@gyanpustak.com         cs123

============================================================
ROLE CAPABILITIES SUMMARY
============================================================

STUDENT
  - Browse / search books (by title, author, category)
  - Add books to cart (Buy or Rent)
  - Checkout with payment info
  - View order history
  - Write reviews for purchased books
  - Submit support tickets
  - Edit profile

CUSTOMER SUPPORT
  - View all tickets (all statuses)
  - Modify only "New" tickets → assign to admin
  - Create new tickets themselves
  - View and cancel orders (except Shipped)

ADMINISTRATOR
  - View/update tickets with status Assigned / In-Process / Completed
  - Add, edit, delete books
  - Link books to courses

SUPER ADMINISTRATOR
  - View all admins and CS staff
  - Add new administrators and customer support employees
  - Remove employees

============================================================
PROJECT STRUCTURE
============================================================

gyanpustak/
├── app.py              ← Main Flask application
├── schema.sql          ← Database schema + sample data
├── requirements.txt    ← Python dependencies
├── README.txt          ← This file
├── templates/
│   ├── base.html
│   ├── landing.html
│   ├── navbar.html
│   ├── student_login.html
│   ├── student_register.html
│   ├── employee_login.html
│   ├── student_dashboard.html
│   ├── book_detail.html
│   ├── student_cart.html
│   ├── checkout.html
│   ├── student_orders.html
│   ├── order_detail.html
│   ├── student_reviews.html
│   ├── student_tickets.html
│   ├── student_profile.html
│   ├── cs_dashboard.html
│   ├── cs_ticket_detail.html
│   ├── cs_create_ticket.html
│   ├── cs_orders.html
│   ├── admin_dashboard.html
│   ├── admin_ticket_detail.html
│   ├── admin_add_book.html
│   ├── admin_edit_book.html
│   ├── admin_course_books.html
│   ├── superadmin_dashboard.html
│   └── superadmin_add_employee.html
└── static/
    ├── css/style.css
    └── js/main.js

============================================================
