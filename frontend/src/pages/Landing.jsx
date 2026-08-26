import { Link } from "react-router-dom";

export default function Landing() {
  return (
    <div className="landing-page">
      <nav className="landing-nav container">
        <Link to="/" className="brand dark">
          <span className="brand-mark">P</span>
          <div>
            <strong>ProcuraAI</strong>
            <small>Government × Startups</small>
          </div>
        </Link>

        <div className="nav-actions">
          <a href="#how">How it works</a>
          <Link className="btn btn-primary" to="/login">Open demo</Link>
        </div>
      </nav>

      <section className="hero container">
        <div className="hero-copy">
          <div className="hero-badge">SIH 26136 • Innovation Procurement</div>
          <h1>
            From public problems to
            <span> startup-powered solutions.</span>
          </h1>
          <p>
            A transparent AI-assisted platform that helps government departments
            discover startups, run evidence-based pilots, evaluate outcomes and scale what works.
          </p>

          <div className="hero-actions">
            <Link className="btn btn-primary btn-lg" to="/login">
              Explore prototype
            </Link>
            <Link className="btn btn-white btn-lg" to="/government/create">
              Post a challenge
            </Link>
          </div>

          <div className="hero-trust">
            <span>✓ Explainable AI matching</span>
            <span>✓ Pilot-first procurement</span>
            <span>✓ KPI-based decisions</span>
          </div>
        </div>

        <div className="hero-panel">
          <div className="mini-window">
            <div className="window-header">
              <span></span><span></span><span></span>
              <small>AI MATCH ENGINE</small>
            </div>
            <div className="ai-demo-card">
              <small>Government problem</small>
              <h3>Detect municipal water leaks in real time</h3>
            </div>
            <div className="connector-line"></div>
            {[
              ["AquaSense", "94%"],
              ["PipeAI", "87%"],
              ["HydroTrack", "81%"]
            ].map(([name, score]) => (
              <div className="result-row" key={name}>
                <div>
                  <strong>{name}</strong>
                  <small>Verified startup</small>
                </div>
                <span>{score}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="stats-strip">
        <div className="container stats-grid">
          <div><strong>50+</strong><span>Demo startups</span></div>
          <div><strong>15</strong><span>Public challenges</span></div>
          <div><strong>5</strong><span>Active pilots</span></div>
          <div><strong>3</strong><span>User roles</span></div>
        </div>
      </section>

      <section id="how" className="how-section container">
        <div className="section-heading">
          <p className="eyebrow">One connected workflow</p>
          <h2>Try before you buy.</h2>
          <p className="muted">
            Procurement becomes measurable, transparent and startup-friendly.
          </p>
        </div>

        <div className="steps-grid">
          {[
            ["01", "Define", "Government posts an outcome-based challenge."],
            ["02", "Match", "AI recommends suitable verified startups."],
            ["03", "Evaluate", "Experts score proposals using fixed criteria."],
            ["04", "Pilot", "Selected solutions are tested with milestones."],
            ["05", "Measure", "KPIs track actual impact and performance."],
            ["06", "Scale", "Authorities decide whether to expand the solution."]
          ].map(([n, t, d]) => (
            <div className="step-card" key={n}>
              <span>{n}</span>
              <h3>{t}</h3>
              <p>{d}</p>
            </div>
          ))}
        </div>
      </section>

      <footer className="landing-footer">
        <div className="container">
          <strong>ProcuraAI</strong>
          <span>SIH 26136 prototype</span>
        </div>
      </footer>
    </div>
  );
}
