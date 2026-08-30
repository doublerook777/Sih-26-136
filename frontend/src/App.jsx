import { Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";

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
    <AuthProvider>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />

        {/* Government Portal */}
        <Route
          path="/government"
          element={
            <ProtectedRoute allowedRoles={["government", "admin"]}>
              <GovernmentDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/government/create"
          element={
            <ProtectedRoute allowedRoles={["government", "admin"]}>
              <CreateChallenge />
            </ProtectedRoute>
          }
        />
        <Route
          path="/government/recommendations"
          element={
            <ProtectedRoute allowedRoles={["government", "admin"]}>
              <Recommendations />
            </ProtectedRoute>
          }
        />
        <Route
          path="/government/pilot"
          element={
            <ProtectedRoute allowedRoles={["government", "admin"]}>
              <PilotDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/government/challenges"
          element={
            <ProtectedRoute allowedRoles={["government", "admin"]}>
              <Placeholder role="government" title="Challenges" />
            </ProtectedRoute>
          }
        />

        {/* Startup Portal */}
        <Route
          path="/startup"
          element={
            <ProtectedRoute allowedRoles={["startup"]}>
              <StartupDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/startup/explore"
          element={
            <ProtectedRoute allowedRoles={["startup"]}>
              <ExploreChallenges />
            </ProtectedRoute>
          }
        />
        <Route
          path="/startup/applications"
          element={
            <ProtectedRoute allowedRoles={["startup"]}>
              <Placeholder role="startup" title="My Applications" />
            </ProtectedRoute>
          }
        />

        {/* Evaluator Portal */}
        <Route
          path="/evaluator"
          element={
            <ProtectedRoute allowedRoles={["expert", "validator", "admin"]}>
              <EvaluatorDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/evaluator/reviews"
          element={
            <ProtectedRoute allowedRoles={["expert", "validator", "admin"]}>
              <Placeholder role="evaluator" title="Pending Reviews" />
            </ProtectedRoute>
          }
        />
      <Route path="*" element={<div style={{ padding: "40px", textAlign: "center" }}>Page not found</div>} />
      </Routes>
    </AuthProvider>
  );
}
