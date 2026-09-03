import { useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import DashboardLayout from "../components/DashboardLayout";
import Badge from "../components/Badge";
import MilestoneTracker from "../components/MilestoneTracker";
import RiskMatrix from "../components/RiskMatrix";
import ChecklistPanel from "../components/ChecklistPanel";
import KpiChart from "../components/KpiChart";
import { getKpis, getPilot, getPilots, getRisks } from "../api/endpoints";
import { useAuth } from "../context/AuthContext";

const toneForRisk = (level) => level === "low" ? "green" : level === "medium" ? "amber" : level === "high" ? "amber" : "blue";

export default function PilotDashboard() {
  const { id } = useParams();
  const { user } = useAuth();
  const location = useLocation();
  const role = user?.role || "government";
  const pilotPath = (pilotId) => role === "startup" ? `/startup/pilots/${pilotId}` : `/government/pilots/${pilotId}`;
  const [pilot, setPilot] = useState(null); const [pilots, setPilots] = useState([]); const [risks, setRisks] = useState([]); const [kpis, setKpis] = useState([]); const [loading, setLoading] = useState(true); const [error, setError] = useState("");
  useEffect(() => { let active = true; (async () => { try { if (!id) { const list = await getPilots(); if (active) setPilots(Array.isArray(list) ? list : []); return; } const [details, riskData, kpiData] = await Promise.all([getPilot(id), getRisks(id), getKpis(id)]); if (!active) return; setPilot(details); setRisks(Array.isArray(riskData) ? riskData : []); setKpis(Array.isArray(kpiData) ? kpiData : []); } catch (err) { if (active) setError(err.detail || err.message || "Unable to load pilot"); } finally { if (active) setLoading(false); } })(); return () => { active = false; }; }, [id]);
  if (!id) return <DashboardLayout role={role} title="Pilot Dashboard" subtitle="Monitor active pilots and measurable delivery.">{loading ? <div className="state-message">Loading pilots…</div> : error ? <div className="state-message state-error">{error}</div> : pilots.length === 0 ? <div className="state-message">No pilots are available.</div> : <div className="pilot-list">{pilots.map((item) => <Link className="panel pilot-list-card" to={pilotPath(item.id)} key={item.id}><div><h3>{item.challenge_title}</h3><p>{item.startup_name} · {item.location}</p></div><Badge tone="blue">{item.status}</Badge></Link>)}</div>}</DashboardLayout>;
  return <DashboardLayout role={role} title="Pilot Dashboard" subtitle="Monitor milestone delivery, evidence, governance, and measurable impact.">{loading ? <div className="state-message">Loading pilot data…</div> : error ? <div className="state-message state-error">{error}</div> : !pilot ? <div className="state-message">Pilot not found.</div> : <>
    {location.state?.notice && <div className="state-message state-success">{location.state.notice}</div>}
    <div className="pilot-hero"><div><p className="eyebrow">{pilot.status} pilot</p><h2>{pilot.challenge_title}</h2><p>{pilot.startup_name} · {pilot.location} · {pilot.duration_days} days</p><div className="pilot-badges"><Badge tone={toneForRisk(pilot.risk_level)}>Risk: {pilot.risk_level || "not assessed"}</Badge><Badge tone={pilot.security_status === "passed" ? "green" : pilot.security_status === "needs_remediation" ? "amber" : "blue"}>Security: {pilot.security_status}</Badge></div></div><div className="paid-summary"><span>Paid to date</span><strong>₹{Number(pilot.paid_to_date || 0).toLocaleString("en-IN")}</strong><small>of ₹{Number(pilot.budget).toLocaleString("en-IN")}</small></div></div>
    <section className="panel"><div className="section-heading"><div><p className="eyebrow">Milestones</p><h2>Implementation progress</h2></div><span>{pilot.milestones?.length || 0} deliverables</span></div><MilestoneTracker milestones={pilot.milestones || []} pilotId={pilot.id} role={role} onChanged={async () => { const refreshed = await getPilot(pilot.id); setPilot(refreshed); }} /></section>
    <section className="pilot-section"><div className="section-heading"><div><p className="eyebrow">Performance</p><h2>Key performance indicators</h2></div></div>{kpis.length ? <div className="kpi-chart-grid">{kpis.map((kpi) => <KpiChart key={kpi.id} kpi={kpi} />)}</div> : <div className="state-message">No KPIs have been configured.</div>}</section>
    {role === "government" && <RiskMatrix pilotId={pilot.id} risks={risks} onRiskAdded={async (risk) => { setRisks((current) => [...current, risk]); try { const refreshed = await getPilot(pilot.id); setPilot(refreshed); } catch { /* The next page load refreshes the overall level. */ } }} />}
    {role === "government" && <ChecklistPanel pilotId={pilot.id} initialChecklist={pilot.security_checklist} initialStatus={pilot.security_status} onChecked={(result) => setPilot((current) => ({ ...current, security_status: result.security_status, security_checklist: result.checklist || current.security_checklist }))} />}
    {role === "government" && <section className="panel lifecycle-actions"><div><p className="eyebrow">Decision support</p><h2>Finalize and replicate</h2></div><div><Link className="btn btn-primary" to={`/government/pilots/${pilot.id}/decision`}>Scale-up decision</Link><Link className="btn btn-soft" to={`/government/pilots/${pilot.id}/replication`}>Replication plan</Link></div></section>}
    <section className="panel agreement-callout"><div><p className="eyebrow">Official document</p><h2>Pilot agreement</h2><p>Review the generated agreement, then print it from the existing document viewer.</p></div><Link className="btn btn-primary" to={`/documents/pilot_agreement/${pilot.id}`}>View pilot agreement</Link></section>
  </>}</DashboardLayout>;
}
