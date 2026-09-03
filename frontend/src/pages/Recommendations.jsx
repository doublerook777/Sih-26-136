import { useEffect, useMemo, useState } from "react";
import DashboardLayout from "../components/DashboardLayout";
import Badge from "../components/Badge";
import ScoreBreakdown from "../components/ScoreBreakdown";
import { discoverStartups, getChallengeApplications, getChallenges, selectApplication, shortlistApplication } from "../api/endpoints";

const message = (error) => error?.detail || error?.message || "Something went wrong";

export default function Recommendations() {
  const [challenges, setChallenges] = useState([]);
  const [challengeId, setChallengeId] = useState("");
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [discovering, setDiscovering] = useState(false);
  const [actingId, setActingId] = useState(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const challenge = useMemo(() => challenges.find((item) => item.id === Number(challengeId)), [challenges, challengeId]);

  useEffect(() => {
    let active = true;
    getChallenges().then((data) => {
      if (!active) return;
      const list = Array.isArray(data) ? data : [];
      setChallenges(list);
      if (list.length) setChallengeId(String(list[0].id));
    }).catch((err) => active && setError(message(err))).finally(() => active && setLoading(false));
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (!challengeId) return;
    let active = true;
    setLoading(true);
    setError("");
    getChallengeApplications(challengeId).then((data) => active && setApplications(Array.isArray(data) ? data : []))
      .catch((err) => active && setError(message(err))).finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [challengeId]);

  async function discover() {
    setDiscovering(true); setError(""); setNotice("");
    try {
      const data = await discoverStartups(challengeId);
      setApplications(Array.isArray(data) ? data : []);
      setNotice(`${Array.isArray(data) ? data.length : 0} startups screened and ranked.`);
    } catch (err) { setError(message(err)); } finally { setDiscovering(false); }
  }

  async function shortlist(id) {
    setActingId(id); setError("");
    try {
      const result = await shortlistApplication(id);
      setApplications((items) => items.map((item) => item.application_id === id ? { ...item, status: result.status } : item));
      setNotice("Startup shortlisted for expert evaluation.");
    } catch (err) { setError(message(err)); } finally { setActingId(null); }
  }

  async function selectWinner(id) {
    setActingId(id); setError("");
    try {
      await selectApplication(id);
      const refreshed = await getChallengeApplications(challengeId);
      setApplications(Array.isArray(refreshed) ? refreshed : []);
      setChallenges((items) => items.map((item) => item.id === Number(challengeId) ? { ...item, status: "selected" } : item));
      setNotice("Winner selected. All other applications were marked rejected.");
    } catch (err) { setError(message(err)); } finally { setActingId(null); }
  }

  return <DashboardLayout role="government" title="AI Startup Recommendations" subtitle="Transparent eligibility screening and explainable, rubric-weighted ranking.">
    <section className="panel discovery-controls"><label>Challenge<select value={challengeId} onChange={(event) => setChallengeId(event.target.value)} disabled={loading || discovering}>{challenges.map((item) => <option key={item.id} value={item.id}>{item.title}</option>)}</select></label><button className="btn btn-primary" type="button" disabled={!challengeId || discovering} onClick={discover}>{discovering ? "Screening startups…" : "Discover startups"}</button></section>
    {challenge && <div className="insight-banner"><div><p className="eyebrow">Matching for</p><h2>{challenge.title}</h2><p>{challenge.department} · {challenge.district} · Status: {challenge.status}</p></div><span className="score-ring">{applications.length}</span></div>}
    {error && <div className="state-message state-error" role="alert">{error}</div>}{notice && <div className="state-message state-success" role="status">{notice}</div>}
    {loading ? <div className="state-message">Loading applications…</div> : applications.length === 0 ? <div className="state-message">No screening results yet. Choose a challenge and run discovery.</div> : <section className="recommendation-list">{applications.map((application, index) => {
      const failures = Object.entries(application.eligibility_report || {}).filter(([, result]) => !result?.passed);
      const canShortlist = application.eligible && ["applied", "screened"].includes(application.status);
      return <article className={`startup-result ${application.eligible ? "" : "startup-result-ineligible"}`} key={application.application_id}><div className="rank">{String(index + 1).padStart(2, "0")}</div><div className="startup-main"><div className="startup-title-row"><div><h3>{application.startup_name}</h3><Badge tone={application.eligible ? "green" : "amber"}>{application.eligible ? "Eligible" : "Ineligible"}</Badge></div><div className="match-score"><strong>{Number(application.match_score || 0).toFixed(1)}%</strong><small>match score</small></div></div>
        {failures.length > 0 && <div className="eligibility-failures"><strong>Eligibility checks requiring action</strong>{failures.map(([key, result]) => <p key={key}><span>{key.replaceAll("_", " ")}:</span> {result.note}</p>)}</div>}
        <div className="why-box"><strong>Why this ranking?</strong><p>{application.explanation || "No explanation supplied."}</p></div><ScoreBreakdown breakdown={application.match_breakdown} snapshot={application.rubric_snapshot} />
        <div className="result-actions">{canShortlist && <button className="btn btn-soft" disabled={actingId === application.application_id} onClick={() => shortlist(application.application_id)}>{actingId === application.application_id ? "Updating…" : "Shortlist"}</button>}{application.status === "shortlisted" && <button className="btn btn-primary" disabled={actingId === application.application_id} onClick={() => selectWinner(application.application_id)}>{actingId === application.application_id ? "Selecting…" : "Select winner"}</button>}{["shortlisted", "selected", "rejected"].includes(application.status) && <Badge tone={application.status === "selected" ? "green" : application.status === "rejected" ? "amber" : "blue"}>{application.status}</Badge>}</div>
      </div></article>;
    })}</section>}
  </DashboardLayout>;
}
