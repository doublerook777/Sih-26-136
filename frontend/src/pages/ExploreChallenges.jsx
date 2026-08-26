import DashboardLayout from "../components/DashboardLayout";
import ChallengeCard from "../components/ChallengeCard";
import { challenges } from "../data/mockData";

export default function ExploreChallenges() {
  return (
    <DashboardLayout
      role="startup"
      title="Explore Challenges"
      subtitle="Browse public-sector pilots matched to your capabilities."
    >
      <section className="filter-bar">
        <input placeholder="Search challenges..." />
        <select><option>All sectors</option><option>Water Management</option><option>Healthcare</option></select>
        <select><option>Any budget</option><option>Under ₹5 lakh</option><option>₹5–10 lakh</option></select>
        <button className="btn btn-soft">Filter</button>
      </section>

      <div className="cards-grid">
        {challenges.map((challenge) => (
          <ChallengeCard key={challenge.id} challenge={challenge} startupView />
        ))}
      </div>
    </DashboardLayout>
  );
}
