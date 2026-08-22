import { useState, useEffect } from "react";
import api from "../../services/api";

function AdminAttendance() {
  const [attendanceRecords, setAttendanceRecords] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedEmployee, setSelectedEmployee] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  useEffect(() => {
    fetchEmployees();
  }, []);

  useEffect(() => {
    if (employees.length > 0) {
      fetchAttendance();
    }
  }, [selectedEmployee, dateFrom, dateTo]);

  const fetchEmployees = async () => {
    try {
      const response = await api.get("/employees/");
      setEmployees(response.data);
    } catch (err) {
      console.error("Error fetching employees:", err);
    }
  };

  const fetchAttendance = async () => {
    setLoading(true);
    try {
      let url = "/attendance/";
      const params = new URLSearchParams();
      
      if (selectedEmployee) {
        params.append("employee_id", selectedEmployee);
      }
      if (dateFrom) {
        params.append("date_from", dateFrom);
      }
      if (dateTo) {
        params.append("date_to", dateTo);
      }
      
      if (params.toString()) {
        url += `?${params.toString()}`;
      }
      
      const response = await api.get(url);
      setAttendanceRecords(response.data);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching attendance:", err);
      setError("Failed to load attendance records.");
      setLoading(false);
    }
  };

  const getEmployeeName = (employeeId) => {
    const emp = employees.find(e => e.id === employeeId);
    return emp ? `${emp.first_name} ${emp.last_name}` : "Unknown";
  };

  if (loading && attendanceRecords.length === 0) {
    return <div>Loading attendance records...</div>;
  }

  if (error) {
    return <div style={{ color: "red" }}>{error}</div>;
  }

  return (
    <div>
      <div className="page-heading">
        <div>
          <h1>Attendance Management</h1>
          <p>View all employee attendance records.</p>
        </div>
        <button className="primary-button" onClick={fetchAttendance}>
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="dashboard-card" style={{ marginBottom: "20px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "15px" }}>
          <div className="form-group">
            <label>Employee</label>
            <select
              value={selectedEmployee}
              onChange={(e) => setSelectedEmployee(e.target.value)}
              style={{ width: "100%", padding: "10px", borderRadius: "8px", border: "1px solid #ddd" }}
            >
              <option value="">All Employees</option>
              {employees.map((emp) => (
                <option key={emp.id} value={emp.id}>
                  {emp.first_name} {emp.last_name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Date From</label>
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              style={{ width: "100%", padding: "10px", borderRadius: "8px", border: "1px solid #ddd" }}
            />
          </div>

          <div className="form-group">
            <label>Date To</label>
            <input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              style={{ width: "100%", padding: "10px", borderRadius: "8px", border: "1px solid #ddd" }}
            />
          </div>

          <div className="form-group" style={{ display: "flex", alignItems: "flex-end" }}>
            <button 
              className="primary-button" 
              onClick={fetchAttendance}
              style={{ width: "100%" }}
            >
              Apply Filters
            </button>
          </div>
        </div>
      </div>

      <div className="dashboard-card">
        <div className="attendance-table-wrapper">
          <table className="attendance-table">
            <thead>
              <tr>
                <th>Employee</th>
                <th>Date</th>
                <th>Check In</th>
                <th>Check Out</th>
                <th>Status</th>
                <th>Remarks</th>
              </tr>
            </thead>
            <tbody>
              {attendanceRecords.length > 0 ? (
                attendanceRecords.map((record) => (
                  <tr key={record.id}>
                    <td>{record.employee_name || "Unknown"}</td>
                    <td>{record.attendance_date}</td>
                    <td>{record.check_in ? new Date(record.check_in).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "--:--"}</td>
                    <td>{record.check_out ? new Date(record.check_out).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "--:--"}</td>
                    <td>
                      <span style={{
                        padding: "4px 8px",
                        borderRadius: "4px",
                        background: record.status === "PRESENT" ? "#dcfce7" : 
                                   record.status === "HALF_DAY" ? "#fef3c7" : 
                                   record.status === "LEAVE" ? "#dbeafe" : "#fee2e2",
                        color: record.status === "PRESENT" ? "#166534" : 
                               record.status === "HALF_DAY" ? "#92400e" : 
                               record.status === "LEAVE" ? "#1e40af" : "#991b1b"
                      }}>
                        {record.status}
                      </span>
                    </td>
                    <td>{record.remarks || "-"}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6">No attendance records found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default AdminAttendance;