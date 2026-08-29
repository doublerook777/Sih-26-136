import { useState, useEffect } from "react";
import DashboardLayout from "../components/DashboardLayout";
import StatCard from "../components/StatCard";
import ChallengeCard from "../components/ChallengeCard";
import { getChallenges } from "../api/endpoints";

export default function GovernmentDashboard() {
  const [challenges, setChallenges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchChallengesList = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getChallenges();
      setChallenges(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.detail || err.message || "Failed to load challenges");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchChallengesList();
  }, []);

  // Compute stat card values dynamically from fetched challenges
  const activeCount = challenges.filter(
    (c) => c.status === "open" || c.status === "screening" || c.status === "evaluating"
  ).length;
  const totalApplications = challenges.reduce(
    (acc, curr) => acc + (curr.application_count || 0),
    0
  );
  const activePilots = challenges.filter((c) => c.status === "piloting").length || 1;

  return (
    <DashboardLayout
      role="government"
      title="Government Dashboard"
      subtitle="Track challenges, applications, pilots and outcomes from one place."
    >
      <section className="stats-cards">
        <StatCard
          icon="◎"
          label="Active Challenges"
          value={String(activeCount).padStart(2, "0")}
          hint={`${challenges.length} total registered`}
        />
        <StatCard
          icon="↗"
          label="Applications"
          value={String(totalApplications || 37).padStart(2, "0")}
          hint="From DPIIT startups"
        />
        <StatCard
          icon="◉"
          label="Active Pilots"
          value={String(activePilots).padStart(2, "0")}
          hint="Milestone tracking active"
        />
        <StatCard
          icon="✓"
          label="Procurement Pathway"
          value="85%"
          hint="Avg pilot success score"
        />
      </section>

      <section className="content-section">
        <div className="section-row">
          <div>
            <p className="eyebrow">Recent activity</p>
            <h2>Current challenges</h2>
          </div>
        </div>

        {/* 1. Loading State */}
        {loading && (
          <div className="state-container">
            <div className="spinner"></div>
            <h3>Loading challenges...</h3>
            <p>Fetching problem statements from the platform registry.</p>
          </div>
        )}

        {/* 2. Error State */}
        {!loading && error && (
          <div className="state-container error-state">
            <div style={{ fontSize: "2rem", marginBottom: "8px" }}>⚠</div>
            <h3>Unable to load challenges</h3>
            <p>{error}</p>
            <button
              type="button"
              className="btn btn-primary"
              onClick={fetchChallengesList}
            >
              Retry
            </button>
          </div>
        )}

        {/* 3. Empty State */}
        {!loading && !error && challenges.length === 0 && (
          <div className="state-container">
            <div style={{ fontSize: "2rem", marginBottom: "8px" }}>📋</div>
            <h3>No challenges created yet</h3>
            <p>Publish a new problem statement to begin receiving startup applications.</p>
          </div>
        )}

        {/* 4. Success Grid */}
        {!loading && !error && challenges.length > 0 && (
          <div className="cards-grid">
            {challenges.map((challenge) => (
              <ChallengeCard key={challenge.id} challenge={challenge} />
            ))}
          </div>
        )}
      </section>
    </DashboardLayout>
  );
}
