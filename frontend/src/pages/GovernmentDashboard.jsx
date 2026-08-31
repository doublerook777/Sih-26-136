import { useEffect, useState } from "react";
import DashboardLayout from "../components/DashboardLayout";
import StatCard from "../components/StatCard";
import ChallengeCard from "../components/ChallengeCard";

const API_URL = "http://127.0.0.1:8000";

export default function GovernmentDashboard() {
  const [challenges, setChallenges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API_URL}/challenges`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to load challenges");
        }
        return response.json();
      })
      .then((data) => {
        setChallenges(data);
      })
      .catch((err) => {
        console.error(err);
        setError("Could not connect to the backend.");
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

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
          value={challenges.length.toString().padStart(2, "0")}
          hint="Currently open"
        />

        <StatCard
          icon="↗"
          label="Applications"
          value="20"
          hint="Screened applications"
        />

        <StatCard
          icon="◉"
          label="Active Pilots"
          value="03"
          hint="All on track"
        />

        <StatCard
          icon="✓"
          label="Successful Pilots"
          value="08"
          hint="67% scale rate"
        />
      </section>

      <section className="content-section">
        <div className="section-row">
          <div>
            <p className="eyebrow">Recent activity</p>
            <h2>Current challenges</h2>
          </div>
        </div>

        {loading && <p>Loading challenges...</p>}

        {error && <p>{error}</p>}

        {!loading && !error && (
          <div className="cards-grid">
            {challenges.map((challenge) => (
              <ChallengeCard
                key={challenge.id}
                challenge={challenge}
              />
            ))}
          </div>
        )}
      </section>
    </DashboardLayout>
  );
}
