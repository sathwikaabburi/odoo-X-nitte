import { useState, useEffect } from "react";
import api from "../../services/api";

function EmployeeDashboard() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const response = await api.get("/dashboard/employee/");
      setDashboardData(response.data);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching dashboard:", err);
      setError("Failed to load dashboard data.");
      setLoading(false);
    }
  };

  const handleCheckIn = async () => {
    try {
      const response = await api.post("/attendance/check-in/");
      alert("✅ Check-in successful!");
      fetchDashboard(); // Refresh data
    } catch (err) {
      if (err.response?.status === 409) {
        alert("⚠️ Already checked in today!");
      } else {
        alert("❌ Check-in failed. Please try again.");
      }
    }
  };

  const handleCheckOut = async () => {
    try {
      const response = await api.post("/attendance/check-out/");
      alert("✅ Check-out successful!");
      fetchDashboard(); // Refresh data
    } catch (err) {
      if (err.response?.status === 400) {
        alert("⚠️ No check-in found for today!");
      } else {
        alert("❌ Check-out failed. Please try again.");
      }
    }
  };

  if (loading) {
    return <div>Loading dashboard...</div>;
  }

  if (error) {
    return <div style={{ color: "red" }}>{error}</div>;
  }

  const { profile, today_attendance, recent_leaves, payroll, unread_notifications } = dashboardData;

  // Determine check-in status
  const isCheckedIn = today_attendance && today_attendance.status === "PRESENT";
  const checkInTime = today_attendance?.check_in 
    ? new Date(today_attendance.check_in).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : "--:--";
  const checkOutTime = today_attendance?.check_out 
    ? new Date(today_attendance.check_out).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : "--:--";

  return (
    <div className="dashboard">
      <div className="page-heading">
        <div>
          <h1>Good morning 👋</h1>
          <p>Here's your work overview for today.</p>
        </div>

        {!isCheckedIn ? (
          <button className="primary-button" onClick={handleCheckIn}>
            Check In
          </button>
        ) : (
          <button className="primary-button" onClick={handleCheckOut}>
            Check Out
          </button>
        )}
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <span>Attendance</span>
          <strong>{today_attendance ? today_attendance.status : "Not Checked In"}</strong>
          <small>Today</small>
        </div>

        <div className="stat-card">
          <span>Notifications</span>
          <strong>{unread_notifications || 0}</strong>
          <small>Unread</small>
        </div>

        <div className="stat-card">
          <span>Working Hours</span>
          <strong>
            {today_attendance?.check_in && today_attendance?.check_out 
              ? "8h 00m" 
              : "In progress"}
          </strong>
          <small>Today</small>
        </div>

        <div className="stat-card">
          <span>Next Payroll</span>
          <strong>31 Aug</strong>
          <small>Upcoming</small>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h3>Today's Attendance</h3>

          <div className="attendance-row">
            <span>Check in</span>
            <strong>{checkInTime}</strong>
          </div>

          <div className="attendance-row">
            <span>Check out</span>
            <strong>{checkOutTime}</strong>
          </div>

          <div className="attendance-row">
            <span>Status</span>
            <strong>{today_attendance ? today_attendance.status : "No record"}</strong>
          </div>
        </div>

        <div className="dashboard-card">
          <h3>Recent Activity</h3>

          {recent_leaves && recent_leaves.length > 0 ? (
            recent_leaves.map((leave, index) => (
              <div className="activity-item" key={index}>
                <span>{leave.leave_type} leave request - {leave.status}</span>
                <small>{new Date(leave.created_at).toLocaleDateString()}</small>
              </div>
            ))
          ) : (
            <div className="activity-item">
              <span>No recent activity</span>
            </div>
          )}

          {payroll && (
            <div className="activity-item">
              <span>Payroll: ₹{parseFloat(payroll.net_salary).toLocaleString()}</span>
              <small>Effective from {new Date(payroll.effective_from).toLocaleDateString()}</small>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default EmployeeDashboard;