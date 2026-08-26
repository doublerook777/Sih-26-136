import DashboardLayout from "../components/DashboardLayout";
import StatCard from "../components/StatCard";
import ChallengeCard from "../components/ChallengeCard";
import { challenges } from "../data/mockData";

export default function GovernmentDashboard() {
  return (
    <DashboardLayout
      role="government"
      title="Government Dashboard"
      subtitle="Track challenges, applications, pilots and outcomes from one place."
    >
      <section className="stats-cards">
        <StatCard icon="◎" label="Active Challenges" value="06" hint="+2 this month" />
        <StatCard icon="↗" label="Applications" value="42" hint="12 awaiting review" />
        <StatCard icon="◉" label="Active Pilots" value="03" hint="All on track" />
        <StatCard icon="✓" label="Successful Pilots" value="08" hint="67% scale rate" />
      </section>

      <section className="content-section">
        <div className="section-row">
          <div>
            <p className="eyebrow">Recent activity</p>
            <h2>Current challenges</h2>
          </div>
        </div>

        <div className="cards-grid">
          {challenges.map((challenge) => (
            <ChallengeCard key={challenge.id} challenge={challenge} />
          ))}
        </div>
      </section>
    </DashboardLayout>
  );
}
