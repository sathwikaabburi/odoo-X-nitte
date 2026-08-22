import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useEffect } from "react";

function AdminLayout() {
  const navigate = useNavigate();
  const userJSON = localStorage.getItem("dayflow_user");
  const user = userJSON ? JSON.parse(userJSON) : null;

  useEffect(() => {
    // If not HR or ADMIN, redirect to employee dashboard
    if (user && user.role !== "HR" && user.role !== "ADMIN") {
      navigate("/employee/dashboard");
    }
    // If no user, redirect to login
    if (!user) {
      navigate("/");
    }
  }, [user, navigate]);

  const handleLogout = () => {
    localStorage.removeItem("dayflow_user");
    navigate("/");
  };

  return (
    <div className="employee-layout">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="logo-mark">D</div>
          <span>Dayflow</span>
        </div>

        <nav className="sidebar-nav">
          <NavLink to="/admin/dashboard">Dashboard</NavLink>
          <NavLink to="/admin/employees">Employees</NavLink>
          <NavLink to="/admin/attendance">Attendance</NavLink>
          <NavLink to="/admin/leaves">Leave Requests</NavLink>
          <NavLink to="/admin/payroll">Payroll</NavLink>
        </nav>

        <button className="logout-button" onClick={handleLogout}>
          Sign out
        </button>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <h2>Admin Portal</h2>
          </div>

          <div className="user-info">
            <div className="avatar">A</div>
            <span>{user?.email || "Admin"}</span>
          </div>
        </header>

        <section className="page-content">
          <Outlet />
        </section>
      </main>
    </div>
  );
}

export default AdminLayout;