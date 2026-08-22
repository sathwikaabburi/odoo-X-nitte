You are a senior PostgreSQL + Django database architect working on the DAYFLOW HRMS hackathon project.

CURRENT GOAL:
Complete ONLY the database layer. Do not build REST APIs, frontend, authentication logic, or complex backend business logic yet.

SOURCE OF TRUTH:
Use the existing Dayflow problem statement and the already-agreed database design. Do not invent new business requirements, tables, states, or fields without explicitly identifying and justifying them.

TECH STACK:
PostgreSQL + Django ORM.
Django models are the schema source of truth.
Flow:
Database design → ER diagram → Django models → migrations → PostgreSQL → verification → seed/demo data.

DATABASE:
Create ONE PostgreSQL database named `dayflow`.

TABLES:
1. users
2. departments
3. employee_profiles
4. attendance
5. leave_requests
6. payroll
7. documents
8. notifications

SCHEMA:

users:
- id BIGSERIAL PK
- employee_id VARCHAR(20) NOT NULL UNIQUE
- email VARCHAR(255) NOT NULL UNIQUE
- password_hash TEXT NOT NULL
- role VARCHAR(20) NOT NULL: EMPLOYEE, HR, ADMIN
- is_verified BOOLEAN NOT NULL DEFAULT FALSE
- is_active BOOLEAN NOT NULL DEFAULT TRUE
- created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
- updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()

departments:
- id BIGSERIAL PK
- name VARCHAR(100) NOT NULL UNIQUE
- description TEXT
- created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()

employee_profiles:
- id BIGSERIAL PK
- user_id BIGINT NOT NULL UNIQUE FK → users.id
- first_name VARCHAR(100) NOT NULL
- last_name VARCHAR(100) NOT NULL
- phone VARCHAR(20)
- address TEXT
- profile_picture TEXT
- department_id BIGINT FK → departments.id
- designation VARCHAR(100)
- joining_date DATE
- date_of_birth DATE
- gender VARCHAR(20)

attendance:
- id BIGSERIAL PK
- employee_id BIGINT NOT NULL FK → employee_profiles.id
- attendance_date DATE NOT NULL
- check_in TIMESTAMPTZ
- check_out TIMESTAMPTZ
- status VARCHAR(20) NOT NULL: PRESENT, ABSENT, HALF_DAY, LEAVE
- remarks TEXT
- created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
- updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
- UNIQUE(employee_id, attendance_date)

leave_requests:
- id BIGSERIAL PK
- employee_id BIGINT NOT NULL FK → employee_profiles.id
- leave_type VARCHAR(20) NOT NULL: PAID, SICK, UNPAID
- start_date DATE NOT NULL
- end_date DATE NOT NULL
- remarks TEXT
- status VARCHAR(20) NOT NULL DEFAULT PENDING: PENDING, APPROVED, REJECTED
- reviewed_by BIGINT FK → users.id
- reviewed_at TIMESTAMPTZ
- admin_comment TEXT
- created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
- updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
- CHECK(end_date >= start_date)

payroll:
- id BIGSERIAL PK
- employee_id BIGINT NOT NULL FK → employee_profiles.id
- basic_salary DECIMAL(12,2) NOT NULL CHECK >= 0
- allowances DECIMAL(12,2) NOT NULL DEFAULT 0 CHECK >= 0
- deductions DECIMAL(12,2) NOT NULL DEFAULT 0 CHECK >= 0
- net_salary DECIMAL(12,2) NOT NULL CHECK >= 0
- effective_from DATE NOT NULL
- updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
- net_salary = basic_salary + allowances - deductions
- money must use DECIMAL/NUMERIC, never FLOAT

documents:
- id BIGSERIAL PK
- employee_id BIGINT NOT NULL FK → employee_profiles.id
- document_type VARCHAR(50) NOT NULL
- document_name VARCHAR(255) NOT NULL
- file_url TEXT NOT NULL
- uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()

notifications:
- id BIGSERIAL PK
- user_id BIGINT NOT NULL FK → users.id
- title VARCHAR(255) NOT NULL
- message TEXT NOT NULL
- notification_type VARCHAR(50)
- is_read BOOLEAN NOT NULL DEFAULT FALSE
- created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()

RELATIONSHIPS:
- users 1:1 employee_profiles
- departments 1:N employee_profiles
- employee_profiles 1:N attendance
- employee_profiles 1:N leave_requests
- employee_profiles 1:N payroll
- employee_profiles 1:N documents
- users 1:N notifications
- users 1:N leave_requests through reviewed_by

IMPORTANT:
These are independent PostgreSQL tables. Attendance, payroll, leave_requests and documents are NOT sub-tables of employee_profiles. They are related using foreign keys.

DATABASE RULES:
- Every table has its own primary key.
- Use foreign keys for relationships.
- Preserve referential integrity.
- Do not duplicate complete employee information in related tables.
- Use UNIQUE where specified.
- Use CHECK constraints for fixed states and valid numeric/date values.
- Use TIMESTAMPTZ for timestamps.
- Use DATE for calendar dates.
- Use DECIMAL(12,2) for salary.
- Add only useful indexes, especially for foreign keys and commonly queried dates.
- Do not over-engineer the schema.

IMPLEMENTATION STEPS:
1. Inspect the existing Django project and existing models first.
2. Compare existing models against this schema.
3. Do NOT blindly recreate existing models.
4. Identify missing, incorrect, or conflicting fields/constraints.
5. Make the minimum required corrections.
6. Configure PostgreSQL database `dayflow`.
7. Store credentials securely using environment variables; never hard-code passwords.
8. Create Django migrations.
9. Apply migrations to PostgreSQL.
10. Verify every table, column, PK, FK, UNIQUE and CHECK constraint.
11. Verify the relationships using PostgreSQL/Django inspection.
12. Create realistic seed/demo rows:
   - departments
   - users with EMPLOYEE/HR/ADMIN roles
   - employee profiles
   - attendance records
   - pending/approved/rejected leave requests
   - payroll records
   - documents if required
13. Verify that foreign keys and constraints work by testing valid and invalid sample data.
14. Do not proceed into API/frontend implementation.

DATA STRUCTURE CONCEPT:
One table contains many rows.
Each row represents one record.
Primary keys uniquely identify rows.
Foreign keys connect rows between tables.

Example:
employee_profiles.id = 5
attendance.employee_id = 5

means the attendance record belongs to that employee.

FINAL OUTPUT REQUIRED:
Provide:
1. Final table list
2. Final column/type/constraint table for each table
3. PK/FK relationship map
4. ER diagram
5. Django model-to-PostgreSQL mapping
6. Migration steps
7. PostgreSQL verification commands
8. Seed/demo-data structure
9. Final database validation checklist

Do not move to backend APIs until the PostgreSQL database is successfully created, migrated, populated with demo data, and verified.