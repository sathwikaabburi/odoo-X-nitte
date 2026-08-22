import { useState } from "react";

function Attendance() {
  const [checkedIn, setCheckedIn] = useState(false);
  const [checkInTime, setCheckInTime] = useState(null);
  const [checkOutTime, setCheckOutTime] = useState(null);

  const handleCheckIn = () => {
    const now = new Date();

    setCheckedIn(true);
    setCheckInTime(
      now.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      })
    );
  };

  const handleCheckOut = () => {
    const now = new Date();

    setCheckedIn(false);
    setCheckOutTime(
      now.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      })
    );
  };

  return (
    <div className="attendance-page">
      <div className="page-heading">
        <div>
          <h1>Attendance</h1>
          <p>Track your daily and weekly attendance.</p>
        </div>

        {!checkedIn ? (
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
          <span>Today's Status</span>
          <strong>{checkedIn ? "Present" : "Not Checked In"}</strong>
          <small>Today</small>
        </div>

        <div className="stat-card">
          <span>Check In</span>
          <strong>{checkInTime || "--:--"}</strong>
          <small>Today</small>
        </div>

        <div className="stat-card">
          <span>Check Out</span>
          <strong>{checkOutTime || "--:--"}</strong>
          <small>Today</small>
        </div>
      </div>

      <div className="dashboard-card">
        <h3>Attendance History</h3>

        <div className="attendance-table-wrapper">
          <table className="attendance-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Check In</th>
                <th>Check Out</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              <tr>
                <td>Today</td>
                <td>{checkInTime || "--:--"}</td>
                <td>{checkOutTime || "--:--"}</td>
                <td>{checkedIn ? "PRESENT" : "ABSENT"}</td>
              </tr>

              <tr>
                <td>Yesterday</td>
                <td>09:05 AM</td>
                <td>05:42 PM</td>
                <td>PRESENT</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default Attendance;