import DashboardLayout from "../components/DashboardLayout";
import Badge from "../components/Badge";
import { startups } from "../data/mockData";

export default function Recommendations() {
  return (
    <DashboardLayout
      role="government"
      title="AI Startup Recommendations"
      subtitle="Semantic matching based on sector, technology, capability and problem relevance."
    >
      <div className="insight-banner">
        <div>
          <p className="eyebrow">Matching for</p>
          <h2>Smart Municipal Water Leak Detection</h2>
          <p>AI is used for discovery support only. Final selection remains human-led.</p>
        </div>
        <span className="score-ring">94%</span>
      </div>

      <section className="recommendation-list">
        {startups.map((startup, index) => (
          <article className="startup-result" key={startup.id}>
            <div className="rank">0{index + 1}</div>
            <div className="startup-main">
              <div className="startup-title-row">
                <div>
                  <h3>{startup.name}</h3>
                  <p className="muted">{startup.description}</p>
                </div>
                <div className="match-score">
                  <strong>{startup.match}%</strong>
                  <small>AI match</small>
                </div>
              </div>

              <div className="chip-row">
                {startup.tech.map((t) => <span key={t}>{t}</span>)}
              </div>

              <div className="reason-grid">
                <div><Badge tone="green">✓ DPIIT verified</Badge></div>
                <div><Badge tone={startup.prototype ? "green" : "amber"}>
                  {startup.prototype ? "✓ Working prototype" : "△ Prototype testing"}
                </Badge></div>
                <div><Badge tone="blue">Sector relevant</Badge></div>
              </div>

              <div className="why-box">
                <strong>Why this match?</strong>
                <p>
                  Strong overlap with water infrastructure monitoring, real-time sensing
                  and anomaly detection. Primary concern: {startup.weakness}
                </p>
              </div>
            </div>
          </article>
        ))}
      </section>
    </DashboardLayout>
  );
}
