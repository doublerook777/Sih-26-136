import { get, post, BASE_URL } from "./client";
import {
  challenges as initialMockChallenges,
  startups as mockStartups,
  users as mockUsers,
  rubrics as mockRubrics,
  mockApplicationsList,
} from "../data/mockData";

const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

// Mutable in-memory store for mock mode
let mockChallenges = [...initialMockChallenges];
let mockApplications = [...mockApplicationsList];
let mockEvaluations = [];

const MOCK_STARTUP_NAMES = [
  "AquaSense Systems", "PipeAI Technologies", "HydroTrack Telemetry",
  "BlueGrid Innovations", "CivicFlow Labs", "JalDrishti Analytics",
  "LeakLens Technologies", "UrbanPulse Systems", "FlowGuard Labs",
  "AquaMetric Works", "District Digital Works", "SensorSpring Labs",
  "Waterline Intelligence", "PublicGrid Systems", "CivicNode Technologies",
  "InfraSight Labs", "FieldSignal Systems", "Municipal Metrics",
  "OpenUtility Labs", "ImpactMesh Technologies",
];

function buildMockDiscovery(challengeId) {
  const existing = mockApplications.filter((item) => Number(item.challenge_id) === Number(challengeId));
  if (existing.length >= 20) return existing;

  const challenge = mockChallenges.find((item) => item.id === Number(challengeId));
  const baseId = mockApplications.reduce((max, item) => Math.max(max, item.application_id || 0), 0) + 1;
  const generated = MOCK_STARTUP_NAMES.map((name, index) => {
    const source = mockStartups[index % mockStartups.length] || {};
    const eligible = index < 14;
    const score = eligible ? Number((94 - index * 2.15).toFixed(1)) : 0;
    const failedGate = index % 3 === 0 ? "required_certification" : index % 3 === 1 ? "min_experience_years" : "technology_overlap";
    const eligibility_report = {
      registered_startup: { passed: true, note: source.dpiit_number || `DIPP${48000 + index}` },
      required_certification: { passed: eligible || failedGate !== "required_certification", note: eligible || failedGate !== "required_certification" ? "Required certification present" : "Required certification is missing" },
      min_experience_years: { passed: eligible || failedGate !== "min_experience_years", note: eligible || failedGate !== "min_experience_years" ? "Experience threshold met" : "1 year experience, needs 2" },
      technology_overlap: { passed: eligible || failedGate !== "technology_overlap", note: eligible || failedGate !== "technology_overlap" ? "3 required technologies matched" : "No required technology matched" },
      budget_within_range: { passed: true, note: "Quote is within the published budget" },
      security_baseline: { passed: true, note: "Security baseline self-declared" },
    };
    return {
      application_id: baseId + index,
      challenge_id: Number(challengeId),
      challenge_title: challenge?.title || "Procurement Challenge",
      startup_id: 100 + index,
      startup_name: name,
      eligible,
      eligibility_report,
      match_score: score,
      match_breakdown: {
        technology_match: eligible ? Math.max(52, 96 - index * 2) : 0,
        domain_experience: eligible ? Math.max(48, 91 - index * 2) : 0,
        past_projects: eligible ? Math.max(45, 87 - index * 2) : 0,
        eligibility: eligible ? 100 : 0,
        cost_fit: eligible ? Math.max(58, 89 - index) : 0,
        scalability: eligible ? Math.max(55, 92 - index * 2) : 0,
      },
      rubric_snapshot: { technology_match: 30, domain_experience: 20, past_projects: 15, eligibility: 15, cost_fit: 10, scalability: 10 },
      explanation: eligible
        ? `${name} is ranked for relevant technology capability, public-sector delivery readiness, and a quote aligned with the pilot budget.`
        : `${name} remains visible for auditability but cannot advance until the failed eligibility gate is resolved.`,
      status: "screened",
    };
  });
  mockApplications = [...mockApplications.filter((item) => Number(item.challenge_id) !== Number(challengeId)), ...generated];
  return generated;
}

/**
 * Base URL for document preview and assets
 */
export const BASE = BASE_URL;

/**
 * Authentication Endpoints
 */
export const login = async (email, password) => {
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, 150));
    const user = mockUsers.find(
      (u) => u.email.toLowerCase() === (email || "").trim().toLowerCase()
    );
    if (!user || password !== "demo1234") {
      const err = new Error("invalid email or password");
      err.detail = "invalid email or password";
      err.status = 401;
      throw err;
    }
    return {
      token: `mock-jwt-${user.id}-${Date.now()}`,
      user: {
        id: user.id,
        name: user.name,
        email: user.email,
        role: user.role,
        department: user.department,
        district: user.district,
      },
    };
  }
  return post("/auth/login", { email, password });
};

export const getMe = async () => {
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, 50));
    const rawUser = localStorage.getItem("user");
    if (rawUser) {
      try {
        return JSON.parse(rawUser);
      } catch {
        // Fall back to default user
      }
    }
    return mockUsers[0];
  }
  return get("/auth/me");
};

/**
 * Rubrics Endpoints (Section 2)
 */
export const getRubrics = async (kind) => {
  const kindVal = typeof kind === "object" && kind !== null ? kind.kind : kind;
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, 100));
    return kindVal ? mockRubrics.filter((r) => r.kind === kindVal) : mockRubrics;
  }
  try {
    return await get("/rubrics", kindVal ? { kind: kindVal } : undefined);
  } catch (err) {
    if (err.status === 404) {
      return kindVal ? mockRubrics.filter((r) => r.kind === kindVal) : mockRubrics;
    }
    throw err;
  }
};

export const getRubric = async (id) => {
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, 80));
    const rubric = mockRubrics.find((r) => r.id === Number(id));
    if (!rubric) {
      const err = new Error("Rubric not found");
      err.detail = "Rubric not found";
      err.status = 404;
      throw err;
    }
    return rubric;
  }
  return get(`/rubrics/${id}`);
};

/**
 * Challenges Endpoints (Section 3)
 */
export const getChallenges = async (params = {}) => {
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, 150));
    let filtered = [...mockChallenges];
    if (params.sector) {
      filtered = filtered.filter(
        (c) => c.sector?.toLowerCase() === params.sector.toLowerCase()
      );
    }
    if (params.status) {
      filtered = filtered.filter(
        (c) => c.status?.toLowerCase() === params.status.toLowerCase()
      );
    }
    return filtered;
  }
  return get("/challenges", params);
};

export const getChallenge = async (id) => {
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, 100));
    const item = mockChallenges.find((c) => c.id === Number(id));
    if (!item) {
      const err = new Error("Challenge not found");
      err.detail = "Challenge not found";
      err.status = 404;
      throw err;
    }
    return item;
  }
  return get(`/challenges/${id}`);
};

export const getChallengeById = getChallenge;

export const discoverStartups = async (challengeId) => {
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, 900));
    return buildMockDiscovery(challengeId);
  }
  return post(`/challenges/${challengeId}/discover`);
};

export const getChallengeApplications = async (challengeId) => {
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, 120));
    return mockApplications.filter((item) => Number(item.challenge_id) === Number(challengeId));
  }
  return get(`/challenges/${challengeId}/applications`);
};

export const shortlistApplication = async (applicationId) => {
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, 180));
    const application = mockApplications.find((item) => item.application_id === Number(applicationId));
    if (!application) throw Object.assign(new Error("Application not found"), { detail: "Application not found", status: 404 });
    application.status = "shortlisted";
    return { application_id: application.application_id, status: application.status };
  }
  return post(`/applications/${applicationId}/shortlist`);
};

export const selectApplication = async (applicationId) => {
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, 180));
    const selected = mockApplications.find((item) => item.application_id === Number(applicationId));
    if (!selected) throw Object.assign(new Error("Application not found"), { detail: "Application not found", status: 404 });
    mockApplications.forEach((item) => {
      if (item.challenge_id === selected.challenge_id) item.status = item.application_id === selected.application_id ? "selected" : "rejected";
    });
    const challenge = mockChallenges.find((item) => item.id === selected.challenge_id);
    if (challenge) challenge.status = "selected";
    return { application_id: selected.application_id, status: "selected", challenge_status: "selected" };
  }
  return post(`/applications/${applicationId}/select`);
};

export const createChallenge = async (body) => {
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, 200));
    const newId = mockChallenges.length > 0 ? Math.max(...mockChallenges.map((c) => c.id)) + 1 : 1;
    const newChallenge = {
      id: newId,
      title: body.title || "Untitled Challenge",
      raw_description: body.raw_description || "",
      department: body.department || "Municipal Administration",
      district: body.district || "District A",
      sector: body.sector || "water",
      budget: Number(body.budget) || 1000000,
      timeline_days: Number(body.timeline_days) || 90,
      deadline: body.deadline || new Date(Date.now() + 30 * 86400000).toISOString().split("T")[0],
      status: body.status || "draft",
      required_tech: Array.isArray(body.required_tech) ? body.required_tech : ["iot", "analytics"],
      application_count: 0,
      created_at: new Date().toISOString(),
      match_rubric_id: body.match_rubric_id || 1,
      evaluation_rubric_id: body.evaluation_rubric_id || 5,
      statement: body.statement || {},
      eligibility_rules: body.eligibility_rules || {
        registered_startup: true,
        required_certification: "ISO 9001:2015",
        min_experience_years: 1,
        min_technology_overlap: 1,
        max_quote: Number(body.budget) || 1000000,
        security_baseline: true,
      },
      kpi_targets: body.kpi_targets || [
        {
          name: "Core efficiency metric",
          unit: "%",
          baseline: 30,
          target: 20,
          category: "impact",
          direction: "lower_is_better",
        },
      ],
    };
    mockChallenges = [newChallenge, ...mockChallenges];
    return newChallenge;
  }
  return post("/challenges", body);
};

export const publishChallenge = async (id) => {
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, 150));
    const challenge = mockChallenges.find((c) => c.id === Number(id));
    if (challenge) {
      challenge.status = "open";
    }
    return challenge;
  }
  return post(`/challenges/${id}/publish`);
};

/**
 * AI Statement Generator Endpoint (Section 3)
 */
export const generateStatement = async (body) => {
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, 1200));
    const sectorFormatted = (body.sector || "water").replace("_", " ");
    const formattedBudget = typeof body.budget === "number"
      ? `INR ${body.budget.toLocaleString("en-IN")}`
      : `INR ${body.budget || "10,00,000"}`;

    return {
      problem: `${body.title || "Challenge"}: ${body.raw_description || "Public sector operational bottleneck"}`,
      background: `${body.department || "Municipal Department"} in ${body.district || "District A"} requires an outcome-focused innovation pilot in the ${sectorFormatted} sector.`,
      existing_system: "Current service delivery relies on manual or periodic monitoring.",
      identified_gap: "The current process lacks timely, measurable operational insight.",
      desired_solution: "A scalable startup-led solution with measurable pilot outcomes.",
      target_users: `Officers and field teams of ${body.department || "the department"}, plus affected citizens.`,
      technical_requirements: "Interoperable, secure technology with auditable data outputs.",
      constraints: `The solution must remain within the ${formattedBudget} pilot allocation and integrate safely with existing operations.`,
      budget: `${formattedBudget}, released against verified milestones.`,
      timeline: `${body.timeline_days || 90} days from pilot commencement.`,
      expected_outcomes: "Measurable improvement in service quality, efficiency, and accountability.",
      kpis: "Baseline, target, and achieved pilot metrics will be independently verified.",
      eligibility_requirements: "Eligible startups must meet the challenge's published requirements.",
      data_requirements: "Data must be securely stored, exportable, and available for audit.",
      security_requirements: "Role-based access, encrypted data handling, and security review are required.",
      generated_by: "template",
    };
  }
  return post("/ai/generate-statement", body);
};

/**
 * Applications Endpoints (Section 5)
 */
export const applyToChallenge = async (body) => {
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, 200));
    const challengeId = Number(body.challenge_id);
    const existing = mockApplications.find((a) => Number(a.challenge_id) === challengeId);
    if (existing) {
      const err = new Error("Startup has already applied to this challenge");
      err.detail = "Startup has already applied to this challenge";
      err.status = 400;
      throw err;
    }

    const matchedChallenge = mockChallenges.find((c) => c.id === challengeId);
    const newApplication = {
      application_id: mockApplications.length > 0 ? Math.max(...mockApplications.map((a) => a.application_id || 0)) + 1 : 1,
      challenge_id: challengeId,
      challenge_title: matchedChallenge?.title || "Pilot Challenge",
      challenge_sector: matchedChallenge?.sector || "water",
      startup_id: 3,
      startup_name: "AquaSense",
      quote: Number(body.quote),
      pitch: body.pitch,
      eligible: true,
      eligibility_report: {
        registered_startup: { passed: true, note: "DIPP12345" },
        required_certification: { passed: true, note: "ISO 9001:2015 present" },
        min_experience_years: { passed: true, note: "3 years active" },
        technology_overlap: { passed: true, note: "Relevant capabilities verified" },
        budget_within_range: { passed: true, note: "Quote within budget" },
        security_baseline: { passed: true, note: "Self-declared" },
      },
      match_score: 91.2,
      match_breakdown: {
        technology_match: 94.0,
        domain_experience: 90.0,
        past_projects: 85.0,
        eligibility: 100.0,
        cost_fit: 80.0,
        scalability: 92.0,
      },
      rubric_snapshot: {
        technology_match: 30,
        domain_experience: 20,
        past_projects: 15,
        eligibility: 15,
        cost_fit: 10,
        scalability: 10,
      },
      explanation: "Recommended because the startup has domain expertise, municipal infrastructure experience, and strong past performance.",
      status: "applied",
      applied_at: new Date().toISOString(),
    };

    mockApplications = [newApplication, ...mockApplications];
    if (matchedChallenge) {
      matchedChallenge.application_count = (matchedChallenge.application_count || 0) + 1;
    }
    return newApplication;
  }
  return post("/applications", body);
};

export const getMyApplications = async () => {
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, 150));
    return [...mockApplications];
  }
  try {
    return await get("/applications");
  } catch (err) {
    if (err.status === 404 || err.status === 405) {
      return [...mockApplications];
    }
    throw err;
  }
};

export const getApplication = async (applicationId) => {
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, 80));
    const item = mockApplications.find((application) => application.application_id === Number(applicationId));
    if (!item) throw Object.assign(new Error("Application not found"), { detail: "Application not found", status: 404 });
    return item;
  }
  return get(`/applications/${applicationId}`);
};

export const submitEvaluation = async (body) => {
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, 650));
    const rubric = mockRubrics.find((item) => item.kind === "evaluation" && item.is_default) || mockRubrics.find((item) => item.kind === "evaluation");
    const weighted_total = Number(rubric.criteria.reduce((total, criterion) => total + body.scores[criterion.key] * criterion.weight / 100, 0).toFixed(1));
    const record = {
      id: mockEvaluations.length + 1,
      application_id: Number(body.application_id),
      expert_id: mockEvaluations.length + 4,
      expert_name: `Demo Expert ${mockEvaluations.length + 1}`,
      scores: body.scores,
      weighted_total,
      rubric_snapshot: rubric.weights,
      comments: body.comments,
      submitted_at: new Date().toISOString(),
    };
    mockEvaluations.push(record);
    return record;
  }
  return post("/evaluations", body);
};

export const getEvaluations = async (applicationId) => {
  if (USE_MOCK) {
    const evaluations = mockEvaluations.filter((item) => item.application_id === Number(applicationId));
    const average_total = evaluations.length ? Number((evaluations.reduce((sum, item) => sum + item.weighted_total, 0) / evaluations.length).toFixed(1)) : 0;
    return { application_id: Number(applicationId), average_total, evaluation_count: evaluations.length, evaluations };
  }
  return get("/evaluations", { application_id: applicationId });
};

/**
 * Document URL Helper (Section 11)
 * Returns plain URL string for <iframe> src, not JSON.
 */
export const documentUrl = (docType, id) => `${BASE}/documents/${docType}/${id}`;

/**
 * Startups Endpoints (Section 4)
 */
export const getStartups = async (params = {}) => {
  if (USE_MOCK) {
    await new Promise((resolve) => setTimeout(resolve, 150));
    let filtered = [...mockStartups];
    if (params.sector) {
      filtered = filtered.filter(
        (s) => s.sector?.toLowerCase() === params.sector.toLowerCase()
      );
    }
    if (params.tech) {
      filtered = filtered.filter(
        (s) => s.tech_tags?.some((t) => t.toLowerCase() === params.tech.toLowerCase())
      );
    }
    return filtered;
  }
  return get("/startups", params);
};
