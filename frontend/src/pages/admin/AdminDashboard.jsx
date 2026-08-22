import { useState, useEffect } from "react";
import api from "../../services/api";

function AdminDashboard() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const response = await api.get("/dashboard/admin/");
      setDashboardData(response.data);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching admin dashboard:", err);
      setError("Failed to load dashboard data.");
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Loading admin dashboard...</div>;
  }

  if (error) {
    return <div style={{ color: "red" }}>{error}</div>;
  }

  const { total_employees, total_departments, today_attendance, pending_leaves, department_summary } = dashboardData;

  return (
    <div className="dashboard">
      <div className="page-heading">
        <div>
          <h1>Admin Dashboard</h1>
          <p>Overview of your organization.</p>
        </div>
        <button className="primary-button" onClick={fetchDashboard}>
          Refresh
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <span>Total Employees</span>
          <strong>{total_employees || 0}</strong>
          <small>Active</small>
        </div>

        <div className="stat-card">
          <span>Departments</span>
          <strong>{total_departments || 0}</strong>
          <small>Total</small>
        </div>

        <div className="stat-card">
          <span>Pending Leaves</span>
          <strong>{pending_leaves || 0}</strong>
          <small>Awaiting approval</small>
        </div>

        <div className="stat-card">
          <span>Today's Attendance</span>
          <strong>{today_attendance?.total_checked_in || 0}</strong>
          <small>Checked in</small>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h3>Today's Attendance Summary</h3>
          
          <div className="attendance-row">
            <span>Present</span>
            <strong>{today_attendance?.present || 0}</strong>
          </div>
          
          <div className="attendance-row">
            <span>Absent</span>
            <strong>{today_attendance?.absent || 0}</strong>
          </div>
          
          <div className="attendance-row">
            <span>Half Day</span>
            <strong>{today_attendance?.half_day || 0}</strong>
          </div>
          
          <div className="attendance-row">
            <span>On Leave</span>
            <strong>{today_attendance?.on_leave || 0}</strong>
          </div>
        </div>

        <div className="dashboard-card">
          <h3>Department Summary</h3>
          
          {department_summary && department_summary.length > 0 ? (
            department_summary.map((dept) => (
              <div className="attendance-row" key={dept.id}>
                <span>{dept.name}</span>
                <strong>{dept.employee_count} employees</strong>
              </div>
            ))
          ) : (
            <p>No departments found.</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default AdminDashboard;