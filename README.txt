GyanPustak – Online Textbook Platform

GyanPustak is a web-based platform that allows college students to buy, rent, and explore textbooks. The system provides access to new, used, and electronic books. It supports two types of users: students and employees (customer support, administrators, and super administrators).

The application is built using Flask, Jinja2, and MySQL.

Features
Student
Browse and search books by title, author, or category
Add books to cart (buy or rent)
Checkout and place orders
View order history
Write and manage reviews
Submit support tickets
Update profile
Customer Support
View all support tickets
Assign new tickets to administrators
Create tickets
Cancel eligible orders
Administrator
Manage books (add, edit, delete)
Handle assigned tickets
Link books to courses
Super Administrator
Add and remove employees
Manage administrators and support staff
Tech Stack
Frontend: HTML, CSS, JavaScript, Jinja2
Backend: Python (Flask)
Database: MySQL
Connector: MySQL Connector for Python

Setup Instructions
1. Clone the Repository
git clone https://github.com/your-username/gyanpustak.git
cd gyanpustak
2. Setup Database
mysql -u root -p < schema.sql
3. Install Dependencies
pip install -r requirements.txt
4. Configure Database (Optional)

Windows:

set DB_HOST=localhost
set DB_USER=root
set DB_PASSWORD=yourpassword

Mac/Linux:

export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=yourpassword
5. Run the Application
python app.py

Open in browser:

http://localhost:5000
Login Credentials
Student
URL: /student/login
Example:
Student ID: 1
Name: Rohit Singh

Register:

/student/register
Employee
Role	Email	Password
Super Admin	superadmin@gyanpustak.com
	superadmin123
Administrator	arun.admin@gyanpustak.com
	admin123
Customer Support	meena.cs@gyanpustak.com
	cs123
System Overview
Role-based authentication using sessions
Book catalog with search and filtering
Cart and order management system
Review and rating functionality
Ticket management with status tracking
Assumptions
Users have access to a web browser (Chrome or similar)
MySQL server is available
Python 3.8 or higher is installed
Future Improvements
Payment gateway integration
Email notifications
Recommendation system
Improved UI responsiveness

License
This project is developed for academic purposes.
