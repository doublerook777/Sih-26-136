import DashboardLayout from "../components/DashboardLayout";

export default function Placeholder({ role, title }) {
  return (
    <DashboardLayout role={role} title={title} subtitle="This screen is ready for backend integration.">
      <section className="panel placeholder">
        <div className="ai-orb">↗</div>
        <h2>{title}</h2>
        <p className="muted">
          Add your API-connected records here once FastAPI and Supabase are wired.
        </p>
      </section>
    </DashboardLayout>
  );
}
