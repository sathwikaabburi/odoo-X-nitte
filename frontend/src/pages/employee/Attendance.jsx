import { useState, useEffect } from "react";
import api from "../../services/api";

function Attendance() {
  const [attendanceRecords, setAttendanceRecords] = useState([]);
  const [todayAttendance, setTodayAttendance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchAttendance();
  }, []);

  const fetchAttendance = async () => {
    try {
      const response = await api.get("/attendance/");
      setAttendanceRecords(response.data);
      
      // Check if there's a record for today
      const today = new Date().toISOString().split('T')[0];
      const todayRecord = response.data.find(rec => rec.attendance_date === today);
      setTodayAttendance(todayRecord || null);
      
      setLoading(false);
    } catch (err) {
      console.error("Error fetching attendance:", err);
      setError("Failed to load attendance data.");
      setLoading(false);
    }
  };

  const handleCheckIn = async () => {
    try {
      await api.post("/attendance/check-in/");
      alert("✅ Check-in successful!");
      fetchAttendance(); // Refresh
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
      await api.post("/attendance/check-out/");
      alert("✅ Check-out successful!");
      fetchAttendance(); // Refresh
    } catch (err) {
      if (err.response?.status === 400) {
        alert("⚠️ No check-in found for today!");
      } else {
        alert("❌ Check-out failed. Please try again.");
      }
    }
  };

  if (loading) {
    return <div>Loading attendance...</div>;
  }

  const isCheckedIn = todayAttendance && todayAttendance.status === "PRESENT";
  const checkInTime = todayAttendance?.check_in 
    ? new Date(todayAttendance.check_in).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : "--:--";
  const checkOutTime = todayAttendance?.check_out 
    ? new Date(todayAttendance.check_out).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : "--:--";

  return (
    <div className="attendance-page">
      <div className="page-heading">
        <div>
          <h1>Attendance</h1>
          <p>Track your daily and weekly attendance.</p>
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
          <span>Today's Status</span>
          <strong>{todayAttendance ? todayAttendance.status : "Not Checked In"}</strong>
          <small>Today</small>
        </div>

        <div className="stat-card">
          <span>Check In</span>
          <strong>{checkInTime}</strong>
          <small>Today</small>
        </div>

        <div className="stat-card">
          <span>Check Out</span>
          <strong>{checkOutTime}</strong>
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
              {attendanceRecords.length > 0 ? (
                attendanceRecords.slice(0, 10).map((record) => (
                  <tr key={record.id}>
                    <td>{record.attendance_date}</td>
                    <td>{record.check_in ? new Date(record.check_in).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "--:--"}</td>
                    <td>{record.check_out ? new Date(record.check_out).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "--:--"}</td>
                    <td>{record.status}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="4">No attendance records found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default Attendance;