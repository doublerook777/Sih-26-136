import DashboardLayout from "../components/DashboardLayout";
import StatCard from "../components/StatCard";
import ChallengeCard from "../components/ChallengeCard";
import { challenges } from "../data/mockData";

export default function StartupDashboard() {
  return (
    <DashboardLayout
      role="startup"
      title="Startup Dashboard"
      subtitle="Discover relevant public-sector opportunities and track your applications."
    >
      <section className="profile-completion">
        <div>
          <p className="eyebrow">AquaSense</p>
          <h2>Your profile is 85% complete</h2>
          <p className="muted">Complete deployment history to improve AI matching quality.</p>
        </div>
        <div className="profile-meter">
          <span style={{ width: "85%" }}></span>
        </div>
      </section>

      <section className="stats-cards three">
        <StatCard icon="↗" label="Applications" value="04" hint="2 active" />
        <StatCard icon="★" label="Shortlisted" value="02" hint="50% shortlist rate" />
        <StatCard icon="◉" label="Active Pilots" value="01" hint="Day 64 of 90" />
      </section>

      <section className="content-section">
        <div className="section-row">
          <div>
            <p className="eyebrow">AI matched</p>
            <h2>Recommended challenges</h2>
          </div>
        </div>

        <div className="cards-grid">
          {challenges.map((challenge) => (
            <ChallengeCard key={challenge.id} challenge={challenge} startupView />
          ))}
        </div>
      </section>
    </DashboardLayout>
  );
}
