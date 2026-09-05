import { Link } from "react-router-dom";
import Badge from "./Badge";

export default function ChallengeCard({ challenge, startupView = false, onApply, hasApplied = false }) {
  const formatBudget = (val) => {
    if (typeof val === "number") {
      return `₹${val.toLocaleString("en-IN")}`;
    }
    return val || "₹0";
  };

  const getStatusTone = (status) => {
    const s = (status || "").toLowerCase();
    if (s === "open" || s === "active") return "green";
    if (s === "screening" || s === "evaluating" || s === "draft") return "amber";
    return "blue";
  };

  return (
    <article className="challenge-card">
      <div className="card-topline">
        <Badge tone={getStatusTone(challenge.status)}>
          {challenge.status}
        </Badge>
        {startupView && challenge.match_score !== undefined && challenge.match_score !== null && (
          <span className="match-pill">{challenge.match_score}% match</span>
        )}
      </div>

      <h3>{challenge.title}</h3>
      <p className="muted">{challenge.department || challenge.district}</p>

      <div className="chip-row">
        <span style={{ textTransform: "capitalize" }}>{challenge.sector}</span>
        <span>{challenge.timeline_days ? `${challenge.timeline_days} days` : challenge.duration || "90 days"}</span>
      </div>

      <div className="challenge-meta">
        <div>
          <small>Budget</small>
          <strong>{formatBudget(challenge.budget)}</strong>
        </div>
        <div>
          <small>Deadline</small>
          <strong>{challenge.deadline}</strong>
        </div>
      </div>

      <div style={{ display: "flex", gap: "8px", marginTop: "12px" }}>
        <Link
          className={`btn btn-soft ${startupView && onApply ? "" : "full"}`}
          style={{ flex: startupView && onApply ? 1 : undefined }}
          to={`/challenges/${challenge.id}`}
        >
          View challenge
        </Link>

        {startupView && onApply && (
          hasApplied ? (
            <span
              className="badge badge-green"
              style={{ padding: "8px 12px", display: "inline-flex", alignItems: "center", justifyContent: "center" }}
            >
              ✓ Applied
            </span>
          ) : (
            <button
              type="button"
              className="btn btn-primary"
              style={{ flex: 1 }}
              onClick={() => onApply(challenge)}
            >
              Apply
            </button>
          )
        )}
      </div>
    </article>
  );
}
