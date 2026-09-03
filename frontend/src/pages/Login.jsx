import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const DEMO_ACCOUNTS = {
  government: {
    email: "officer@water.gov.in",
    password: "demo1234",
    label: "Government",
    icon: "🏛️",
  },
  startup: {
    email: "founder@aquasense.in",
    password: "demo1234",
    label: "Startup",
    icon: "🚀",
  },
  expert: {
    email: "expert1@procura.gov.in",
    password: "demo1234",
    label: "Evaluator",
    icon: "🧾",
  },
  validator: {
    email: "validator@procura.gov.in",
    password: "demo1234",
    label: "Validator",
    icon: "✓",
  },
};

export default function Login() {
  const [selectedRole, setSelectedRole] = useState("government");
  const [email, setEmail] = useState("officer@water.gov.in");
  const [password, setPassword] = useState("demo1234");
  const [errorMessage, setErrorMessage] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleRoleSelect = (roleKey) => {
    setSelectedRole(roleKey);
    const account = DEMO_ACCOUNTS[roleKey];
    if (account) {
      setEmail(account.email);
      setPassword(account.password);
    }
    setErrorMessage(null);
  };

  const handleLogin = async () => {
    setErrorMessage(null);
    setSubmitting(true);
    try {
      const user = await login(email, password);
      if (user.role === "government") {
        navigate("/government");
      } else if (user.role === "startup") {
        navigate("/startup");
      } else if (user.role === "expert") {
        navigate("/evaluator");
      } else if (user.role === "validator") {
        navigate("/validator");
      } else {
        navigate("/government");
      }
    } catch (err) {
      setErrorMessage(err.detail || err.message || "Invalid email or password");
    } finally {
      setSubmitting(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleLogin();
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-orb orb-one"></div>
      <div className="auth-orb orb-two"></div>

      <div className="auth-card">
        <div className="brand centered">
          <span className="brand-mark">P</span>
          <div>
            <strong>ProcuraAI</strong>
            <small>Prototype Access</small>
          </div>
        </div>

        <h1>Welcome back</h1>
        <p className="muted">Choose a demo role or enter your credentials.</p>

        <div className="role-selector">
          {Object.entries(DEMO_ACCOUNTS).map(([key, item]) => (
            <button
              type="button"
              key={key}
              className={selectedRole === key ? "role-option selected" : "role-option"}
              onClick={() => handleRoleSelect(key)}
            >
              <span>{item.icon}</span>
              {item.label}
            </button>
          ))}
        </div>

        {errorMessage && (
          <div className="auth-error-banner" role="alert">
            <span>⚠</span> {errorMessage}
          </div>
        )}

        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="officer@water.gov.in"
          />
        </label>

        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="••••••••"
          />
        </label>

        <button
          className="btn btn-primary full btn-lg"
          type="button"
          onClick={handleLogin}
          disabled={submitting}
        >
          {submitting ? (
            <>
              <span className="spinner spinner-sm"></span> Signing in...
            </>
          ) : (
            "Enter dashboard"
          )}
        </button>

        <p className="demo-note muted">
          Demo mode — all accounts use <code>demo1234</code>. Switch roles anytime.
        </p>
      </div>
    </div>
  );
}
