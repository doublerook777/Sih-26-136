import { Navigate, useLocation, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute({ allowedRoles, children }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="auth-page">
        <div className="auth-card" style={{ textAlign: "center" }}>
          <div className="brand centered">
            <span className="brand-mark">P</span>
          </div>
          <h2 style={{ marginTop: "16px" }}>Authenticating...</h2>
          <p className="muted">Verifying your credentials and session.</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (allowedRoles) {
    const roles = Array.isArray(allowedRoles) ? allowedRoles : [allowedRoles];
    if (!roles.includes(user.role)) {
      return (
        <div className="auth-page">
          <div className="auth-card" style={{ textAlign: "center" }}>
            <div className="brand centered">
              <span className="brand-mark" style={{ background: "#e53e3e" }}>✕</span>
            </div>
            <h2 style={{ marginTop: "16px" }}>Access Not Allowed</h2>
            <p className="muted">
              Your account with role <strong>{user.role}</strong> does not have access to this view.
            </p>
            <div style={{ marginTop: "24px", display: "flex", gap: "12px", justifyContent: "center" }}>
              <Link to={`/${["expert", "validator"].includes(user.role) ? "evaluator" : user.role}`} className="btn btn-primary">
                Go to your dashboard
              </Link>
              <Link to="/" className="btn btn-ghost">
                Home
              </Link>
            </div>
          </div>
        </div>
      );
    }
  }

  return children;
}
