import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import DashboardLayout from "../components/DashboardLayout";
import Badge from "../components/Badge";
import { getMyApplications } from "../api/endpoints";

export default function MyApplications() {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchApplications = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getMyApplications();
      setApplications(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.detail || err.message || "Failed to load applications");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApplications();
  }, []);

  const getStatusTone = (status) => {
    const s = (status || "").toLowerCase();
    if (s === "selected") return "green";
    if (s === "shortlisted" || s === "screened" || s === "applied") return "blue";
    if (s === "evaluating") return "amber";
    return "blue";
  };

  const formatBudget = (val) => {
    if (typeof val === "number") return `₹${val.toLocaleString("en-IN")}`;
    return val || "₹0";
  };

  return (
    <DashboardLayout
      role="startup"
      title="My Applications"
      subtitle="Track your submitted pilot applications, eligibility status, and evaluation progress."
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <p className="muted" style={{ margin: 0 }}>
          Showing {applications.length} submitted application{applications.length === 1 ? "" : "s"}
        </p>
        <button
          type="button"
          onClick={fetchApplications}
          className="btn btn-soft"
        >
          Refresh
        </button>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="state-container">
          <div className="spinner"></div>
          <h3>Loading your applications...</h3>
          <p>Retrieving pilot proposals and review statuses.</p>
        </div>
      )}

      {/* Error State */}
      {!loading && error && (
        <div className="state-container error-state">
          <div style={{ fontSize: "2rem", marginBottom: "8px" }}>⚠</div>
          <h3>Unable to load applications</h3>
          <p>{error}</p>
          <button
            type="button"
            className="btn btn-primary"
            onClick={fetchApplications}
          >
            Retry
          </button>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && applications.length === 0 && (
        <div className="state-container">
          <div style={{ fontSize: "2.2rem", marginBottom: "8px" }}>🚀</div>
          <h3>No applications submitted yet</h3>
          <p>
            Explore available public-sector challenges and apply with your technology pilot proposal.
          </p>
          <Link to="/startup/explore" className="btn btn-primary">
            Explore Challenges
          </Link>
        </div>
      )}

      {/* Applications List */}
      {!loading && !error && applications.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {applications.map((app) => (
            <article
              key={app.application_id || app.id}
              className="panel"
              style={{ display: "flex", flexDirection: "column", gap: "14px" }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "12px" }}>
                <div>
                  <div style={{ display: "flex", gap: "8px", alignItems: "center", marginBottom: "6px" }}>
                    <Badge tone={getStatusTone(app.status)}>
                      {app.status || "applied"}
                    </Badge>
                    {app.challenge_sector && (
                      <span className="badge badge-blue" style={{ textTransform: "capitalize" }}>
                        {app.challenge_sector}
                      </span>
                    )}
                    {app.match_score !== undefined && app.match_score !== null && (
                      <span className="match-pill">{app.match_score}% match</span>
                    )}
                  </div>
                  <h3 style={{ fontSize: "1.2rem", margin: 0 }}>
                    {app.challenge_title || `Challenge #${app.challenge_id}`}
                  </h3>
                  {app.applied_at && (
                    <small className="muted" style={{ display: "block", marginTop: "4px" }}>
                      Applied on: {new Date(app.applied_at).toLocaleDateString()}
                    </small>
                  )}
                </div>

                <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                  <div>
                    <small className="muted" style={{ display: "block" }}>Proposed Quote</small>
                    <strong style={{ fontSize: "1.1rem", color: "var(--navy)" }}>
                      {formatBudget(app.quote)}
                    </strong>
                  </div>
                  {app.challenge_id && (
                    <Link
                      to={`/challenges/${app.challenge_id}`}
                      className="btn btn-soft"
                    >
                      View Challenge
                    </Link>
                  )}
                </div>
              </div>

              {app.pitch && (
                <div style={{ background: "var(--surface-soft)", padding: "12px 16px", borderRadius: "10px", border: "1px solid var(--border)" }}>
                  <small className="eyebrow" style={{ display: "block", margin: "0 0 4px" }}>Your Proposal Pitch</small>
                  <p style={{ margin: 0, fontSize: "0.92rem", whiteSpace: "pre-wrap" }}>
                    {app.pitch}
                  </p>
                </div>
              )}
            </article>
          ))}
        </div>
      )}
    </DashboardLayout>
  );
}
