import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import DashboardLayout from "../components/DashboardLayout";
import { createPilot, getApplication, getChallenge } from "../api/endpoints";

const splitBudget = (budget) => {
  const total = Math.max(0, Number(budget) || 0);
  const first = Math.floor(total * 0.2);
  const second = Math.floor(total * 0.3);
  const third = Math.floor(total * 0.3);
  return [first, second, third, total - first - second - third];
};

const addDays = (days) => {
  const value = new Date();
  value.setDate(value.getDate() + days);
  return value.toISOString().slice(0, 10);
};

export default function CreatePilot() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const applicationId = searchParams.get("application_id");
  const [application, setApplication] = useState(null);
  const [challenge, setChallenge] = useState(null);
  const [form, setForm] = useState({ location: "", duration_days: 90, budget: 0, objectives: "" });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        if (!applicationId) throw new Error("A selected application is required to create a pilot");
        const selected = await getApplication(applicationId);
        const details = await getChallenge(selected.challenge_id);
        if (!active) return;
        setApplication(selected);
        setChallenge(details);
        setForm({
          location: details.district || "",
          duration_days: Number(details.timeline_days) || 90,
          budget: Number(details.budget) || 0,
          objectives: details.statement?.expected_outcomes || `Validate measurable outcomes for ${details.title}.`,
        });
      } catch (err) {
        if (active) setError(err.detail || err.message || "Unable to prepare pilot");
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => { active = false; };
  }, [applicationId]);

  const amounts = useMemo(() => splitBudget(form.budget), [form.budget]);
  const milestones = useMemo(() => [
    { seq: 1, title: "Prototype", deliverable: "Working prototype and deployment plan", amount: amounts[0], due_date: addDays(20) },
    { seq: 2, title: "Field trial", deliverable: "Live field trial with evidence capture", amount: amounts[1], due_date: addDays(45) },
    { seq: 3, title: "Deployment", deliverable: "Pilot-area deployment and operational handover", amount: amounts[2], due_date: addDays(70) },
    { seq: 4, title: "Final results", deliverable: "Verified KPI and final outcome report", amount: amounts[3], due_date: addDays(Number(form.duration_days) || 90) },
  ], [amounts, form.duration_days]);
  const milestoneTotal = milestones.reduce((sum, item) => sum + item.amount, 0);

  const update = (key, value) => setForm((current) => ({ ...current, [key]: value }));
  async function submit(event) {
    event.preventDefault();
    setSubmitting(true); setError("");
    try {
      const pilot = await createPilot({
        challenge_id: Number(application.challenge_id),
        startup_id: Number(application.startup_id),
        location: form.location,
        duration_days: Number(form.duration_days),
        budget: Number(form.budget),
        objectives: form.objectives,
        milestones,
        kpis: Array.isArray(challenge.kpi_targets) ? challenge.kpi_targets : [],
      });
      navigate(`/government/pilots/${pilot.id}`);
    } catch (err) {
      setError(err.detail || err.message || "Pilot could not be created");
    } finally {
      setSubmitting(false);
    }
  }

  return <DashboardLayout role="government" title="Create Pilot" subtitle="Turn the selected proposal into a milestone-based, measurable pilot.">
    {loading ? <div className="state-message">Loading selected application…</div> : error && !application ? <div className="state-message state-error">{error}</div> : <form className="pilot-create-layout" onSubmit={submit}>
      <section className="panel"><div className="pilot-selection-summary"><div><span>Challenge</span><strong>{challenge.title}</strong></div><div><span>Selected startup</span><strong>{application.startup_name}</strong></div></div>
        <div className="form-grid"><label>Location<input required value={form.location} onChange={(event) => update("location", event.target.value)} /></label><label>Duration (days)<input required min="1" type="number" value={form.duration_days} onChange={(event) => update("duration_days", event.target.value)} /></label><label>Budget (INR)<input required min="1" type="number" value={form.budget} onChange={(event) => update("budget", event.target.value)} /></label><label className="full-width">Objectives<textarea required rows="4" value={form.objectives} onChange={(event) => update("objectives", event.target.value)} /></label></div>
      </section>
      <section className="panel"><div className="section-heading"><div><p className="eyebrow">Payment plan</p><h2>Milestone split</h2></div><strong>₹{milestoneTotal.toLocaleString("en-IN")} total</strong></div><div className="milestone-preview">{milestones.map((item) => <div key={item.seq}><span>{item.seq}</span><div><strong>{item.title}</strong><small>{item.deliverable}</small></div><b>₹{item.amount.toLocaleString("en-IN")}</b></div>)}</div><p className={milestoneTotal === Number(form.budget) ? "budget-valid" : "budget-invalid"}>Milestones total ₹{milestoneTotal.toLocaleString("en-IN")} of ₹{Number(form.budget || 0).toLocaleString("en-IN")} budget.</p></section>
      <section className="panel"><p className="eyebrow">KPI targets</p><h2>Measures carried into the pilot</h2>{challenge.kpi_targets?.length ? <div className="kpi-target-list">{challenge.kpi_targets.map((item) => <div key={`${item.name}-${item.unit}`}><strong>{item.name}</strong><span>{item.baseline} → {item.target} {item.unit}</span></div>)}</div> : <div className="state-message">No KPI targets were published for this challenge.</div>}{error && <div className="state-message state-error">{error}</div>}<button className="btn btn-primary" disabled={submitting || milestoneTotal !== Number(form.budget)}>{submitting ? "Creating pilot…" : "Create pilot"}</button></section>
    </form>}
  </DashboardLayout>;
}
