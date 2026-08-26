import { Routes, Route } from "react-router-dom";

import Landing from "./pages/Landing";
import Login from "./pages/Login";
import GovernmentDashboard from "./pages/GovernmentDashboard";
import CreateChallenge from "./pages/CreateChallenge";
import Recommendations from "./pages/Recommendations";
import PilotDashboard from "./pages/PilotDashboard";
import StartupDashboard from "./pages/StartupDashboard";
import ExploreChallenges from "./pages/ExploreChallenges";
import EvaluatorDashboard from "./pages/EvaluatorDashboard";
import Placeholder from "./pages/Placeholder";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />

      <Route path="/government" element={<GovernmentDashboard />} />
      <Route path="/government/create" element={<CreateChallenge />} />
      <Route path="/government/recommendations" element={<Recommendations />} />
      <Route path="/government/pilot" element={<PilotDashboard />} />
      <Route path="/government/challenges" element={<Placeholder role="government" title="Challenges" />} />

      <Route path="/startup" element={<StartupDashboard />} />
      <Route path="/startup/explore" element={<ExploreChallenges />} />
      <Route path="/startup/applications" element={<Placeholder role="startup" title="My Applications" />} />

      <Route path="/evaluator" element={<EvaluatorDashboard />} />
      <Route path="/evaluator/reviews" element={<Placeholder role="evaluator" title="Pending Reviews" />} />
    </Routes>
  );
}
