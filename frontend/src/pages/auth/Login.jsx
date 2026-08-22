import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../../services/api";

function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (event) => {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      const response = await api.post("/auth/login/", {
        email,
        password,
      });

      const { token, user } = response.data;

      localStorage.setItem("dayflow_token", token);
      localStorage.setItem("dayflow_user", JSON.stringify(user));

      if (user.role === "EMPLOYEE") {
        navigate("/employee/dashboard");
      } else if (user.role === "HR") {
        navigate("/hr/dashboard");
      } else if (user.role === "ADMIN") {
        navigate("/admin/dashboard");
      } else {
        setError("Unknown user role.");
      }
    } catch (err) {
      console.error("Login error:", err);

      if (err.response?.data?.message) {
        setError(err.response.data.message);
      } else if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Login failed. Please check your email and password.");
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
            <h2>Welcome back</h2>
            <p>Sign in to your Dayflow account</p>
          </div>

          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label htmlFor="email">Email address</label>

              <input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <div className="password-label">
                <label htmlFor="password">Password</label>
                <a href="#" onClick={(e) => e.preventDefault()}>
                  Forgot password?
                </a>
              </div>

              <input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
              />
            </div>

            {error && (
              <p style={{ color: "#dc2626", marginBottom: "12px" }}>
                {error}
              </p>
            )}

            <button
              className="login-button"
              type="submit"
              disabled={loading}
            >
              {loading ? "Signing in..." : "Sign in"}
            </button>
          </form>

          <div className="signup-text">
            Don't have an account?
            <Link to="/signup"> Create account</Link>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Login;