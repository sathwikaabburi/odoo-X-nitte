import { Link } from "react-router-dom";

function Signup() {
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

          <form>
            <div className="form-group">
              <label htmlFor="employeeId">Employee ID</label>
              <input
                id="employeeId"
                type="text"
                placeholder="Enter your employee ID"
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Email address</label>
              <input
                id="email"
                type="email"
                placeholder="you@example.com"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                placeholder="Create a password"
              />
            </div>

            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm password</label>
              <input
                id="confirmPassword"
                type="password"
                placeholder="Confirm your password"
              />
            </div>

            <button className="login-button" type="submit">
              Create account
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