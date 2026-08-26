import DashboardLayout from "../components/DashboardLayout";

const kpis = [
  ["Leak reduction", "30%", "42%", 100],
  ["Detection accuracy", "90%", "94%", 94],
  ["Response time", "< 30 min", "22 min", 86],
  ["System uptime", "95%", "98.6%", 99],
];

export default function PilotDashboard() {
  return (
    <DashboardLayout
      role="government"
      title="Pilot Dashboard"
      subtitle="Monitor milestone delivery and measurable impact before scaling."
    >
      <div className="pilot-hero">
        <div>
          <p className="eyebrow">Active pilot</p>
          <h2>Smart Municipal Water Leak Detection</h2>
          <p>AquaSense • Bengaluru • Day 64 of 90</p>
        </div>
        <div className="progress-big">
          <strong>72%</strong>
          <span>complete</span>
        </div>
      </div>

      <div className="kpi-grid">
        {kpis.map(([label, target, actual, progress]) => (
          <div className="kpi-card" key={label}>
            <p className="muted">{label}</p>
            <div className="kpi-values">
              <div><small>Target</small><strong>{target}</strong></div>
              <div><small>Actual</small><strong>{actual}</strong></div>
            </div>
            <div className="progress-track">
              <div style={{ width: `${progress}%` }}></div>
            </div>
            <span className="success-text">✓ On track</span>
          </div>
        ))}
      </div>

      <div className="two-column lower">
        <section className="panel">
          <p className="eyebrow">Milestones</p>
          <h2>Implementation progress</h2>
          <div className="timeline">
            {[
              ["Installation", "Completed", true],
              ["Initial Testing", "Completed", true],
              ["30-Day Evaluation", "Completed", true],
              ["60-Day Evaluation", "In progress", false],
              ["Final Evaluation", "Upcoming", false],
            ].map(([name, status, done], idx) => (
              <div className="timeline-item" key={name}>
                <span className={done ? "timeline-dot done" : "timeline-dot"}>{done ? "✓" : idx + 1}</span>
                <div>
                  <strong>{name}</strong>
                  <small>{status}</small>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="panel decision-panel">
          <div className="ai-orb small">✦</div>
          <p className="eyebrow">Decision support</p>
          <h2>Scaling outlook: Positive</h2>
          <p>
            Current pilot performance exceeds three of four primary targets.
            Continue monitoring until final evaluation.
          </p>
          <div className="decision-note">
            AI recommendation is advisory. Final procurement authority remains with the department.
          </div>
          <button className="btn btn-primary full">View evaluation report</button>
        </section>
      </div>
    </DashboardLayout>
  );
}
