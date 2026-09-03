import { useState, useEffect } from "react";
import { getRubrics } from "../api/endpoints";

export default function RubricSelect({ value, onChange, kind = "match", label = "Evaluation Rubric" }) {
  const [rubrics, setRubrics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;
    async function loadRubrics() {
      setLoading(true);
      setError(null);
      try {
        const data = await getRubrics(kind);
        if (!isMounted) return;
        const list = Array.isArray(data) ? data : [];
        setRubrics(list);

        // If no value is currently selected or passed, default to is_default or first item
        if (list.length > 0 && !value && onChange) {
          const defaultRubric = list.find((r) => r.is_default) || list[0];
          onChange(defaultRubric.id);
        }
      } catch (err) {
        if (!isMounted) return;
        setError(err.detail || err.message || "Failed to load rubrics");
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadRubrics();
    return () => {
      isMounted = false;
    };
  }, [kind]);

  const selectedRubric = rubrics.find((r) => r.id === Number(value)) || rubrics[0];
  const totalWeight = selectedRubric?.criteria
    ? selectedRubric.criteria.reduce((sum, c) => sum + (Number(c.weight) || 0), 0)
    : 0;

  return (
    <div className="rubric-select-container">
      <label style={{ display: "block", marginBottom: "6px", fontWeight: 600 }}>
        {label}
        {loading ? (
          <div className="rubric-loading-text">Loading rubrics...</div>
        ) : error ? (
          <div className="rubric-error-text">{error}</div>
        ) : (
          <select
            value={value || selectedRubric?.id || ""}
            onChange={(e) => onChange && onChange(Number(e.target.value))}
            className="rubric-dropdown"
          >
            {rubrics.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name} {r.is_default ? "(Default)" : ""}
              </option>
            ))}
          </select>
        )}
      </label>

      {/* Live Weight Preview */}
      {selectedRubric && Array.isArray(selectedRubric.criteria) && (
        <div className="rubric-preview-panel">
          <div className="rubric-preview-header">
            <span className="eyebrow" style={{ margin: 0 }}>Weights Breakdown</span>
            <span className={`rubric-total-badge ${totalWeight === 100 ? "badge-valid" : "badge-invalid"}`}>
              Total: {totalWeight}%
            </span>
          </div>

          <div className="rubric-criteria-list">
            {selectedRubric.criteria.map((criterion) => (
              <div
                key={criterion.key}
                className="rubric-criterion-row"
                title={criterion.help || ""}
              >
                <div className="rubric-criterion-info">
                  {/* Criterion label strictly from API response — never hardcoded */}
                  <span className="rubric-criterion-label">{criterion.label}</span>
                  <span className="rubric-criterion-weight">{criterion.weight}%</span>
                </div>
                <div className="rubric-progress-track">
                  <div
                    className="rubric-progress-fill"
                    style={{ width: `${criterion.weight}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
