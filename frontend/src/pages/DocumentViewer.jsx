import { useState, useRef, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import DashboardLayout from "../components/DashboardLayout";
import { getChallenge, getDocumentHtml, getPilot } from "../api/endpoints";
import { useAuth } from "../context/AuthContext";

const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

const SUPPORTED_DOC_TYPES = {
  problem_statement: {
    title: "Problem Statement",
    description: "Standard 15-section public challenge specification",
  },
  eligibility_criteria: {
    title: "Eligibility Criteria",
    description: "Startup eligibility gates and mandatory screening rules",
  },
  pilot_agreement: {
    title: "Pilot Agreement",
    description: "Milestone-based pilot agreement covering scope, payment, data, and validation",
  },
  evaluation_criteria: { title: "Evaluation Criteria", description: "Expert scoring criteria and weights" },
  milestone_contract: { title: "Milestone Contract", description: "Milestone deliverables and release conditions" },
  data_ip: { title: "Data and IP Agreement", description: "Data governance and intellectual-property clauses" },
  security_checklist: { title: "Security Checklist", description: "Cybersecurity control verification" },
  risk_register: { title: "Risk Register", description: "Risk scoring, ownership, and mitigation" },
  kpi_report: { title: "KPI Report", description: "Baseline, target, achieved, and attainment evidence" },
  validation_report: { title: "Validation Report", description: "Independent milestone validation record" },
  payment_approval: { title: "Payment Approval", description: "Validated milestone payment authorization" },
  procurement_recommendation: { title: "Procurement Recommendation", description: "Evidence-backed procurement pathway" },
  scale_up_decision: { title: "Scale-up Decision", description: "Final score and scale-up outcome" },
};

const CHALLENGE_DOCUMENTS = new Set(["problem_statement", "eligibility_criteria", "evaluation_criteria"]);

export default function DocumentViewer() {
  const { docType: initialDocType, id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const iframeRef = useRef(null);

  const [activeDocType, setActiveDocType] = useState(initialDocType || "problem_statement");
  const [challenge, setChallenge] = useState(null);
  const [mockHtml, setMockHtml] = useState(null);
  const [liveHtml, setLiveHtml] = useState(null);
  const [liveError, setLiveError] = useState("");

  const isSupported = Boolean(SUPPORTED_DOC_TYPES[activeDocType]);

  useEffect(() => {
    async function loadMetadata() {
      try {
        const c = CHALLENGE_DOCUMENTS.has(activeDocType) ? await getChallenge(id) : await getPilot(id);
        setChallenge(c);

        // In mock mode, construct HTML for iframe so VITE_USE_MOCK=true renders document
        if (USE_MOCK && isSupported) {
          const title = c.title || c.challenge_title || "Innovation Pilot Challenge";
          const dept = c.department || "Municipal Administration";
          const district = c.district || "District A";
          const sector = (c.sector || "water").toUpperCase();
          const budgetFormatted = typeof c.budget === "number" ? `₹${c.budget.toLocaleString("en-IN")}` : c.budget;

          let bodyContent = "";
          if (activeDocType === "problem_statement") {
            const statement = c.statement || {};
            const sectionItems = [
              ["1. Problem Statement", statement.problem || c.raw_description],
              ["2. Background & Context", statement.background],
              ["3. Existing System", statement.existing_system],
              ["4. Identified Gap", statement.identified_gap],
              ["5. Desired Solution Scope", statement.desired_solution],
              ["6. Target Users", statement.target_users],
              ["7. Technical Requirements", statement.technical_requirements],
              ["8. Operational Constraints", statement.constraints],
              ["9. Pilot Budget", statement.budget || budgetFormatted],
              ["10. Timeline", statement.timeline || `${c.timeline_days} days`],
              ["11. Expected Outcomes", statement.expected_outcomes],
              ["12. KPIs", statement.kpis],
              ["13. Eligibility Requirements", statement.eligibility_requirements],
              ["14. Data Governance", statement.data_requirements],
              ["15. Security Requirements", statement.security_requirements],
            ];

            bodyContent = `
              <h1>${title}</h1>
              <div class="meta">
                <span><strong>Department:</strong> ${dept}</span> |
                <span><strong>District:</strong> ${district}</span> |
                <span><strong>Sector:</strong> ${sector}</span> |
                <span><strong>Budget:</strong> ${budgetFormatted}</span>
              </div>
              <hr style="margin: 20px 0; border: 0; border-top: 1px solid #ddd;" />
              ${sectionItems
                .map(
                  ([heading, content]) => `
                <div style="margin-bottom: 20px;">
                  <h3 style="color: #0e1730; margin-bottom: 6px;">${heading}</h3>
                  <p style="color: #334155; line-height: 1.6; margin: 0;">${content || "Not specified"}</p>
                </div>
              `
                )
                .join("")}
            `;
          } else if (activeDocType === "eligibility_criteria") {
            const rules = c.eligibility_rules || {};
            bodyContent = `
              <h1>Eligibility & Mandatory Screening Criteria</h1>
              <h2>${title}</h2>
              <p><strong>Department:</strong> ${dept} (${district})</p>
              <hr style="margin: 20px 0; border: 0; border-top: 1px solid #ddd;" />
              <table style="width: 100%; border-collapse: collapse; margin-top: 16px;">
                <tr style="background: #f8fafc; border-bottom: 2px solid #cbd5e1;">
                  <th style="padding: 10px; text-align: left;">Requirement</th>
                  <th style="padding: 10px; text-align: left;">Threshold</th>
                  <th style="padding: 10px; text-align: left;">Verification Type</th>
                </tr>
                <tr style="border-bottom: 1px solid #e2e8f0;">
                  <td style="padding: 10px;">DPIIT Recognition</td>
                  <td style="padding: 10px;">${rules.registered_startup ? "Mandatory" : "Optional"}</td>
                  <td style="padding: 10px;">Startup India Database API</td>
                </tr>
                <tr style="border-bottom: 1px solid #e2e8f0;">
                  <td style="padding: 10px;">Required Certification</td>
                  <td style="padding: 10px;">${rules.required_certification || "None"}</td>
                  <td style="padding: 10px;">Certificate Audit</td>
                </tr>
                <tr style="border-bottom: 1px solid #e2e8f0;">
                  <td style="padding: 10px;">Minimum Operating Experience</td>
                  <td style="padding: 10px;">${rules.min_experience_years || 0} Years</td>
                  <td style="padding: 10px;">Incorporation Certificate</td>
                </tr>
                <tr style="border-bottom: 1px solid #e2e8f0;">
                  <td style="padding: 10px;">Technology Capability Match</td>
                  <td style="padding: 10px;">≥ ${rules.min_technology_overlap || 1} tech overlap</td>
                  <td style="padding: 10px;">Tech Portfolio Evaluation</td>
                </tr>
                <tr style="border-bottom: 1px solid #e2e8f0;">
                  <td style="padding: 10px;">Maximum Permissible Quote</td>
                  <td style="padding: 10px;">${budgetFormatted}</td>
                  <td style="padding: 10px;">Financial Bid Gate</td>
                </tr>
              </table>
            `;
          } else if (activeDocType === "pilot_agreement") {
            const milestoneRows = (c.milestones || []).map((milestone) => `<tr><td>${milestone.seq}</td><td>${milestone.title}</td><td>${milestone.deliverable}</td><td>INR ${Number(milestone.amount).toLocaleString("en-IN")}</td><td>${milestone.due_date}</td></tr>`).join("");
            bodyContent = `<h1>Pilot Implementation Agreement</h1><h2>${title}</h2><div class="meta"><strong>Startup:</strong> ${c.startup_name} | <strong>Location:</strong> ${c.location} | <strong>Duration:</strong> ${c.duration_days} days | <strong>Budget:</strong> INR ${Number(c.budget).toLocaleString("en-IN")}</div><hr style="margin:20px 0;border:0;border-top:1px solid #ddd"/><h3>1. Objectives</h3><p>${c.objectives}</p><h3>2. Milestone-linked consideration</h3><table><thead><tr><th>Seq</th><th>Milestone</th><th>Deliverable</th><th>Amount</th><th>Due date</th></tr></thead><tbody>${milestoneRows}</tbody></table><h3>3. Validation and payment</h3><p>Each milestone payment is released only after evidence submission and independent validation. Rejected deliverables remain unpaid until corrected and approved.</p><h3>4. Data, security, and intellectual property</h3><p>The startup must follow the published security checklist, maintain auditable operational records, and provide exportable pilot data to the department. Pre-existing intellectual property remains with its owner; pilot outputs are licensed for government evaluation and approved public use.</p><h3>5. Acceptance</h3><p>This pilot remains outcome-based and does not guarantee scale-up procurement. Final procurement follows verified KPI performance, security clearance, and applicable public procurement rules.</p><div class="signature-grid"><div>For the Department<br/><br/><br/>Signature and date</div><div>For ${c.startup_name}<br/><br/><br/>Signature and date</div></div>`;
          } else {
            const metadata = SUPPORTED_DOC_TYPES[activeDocType];
            bodyContent = `<h1>${metadata.title}</h1><h2>${title}</h2><div class="meta"><strong>Entity:</strong> #${id} | <strong>Department:</strong> ${dept}</div><hr style="margin:20px 0;border:0;border-top:1px solid #ddd"/><h3>Purpose</h3><p>${metadata.description}.</p><h3>Record</h3><p>This document is generated from the current procurement lifecycle record and is suitable for review and printing.</p><table><tbody><tr><th>Status</th><td>${c.status || "Draft"}</td></tr><tr><th>Location</th><td>${c.location || district}</td></tr><tr><th>Budget</th><td>${budgetFormatted || "Not specified"}</td></tr><tr><th>Security status</th><td>${c.security_status || "Not applicable"}</td></tr></tbody></table>`;
          }

          setMockHtml(`
            <!DOCTYPE html>
            <html>
              <head>
                <meta charset="utf-8" />
                <title>${title} - ${SUPPORTED_DOC_TYPES[activeDocType].title}</title>
                <style>
                  body {
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                    padding: 40px;
                    color: #172033;
                    background: #ffffff;
                    line-height: 1.6;
                  }
                  h1 { font-size: 24px; margin-bottom: 8px; color: #0e1730; }
                  h2 { font-size: 18px; margin-top: 0; color: #475569; font-weight: normal; }
                  .meta { color: #64748b; font-size: 14px; margin-bottom: 16px; }
                  table { width: 100%; border-collapse: collapse; margin: 14px 0 24px; font-size: 13px; }
                  th, td { border: 1px solid #d8dee8; padding: 8px; text-align: left; vertical-align: top; }
                  th { background: #f5f7fa; }
                  .signature-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 50px; margin-top: 56px; }
                  @media print {
                    body { padding: 0; }
                    .no-print { display: none; }
                  }
                </style>
              </head>
              <body>
                ${bodyContent}
              </body>
            </html>
          `);
        }
      } catch {
        // Non-blocking
      }
    }
    loadMetadata();
  }, [id, activeDocType, isSupported]);

  useEffect(() => {
    if (USE_MOCK || !isSupported) return;
    let active = true;
    setLiveHtml(null);
    setLiveError("");
    getDocumentHtml(activeDocType, id)
      .then((html) => { if (active) setLiveHtml(html); })
      .catch((err) => { if (active) setLiveError(err.detail || err.message || "Unable to load document"); });
    return () => { active = false; };
  }, [id, activeDocType, isSupported]);

  const handlePrint = () => {
    if (iframeRef.current && iframeRef.current.contentWindow) {
      try {
        iframeRef.current.contentWindow.print();
        return;
      } catch {
        // Cross-origin restriction fallback
      }
    }
    window.print();
  };

  const currentRole = user?.role || "government";

  return (
    <DashboardLayout
      role={currentRole}
      title="Official Document Viewer"
      subtitle={`Viewing official procurement documentation for entity #${id}`}
    >
      {/* Top navigation & action bar */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px", flexWrap: "wrap", gap: "12px" }}>
        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
          <button
            type="button"
            onClick={() => navigate(CHALLENGE_DOCUMENTS.has(activeDocType) ? `/challenges/${id}` : `/government/pilots/${id}`)}
            className="btn btn-ghost"
          >
            ← Back to {CHALLENGE_DOCUMENTS.has(activeDocType) ? "Challenge" : "Pilot"}
          </button>

          {/* Doc Type Selector */}
          <div style={{ display: "flex", gap: "6px" }}>
            <button
              type="button"
              className={`btn ${activeDocType === "problem_statement" ? "btn-primary" : "btn-soft"}`}
              onClick={() => setActiveDocType("problem_statement")}
            >
              Problem Statement
            </button>
            <button
              type="button"
              className={`btn ${activeDocType === "eligibility_criteria" ? "btn-primary" : "btn-soft"}`}
              onClick={() => setActiveDocType("eligibility_criteria")}
            >
              Eligibility Criteria
            </button>
            <button
              type="button"
              className={`btn ${activeDocType === "pilot_agreement" ? "btn-primary" : "btn-soft"}`}
              onClick={() => setActiveDocType("pilot_agreement")}
            >
              Pilot Agreement
            </button>
          </div>
        </div>

        {isSupported && (
          <button
            type="button"
            className="btn btn-primary"
            onClick={handlePrint}
          >
            🖨 Print Document
          </button>
        )}
      </div>

      {/* Document Frame Shell */}
      <div className="doc-viewer-shell">
        <div className="doc-viewer-toolbar">
          <div>
            <strong>
              {isSupported ? SUPPORTED_DOC_TYPES[activeDocType].title : `Document: ${activeDocType}`}
            </strong>
            <small className="muted" style={{ display: "block" }}>
              {isSupported ? SUPPORTED_DOC_TYPES[activeDocType].description : "Procurement system document"}
            </small>
          </div>
          <span className="badge badge-blue">
            {challenge?.title || challenge?.challenge_title || challenge?.startup_name || `Entity #${id}`}
          </span>
        </div>

        {/* Handling 404 / Unavailable document types gracefully (Checkpoint 6) */}
        {!isSupported ? (
          <div className="state-container" style={{ margin: "auto", maxWidth: "560px" }}>
            <div style={{ fontSize: "2.6rem", marginBottom: "12px" }}>📄</div>
            <h3>Document Type Unavailable</h3>
            <p>
              The document type <code>{activeDocType}</code> is not available in this viewer.
            </p>
            <div style={{ display: "flex", gap: "10px", justifyContent: "center", marginTop: "16px" }}>
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => setActiveDocType("problem_statement")}
              >
                View Problem Statement
              </button>
              <button
                type="button"
                className="btn btn-soft"
                onClick={() => setActiveDocType("eligibility_criteria")}
              >
                View Eligibility Criteria
              </button>
            </div>
          </div>
        ) : USE_MOCK && mockHtml ? (
          <iframe
            ref={iframeRef}
            srcDoc={mockHtml}
            title={SUPPORTED_DOC_TYPES[activeDocType].title}
            className="doc-viewer-iframe"
          />
        ) : liveError ? (
          <div className="state-message state-error" style={{ margin: "auto" }}>{liveError}</div>
        ) : liveHtml ? (
          <iframe
            ref={iframeRef}
            srcDoc={liveHtml}
            title={SUPPORTED_DOC_TYPES[activeDocType].title}
            className="doc-viewer-iframe"
          />
        ) : (
          <div className="state-message" style={{ margin: "auto" }}>Loading document…</div>
        )}
      </div>
    </DashboardLayout>
  );
}
