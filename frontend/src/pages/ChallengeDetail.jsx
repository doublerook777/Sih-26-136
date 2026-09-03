import { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import DashboardLayout from "../components/DashboardLayout";
import Badge from "../components/Badge";
import ApplyModal from "../components/ApplyModal";
import { getChallenge, getRubric, getMyApplications } from "../api/endpoints";
import { useAuth } from "../context/AuthContext";

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
  problem: "1. Problem Statement",
  background: "2. Background & Context",
  existing_system: "3. Existing System & Baseline",
  identified_gap: "4. Identified Gap",
  desired_solution: "5. Desired Solution Scope",
  target_users: "6. Target Users & Beneficiaries",
  technical_requirements: "7. Technical & Architectural Requirements",
  constraints: "8. Operational Constraints",
  budget: "9. Budget Allocation & Financial Rules",
  timeline: "10. Pilot Timeline & Milestones",
  expected_outcomes: "11. Expected Outcomes & Impact",
  kpis: "12. Key Performance Indicators (KPIs)",
  eligibility_requirements: "13. Mandatory Eligibility Requirements",
  data_requirements: "14. Data Governance & Storage",
  security_requirements: "15. Cybersecurity & Compliance",
};

export default function ChallengeDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [challenge, setChallenge] = useState(null);
  const [matchRubric, setMatchRubric] = useState(null);
  const [evalRubric, setEvalRubric] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Application state
  const [isApplyModalOpen, setIsApplyModalOpen] = useState(false);
  const [hasApplied, setHasApplied] = useState(false);

  useEffect(() => {
    async function loadChallengeData() {
      setLoading(true);
      setError(null);
      try {
        const data = await getChallenge(id);
        setChallenge(data);

        // Fetch rubrics if IDs exist
        if (data.match_rubric_id) {
          try {
            const mr = await getRubric(data.match_rubric_id);
            setMatchRubric(mr);
          } catch {
            // Non-blocking
          }
        }
        if (data.evaluation_rubric_id) {
          try {
            const er = await getRubric(data.evaluation_rubric_id);
            setEvalRubric(er);
          } catch {
            // Non-blocking
          }
        }

        // Check if current startup user has already applied
        if (user?.role === "startup") {
          try {
            const apps = await getMyApplications();
            const applied = apps.some((a) => Number(a.challenge_id) === Number(id));
            if (applied) {
              setHasApplied(true);
            }
          } catch {
            // Non-blocking
          }
        }
      } catch (err) {
        setError(err.detail || err.message || "Failed to load challenge details");
      } finally {
        setLoading(false);
      }
    }
    loadChallengeData();
  }, [id, user]);

  const formatBudget = (val) => {
    if (typeof val === "number") return `₹${val.toLocaleString("en-IN")}`;
    return val || "₹0";
  };

  const currentRole = user?.role || "government";
  const statement = challenge?.statement || {};
  const eligibility = challenge?.eligibility_rules || {};
  const kpis = Array.isArray(challenge?.kpi_targets) ? challenge.kpi_targets : [];

  return (
    <DashboardLayout
      role={currentRole}
      title={challenge?.title || "Challenge Details"}
      subtitle={`Sector: ${challenge?.sector || "Public Innovation"} • Department: ${challenge?.department || "Administration"}`}
    >
      {/* Top action bar */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <button
          type="button"
          onClick={() => navigate(-1)}
          className="btn btn-ghost"
        >
          ← Back
        </button>

        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
          {challenge && (
            <>
              <Link
                to={`/documents/problem_statement/${challenge.id}`}
                className="btn btn-soft"
              >
                📄 Problem Statement Doc
              </Link>
              <Link
                to={`/documents/eligibility_criteria/${challenge.id}`}
                className="btn btn-soft"
              >
                📋 Eligibility Criteria Doc
              </Link>
            </>
          )}

          {/* Startup Apply Button */}
          {user?.role === "startup" && (
            hasApplied ? (
              <span className="badge badge-green" style={{ padding: "10px 16px", fontSize: "0.9rem" }}>
                ✓ Applied
              </span>
            ) : (
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => setIsApplyModalOpen(true)}
              >
                Apply to Challenge
              </button>
            )
          )}
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="state-container">
          <div className="spinner"></div>
          <h3>Loading challenge details...</h3>
          <p>Retrieving 15-section statement, KPIs, and rubric assignments.</p>
        </div>
      )}

      {/* Error State */}
      {!loading && error && (
        <div className="state-container error-state">
          <div style={{ fontSize: "2rem", marginBottom: "8px" }}>⚠</div>
          <h3>Failed to load challenge</h3>
          <p>{error}</p>
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => window.location.reload()}
          >
            Retry
          </button>
        </div>
      )}

      {/* Challenge Content */}
      {!loading && !error && challenge && (
        <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
          {/* Metadata Banner */}
          <section className="panel">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "16px" }}>
              <div>
                <div style={{ display: "flex", gap: "10px", alignItems: "center", marginBottom: "8px" }}>
                  <Badge tone={challenge.status === "open" ? "green" : "blue"}>
                    {challenge.status}
                  </Badge>
                  <span className="badge badge-blue" style={{ textTransform: "capitalize" }}>
                    {challenge.sector}
                  </span>
                </div>
                <h2>{challenge.title}</h2>
                <p className="muted" style={{ marginTop: "4px" }}>
                  {challenge.department} — {challenge.district}
                </p>
              </div>

              <div style={{ display: "flex", gap: "24px" }}>
                <div>
                  <small className="muted" style={{ display: "block" }}>Pilot Budget</small>
                  <strong style={{ fontSize: "1.2rem", color: "var(--navy)" }}>{formatBudget(challenge.budget)}</strong>
                </div>
                <div>
                  <small className="muted" style={{ display: "block" }}>Pilot Duration</small>
                  <strong style={{ fontSize: "1.2rem", color: "var(--navy)" }}>{challenge.timeline_days} days</strong>
                </div>
                <div>
                  <small className="muted" style={{ display: "block" }}>Deadline</small>
                  <strong style={{ fontSize: "1.2rem", color: "var(--navy)" }}>{challenge.deadline}</strong>
                </div>
              </div>
            </div>

            {/* Required Technologies */}
            {Array.isArray(challenge.required_tech) && challenge.required_tech.length > 0 && (
              <div style={{ marginTop: "16px" }}>
                <small className="eyebrow" style={{ display: "block" }}>Required Technologies</small>
                <div className="chip-row" style={{ marginTop: "6px" }}>
                  {challenge.required_tech.map((t) => (
                    <span key={t} style={{ textTransform: "uppercase" }}>{t}</span>
                  ))}
                </div>
              </div>
            )}
          </section>

          {/* 15 Statement Sections */}
          <section className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Procurement Specification</p>
                <h2>15-Section Statement</h2>
              </div>
              {statement.generated_by && (
                <span className="ai-tag">
                  {statement.generated_by === "llm" ? "AI Generated" : "Template Baseline"}
                </span>
              )}
            </div>

            <div className="sections-accordion">
              {SECTION_KEYS.map((key) => {
                const content = statement[key];
                return (
                  <article key={key} className="section-item">
                    <h3 className="section-item-title" style={{ marginBottom: "8px" }}>
                      {SECTION_LABELS[key] || key}
                    </h3>
                    <p style={{ margin: 0, whiteSpace: "pre-wrap", color: content ? "var(--text)" : "var(--muted)" }}>
                      {content || "No detailed specification provided for this section."}
                    </p>
                  </article>
                );
              })}
            </div>
          </section>

          {/* Eligibility Rules & KPI Targets */}
          <div className="two-column">
            {/* Eligibility Rules */}
            <section className="panel">
              <div className="panel-heading">
                <div>
                  <p className="eyebrow">Screening Gate</p>
                  <h2>Eligibility Rules</h2>
                </div>
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                <div className="metric-row">
                  <span>DPIIT Startup Recognition</span>
                  <strong>{eligibility.registered_startup ? "Mandatory" : "Optional"}</strong>
                </div>
                <div className="metric-row">
                  <span>Required Certification</span>
                  <strong>{eligibility.required_certification || "None"}</strong>
                </div>
                <div className="metric-row">
                  <span>Minimum Track Record</span>
                  <strong>{eligibility.min_experience_years ? `${eligibility.min_experience_years} years` : "0 years"}</strong>
                </div>
                <div className="metric-row">
                  <span>Technology Overlap</span>
                  <strong>≥ {eligibility.min_technology_overlap || 1} required tech</strong>
                </div>
                <div className="metric-row">
                  <span>Maximum Quote Fit</span>
                  <strong>{formatBudget(eligibility.max_quote || challenge.budget)}</strong>
                </div>
                <div className="metric-row">
                  <span>Security Baseline Compliance</span>
                  <strong>{eligibility.security_baseline ? "Required" : "Optional"}</strong>
                </div>
              </div>
            </section>

            {/* KPI Targets */}
            <section className="panel">
              <div className="panel-heading">
                <div>
                  <p className="eyebrow">Pilot Metrics</p>
                  <h2>KPI Targets</h2>
                </div>
              </div>

              {kpis.length === 0 ? (
                <p className="muted">No explicit KPI targets defined.</p>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                  {kpis.map((kpi, idx) => (
                    <div key={idx} className="metric-card" style={{ padding: "14px", border: "1px solid var(--border)", borderRadius: "10px" }}>
                      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                        <strong>{kpi.name}</strong>
                        <span className="badge badge-blue">{kpi.category || "impact"}</span>
                      </div>
                      <div style={{ fontSize: "0.85rem", color: "var(--muted)" }}>
                        Baseline: {kpi.baseline} {kpi.unit} → Target: {kpi.target} {kpi.unit} ({kpi.direction?.replace(/_/g, " ")})
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </div>

          {/* Rubric Details */}
          <section className="panel">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Scoring Framework</p>
                <h2>Assigned Scoring Rubrics</h2>
              </div>
            </div>

            <div className="two-column">
              <div>
                <small className="eyebrow">Match Rubric (ID: {challenge.match_rubric_id})</small>
                <h3>{matchRubric?.name || `Match Rubric #${challenge.match_rubric_id}`}</h3>
                {matchRubric?.criteria && (
                  <div className="chip-row" style={{ marginTop: "8px" }}>
                    {matchRubric.criteria.map((c) => (
                      <span key={c.key}>{c.label}: {c.weight}%</span>
                    ))}
                  </div>
                )}
              </div>

              <div>
                <small className="eyebrow">Evaluation Rubric (ID: {challenge.evaluation_rubric_id})</small>
                <h3>{evalRubric?.name || `Evaluation Rubric #${challenge.evaluation_rubric_id}`}</h3>
                {evalRubric?.criteria && (
                  <div className="chip-row" style={{ marginTop: "8px" }}>
                    {evalRubric.criteria.map((c) => (
                      <span key={c.key}>{c.label}: {c.weight}%</span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </section>
        </div>
      )}

      {/* Apply Modal */}
      {challenge && (
        <ApplyModal
          challenge={challenge}
          isOpen={isApplyModalOpen}
          onClose={() => setIsApplyModalOpen(false)}
          onSuccess={() => setHasApplied(true)}
        />
      )}
    </DashboardLayout>
  );
}
