import { NavLink, Link } from "react-router-dom";

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
  evaluator: [
    ["Overview", "/evaluator"],
    ["Pending Reviews", "/evaluator/reviews"],
  ],
};

export default function DashboardLayout({ role, title, subtitle, children }) {
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

        <div className="role-chip">{role}</div>

        <nav className="side-nav">
          {roleNav[role].map(([label, path]) => (
            <NavLink
              key={path}
              to={path}
              end={path === `/${role}`}
              className={({ isActive }) => isActive ? "side-link active" : "side-link"}
            >
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <span className="avatar">A</span>
          <div>
            <strong>Demo User</strong>
            <small>{role}@demo.in</small>
          </div>
        </div>
      </aside>

      <main className="dashboard-main">
        <header className="dash-header">
          <div>
            <p className="eyebrow">Innovation Procurement Platform</p>
            <h1>{title}</h1>
            <p className="muted">{subtitle}</p>
          </div>
          <Link to="/" className="btn btn-ghost">Home</Link>
        </header>

        {children}
      </main>
    </div>
  );
}
