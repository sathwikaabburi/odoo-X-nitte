import { useState, useEffect } from "react";
import api from "../../services/api";

function AdminLeaves() {
  const [leaves, setLeaves] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("PENDING");

  useEffect(() => {
    fetchLeaves();
  }, [filter]);

  const fetchLeaves = async () => {
    try {
      const response = await api.get(`/leaves/?status=${filter}`);
      setLeaves(response.data);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching leaves:", err);
      setError("Failed to load leave requests.");
      setLoading(false);
    }
  };

  const handleApprove = async (leaveId) => {
    const comment = prompt("Add an approval comment (optional):");
    try {
      await api.patch(`/leaves/${leaveId}/approve/`, {
        admin_comment: comment || "Approved",
      });
      alert("✅ Leave approved!");
      fetchLeaves();
    } catch (err) {
      alert("❌ Failed to approve leave.");
      console.error(err);
    }
  };

  const handleReject = async (leaveId) => {
    const comment = prompt("Add a rejection comment (optional):");
    try {
      await api.patch(`/leaves/${leaveId}/reject/`, {
        admin_comment: comment || "Rejected",
      });
      alert("✅ Leave rejected!");
      fetchLeaves();
    } catch (err) {
      alert("❌ Failed to reject leave.");
      console.error(err);
    }
  };

  if (loading) {
    return <div>Loading leave requests...</div>;
  }

  if (error) {
    return <div style={{ color: "red" }}>{error}</div>;
  }

  return (
    <div>
      <div className="page-heading">
        <div>
          <h1>Leave Requests</h1>
          <p>Approve or reject employee leave requests.</p>
        </div>
        <div style={{ display: "flex", gap: "10px" }}>
          <select 
            value={filter} 
            onChange={(e) => setFilter(e.target.value)}
            style={{ padding: "10px", borderRadius: "8px", border: "1px solid #ddd" }}
          >
            <option value="PENDING">Pending</option>
            <option value="APPROVED">Approved</option>
            <option value="REJECTED">Rejected</option>
          </select>
          <button className="primary-button" onClick={fetchLeaves}>
            Refresh
          </button>
        </div>
      </div>

      <div className="dashboard-card">
        <div className="attendance-table-wrapper">
          <table className="attendance-table">
            <thead>
              <tr>
                <th>Employee</th>
                <th>Type</th>
                <th>Start Date</th>
                <th>End Date</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {leaves.length > 0 ? (
                leaves.map((leave) => (
                  <tr key={leave.id}>
                    <td>{leave.employee_name || "N/A"}</td>
                    <td>{leave.leave_type}</td>
                    <td>{leave.start_date}</td>
                    <td>{leave.end_date}</td>
                    <td>
                      <span style={{
                        padding: "4px 8px",
                        borderRadius: "4px",
                        background: leave.status === "APPROVED" ? "#dcfce7" : 
                                   leave.status === "REJECTED" ? "#fee2e2" : "#fef3c7",
                        color: leave.status === "APPROVED" ? "#166534" : 
                               leave.status === "REJECTED" ? "#991b1b" : "#92400e"
                      }}>
                        {leave.status}
                      </span>
                    </td>
                    <td>
                      {leave.status === "PENDING" && (
                        <div style={{ display: "flex", gap: "8px" }}>
                          <button 
                            onClick={() => handleApprove(leave.id)}
                            style={{ padding: "6px 12px", background: "#22c55e", color: "white", border: "none", borderRadius: "4px", cursor: "pointer" }}
                          >
                            Approve
                          </button>
                          <button 
                            onClick={() => handleReject(leave.id)}
                            style={{ padding: "6px 12px", background: "#ef4444", color: "white", border: "none", borderRadius: "4px", cursor: "pointer" }}
                          >
                            Reject
                          </button>
                        </div>
                      )}
                      {leave.status !== "PENDING" && leave.admin_comment && (
                        <span style={{ fontSize: "12px", color: "#6b7280" }}>
                          {leave.admin_comment}
                        </span>
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6">No leave requests found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default AdminLeaves;