import { Link } from "react-router-dom";
import Badge from "./Badge";

export default function ChallengeCard({ challenge, startupView = false }) {
  return (
    <article className="challenge-card">
      <div className="card-topline">
        <Badge tone={challenge.status === "Active" ? "green" : "amber"}>
          {challenge.status}
        </Badge>
        {startupView && (
          <span className="match-pill">{challenge.match}% match</span>
        )}
      </div>

      <h3>{challenge.title}</h3>
      <p className="muted">{challenge.department}</p>

      <div className="chip-row">
        <span>{challenge.sector}</span>
        <span>{challenge.duration}</span>
      </div>

      <div className="challenge-meta">
        <div>
          <small>Budget</small>
          <strong>{challenge.budget}</strong>
        </div>
        <div>
          <small>Deadline</small>
          <strong>{challenge.deadline}</strong>
        </div>
      </div>

      <Link className="btn btn-soft full" to={startupView ? "/startup/explore" : "/government/challenges"}>
        View challenge
      </Link>
    </article>
  );
}
