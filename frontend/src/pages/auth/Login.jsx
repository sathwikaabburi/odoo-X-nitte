import { Link } from "react-router-dom";
function Login() {
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

          <form>
            <div className="form-group">
              <label htmlFor="email">Email address</label>
              <input
                id="email"
                type="email"
                placeholder="you@example.com"
              />
            </div>

            <div className="form-group">
              <div className="password-label">
                <label htmlFor="password">Password</label>
                <a href="#">Forgot password?</a>
              </div>

              <input
                id="password"
                type="password"
                placeholder="Enter your password"
              />
            </div>

            <button className="login-button" type="submit">
              Sign in
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