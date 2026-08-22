import { useState, useEffect } from "react";
import api from "../../services/api";

function AdminPayroll() {
  const [payrollRecords, setPayrollRecords] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedEmployee, setSelectedEmployee] = useState("");
  const [editingPayroll, setEditingPayroll] = useState(null);

  useEffect(() => {
    fetchEmployees();
  }, []);

  useEffect(() => {
    if (employees.length > 0) {
      fetchPayroll();
    }
  }, [selectedEmployee]);

  const fetchEmployees = async () => {
    try {
      const response = await api.get("/employees/");
      setEmployees(response.data);
    } catch (err) {
      console.error("Error fetching employees:", err);
    }
  };

  const fetchPayroll = async () => {
    setLoading(true);
    try {
      let url = "/payroll/";
      if (selectedEmployee) {
        url += `?employee_id=${selectedEmployee}`;
      }
      const response = await api.get(url);
      setPayrollRecords(response.data);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching payroll:", err);
      setError("Failed to load payroll records.");
      setLoading(false);
    }
  };

  const handleEdit = (payroll) => {
    setEditingPayroll({
      id: payroll.id,
      basic_salary: payroll.basic_salary,
      allowances: payroll.allowances,
      deductions: payroll.deductions,
      effective_from: payroll.effective_from,
    });
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    try {
      await api.put(`/payroll/${editingPayroll.id}/`, {
        basic_salary: parseFloat(editingPayroll.basic_salary),
        allowances: parseFloat(editingPayroll.allowances || 0),
        deductions: parseFloat(editingPayroll.deductions || 0),
        effective_from: editingPayroll.effective_from,
      });
      alert("✅ Payroll updated successfully!");
      setEditingPayroll(null);
      fetchPayroll();
    } catch (err) {
      alert("❌ Failed to update payroll.");
      console.error(err);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setEditingPayroll((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  if (loading && payrollRecords.length === 0) {
    return <div>Loading payroll records...</div>;
  }

  if (error) {
    return <div style={{ color: "red" }}>{error}</div>;
  }

  return (
    <div>
      <div className="page-heading">
        <div>
          <h1>Payroll Management</h1>
          <p>View and manage employee salaries.</p>
        </div>
        <div style={{ display: "flex", gap: "10px" }}>
          <select
            value={selectedEmployee}
            onChange={(e) => setSelectedEmployee(e.target.value)}
            style={{ padding: "10px", borderRadius: "8px", border: "1px solid #ddd" }}
          >
            <option value="">All Employees</option>
            {employees.map((emp) => (
              <option key={emp.id} value={emp.id}>
                {emp.first_name} {emp.last_name}
              </option>
            ))}
          </select>
          <button className="primary-button" onClick={fetchPayroll}>
            Refresh
          </button>
        </div>
      </div>

      {/* Edit Modal */}
      {editingPayroll && (
        <div style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: "rgba(0,0,0,0.5)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 1000
        }}>
          <div style={{
            background: "white",
            padding: "30px",
            borderRadius: "12px",
            maxWidth: "500px",
            width: "100%"
          }}>
            <h2>Edit Payroll</h2>
            <form onSubmit={handleUpdate}>
              <div className="form-group">
                <label>Basic Salary</label>
                <input
                  type="number"
                  name="basic_salary"
                  value={editingPayroll.basic_salary}
                  onChange={handleChange}
                  step="0.01"
                  required
                  style={{ width: "100%", padding: "10px", borderRadius: "8px", border: "1px solid #ddd" }}
                />
              </div>

              <div className="form-group">
                <label>Allowances</label>
                <input
                  type="number"
                  name="allowances"
                  value={editingPayroll.allowances}
                  onChange={handleChange}
                  step="0.01"
                  style={{ width: "100%", padding: "10px", borderRadius: "8px", border: "1px solid #ddd" }}
                />
              </div>

              <div className="form-group">
                <label>Deductions</label>
                <input
                  type="number"
                  name="deductions"
                  value={editingPayroll.deductions}
                  onChange={handleChange}
                  step="0.01"
                  style={{ width: "100%", padding: "10px", borderRadius: "8px", border: "1px solid #ddd" }}
                />
              </div>

              <div className="form-group">
                <label>Effective From</label>
                <input
                  type="date"
                  name="effective_from"
                  value={editingPayroll.effective_from}
                  onChange={handleChange}
                  required
                  style={{ width: "100%", padding: "10px", borderRadius: "8px", border: "1px solid #ddd" }}
                />
              </div>

              <div style={{ display: "flex", gap: "10px", marginTop: "20px" }}>
                <button type="submit" className="primary-button" style={{ flex: 1 }}>
                  Save Changes
                </button>
                <button
                  type="button"
                  onClick={() => setEditingPayroll(null)}
                  style={{
                    flex: 1,
                    padding: "10px",
                    borderRadius: "8px",
                    border: "1px solid #ddd",
                    background: "#f3f4f6",
                    cursor: "pointer"
                  }}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="dashboard-card">
        <div className="attendance-table-wrapper">
          <table className="attendance-table">
            <thead>
              <tr>
                <th>Employee</th>
                <th>Basic Salary</th>
                <th>Allowances</th>
                <th>Deductions</th>
                <th>Net Salary</th>
                <th>Effective From</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {payrollRecords.length > 0 ? (
                payrollRecords.map((record) => (
                  <tr key={record.id}>
                    <td>{record.employee_name || "Unknown"}</td>
                    <td>₹{parseFloat(record.basic_salary).toLocaleString()}</td>
                    <td>₹{parseFloat(record.allowances).toLocaleString()}</td>
                    <td>₹{parseFloat(record.deductions).toLocaleString()}</td>
                    <td>
                      <strong>₹{parseFloat(record.net_salary).toLocaleString()}</strong>
                    </td>
                    <td>{record.effective_from}</td>
                    <td>
                      <button
                        onClick={() => handleEdit(record)}
                        style={{
                          padding: "6px 12px",
                          background: "#2563eb",
                          color: "white",
                          border: "none",
                          borderRadius: "4px",
                          cursor: "pointer"
                        }}
                      >
                        Edit
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="7">No payroll records found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default AdminPayroll;