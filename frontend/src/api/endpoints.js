import { get, post } from "./client";
import { challenges as mockChallenges, startups as mockStartups, users as mockUsers } from "../data/mockData";

const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

/**
 * Authentication Endpoints
 */
export const login = async (email, password) => {
  if (USE_MOCK) {
    // Artificial small delay for realistic UX
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
 * Challenges Endpoints
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

export const getChallengeById = async (id) => {
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

/**
 * Startups Endpoints
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
        (s) => s.technologies?.some((t) => t.toLowerCase() === params.tech.toLowerCase())
      );
    }
    return filtered;
  }
  return get("/startups", params);
};
