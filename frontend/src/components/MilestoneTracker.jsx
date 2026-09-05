import { useState } from "react";
import { Link } from "react-router-dom";
import Badge from "./Badge";
import { payMilestone } from "../api/endpoints";

const TONES = { pending: "blue", in_progress: "blue", submitted: "amber", validated: "green", rejected: "amber", paid: "green" };

export default function MilestoneTracker({ milestones = [], pilotId, role = "government", onChanged }) {
  const [payingId, setPayingId] = useState(null);
  const [error, setError] = useState("");
  async function pay(id) {
    setPayingId(id); setError("");
    try { await payMilestone(id); await onChanged?.(); }
    catch (err) { setError(err.detail || err.message || "Payment could not be released"); }
    finally { setPayingId(null); }
  }
  if (!milestones.length) return <div className="state-message">No milestones have been created.</div>;
  return <div className="milestone-tracker">{error && <div className="state-message state-error">{error}</div>}{milestones.map((milestone) => <article className={`milestone-step milestone-${milestone.status}`} key={milestone.id || milestone.seq}><div className="milestone-step-marker">{milestone.seq}</div><div className="milestone-step-body"><div className="milestone-step-heading"><div><h3>{milestone.title}</h3><p>{milestone.deliverable}</p></div><Badge tone={TONES[milestone.status] || "blue"}>{milestone.status}</Badge></div><dl><div><dt>Amount</dt><dd>₹{Number(milestone.amount).toLocaleString("en-IN")}</dd></div><div><dt>Due</dt><dd>{milestone.due_date}</dd></div></dl>{milestone.evidence_text && <div className="milestone-evidence submitted"><strong>Startup evidence</strong><p>{milestone.evidence_text}</p>{milestone.evidence_url && <a href={milestone.evidence_url} target="_blank" rel="noreferrer">Open evidence</a>}<small>Claimed value: <strong>{milestone.claimed_value ?? milestone.validation?.claimed_value ?? "Not supplied"}</strong> — awaiting independent verification where applicable.</small></div>}{milestone.validation ? <div className="milestone-evidence validated"><strong>Validation: {milestone.validation.verdict}</strong><p>{milestone.validation.notes}</p><small>Claimed {milestone.validation.claimed_value}; verified {milestone.validation.verified_value} by {milestone.validation.validator_name}</small></div> : <div className="milestone-evidence empty">Validation pending</div>}{milestone.payment ? <div className="milestone-evidence paid"><strong>Payment {milestone.payment.status}</strong><p>₹{Number(milestone.payment.amount).toLocaleString("en-IN")} · <b>{milestone.payment.mock_txn_ref}</b></p></div> : <div className="milestone-evidence empty">Payment not released</div>}<div className="milestone-actions">{role === "startup" && ["pending", "in_progress", "rejected"].includes(milestone.status) && <Link className="btn btn-soft" to={`/startup/pilots/${pilotId}/milestones/${milestone.id}/submit`}>Submit evidence</Link>}{role === "government" && <button type="button" className="btn btn-soft" disabled={milestone.status !== "validated" || payingId === milestone.id} onClick={() => pay(milestone.id)}>{milestone.status === "paid" ? "Paid" : payingId === milestone.id ? "Releasing…" : "Pay milestone"}</button>}</div></div></article>)}</div>;
}
