function EmployeeDashboard() {
  return (
    <div className="dashboard">
      <div className="page-heading">
        <div>
          <h1>Good morning 👋</h1>
          <p>Here's your work overview for today.</p>
        </div>

        <button className="primary-button">
          Check In
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <span>Attendance</span>
          <strong>Present</strong>
          <small>Today</small>
        </div>

        <div className="stat-card">
          <span>Leave Balance</span>
          <strong>12 Days</strong>
          <small>Available</small>
        </div>

        <div className="stat-card">
          <span>Working Hours</span>
          <strong>7h 42m</strong>
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
            <strong>09:12 AM</strong>
          </div>

          <div className="attendance-row">
            <span>Check out</span>
            <strong>--:--</strong>
          </div>
        </div>

        <div className="dashboard-card">
          <h3>Recent Activity</h3>

          <div className="activity-item">
            <span>Leave request submitted</span>
            <small>2 days ago</small>
          </div>

          <div className="activity-item">
            <span>Profile updated</span>
            <small>5 days ago</small>
          </div>

          <div className="activity-item">
            <span>Payroll generated</span>
            <small>12 days ago</small>
          </div>
        </div>
      </div>
    </div>
  );
}

export default EmployeeDashboard;