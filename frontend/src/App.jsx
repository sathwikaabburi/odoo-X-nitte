import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "./pages/auth/Login";
import Signup from "./pages/auth/Signup";
import ProtectedRoute from "./components/ProtectedRoute";

// Employee pages
import EmployeeLayout from "./layouts/EmployeeLayout";
import EmployeeDashboard from "./pages/employee/EmployeeDashboard";
import Attendance from "./pages/employee/Attendance";
import Leave from "./pages/employee/Leave";
import Payroll from "./pages/employee/Payroll";
import Profile from "./pages/employee/Profile";

// Admin pages
import AdminLayout from "./layouts/AdminLayout";
import AdminDashboard from "./pages/admin/AdminDashboard";
import AdminEmployees from "./pages/admin/AdminEmployees";
import AdminLeaves from "./pages/admin/AdminLeaves";
import AdminAttendance from "./pages/admin/AdminAttendance";
import AdminPayroll from "./pages/admin/AdminPayroll";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        {/* Protected Employee Routes */}
        <Route
          path="/employee"
          element={
            <ProtectedRoute>
              <EmployeeLayout />
            </ProtectedRoute>
          }
        >
          <Route path="dashboard" element={<EmployeeDashboard />} />
          <Route path="profile" element={<Profile />} />
          <Route path="attendance" element={<Attendance />} />
          <Route path="leave" element={<Leave />} />
          <Route path="payroll" element={<Payroll />} />
        </Route>

        {/* Protected Admin/HR Routes */}
        <Route
          path="/admin"
          element={
            <ProtectedRoute>
              <AdminLayout />
            </ProtectedRoute>
          }
        >
          <Route path="dashboard" element={<AdminDashboard />} />
          <Route path="employees" element={<AdminEmployees />} />
          <Route path="attendance" element={<AdminAttendance />} />
          <Route path="leaves" element={<AdminLeaves />} />
          <Route path="payroll" element={<AdminPayroll />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;