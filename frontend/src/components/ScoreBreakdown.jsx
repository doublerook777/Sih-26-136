const LABELS = {
  technology_match: "Technology match",
  domain_experience: "Domain experience",
  past_projects: "Past projects",
  eligibility: "Eligibility",
  cost_fit: "Cost fit",
  scalability: "Scalability",
  technical_feasibility: "Technical feasibility",
  innovation: "Innovation",
  cost_effectiveness: "Cost effectiveness",
  security: "Security",
  implementation_capability: "Implementation capability",
  social_impact: "Social impact",
};

export default function ScoreBreakdown({ breakdown = {}, snapshot = {}, criteria = [] }) {
  const labels = Object.fromEntries(criteria.map((item) => [item.key, item.label]));
  const entries = Object.entries(breakdown).filter(([, score]) => Number.isFinite(Number(score)));

  if (!entries.length) return <p className="muted score-breakdown-empty">No score breakdown available.</p>;

  return (
    <div className="score-breakdown" aria-label="Score breakdown">
      {entries.map(([key, rawScore]) => {
        const score = Math.max(0, Math.min(100, Number(rawScore)));
        return (
          <div className="score-breakdown-row" key={key}>
            <div className="score-breakdown-meta">
              <span>{labels[key] || LABELS[key] || key.replaceAll("_", " ")}</span>
              <span><strong>{score.toFixed(1)}</strong>/100{snapshot[key] != null ? ` · ${snapshot[key]}% weight` : ""}</span>
            </div>
            <div className="score-breakdown-track" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow={score}>
              <span style={{ width: `${score}%` }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}
