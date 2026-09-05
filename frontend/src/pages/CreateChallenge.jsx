import { useState } from "react";
import { useNavigate } from "react-router-dom";
import DashboardLayout from "../components/DashboardLayout";
import RubricSelect from "../components/RubricSelect";
import { generateStatement, createChallenge, publishChallenge } from "../api/endpoints";

const SECTION_KEYS = [
  "problem",
  "background",
  "existing_system",
  "identified_gap",
  "desired_solution",
  "target_users",
  "technical_requirements",
  "constraints",
  "budget",
  "timeline",
  "expected_outcomes",
  "kpis",
  "eligibility_requirements",
  "data_requirements",
  "security_requirements",
];

const SECTION_LABELS = {
  problem: "Problem Statement",
  background: "Background & Context",
  existing_system: "Existing System & Baseline",
  identified_gap: "Identified Gap",
  desired_solution: "Desired Solution Scope",
  target_users: "Target Users & Stakeholders",
  technical_requirements: "Technical & Architectural Requirements",
  constraints: "Operational Constraints",
  budget: "Budget Allocation & Milestones",
  timeline: "Pilot Timeline & Milestones",
  expected_outcomes: "Expected Outcomes & Impact",
  kpis: "Key Performance Indicators (KPIs)",
  eligibility_requirements: "Eligibility Requirements",
  data_requirements: "Data Governance & Storage",
  security_requirements: "Security, Privacy & Compliance",
};

export default function CreateChallenge() {
  const navigate = useNavigate();

  // Workflow state: 'before' | 'generating' | 'after'
  const [workflowState, setWorkflowState] = useState("before");
  const [error, setError] = useState(null);
  const [publishing, setPublishing] = useState(false);

  // Challenge metadata form fields
  const [title, setTitle] = useState("Reduce Municipal Water Leakage");
  const [department, setDepartment] = useState("Urban Water Supply");
  const [district, setDistrict] = useState("District A");
  const [sector, setSector] = useState("water");
  const [rawDescription, setRawDescription] = useState(
    "Our underground distribution pipes leak frequently, and we only detect anomalies after substantial water loss or road flooding. We require continuous real-time acoustic telemetry and predictive pressure monitoring."
  );
  const [budget, setBudget] = useState(1000000);
  const [timelineDays, setTimelineDays] = useState(90);
  const [deadline, setDeadline] = useState("2026-09-30");
  const [requiredTech, setRequiredTech] = useState("iot, sensors, analytics");
  const [matchRubricId, setMatchRubricId] = useState(1);

  // 15-section structured statement
  const [statement, setStatement] = useState({});

  const handleGenerate = async () => {
    if (!rawDescription.trim() || !title.trim()) {
      setError("Please provide a challenge title and problem description.");
      return;
    }

    setWorkflowState("generating");
    setError(null);

    try {
      const payload = {
        title,
        raw_description: rawDescription,
        department,
        district,
        sector,
        budget: Number(budget),
        timeline_days: Number(timelineDays),
      };

      const result = await generateStatement(payload);
      setStatement(result || {});
      setWorkflowState("after");
    } catch (err) {
      // Readable error state if backend is down or unreachable (no white screen)
      setError(err.detail || err.message || "Failed to generate structured challenge from API.");
      setWorkflowState("before");
    }
  };

  const handleSectionChange = (key, value) => {
    setStatement((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handlePublish = async () => {
    setPublishing(true);
    setError(null);

    try {
      const techList = typeof requiredTech === "string"
        ? requiredTech.split(",").map((t) => t.trim().toLowerCase()).filter(Boolean)
        : requiredTech;

      const challengePayload = {
        title,
        raw_description: rawDescription,
        department,
        district,
        sector,
        budget: Number(budget),
        timeline_days: Number(timelineDays),
        deadline,
        required_tech: techList,
        match_rubric_id: matchRubricId || 1,
        evaluation_rubric_id: 5,
        eligibility_rules: {
          registered_startup: true,
          required_certification: "ISO 9001:2015",
          min_experience_years: 1,
          min_technology_overlap: 1,
          max_quote: Number(budget),
          security_baseline: true,
        },
        kpi_targets: [
          {
            name: "Primary outcome metric",
            unit: "%",
            baseline: 30,
            target: 20,
            category: "impact",
            direction: "lower_is_better",
          },
        ],
        statement,
      };

      const created = await createChallenge(challengePayload);
      await publishChallenge(created.id);
      navigate("/government/challenges");
    } catch (err) {
      setError(err.detail || err.message || "Failed to publish challenge.");
      setPublishing(false);
    }
  };

  return (
    <DashboardLayout
      role="government"
      title="Create Challenge"
      subtitle="Turn a public-sector operational problem into a structured, measurable pilot."
    >
      {error && (
        <div className="auth-error-banner" style={{ marginBottom: "20px" }}>
          <span>⚠</span>
          <span>{error}</span>
          <button
            type="button"
            onClick={() => setError(null)}
            style={{ marginLeft: "auto", background: "none", border: "none", color: "inherit", cursor: "pointer" }}
          >
            ✕
          </button>
        </div>
      )}

      <div className="two-column">
        {/* Left Column: Problem Input & Metadata */}
        <section className="panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Step 1 — Challenge Definition</p>
              <h2>Describe the problem</h2>
            </div>
            <span className="ai-tag">AI assisted</span>
          </div>

          <div className="form-grid">
            <label className="span-2">
              Challenge Title
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                disabled={workflowState === "generating"}
              />
            </label>

            <label>
              Department
              <input
                type="text"
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                disabled={workflowState === "generating"}
              />
            </label>

            <label>
              District
              <input
                type="text"
                value={district}
                onChange={(e) => setDistrict(e.target.value)}
                disabled={workflowState === "generating"}
              />
            </label>

            <label>
              Sector
              <select
                value={sector}
                onChange={(e) => setSector(e.target.value)}
                disabled={workflowState === "generating"}
              >
                <option value="water">Water</option>
                <option value="healthcare">Healthcare</option>
                <option value="waste">Waste Management</option>
                <option value="transport">Transport</option>
              </select>
            </label>

            <label>
              Pilot Budget (₹)
              <input
                type="number"
                value={budget}
                onChange={(e) => setBudget(Number(e.target.value))}
                disabled={workflowState === "generating"}
              />
            </label>

            <label>
              Pilot Duration (days)
              <input
                type="number"
                value={timelineDays}
                onChange={(e) => setTimelineDays(Number(e.target.value))}
                disabled={workflowState === "generating"}
              />
            </label>

            <label>
              Application Deadline
              <input
                type="date"
                value={deadline}
                onChange={(e) => setDeadline(e.target.value)}
                disabled={workflowState === "generating"}
              />
            </label>

            <label className="span-2">
              Required Technologies (comma separated)
              <input
                type="text"
                value={requiredTech}
                onChange={(e) => setRequiredTech(e.target.value)}
                placeholder="e.g. iot, sensors, analytics, gis"
                disabled={workflowState === "generating"}
              />
            </label>

            <label className="span-2">
              Rough Problem Description
              <textarea
                rows={5}
                value={rawDescription}
                onChange={(e) => setRawDescription(e.target.value)}
                disabled={workflowState === "generating"}
                placeholder="Describe what is failing, current manual baseline, and desired operational outcome..."
              />
            </label>

            <div className="span-2">
              <RubricSelect
                value={matchRubricId}
                onChange={setMatchRubricId}
                kind="match"
                label="Match Scoring Rubric"
              />
            </div>
          </div>

          <div style={{ marginTop: "24px" }}>
            <button
              type="button"
              onClick={handleGenerate}
              disabled={workflowState === "generating"}
              className="btn btn-ai btn-lg full"
            >
              {workflowState === "generating" ? (
                <>
                  <span className="spinner spinner-sm" style={{ marginRight: "8px" }}></span>
                  Generating 15-section statement...
                </>
              ) : (
                <>✦ Generate structured challenge</>
              )}
            </button>
          </div>
        </section>

        {/* Right Column: 3 States (Before, Generating, After) */}
        <section className={`panel ai-output ${workflowState === "after" ? "revealed" : ""}`}>
          {/* State 1: Before Generation */}
          {workflowState === "before" && (
            <div className="empty-ai">
              <div className="ai-orb">✦</div>
              <h3>AI-Generated Challenge Preview</h3>
              <p>
                Fill in the problem definition and click generate. The system will create a comprehensive,
                15-section structured specification ready for officer review and publishing.
              </p>
            </div>
          )}

          {/* State 2: Generating Loading State */}
          {workflowState === "generating" && (
            <div className="state-container" style={{ margin: "40px 0" }}>
              <div className="spinner"></div>
              <h3>Synthesizing structured challenge...</h3>
              <p>
                Analyzing operational requirements, building 15-section procurement specifications,
                and calculating milestone KPIs. This may take several seconds.
              </p>
            </div>
          )}

          {/* State 3: After Generation — 15 Sections in Order */}
          {workflowState === "after" && (
            <>
              <div className="panel-heading">
                <div>
                  <p className="eyebrow">Step 2 — Review & Edit</p>
                  <h2>15-Section Statement</h2>
                </div>
                <span className="badge badge-green">Ready to Publish</span>
              </div>

              {/* Muted note if fallback template was returned */}
              {statement.generated_by === "template" && (
                <div className="fallback-notice-banner">
                  <span>ℹ</span>
                  <span>
                    Generated via baseline procurement template (AI engine offline or fallback mode).
                    All 15 sections are editable below.
                  </span>
                </div>
              )}

              <p className="muted" style={{ fontSize: "0.88rem", marginBottom: "16px" }}>
                Review and edit each section before publishing to the platform for startups.
              </p>

              <div className="sections-accordion">
                {SECTION_KEYS.map((key, index) => {
                  const val = statement[key] || "";
                  return (
                    <div key={key} className="section-item">
                      <div className="section-item-header">
                        <span className="section-item-title">{SECTION_LABELS[key] || key}</span>
                        <span className="section-item-num">{index + 1} of 15</span>
                      </div>
                      <textarea
                        className="section-item-textarea"
                        rows={key === "problem" || key === "background" ? 3 : 2}
                        value={val}
                        onChange={(e) => handleSectionChange(key, e.target.value)}
                      />
                    </div>
                  );
                })}
              </div>

              <div className="button-row" style={{ marginTop: "24px" }}>
                <button
                  type="button"
                  onClick={handleGenerate}
                  className="btn btn-soft"
                  disabled={publishing}
                >
                  Regenerate
                </button>
                <button
                  type="button"
                  onClick={handlePublish}
                  disabled={publishing}
                  className="btn btn-primary"
                >
                  {publishing ? "Publishing..." : "Publish Challenge"}
                </button>
              </div>
            </>
          )}
        </section>
      </div>
    </DashboardLayout>
  );
}
