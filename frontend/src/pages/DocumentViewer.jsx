import { useState, useRef, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import DashboardLayout from "../components/DashboardLayout";
import { documentUrl, getChallenge } from "../api/endpoints";
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
};

export default function DocumentViewer() {
  const { docType: initialDocType, id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const iframeRef = useRef(null);

  const [activeDocType, setActiveDocType] = useState(initialDocType || "problem_statement");
  const [challenge, setChallenge] = useState(null);
  const [mockHtml, setMockHtml] = useState(null);

  const isSupported = Boolean(SUPPORTED_DOC_TYPES[activeDocType]);

  useEffect(() => {
    async function loadMetadata() {
      try {
        const c = await getChallenge(id);
        setChallenge(c);

        // In mock mode, construct HTML for iframe so VITE_USE_MOCK=true renders document
        if (USE_MOCK && isSupported) {
          const title = c.title || "Innovation Pilot Challenge";
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
      subtitle={`Viewing legal procurement documentation for Challenge #${id}`}
    >
      {/* Top navigation & action bar */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px", flexWrap: "wrap", gap: "12px" }}>
        <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
          <button
            type="button"
            onClick={() => navigate(`/challenges/${id}`)}
            className="btn btn-ghost"
          >
            ← Back to Challenge
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
            {challenge?.title || `Challenge #${id}`}
          </span>
        </div>

        {/* Handling 404 / Unavailable document types gracefully (Checkpoint 6) */}
        {!isSupported ? (
          <div className="state-container" style={{ margin: "auto", maxWidth: "560px" }}>
            <div style={{ fontSize: "2.6rem", marginBottom: "12px" }}>📄</div>
            <h3>Document Type Unavailable</h3>
            <p>
              The document type <code>{activeDocType}</code> is scheduled for Day 4 release and has not been wired yet.
              Today, only <strong>problem_statement</strong> and <strong>eligibility_criteria</strong> are available.
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
        ) : (
          <iframe
            ref={iframeRef}
            src={documentUrl(activeDocType, id)}
            title={SUPPORTED_DOC_TYPES[activeDocType].title}
            className="doc-viewer-iframe"
          />
        )}
      </div>
    </DashboardLayout>
  );
}
