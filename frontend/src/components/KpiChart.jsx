import { useState } from "react";
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { updateKpi } from "../api/endpoints";

export default function KpiChart({ kpi, pilotId, role, onUpdated }) {
  const [value, setValue] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const data = [{ label: "Baseline", value: kpi.baseline, fill: "#8490a8" }, { label: "Target", value: kpi.target, fill: "#5268dc" }, { label: "Achieved", value: kpi.achieved, fill: kpi.met ? "#35a47a" : "#d28b1d" }].filter((item) => item.value != null);
  const directionLabel = kpi.direction === "lower_is_better" ? "Lower values meet the goal" : "Higher values meet the goal";
  async function record() {
    setSaving(true); setError("");
    try {
      const updated = await updateKpi(pilotId, { kpi_id: kpi.id, achieved: Number(value) });
      setValue("");
      onUpdated?.(updated);
    } catch (err) { setError(err.detail || err.message || "Could not record achieved value"); } finally { setSaving(false); }
  }
  return <article className={`panel kpi-chart-card ${kpi.met ? "kpi-met" : ""}`}><div className="kpi-chart-heading"><div><h3>{kpi.name}</h3><p>{directionLabel}</p></div><span className={kpi.met ? "kpi-outcome success" : "kpi-outcome"}>{kpi.achieved == null ? "Awaiting measurement" : kpi.met ? "Target met" : "Target pending"}</span></div><div className="kpi-chart-values"><span>Baseline <strong>{kpi.baseline} {kpi.unit}</strong></span><span>Target <strong>{kpi.target} {kpi.unit}</strong></span><span>Achieved <strong>{kpi.achieved == null ? "Pending" : `${kpi.achieved} ${kpi.unit}`}</strong></span></div><div className="kpi-chart"><ResponsiveContainer width="100%" height="100%"><BarChart data={data} margin={{ top: 8, right: 8, left: -18, bottom: 0 }}><CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey="label" /><YAxis /><Tooltip formatter={(value) => [`${value} ${kpi.unit}`, "Value"]} /><Bar dataKey="value" radius={[7, 7, 0, 0]}>{data.map((item) => <Cell key={item.label} fill={item.fill} />)}</Bar></BarChart></ResponsiveContainer></div>{kpi.achieved != null && <p className="kpi-achievement">Server-calculated achievement: <strong>{kpi.achievement}%</strong></p>}{role === "government" && <div className="kpi-record-row"><input type="number" step="any" value={value} onChange={(event) => setValue(event.target.value)} placeholder={`Measured value (${kpi.unit})`} /><button className="btn btn-soft" type="button" disabled={saving || value === ""} onClick={record}>{saving ? "Saving…" : kpi.achieved == null ? "Record achieved value" : "Update achieved value"}</button>{error && <small className="state-error">{error}</small>}</div>}</article>;
}
