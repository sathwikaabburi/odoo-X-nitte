import { useState } from "react";

function Leave() {
  const [form, setForm] = useState({
    leaveType: "PAID",
    startDate: "",
    endDate: "",
    remarks: "",
  });

  const [requests, setRequests] = useState([
    {
      type: "PAID",
      startDate: "2026-08-18",
      endDate: "2026-08-19",
      status: "APPROVED",
      comment: "Approved by HR",
    },
  ]);

  const handleChange = (event) => {
    const { name, value } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    if (!form.startDate || !form.endDate) {
      return;
    }

    if (form.startDate > form.endDate) {
      return;
    }

    const newRequest = {
      type: form.leaveType,
      startDate: form.startDate,
      endDate: form.endDate,
      status: "PENDING",
      comment: "-",
    };

    setRequests((previous) => [newRequest, ...previous]);

    setForm({
      leaveType: "PAID",
      startDate: "",
      endDate: "",
      remarks: "",
    });
  };

  return (
    <div className="leave-page">
      <div className="page-heading">
        <div>
          <h1>Leave Management</h1>
          <p>Apply for leave and view your leave requests.</p>
        </div>
      </div>

      <div className="dashboard-card leave-form-card">
        <h3>Apply for Leave</h3>

        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="leaveType">Leave Type</label>

              <select
                id="leaveType"
                name="leaveType"
                value={form.leaveType}
                onChange={handleChange}
              >
                <option value="PAID">PAID</option>
                <option value="SICK">SICK</option>
                <option value="UNPAID">UNPAID</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="startDate">Start Date</label>

              <input
                id="startDate"
                name="startDate"
                type="date"
                value={form.startDate}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="endDate">End Date</label>

              <input
                id="endDate"
                name="endDate"
                type="date"
                value={form.endDate}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group form-group-full">
              <label htmlFor="remarks">Remarks</label>

              <textarea
                id="remarks"
                name="remarks"
                rows="4"
                value={form.remarks}
                onChange={handleChange}
                placeholder="Add a remark if needed"
              />
            </div>
          </div>

          <button type="submit" className="primary-button">
            Submit Leave
          </button>
        </form>
      </div>

      <div className="dashboard-card">
        <h3>My Leave Requests</h3>

        <div className="attendance-table-wrapper">
          <table className="attendance-table">
            <thead>
              <tr>
                <th>Type</th>
                <th>Start Date</th>
                <th>End Date</th>
                <th>Status</th>
                <th>Admin Comment</th>
              </tr>
            </thead>

            <tbody>
              {requests.map((request, index) => (
                <tr key={`${request.startDate}-${index}`}>
                  <td>{request.type}</td>
                  <td>{request.startDate}</td>
                  <td>{request.endDate}</td>
                  <td>{request.status}</td>
                  <td>{request.comment}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default Leave;