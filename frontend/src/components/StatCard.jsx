export default function StatCard({ label, value, hint, icon }) {
  return (
    <div className="stat-card">
      <div className="stat-icon">{icon}</div>
      <div>
        <p className="muted stat-label">{label}</p>
        <h3>{value}</h3>
        {hint && <small>{hint}</small>}
      </div>
    </div>
  );
}
