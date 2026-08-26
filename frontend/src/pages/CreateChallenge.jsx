import { useState } from "react";
import DashboardLayout from "../components/DashboardLayout";

export default function CreateChallenge() {
  const [generated, setGenerated] = useState(false);
  const [problem, setProblem] = useState(
    "Frequent undetected water leakage in municipal pipelines leads to water loss and delayed maintenance."
  );

  const generate = () => {
    setGenerated(true);
  };

  return (
    <DashboardLayout
      role="government"
      title="Create Challenge"
      subtitle="Turn a public-sector problem into a measurable innovation pilot."
    >
      <div className="two-column">
        <section className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Step 1</p>
              <h2>Describe the problem</h2>
            </div>
            <span className="ai-tag">AI assisted</span>
          </div>

          <div className="form-grid">
            <label>
              Department
              <input defaultValue="Urban Water Authority" />
            </label>

            <label>
              Sector
              <select defaultValue="Water Management">
                <option>Water Management</option>
                <option>Healthcare</option>
                <option>Waste Management</option>
                <option>Transport</option>
              </select>
            </label>

            <label className="span-2">
              Problem description
              <textarea
                rows="7"
                value={problem}
                onChange={(e) => setProblem(e.target.value)}
              />
            </label>

            <label>
              Pilot budget
              <input defaultValue="₹5,00,000" />
            </label>

            <label>
              Pilot duration
              <input defaultValue="90 days" />
            </label>

            <label>
              Location
              <input defaultValue="Bengaluru, Karnataka" />
            </label>

            <label>
              Application deadline
              <input type="date" defaultValue="2026-09-20" />
            </label>
          </div>

          <button onClick={generate} className="btn btn-ai btn-lg">
            ✦ Generate structured challenge
          </button>
        </section>

        <section className={`panel ai-output ${generated ? "revealed" : ""}`}>
          {!generated ? (
            <div className="empty-ai">
              <div className="ai-orb">✦</div>
              <h3>AI-generated challenge preview</h3>
              <p>
                Your structured objective, KPIs, technologies and evaluation criteria will appear here.
              </p>
            </div>
          ) : (
            <>
              <div className="panel-heading">
                <div>
                  <p className="eyebrow">AI Draft</p>
                  <h2>Smart Municipal Water Leak Detection</h2>
                </div>
                <span className="badge badge-green">Ready</span>
              </div>

              <div className="generated-block">
                <small>Objective</small>
                <p>
                  Develop and pilot a real-time technology solution capable of detecting
                  municipal pipeline leakage and reducing response time.
                </p>
              </div>

              <div className="generated-block">
                <small>Suggested KPIs</small>
                <ul className="check-list">
                  <li>Leak detection accuracy ≥ 90%</li>
                  <li>Maintenance response time reduced by 30%</li>
                  <li>Water loss reduced by 25%</li>
                  <li>System uptime ≥ 95%</li>
                </ul>
              </div>

              <div className="generated-block">
                <small>Suggested technologies</small>
                <div className="chip-row">
                  <span>IoT</span>
                  <span>Pressure Sensors</span>
                  <span>AI</span>
                  <span>Analytics</span>
                </div>
              </div>

              <div className="button-row">
                <button className="btn btn-soft">Edit draft</button>
                <button className="btn btn-primary">Publish challenge</button>
              </div>
            </>
          )}
        </section>
      </div>
    </DashboardLayout>
  );
}
