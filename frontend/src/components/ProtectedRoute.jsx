import { Navigate } from "react-router-dom";

function ProtectedRoute({ children, requiredRole }) {
  const userJSON = localStorage.getItem("dayflow_user");
  const user = userJSON ? JSON.parse(userJSON) : null;

  // If no user, redirect to login
  if (!user) {
    return <Navigate to="/" />;
  }

  // If role doesn't match, redirect to employee dashboard
  if (requiredRole && user.role !== requiredRole) {
    if (user.role === "EMPLOYEE") {
      return <Navigate to="/employee/dashboard" />;
    } else if (user.role === "HR" || user.role === "ADMIN") {
      return <Navigate to="/admin/dashboard" />;
    }
    return <Navigate to="/" />;
  }

  return children;
}

export default ProtectedRoute;