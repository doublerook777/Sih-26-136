export const startups = [
  {
    id: 1,
    name: "AquaSense",
    sector: "Water Management",
    tech: ["IoT", "Sensors", "AI"],
    match: 94,
    dpiit: true,
    prototype: true,
    description:
      "Real-time water infrastructure monitoring using pressure sensors and anomaly detection.",
    weakness: "No large city-wide deployment yet."
  },
  {
    id: 2,
    name: "PipeAI",
    sector: "Smart Infrastructure",
    tech: ["Machine Learning", "Analytics", "IoT"],
    match: 87,
    dpiit: true,
    prototype: true,
    description:
      "Predictive maintenance platform for pipelines and municipal infrastructure.",
    weakness: "Limited water-utility specific case studies."
  },
  {
    id: 3,
    name: "HydroTrack",
    sector: "Water Management",
    tech: ["Sensors", "Telemetry", "Dashboards"],
    match: 81,
    dpiit: true,
    prototype: false,
    description:
      "Water flow monitoring and infrastructure telemetry for public utilities.",
    weakness: "Prototype still under controlled testing."
  }
];

export const challenges = [
  {
    id: 1,
    title: "Smart Municipal Water Leak Detection",
    department: "Urban Water Authority",
    sector: "Water Management",
    budget: "₹5,00,000",
    duration: "90 days",
    deadline: "20 Sep 2026",
    applications: 12,
    status: "Active",
    match: 94
  },
  {
    id: 2,
    title: "AI-Based Hospital Queue Optimisation",
    department: "Department of Health",
    sector: "Healthcare",
    budget: "₹7,50,000",
    duration: "120 days",
    deadline: "28 Sep 2026",
    applications: 8,
    status: "Evaluation",
    match: 76
  },
  {
    id: 3,
    title: "Smart Waste Collection Optimisation",
    department: "Municipal Corporation",
    sector: "Waste Management",
    budget: "₹6,00,000",
    duration: "90 days",
    deadline: "5 Oct 2026",
    applications: 17,
    status: "Active",
    match: 82
  }
];

export const evaluations = [
  { startup: "AquaSense", challenge: "Water Leak Detection", status: "Pending" },
  { startup: "PipeAI", challenge: "Water Leak Detection", status: "Pending" },
  { startup: "MedQueue", challenge: "Hospital Queue Optimisation", status: "Completed" }
];
