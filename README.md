odoo-X-nmit
Dayflow HRMS
Human Resource Management System
A secure, role-based HRMS designed to simplify employee and HR operations through a centralized web application.

Odoo x NMIT Bangalore Hackathon '26

🎥 Working Prototype
Watch the Dayflow HRMS in action
Demo Video: https://drive.google.com/file/d/1j4q8fqA5jCMzZKPGxfK0p3SJfDXHGie8/view?usp=drivesdk

The demonstration covers the core functional flow of Dayflow, including:

User authentication
Role-based access
Employee dashboard
Employee profile
Attendance
Check-in / check-out
Leave application
HR/Admin leave review
Leave approval/rejection
Payroll information
HR/Admin employee management
The video demonstrates the functional prototype and is intended to give evaluators a quick understanding of the application's workflow and capabilities.

📌 About Dayflow
Dayflow is a web-based Human Resource Management System developed for the Odoo x NMIT Bangalore Hackathon '26.

The system provides a centralized platform where employees can manage their essential HR activities while HR and Admin users can manage employee information and core HR workflows.

Dayflow focuses on a clean, secure, role-based architecture with reliable core workflows rather than unnecessary enterprise complexity.

🎯 Problem We Address
Traditional HR processes can involve disconnected workflows for:

Employee information
Attendance
Leave management
Payroll
Employee documents
Dayflow brings these essential HR operations together into a single system with role-based access and centralized data management.

✨ Core Features
👨‍💼 Employee
Employees can:

Sign in securely
View their profile
Update permitted profile information
Check in
Check out
View attendance records
Apply for leave
Track leave status
View payroll information
Access their documents
👩‍💼 HR / Admin
HR and Admin users can:

View employees
Manage employee information
View attendance
Review leave requests
Approve leave requests
Reject leave requests
View payroll
Update salary structures
👥 Role-Based Access
Dayflow supports three user roles:

Role	Access
EMPLOYEE	Own profile, attendance, leaves, payroll and documents
HR	Employee management and HR operations
ADMIN	Administrative HR operations
Authorization is enforced on the backend.

The frontend is not treated as the security boundary.

🔄 Core Workflows
Authentication
User
 ↓
Login
 ↓
JWT Authentication
 ↓
Role Detection
 ↓
Role-Based Dashboard

---
# 🚀 Getting Started

Follow these steps to clone and run the Dayflow HRMS project locally.

## 1. Clone the Repository

Open Git Bash or a terminal and run:

```bash
git clone https://github.com/sathwikaabburi/odoo-X-nitte.git
cd odoo-X-nitte

Project Structure

odoo-X-nitte/
│
├── backend/              # Django + Django REST Framework
├── frontend/             # Frontend application
├── .gitignore
├── README.md
└── requirements.txt

Backend Setup

Open the backend directory:
cd backend

Create a Python virtual environment:
python -m venv venv

Activate the virtual environment on Windows Git Bash:
source venv/Scripts/activate

For Windows PowerShell:
venv\Scripts\Activate.ps1

Install the required Python dependencies:
pip install -r requirements.txt

Configure Environment Variables

Create a .env file inside the backend/ directory.
DAYFLOW_DB_NAME=dayflow
DAYFLOW_DB_USER=postgres
DAYFLOW_DB_PASSWORD=your_postgres_password
DAYFLOW_DB_HOST=localhost
DAYFLOW_DB_PORT=5432

Replace your_postgres_password with the password you created while installing PostgreSQL.

⚠️ Never commit the .env file or real database passwords to GitHub.

PostgreSQL Database Setup

Make sure PostgreSQL is installed and the PostgreSQL service is running.

Create the Dayflow database:
createdb -U postgres dayflow

If createdb is not recognized, create a database named dayflow using pgAdmin instead.

6. Apply Django Migrations

From the backend/ directory, run:
python manage.py migrate

Load Demo Data

Run:
python manage.py seed_data
This loads sample departments, users, attendance records, leave requests, payroll records, documents, and notifications for demonstration.

Start the Backend Server
python manage.py runserver
The backend will be available at:
http://127.0.0.1:8000

Run the Frontend

Open a new terminal and navigate to the frontend directory:
cd frontend

Run the Frontend

Open a new terminal and navigate to the frontend directory:

cd frontend

Install frontend dependencies:

npm install

Start the frontend:

npm run dev

Open the URL displayed by the frontend development server in your browser.

Employee ID	Email	Role	Password
EMP001	admin@dayflow.io	ADMIN	Admin@123
EMP002	hr@dayflow.io	HR	Hr@123
EMP003	rahul@dayflow.io	EMPLOYEE	Rahul@123
EMP004	priya@dayflow.io	EMPLOYEE	Priya@123
EMP005	amit@dayflow.io	EMPLOYEE	Amit@123
EMP006	sneha@dayflow.io	EMPLOYEE	Sneha@123

These credentials are for local demonstration purposes only.

🔑 Backend API

Backend base URL:

http://127.0.0.1:8000

Authentication uses JWT.

Protected requests require:

Authorization: Bearer <access_token>

Main API areas include:

POST   /api/auth/login/

GET    /api/employees/
GET    /api/employees/{id}/
PUT    /api/employees/{id}/

POST   /api/attendance/check-in/
POST   /api/attendance/check-out/
GET    /api/attendance/

POST   /api/leaves/
GET    /api/leaves/
PATCH  /api/leaves/{id}/approve/
PATCH  /api/leaves/{id}/reject/

GET    /api/payroll/
PUT    /api/payroll/{id}/

🏗️ Technology Stack
Frontend
React
JavaScript
HTML
CSS
Backend
Python
Django
Django REST Framework
JWT Authentication
Database
PostgreSQL
Architecture
Frontend
   ↓
REST API / HTTP
   ↓
Django + Django REST Framework
   ↓
PostgreSQL
👥 User Roles


🗄️ Database

Dayflow uses PostgreSQL with the following core tables:

users
departments
employee_profiles
attendance
leave_requests
payroll
documents
notifications

The database follows a relational structure using primary keys, foreign keys, unique constraints, validation constraints, and normalized relationships.

🔒 Security
JWT-based authentication
Role-based authorization
Backend-enforced permissions
Employee ownership checks
Password hashing through Django
Environment variables for database credentials
Salary calculations performed by the backend
Database constraints for data integrity
⚠️ Troubleshooting
PostgreSQL command not found

If you see:

'psql' is not recognized

or:

'createdb' is not recognized

use pgAdmin to create and manage the dayflow database, or add PostgreSQL's bin directory to the Windows PATH.

Virtual environment activation issue

For Git Bash:

source venv/Scripts/activate

For PowerShell:

venv\Scripts\Activate.ps1
Backend server

Make sure you are inside:

odoo-X-nitte/backend/

before running:

python manage.py runserver
Frontend

Make sure you are inside:

odoo-X-nitte/frontend/

before running:

npm install
npm run dev
🤝 Development

This project was developed as part of a national-level hackathon with a focus on:

Reliable core HRMS workflows
Secure role-based access
Clean relational database design
REST API integration
Demonstrable end-to-end functionality
Simple and scalable architecture
📌 Project Repository

GitHub:

https://github.com/sathwikaabburi/odoo-X-nitte.git


**One important thing:** don't put the actual PostgreSQL password in the README. Keep only `your_postgres_password` as above.