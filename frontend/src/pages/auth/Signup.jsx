import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../../services/api";

function Signup() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    employee_id: "",
    email: "",
    password: "",
    confirmPassword: "",
    first_name: "",
    last_name: "",
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSignup = async (event) => {
    event.preventDefault();

    setError("");
    setLoading(true);

    // Check if passwords match
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match.");
      setLoading(false);
      return;
    }

    // Check password length
    if (formData.password.length < 8) {
      setError("Password must be at least 8 characters long.");
      setLoading(false);
      return;
    }

    try {
      const response = await api.post("/auth/signup/", {
        employee_id: formData.employee_id,
        email: formData.email,
        password: formData.password,
        first_name: formData.first_name,
        last_name: formData.last_name,
        // ❌ NO role field! Backend automatically sets EMPLOYEE
      });

      console.log("Signup successful:", response.data);

      // Redirect to login page
      navigate("/");
    } catch (err) {
      console.error("Signup error:", err);

      if (err.response?.data?.employee_id) {
        setError(err.response.data.employee_id[0]);
      } else if (err.response?.data?.email) {
        setError(err.response.data.email[0]);
      } else if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else {
        setError("Signup failed. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <section className="login-brand">
        <div className="brand-content">
          <div className="logo-mark">D</div>

          <h1>Dayflow</h1>

          <p className="brand-tagline">
            Human Resource Management,
            <br />
            simplified.
          </p>

          <div className="feature-list">
            <div>✓ Smart attendance tracking</div>
            <div>✓ Simple leave management</div>
            <div>✓ Transparent payroll</div>
          </div>
        </div>

        <div className="brand-decoration decoration-one" />
        <div className="brand-decoration decoration-two" />
      </section>

      <section className="login-section">
        <div className="login-card">
          <div className="mobile-logo">D</div>

          <div className="login-header">
            <h2>Create your account</h2>
            <p>Join your organization on Dayflow</p>
          </div>

          <form onSubmit={handleSignup}>
            <div className="form-group">
              <label htmlFor="employeeId">Employee ID</label>
              <input
                id="employeeId"
                name="employee_id"
                type="text"
                placeholder="Enter your employee ID"
                value={formData.employee_id}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="firstName">First Name</label>
              <input
                id="firstName"
                name="first_name"
                type="text"
                placeholder="Enter your first name"
                value={formData.first_name}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="lastName">Last Name</label>
              <input
                id="lastName"
                name="last_name"
                type="text"
                placeholder="Enter your last name"
                value={formData.last_name}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Email address</label>
              <input
                id="email"
                name="email"
                type="email"
                placeholder="you@example.com"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                name="password"
                type="password"
                placeholder="Create a password (min 8 characters)"
                value={formData.password}
                onChange={handleChange}
                required
                minLength="8"
              />
            </div>

            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm password</label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                placeholder="Confirm your password"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
              />
            </div>

            {error && (
              <p style={{ color: "#dc2626", marginBottom: "12px", fontSize: "14px" }}>
                {error}
              </p>
            )}

            <button className="login-button" type="submit" disabled={loading}>
              {loading ? "Creating account..." : "Create account"}
            </button>
          </form>

          <div className="signup-text">
            Already have an account?
            <Link to="/"> Sign in</Link>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Signup;