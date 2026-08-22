# DAYFLOW HRMS — REST API Integration Contract

> **Base URL**: `http://localhost:8000/api/`  
> **Auth Header**: Cookies / Session (SameSite: `Lax`, Credentials: `include` in fetch/axios)  
> **Content-Type**: `application/json`

---

## 1. Authentication Endpoints

### 1.1 Sign Up
- **Method**: `POST`
- **URL**: `/api/auth/signup/`
- **Auth Required**: No (Public)
- **Allowed Roles**: Any (EMPLOYEE, HR, ADMIN)
- **Database Operation**: Creates a row in `users` and a corresponding default row in `employee_profiles` within a database transaction.
- **Validation Rules**:
  - `employee_id`: Required, max 20 chars, unique across `users`.
  - `email`: Required, valid email format, unique across `users`.
  - `password`: Required, minimum 8 characters. Hashed using Django's PBKDF2 (`make_password`).
  - `role`: Must be one of `EMPLOYEE`, `HR`, `ADMIN`.
  - `first_name`, `last_name`: Required, max 100 chars.
- **Request Body**:
  ```json
  {
    "employee_id": "EMP101",
    "email": "alex@dayflow.io",
    "password": "SecurePassword@123",
    "role": "EMPLOYEE",
    "first_name": "Alex",
    "last_name": "Taylor"
  }
  ```
- **Success Response (`201 Created`)**:
  ```json
  {
    "message": "Account created.",
    "user": {
      "id": 7,
      "employee_id": "EMP101",
      "email": "alex@dayflow.io",
      "role": "EMPLOYEE",
      "is_verified": true,
      "is_active": true,
      "created_at": "2026-08-22T10:00:00Z",
      "updated_at": "2026-08-22T10:00:00Z"
    }
  }
  ```
- **Error Responses**:
  - `400 Bad Request`: `{"employee_id": ["Employee ID already exists."]}` or validation error.
  - `409 Conflict`: `{"error": "Employee ID or email already exists."}`

---

### 1.2 Login
- **Method**: `POST`
- **URL**: `/api/auth/login/`
- **Auth Required**: No (Public)
- **Allowed Roles**: Any
- **Database Operation**: Queries `users` by email, verifies PBKDF2 hash using `check_password`, stores `_dayflow_user_id` into Django session table `django_session`.
- **Validation Rules**:
  - `email`: Required.
  - `password`: Required.
  - User `is_active` must be `true`.
  - User `is_verified` must be `true`.
- **Request Body**:
  ```json
  {
    "email": "rahul@dayflow.io",
    "password": "Rahul@123"
  }
  ```
- **Success Response (`200 OK`)**:
  ```json
  {
    "message": "Login successful.",
    "user": {
      "id": 3,
      "employee_id": "EMP003",
      "email": "rahul@dayflow.io",
      "role": "EMPLOYEE",
      "is_verified": true,
      "is_active": true,
      "created_at": "2026-08-22T04:00:00Z",
      "updated_at": "2026-08-22T04:00:00Z"
    }
  }
  ```
- **Error Responses**:
  - `401 Unauthorized`: `{"error": "Invalid email or password."}`
  - `403 Forbidden`: `{"error": "Account not verified."}`

---

### 1.3 Logout
- **Method**: `POST`
- **URL**: `/api/auth/logout/`
- **Auth Required**: Yes
- **Allowed Roles**: Any authenticated user
- **Database Operation**: Flushes session in `django_session`.
- **Request Body**: None (`{}`)
- **Success Response (`200 OK`)**:
  ```json
  {
    "message": "Logged out."
  }
  ```
- **Error Response**:
  - `403 Forbidden`: `{"detail": "Authentication credentials were not provided."}`

---

### 1.4 Current Authenticated User (`Me`)
- **Method**: `GET`
- **URL**: `/api/auth/me/`
- **Auth Required**: Yes
- **Allowed Roles**: Any authenticated user
- **Database Operation**: Reads authenticated row from `users` and related `employee_profiles`.
- **Success Response (`200 OK`)**:
  ```json
  {
    "id": 3,
    "employee_id": "EMP003",
    "email": "rahul@dayflow.io",
    "role": "EMPLOYEE",
    "is_verified": true,
    "is_active": true,
    "created_at": "2026-08-22T04:00:00Z",
    "updated_at": "2026-08-22T04:00:00Z",
    "profile": {
      "id": 3,
      "first_name": "Rahul",
      "last_name": "Sharma",
      "phone": "9876543212",
      "address": null,
      "profile_picture": null,
      "department": {
        "id": 1,
        "name": "Engineering",
        "description": "Software development and infrastructure",
        "created_at": "2026-08-22T04:00:00Z"
      },
      "designation": "Software Engineer",
      "joining_date": "2023-06-10",
      "date_of_birth": "1995-02-14",
      "gender": "Male"
    }
  }
  ```

---

## 2. Employee Profile Endpoints

### 2.1 List Employees
- **Method**: `GET`
- **URL**: `/api/employees/`
- **Query Params**: `search` (optional substring on first/last name), `department` (optional dept ID)
- **Auth Required**: Yes
- **Allowed Roles**: 
  - `HR` / `ADMIN`: Returns all employees matching filters.
  - `EMPLOYEE`: Returns only own profile.
- **Database Operation**: `SELECT` from `employee_profiles` joined with `users` and `departments`.
- **Success Response (`200 OK`)**:
  ```json
  [
    {
      "id": 3,
      "user": {
        "id": 3,
        "employee_id": "EMP003",
        "email": "rahul@dayflow.io",
        "role": "EMPLOYEE",
        "is_verified": true,
        "is_active": true
      },
      "first_name": "Rahul",
      "last_name": "Sharma",
      "phone": "9876543212",
      "address": "123 Main St",
      "profile_picture": null,
      "department": {
        "id": 1,
        "name": "Engineering",
        "description": "Software development"
      },
      "designation": "Software Engineer",
      "joining_date": "2023-06-10",
      "date_of_birth": "1995-02-14",
      "gender": "Male"
    }
  ]
  ```

---

### 2.2 Retrieve Employee Detail
- **Method**: `GET`
- **URL**: `/api/employees/{id}/`
- **Auth Required**: Yes
- **Allowed Roles**:
  - `HR` / `ADMIN`: Any employee.
  - `EMPLOYEE`: Own profile ID only.
- **Success Response (`200 OK`)**: Same schema as individual item above.
- **Error Response**:
  - `403 Forbidden`: Employee trying to view another employee.
  - `404 Not Found`: If ID does not exist.

---

### 2.3 Update Employee Profile
- **Method**: `PUT`
- **URL**: `/api/employees/{id}/`
- **Auth Required**: Yes
- **Allowed Roles**:
  - `EMPLOYEE`: Own profile only. Editable fields restricted to `phone`, `address`, `profile_picture`.
  - `HR` / `ADMIN`: Any employee. Can update `first_name`, `last_name`, `phone`, `address`, `profile_picture`, `department_id`, `designation`, `joining_date`, `date_of_birth`, `gender`.
- **Request Body (Employee)**:
  ```json
  {
    "phone": "9876543210",
    "address": "456 Silicon Ave, Apt 12B",
    "profile_picture": "https://example.com/avatar.jpg"
  }
  ```
- **Success Response (`200 OK`)**: Updated `EmployeeProfile` object.
- **Error Response**:
  - `403 Forbidden`: Unauthorized edit attempt.

---

## 3. Attendance Endpoints

### 3.1 Check-In
- **Method**: `POST`
- **URL**: `/api/attendance/check-in/`
- **Auth Required**: Yes
- **Allowed Roles**: `EMPLOYEE`, `HR`, `ADMIN`
- **Database Operation**: `INSERT` into `attendance` with `attendance_date = CURRENT_DATE`, `check_in = NOW()`, `status = 'PRESENT'`.
- **Validation Rules**: Duplicate check-in on the same date for the same employee is rejected by unique constraint.
- **Request Body**: None (`{}`)
- **Success Response (`201 Created`)**:
  ```json
  {
    "id": 16,
    "employee": 3,
    "employee_name": "Rahul Sharma",
    "attendance_date": "2026-08-22",
    "check_in": "2026-08-22T09:05:00Z",
    "check_out": null,
    "status": "PRESENT",
    "remarks": null,
    "created_at": "2026-08-22T09:05:00Z",
    "updated_at": "2026-08-22T09:05:00Z"
  }
  ```
- **Error Response**:
  - `409 Conflict`: `{"error": "Already checked in today."}`

---

### 3.2 Check-Out
- **Method**: `POST`
- **URL**: `/api/attendance/check-out/`
- **Auth Required**: Yes
- **Allowed Roles**: Authenticated employee with an active check-in today.
- **Database Operation**: `UPDATE attendance SET check_out = NOW() WHERE employee_id = profile.id AND attendance_date = CURRENT_DATE`.
- **Request Body**: None (`{}`)
- **Success Response (`200 OK`)**: Updated Attendance object with populated `check_out`.
- **Error Responses**:
  - `400 Bad Request`: `{"error": "No check-in found for today."}` or `{"error": "Already checked out today."}`

---

### 3.3 List Attendance Records
- **Method**: `GET`
- **URL**: `/api/attendance/`
- **Query Params**: `date_from` (YYYY-MM-DD), `date_to` (YYYY-MM-DD), `employee_id` (HR/Admin only)
- **Auth Required**: Yes
- **Allowed Roles**:
  - `EMPLOYEE`: Sees only own attendance.
  - `HR` / `ADMIN`: Sees all employees' attendance.
- **Success Response (`200 OK`)**: List of `Attendance` objects ordered by `-attendance_date`.

---

### 3.4 Weekly Attendance
- **Method**: `GET`
- **URL**: `/api/attendance/weekly/`
- **Auth Required**: Yes
- **Allowed Roles**: `EMPLOYEE` (own weekly), `HR`/`ADMIN` (all employees weekly)
- **Database Operation**: Queries records from current week's Monday through today.
- **Success Response (`200 OK`)**: List of `Attendance` objects.

---

## 4. Leave Management Endpoints

### 4.1 Apply for Leave (Create Request)
- **Method**: `POST`
- **URL**: `/api/leaves/`
- **Auth Required**: Yes
- **Allowed Roles**: `EMPLOYEE`, `HR`, `ADMIN`
- **Database Operation**: `INSERT` into `leave_requests` with `status = 'PENDING'`.
- **Validation Rules**:
  - `leave_type`: Required, must be `PAID`, `SICK`, or `UNPAID`.
  - `start_date`: Required (YYYY-MM-DD).
  - `end_date`: Required (YYYY-MM-DD), must be `>= start_date`.
  - `remarks`: Optional text.
- **Request Body**:
  ```json
  {
    "leave_type": "PAID",
    "start_date": "2026-09-10",
    "end_date": "2026-09-12",
    "remarks": "Attending family conference."
  }
  ```
- **Success Response (`201 Created`)**:
  ```json
  {
    "id": 4,
    "employee": 3,
    "employee_name": "Rahul Sharma",
    "leave_type": "PAID",
    "start_date": "2026-09-10",
    "end_date": "2026-09-12",
    "remarks": "Attending family conference.",
    "status": "PENDING",
    "reviewed_by": null,
    "reviewed_by_name": null,
    "reviewed_at": null,
    "admin_comment": null,
    "created_at": "2026-08-22T10:15:00Z",
    "updated_at": "2026-08-22T10:15:00Z"
  }
  ```
- **Error Response**:
  - `400 Bad Request`: `{"end_date": ["End date must be >= start date."]}`

---

### 4.2 List Leave Requests
- **Method**: `GET`
- **URL**: `/api/leaves/`
- **Query Params**: `status` (`PENDING`, `APPROVED`, `REJECTED`)
- **Auth Required**: Yes
- **Allowed Roles**:
  - `EMPLOYEE`: Own requests only.
  - `HR` / `ADMIN`: All employee requests.
- **Success Response (`200 OK`)**: List of `LeaveRequest` objects.

---

### 4.3 Approve Leave Request
- **Method**: `PATCH`
- **URL**: `/api/leaves/{id}/approve/`
- **Auth Required**: Yes
- **Allowed Roles**: `HR`, `ADMIN` (Employees return `403`)
- **Database Operation**: Updates `status = 'APPROVED'`, `reviewed_by = user.id`, `reviewed_at = NOW()`, `admin_comment`, and creates a notification row for the employee.
- **Request Body**:
  ```json
  {
    "admin_comment": "Approved. Have a good break!"
  }
  ```
- **Success Response (`200 OK`)**: Updated `LeaveRequest` object with `status: "APPROVED"`.
- **Error Responses**:
  - `400 Bad Request`: If leave request is not in `PENDING` state.
  - `403 Forbidden`: If attempted by `EMPLOYEE` role.

---

### 4.4 Reject Leave Request
- **Method**: `PATCH`
- **URL**: `/api/leaves/{id}/reject/`
- **Auth Required**: Yes
- **Allowed Roles**: `HR`, `ADMIN`
- **Database Operation**: Updates `status = 'REJECTED'`, `reviewed_by`, `reviewed_at`, `admin_comment`, and creates an employee notification.
- **Request Body**:
  ```json
  {
    "admin_comment": "Critical sprint deadline during requested period."
  }
  ```
- **Success Response (`200 OK`)**: Updated `LeaveRequest` object with `status: "REJECTED"`.

---

## 5. Payroll Endpoints

### 5.1 List Payroll Records
- **Method**: `GET`
- **URL**: `/api/payroll/`
- **Auth Required**: Yes
- **Allowed Roles**:
  - `EMPLOYEE`: Own payroll records only (Read-only).
  - `HR` / `ADMIN`: All payroll records.
- **Success Response (`200 OK`)**:
  ```json
  [
    {
      "id": 3,
      "employee": 3,
      "employee_name": "Rahul Sharma",
      "basic_salary": "60000.00",
      "allowances": "10000.00",
      "deductions": "7000.00",
      "net_salary": "63000.00",
      "effective_from": "2023-06-01",
      "updated_at": "2026-08-22T04:00:00Z"
    }
  ]
  ```

---

### 5.2 Update Payroll (Salary Structure)
- **Method**: `PUT`
- **URL**: `/api/payroll/{id}/`
- **Auth Required**: Yes
- **Allowed Roles**: `HR`, `ADMIN` (`EMPLOYEE` returns `403 Forbidden`)
- **Database Operation**: `UPDATE payroll SET basic_salary = ..., allowances = ..., deductions = ..., effective_from = ..., net_salary = (basic + allowances - deductions)`.
- **Calculation Rule**: `net_salary` is strictly computed on the backend server.
- **Validation Rules**: `basic_salary >= 0`, `allowances >= 0`, `deductions >= 0`.
- **Request Body**:
  ```json
  {
    "basic_salary": "65000.00",
    "allowances": "12000.00",
    "deductions": "7000.00",
    "effective_from": "2026-09-01"
  }
  ```
- **Success Response (`200 OK`)**:
  ```json
  {
    "id": 3,
    "employee": 3,
    "employee_name": "Rahul Sharma",
    "basic_salary": "65000.00",
    "allowances": "12000.00",
    "deductions": "7000.00",
    "net_salary": "70000.00",
    "effective_from": "2026-09-01",
    "updated_at": "2026-08-22T10:30:00Z"
  }
  ```
- **Error Response**:
  - `403 Forbidden`: If attempted by an employee.

---

## 6. Document Endpoints

### 6.1 List & Upload Documents
- **Method**: `GET` (List) / `POST` (Upload metadata)
- **URL**: `/api/documents/`
- **Auth Required**: Yes
- **Allowed Roles**: `EMPLOYEE` (own documents), `HR`/`ADMIN` (all documents)
- **POST Request Body**:
  ```json
  {
    "document_type": "CERTIFICATE",
    "document_name": "AWS Solutions Architect",
    "file_url": "https://storage.example.com/docs/aws_cert.pdf"
  }
  ```
- **Success Response (`201 Created`)**:
  ```json
  {
    "id": 4,
    "employee": 3,
    "document_type": "CERTIFICATE",
    "document_name": "AWS Solutions Architect",
    "file_url": "https://storage.example.com/docs/aws_cert.pdf",
    "uploaded_at": "2026-08-22T10:35:00Z"
  }
  ```

---

### 6.2 Delete Document
- **Method**: `DELETE`
- **URL**: `/api/documents/{id}/`
- **Auth Required**: Yes
- **Allowed Roles**: Document owner or `HR`/`ADMIN`
- **Success Response (`204 No Content`)**: Empty response body.

---

## 7. Notification Endpoints

### 7.1 List Notifications
- **Method**: `GET`
- **URL**: `/api/notifications/`
- **Auth Required**: Yes
- **Allowed Roles**: Authenticated user (sees only their own notifications)
- **Success Response (`200 OK`)**:
  ```json
  [
    {
      "id": 1,
      "user": 3,
      "title": "Leave Approved",
      "message": "Your PAID leave (2026-09-10 to 2026-09-12) has been approved.",
      "notification_type": "LEAVE",
      "is_read": false,
      "created_at": "2026-08-22T10:20:00Z"
    }
  ]
  ```

---

### 7.2 Mark Notification as Read
- **Method**: `PATCH`
- **URL**: `/api/notifications/{id}/read/`
- **Auth Required**: Yes
- **Success Response (`200 OK`)**: Updated Notification object with `is_read: true`.

---

## 8. Dashboard Endpoints

### 8.1 Employee Dashboard
- **Method**: `GET`
- **URL**: `/api/dashboard/employee/`
- **Auth Required**: Yes
- **Allowed Roles**: `EMPLOYEE`, `HR`, `ADMIN`
- **Success Response (`200 OK`)**:
  ```json
  {
    "profile": { ... },
    "today_attendance": { ... } or null,
    "recent_leaves": [ ... ],
    "payroll": { ... } or null,
    "unread_notifications": 2
  }
  ```

---

### 8.2 Admin / HR Dashboard
- **Method**: `GET`
- **URL**: `/api/dashboard/admin/`
- **Auth Required**: Yes
- **Allowed Roles**: `HR`, `ADMIN` (`EMPLOYEE` returns `403 Forbidden`)
- **Success Response (`200 OK`)**:
  ```json
  {
    "total_employees": 6,
    "total_departments": 4,
    "today_attendance": {
      "present": 3,
      "absent": 0,
      "half_day": 0,
      "on_leave": 0,
      "total_checked_in": 3
    },
    "pending_leaves": 1,
    "department_summary": [
      {
        "id": 1,
        "name": "Engineering",
        "employee_count": 3
      },
      {
        "id": 2,
        "name": "Human Resources",
        "employee_count": 1
      },
      {
        "id": 3,
        "name": "Finance",
        "employee_count": 1
      },
      {
        "id": 4,
        "name": "Marketing",
        "employee_count": 1
      }
    ]
  }
  ```

---

## 9. Department Endpoints

### 9.1 List Departments
- **Method**: `GET`
- **URL**: `/api/departments/`
- **Auth Required**: Yes
- **Allowed Roles**: Any authenticated user
- **Success Response (`200 OK`)**: List of `Department` objects.
