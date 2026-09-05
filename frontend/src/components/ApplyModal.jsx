import { useState } from "react";
import { applyToChallenge } from "../api/endpoints";

export default function ApplyModal({ challenge, isOpen, onClose, onSuccess }) {
  const [quote, setQuote] = useState(challenge?.budget || 850000);
  const [pitch, setPitch] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  if (!isOpen || !challenge) return null;

  const handleSubmit = async () => {
    if (!pitch.trim()) {
      setError("Please describe your technical approach and deployment pitch.");
      return;
    }
    if (!quote || Number(quote) <= 0) {
      setError("Please enter a valid pilot quote.");
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const payload = {
        challenge_id: challenge.id,
        quote: Number(quote),
        pitch: pitch.trim(),
      };

      const application = await applyToChallenge(payload);
      setSuccess(true);
      if (onSuccess) {
        onSuccess(application);
      }
      setTimeout(() => {
        onClose();
        setSuccess(false);
      }, 1500);
    } catch (err) {
      // 400 or other API errors: display the exact detail message from the API
      setError(err.detail || err.message || "Failed to submit application.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <p className="eyebrow" style={{ margin: 0 }}>Pilot Application</p>
            <h2 style={{ fontSize: "1.25rem", marginTop: "4px" }}>{challenge.title}</h2>
          </div>
          <button
            type="button"
            className="modal-close-btn"
            onClick={onClose}
            title="Close dialog"
          >
            ✕
          </button>
        </div>

        {error && (
          <div className="auth-error-banner" style={{ marginBottom: "16px" }}>
            <span>⚠</span>
            <span>{error}</span>
          </div>
        )}

        {success ? (
          <div className="state-container" style={{ padding: "24px", margin: "16px 0" }}>
            <div style={{ fontSize: "2.4rem", color: "var(--green)" }}>✓</div>
            <h3>Application Submitted</h3>
            <p>Your proposal and commercial quote have been submitted to the department.</p>
          </div>
        ) : (
          <div>
            <div className="form-grid" style={{ marginBottom: "20px" }}>
              <label className="span-2">
                Proposed Pilot Budget Quote (₹)
                <input
                  type="number"
                  value={quote}
                  onChange={(e) => setQuote(e.target.value)}
                  disabled={submitting}
                  placeholder="Enter quote in INR"
                />
                <small className="muted">
                  Challenge Budget: ₹{Number(challenge.budget || 0).toLocaleString("en-IN")}
                </small>
              </label>

              <label className="span-2">
                Technical Approach & Pilot Pitch
                <textarea
                  rows={5}
                  value={pitch}
                  onChange={(e) => setPitch(e.target.value)}
                  disabled={submitting}
                  placeholder="Outline your technology architecture, hardware readiness, deployment methodology, and previous experience..."
                />
              </label>
            </div>

            <div className="button-row" style={{ justifyContent: "flex-end" }}>
              <button
                type="button"
                className="btn btn-ghost"
                onClick={onClose}
                disabled={submitting}
              >
                Cancel
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleSubmit}
                disabled={submitting}
              >
                {submitting ? "Submitting Application..." : "Submit Application"}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
