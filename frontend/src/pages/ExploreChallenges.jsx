import { useState, useEffect } from "react";
import DashboardLayout from "../components/DashboardLayout";
import ChallengeCard from "../components/ChallengeCard";
import ApplyModal from "../components/ApplyModal";
import { getChallenges, getMyApplications } from "../api/endpoints";

export default function ExploreChallenges() {
  const [challenges, setChallenges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [searchTerm, setSearchTerm] = useState("");
  const [sectorFilter, setSectorFilter] = useState("all");
  const [budgetFilter, setBudgetFilter] = useState("all");

  // Apply modal state
  const [selectedChallengeForApply, setSelectedChallengeForApply] = useState(null);
  const [isApplyModalOpen, setIsApplyModalOpen] = useState(false);
  const [appliedChallengeIds, setAppliedChallengeIds] = useState(new Set());

  const fetchChallengesList = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {};
      if (sectorFilter !== "all") {
        params.sector = sectorFilter;
      }
      const data = await getChallenges(params);
      setChallenges(Array.isArray(data) ? data : []);

      // Also fetch user's applications to highlight already applied challenges
      try {
        const apps = await getMyApplications();
        if (Array.isArray(apps)) {
          setAppliedChallengeIds(new Set(apps.map((a) => Number(a.challenge_id))));
        }
      } catch {
        // Non-blocking
      }
    } catch (err) {
      setError(err.detail || err.message || "Failed to load challenges");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchChallengesList();
  }, [sectorFilter]);

  // Client-side filtering for search keywords and budget range
  const filteredChallenges = challenges.filter((c) => {
    const matchesSearch =
      !searchTerm ||
      c.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.department?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.raw_description?.toLowerCase().includes(searchTerm.toLowerCase());

    let matchesBudget = true;
    if (budgetFilter === "under_5l") {
      matchesBudget = c.budget && c.budget < 500000;
    } else if (budgetFilter === "5l_10l") {
      matchesBudget = c.budget && c.budget >= 500000 && c.budget <= 1000000;
    } else if (budgetFilter === "above_10l") {
      matchesBudget = c.budget && c.budget > 1000000;
    }

    return matchesSearch && matchesBudget;
  });

  const handleOpenApply = (challenge) => {
    setSelectedChallengeForApply(challenge);
    setIsApplyModalOpen(true);
  };

  const handleApplySuccess = (newApp) => {
    if (newApp && newApp.challenge_id) {
      setAppliedChallengeIds((prev) => new Set([...prev, Number(newApp.challenge_id)]));
    }
  };

  return (
    <DashboardLayout
      role="startup"
      title="Explore Challenges"
      subtitle="Browse public-sector pilots matched to your capabilities."
    >
      <section className="filter-bar">
        <input
          type="text"
          placeholder="Search challenges by keyword..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <select
          value={sectorFilter}
          onChange={(e) => setSectorFilter(e.target.value)}
        >
          <option value="all">All sectors</option>
          <option value="water">Water</option>
          <option value="healthcare">Healthcare</option>
          <option value="waste">Waste Management</option>
          <option value="transport">Transport</option>
        </select>
        <select
          value={budgetFilter}
          onChange={(e) => setBudgetFilter(e.target.value)}
        >
          <option value="all">Any budget</option>
          <option value="under_5l">Under ₹5 lakh</option>
          <option value="5l_10l">₹5–10 lakh</option>
          <option value="above_10l">Above ₹10 lakh</option>
        </select>
        <button
          type="button"
          className="btn btn-soft"
          onClick={fetchChallengesList}
        >
          Refresh
        </button>
      </section>

      {/* 1. Loading State */}
      {loading && (
        <div className="state-container">
          <div className="spinner"></div>
          <h3>Loading challenges...</h3>
          <p>Finding public innovation opportunities for startups.</p>
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
      {!loading && !error && filteredChallenges.length === 0 && (
        <div className="state-container">
          <div style={{ fontSize: "2rem", marginBottom: "8px" }}>🔍</div>
          <h3>No matching challenges found</h3>
          <p>Try adjusting your search criteria or selecting a different sector.</p>
        </div>
      )}

      {/* 4. Results Grid */}
      {!loading && !error && filteredChallenges.length > 0 && (
        <div className="cards-grid">
          {filteredChallenges.map((challenge) => (
            <ChallengeCard
              key={challenge.id}
              challenge={challenge}
              startupView
              onApply={handleOpenApply}
              hasApplied={appliedChallengeIds.has(Number(challenge.id))}
            />
          ))}
        </div>
      )}

      {/* Apply Modal */}
      {selectedChallengeForApply && (
        <ApplyModal
          challenge={selectedChallengeForApply}
          isOpen={isApplyModalOpen}
          onClose={() => {
            setIsApplyModalOpen(false);
            setSelectedChallengeForApply(null);
          }}
          onSuccess={handleApplySuccess}
        />
      )}
    </DashboardLayout>
  );
}
