import { NavLink, Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const roleNav = {
  government: [
    ["Overview", "/government"],
    ["Create Challenge", "/government/create"],
    ["Challenges", "/government/challenges"],
    ["AI Recommendations", "/government/recommendations"],
    ["Pilot Dashboard", "/government/pilot"],
  ],
  startup: [
    ["Overview", "/startup"],
    ["Explore Challenges", "/startup/explore"],
    ["My Applications", "/startup/applications"],
  ],
  expert: [
    ["Overview", "/evaluator"],
    ["Pending Reviews", "/evaluator/reviews"],
  ],
  evaluator: [
    ["Overview", "/evaluator"],
    ["Pending Reviews", "/evaluator/reviews"],
  ],
  validator: [
    ["Overview", "/evaluator"],
    ["Pending Reviews", "/evaluator/reviews"],
  ],
  admin: [
    ["Overview", "/government"],
    ["Create Challenge", "/government/create"],
  ],
};

export default function DashboardLayout({ role, title, subtitle, children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const currentRole = role || user?.role || "government";
  const navItems = roleNav[currentRole] || roleNav.government;

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const userInitial = (user?.name || currentRole || "U").charAt(0).toUpperCase();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Link to="/" className="brand">
          <span className="brand-mark">P</span>
          <div>
            <strong>ProcuraAI</strong>
            <small>SIH 26136</small>
          </div>
        </Link>

        <div className="role-chip" style={{ textTransform: "capitalize" }}>
          {user?.role || currentRole}
        </div>

        <nav className="side-nav">
          {navItems.map(([label, path]) => (
            <NavLink
              key={path}
              to={path}
              end={path === `/${currentRole}`}
              className={({ isActive }) => (isActive ? "side-link active" : "side-link")}
            >
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer" style={{ marginTop: "auto" }}>
          <span className="avatar">{userInitial}</span>
          <div style={{ flex: 1, minWidth: 0 }}>
            <strong style={{ display: "block", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
              {user?.name || "Demo User"}
            </strong>
            <small style={{ display: "block", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
              {user?.email || `${currentRole}@demo.in`}
            </small>
          </div>
          <button
            type="button"
            onClick={handleLogout}
            title="Log out"
            style={{
              background: "transparent",
              border: "none",
              color: "#8190b1",
              fontSize: "1.1rem",
              padding: "4px",
              cursor: "pointer",
            }}
          >
            ⎋
          </button>
        </div>
      </aside>

      <main className="dashboard-main">
        <header className="dash-header">
          <div>
            <p className="eyebrow">Innovation Procurement Platform</p>
            <h1>{title}</h1>
            <p className="muted">{subtitle}</p>
          </div>
          <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
            <Link to="/" className="btn btn-ghost">Home</Link>
            <button type="button" onClick={handleLogout} className="btn btn-soft">
              Logout
            </button>
          </div>
        </header>

        {children}
      </main>
    </div>
  );
}
