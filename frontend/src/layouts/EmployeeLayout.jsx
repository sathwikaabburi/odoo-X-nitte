import { NavLink, Outlet } from "react-router-dom";

function EmployeeLayout() {
  return (
    <div className="employee-layout">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="logo-mark">D</div>
          <span>Dayflow</span>
        </div>

        <nav className="sidebar-nav">
          <NavLink to="/employee/dashboard">Dashboard</NavLink>
          <NavLink to="/employee/profile">Profile</NavLink>
          <NavLink to="/employee/attendance">Attendance</NavLink>
          <NavLink to="/employee/leave">Leave</NavLink>
          <NavLink to="/employee/payroll">Payroll</NavLink>
        </nav>

        <button className="logout-button">
          Sign out
        </button>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <h2>Employee Portal</h2>
          </div>

          <div className="user-info">
            <div className="avatar">E</div>
            <span>Employee</span>
          </div>
        </header>

        <section className="page-content">
          <Outlet />
        </section>
      </main>
    </div>
  );
}

export default EmployeeLayout;