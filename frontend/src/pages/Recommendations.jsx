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
          <h2>Reduce Municipal Water Leakage in Distribution Networks</h2>
          <p>AI is used for discovery support only. Final selection remains human-led.</p>
        </div>
        <span className="score-ring">94%</span>
      </div>

      <section className="recommendation-list">
        {startups.map((startup, index) => {
          const match_score = startup.match_score || 90;
          const techList = startup.technologies || startup.tech || [];
          return (
            <article className="startup-result" key={startup.id}>
              <div className="rank">0{index + 1}</div>
              <div className="startup-main">
                <div className="startup-title-row">
                  <div>
                    <h3>{startup.name}</h3>
                    <p className="muted">{startup.description}</p>
                  </div>
                  <div className="match-score">
                    <strong>{match_score}%</strong>
                    <small>AI match</small>
                  </div>
                </div>

                <div className="chip-row">
                  {techList.map((t) => (
                    <span key={t}>{t}</span>
                  ))}
                </div>

                <div className="reason-grid">
                  <div>
                    <Badge tone="green">
                      {startup.dpiit_number ? `✓ DPIIT (${startup.dpiit_number})` : "✓ DPIIT verified"}
                    </Badge>
                  </div>
                  <div>
                    <Badge tone="green">✓ Working prototype</Badge>
                  </div>
                  <div>
                    <Badge tone="blue">Sector relevant</Badge>
                  </div>
                </div>

                <div className="why-box">
                  <strong>Why this match?</strong>
                  <p>
                    Strong overlap with water infrastructure monitoring, real-time sensing
                    and anomaly detection.
                  </p>
                </div>
              </div>
            </article>
          );
        })}
      </section>
    </DashboardLayout>
  );
}
