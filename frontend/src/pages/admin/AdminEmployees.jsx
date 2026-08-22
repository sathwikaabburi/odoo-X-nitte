import { useState, useEffect } from "react";
import api from "../../services/api";

function AdminEmployees() {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      const response = await api.get("/employees/");
      setEmployees(response.data);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching employees:", err);
      setError("Failed to load employees.");
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Loading employees...</div>;
  }

  if (error) {
    return <div style={{ color: "red" }}>{error}</div>;
  }

  return (
    <div>
      <div className="page-heading">
        <div>
          <h1>All Employees</h1>
          <p>Manage your workforce.</p>
        </div>
        <button className="primary-button" onClick={fetchEmployees}>
          Refresh
        </button>
      </div>

      <div className="dashboard-card">
        <div className="attendance-table-wrapper">
          <table className="attendance-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Department</th>
                <th>Designation</th>
              </tr>
            </thead>
            <tbody>
              {employees.length > 0 ? (
                employees.map((emp) => (
                  <tr key={emp.id}>
                    <td>{emp.user?.employee_id || "N/A"}</td>
                    <td>{emp.first_name} {emp.last_name}</td>
                    <td>{emp.user?.email || "N/A"}</td>
                    <td>{emp.user?.role || "N/A"}</td>
                    <td>{emp.department?.name || "N/A"}</td>
                    <td>{emp.designation || "N/A"}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6">No employees found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default AdminEmployees;