function Payroll() {
  const payroll = {
    basicSalary: "₹45,000",
    allowances: "₹8,000",
    deductions: "₹3,000",
    netSalary: "₹50,000",
    effectiveFrom: "01 Aug 2026",
  };

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
          <strong>{payroll.basicSalary}</strong>
          <small>Monthly</small>
        </div>

        <div className="stat-card">
          <span>Allowances</span>
          <strong>{payroll.allowances}</strong>
          <small>Monthly</small>
        </div>

        <div className="stat-card">
          <span>Deductions</span>
          <strong>{payroll.deductions}</strong>
          <small>Monthly</small>
        </div>

        <div className="stat-card">
          <span>Net Salary</span>
          <strong>{payroll.netSalary}</strong>
          <small>Monthly</small>
        </div>
      </div>

      <div className="dashboard-card">
        <h3>Salary Details</h3>

        <div className="attendance-row">
          <span>Basic Salary</span>
          <strong>{payroll.basicSalary}</strong>
        </div>

        <div className="attendance-row">
          <span>Allowances</span>
          <strong>{payroll.allowances}</strong>
        </div>

        <div className="attendance-row">
          <span>Deductions</span>
          <strong>{payroll.deductions}</strong>
        </div>

        <div className="attendance-row">
          <span>Net Salary</span>
          <strong>{payroll.netSalary}</strong>
        </div>

        <div className="attendance-row">
          <span>Effective From</span>
          <strong>{payroll.effectiveFrom}</strong>
        </div>
      </div>
    </div>
  );
}

export default Payroll;