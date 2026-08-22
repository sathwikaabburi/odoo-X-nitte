import { useState, useEffect } from "react";
import api from "../../services/api";

function Payroll() {
  const [payrollData, setPayrollData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchPayroll();
  }, []);

  const fetchPayroll = async () => {
    try {
      const response = await api.get("/payroll/");
      // Get the latest payroll record
      const latest = response.data[0];
      setPayrollData(latest);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching payroll:", err);
      setError("Failed to load payroll data.");
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Loading payroll...</div>;
  }

  if (error) {
    return <div style={{ color: "red" }}>{error}</div>;
  }

  if (!payrollData) {
    return <div>No payroll records found.</div>;
  }

  return (
    <div className="payroll-page">
      <div className="page-heading">
        <div>
          <h1>Payroll</h1>
          <p>View your salary and payroll information.</p>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <span>Basic Salary</span>
          <strong>₹{parseFloat(payrollData.basic_salary).toLocaleString()}</strong>
          <small>Monthly</small>
        </div>

        <div className="stat-card">
          <span>Allowances</span>
          <strong>₹{parseFloat(payrollData.allowances).toLocaleString()}</strong>
          <small>Monthly</small>
        </div>

        <div className="stat-card">
          <span>Deductions</span>
          <strong>₹{parseFloat(payrollData.deductions).toLocaleString()}</strong>
          <small>Monthly</small>
        </div>

        <div className="stat-card">
          <span>Net Salary</span>
          <strong>₹{parseFloat(payrollData.net_salary).toLocaleString()}</strong>
          <small>Monthly</small>
        </div>
      </div>

      <div className="dashboard-card">
        <h3>Salary Details</h3>

        <div className="attendance-row">
          <span>Basic Salary</span>
          <strong>₹{parseFloat(payrollData.basic_salary).toLocaleString()}</strong>
        </div>

        <div className="attendance-row">
          <span>Allowances</span>
          <strong>₹{parseFloat(payrollData.allowances).toLocaleString()}</strong>
        </div>

        <div className="attendance-row">
          <span>Deductions</span>
          <strong>₹{parseFloat(payrollData.deductions).toLocaleString()}</strong>
        </div>

        <div className="attendance-row">
          <span>Net Salary</span>
          <strong>₹{parseFloat(payrollData.net_salary).toLocaleString()}</strong>
        </div>

        <div className="attendance-row">
          <span>Effective From</span>
          <strong>{new Date(payrollData.effective_from).toLocaleDateString()}</strong>
        </div>
      </div>
    </div>
  );
}

export default Payroll;