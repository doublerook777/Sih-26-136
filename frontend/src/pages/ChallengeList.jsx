import { useState, useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
import DashboardLayout from "../components/DashboardLayout";
import ChallengeCard from "../components/ChallengeCard";
import { getChallenges } from "../api/endpoints";

export default function ChallengeList() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialSector = searchParams.get("sector") || "all";
  const initialStatus = searchParams.get("status") || "all";

  const [challenges, setChallenges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [sectorFilter, setSectorFilter] = useState(initialSector);
  const [statusFilter, setStatusFilter] = useState(initialStatus);

  const fetchChallengesList = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {};
      if (sectorFilter !== "all") params.sector = sectorFilter;
      if (statusFilter !== "all") params.status = statusFilter;

      const data = await getChallenges(params);
      setChallenges(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.detail || err.message || "Failed to load challenges");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Sync URL search params
    const nextParams = {};
    if (sectorFilter !== "all") nextParams.sector = sectorFilter;
    if (statusFilter !== "all") nextParams.status = statusFilter;
    setSearchParams(nextParams, { replace: true });

    fetchChallengesList();
  }, [sectorFilter, statusFilter]);

  return (
    <DashboardLayout
      role="government"
      title="Government Challenges"
      subtitle="Manage public sector innovation challenges, monitor applications, and track pilot progress."
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
        <section className="filter-bar" style={{ margin: 0, flex: 1, marginRight: "16px" }}>
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
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="all">All statuses</option>
            <option value="draft">Draft</option>
            <option value="open">Open</option>
            <option value="screening">Screening</option>
            <option value="evaluating">Evaluating</option>
            <option value="selected">Selected</option>
            <option value="piloting">Piloting</option>
            <option value="closed">Closed</option>
          </select>

          <button
            type="button"
            className="btn btn-soft"
            onClick={fetchChallengesList}
          >
            Refresh
          </button>
        </section>

        <Link to="/government/create" className="btn btn-primary">
          + New Challenge
        </Link>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="state-container">
          <div className="spinner"></div>
          <h3>Loading challenges...</h3>
          <p>Retrieving platform innovation challenges.</p>
        </div>
      )}

      {/* Error State */}
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

      {/* Empty State */}
      {!loading && !error && challenges.length === 0 && (
        <div className="state-container">
          <div style={{ fontSize: "2rem", marginBottom: "8px" }}>📋</div>
          <h3>No challenges match criteria</h3>
          <p>Try switching filter options or create a new public sector challenge.</p>
          <Link to="/government/create" className="btn btn-primary">
            Create Challenge
          </Link>
        </div>
      )}

      {/* Grid of Cards */}
      {!loading && !error && challenges.length > 0 && (
        <div className="cards-grid">
          {challenges.map((c) => (
            <ChallengeCard key={c.id} challenge={c} />
          ))}
        </div>
      )}
    </DashboardLayout>
  );
}
