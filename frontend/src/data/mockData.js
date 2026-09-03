export const users = [
  {
    id: 1,
    name: "R Kumar",
    email: "officer@water.gov.in",
    role: "government",
    department: "Urban Water Supply",
    district: "District A"
  },
  {
    id: 2,
    name: "Platform Admin",
    email: "admin@procura.gov.in",
    role: "admin",
    department: null,
    district: null
  },
  {
    id: 3,
    name: "AquaSense",
    email: "founder@aquasense.in",
    role: "startup",
    department: null,
    district: null
  },
  {
    id: 4,
    name: "Dr S Rao",
    email: "expert1@procura.gov.in",
    role: "expert",
    department: null,
    district: null
  },
  {
    id: 5,
    name: "Prof M Iyer",
    email: "expert2@procura.gov.in",
    role: "expert",
    department: null,
    district: null
  },
  {
    id: 6,
    name: "Dr A Banerjee",
    email: "expert3@procura.gov.in",
    role: "expert",
    department: null,
    district: null
  },
  {
    id: 7,
    name: "N Sharma",
    email: "validator@procura.gov.in",
    role: "validator",
    department: null,
    district: null
  }
];

export const challenges = [
  {
    id: 1,
    title: "Reduce Municipal Water Leakage in Distribution Networks",
    department: "Urban Water Supply",
    district: "District A",
    sector: "water",
    budget: 1000000,
    timeline_days: 90,
    deadline: "2026-09-15",
    status: "open",
    required_tech: ["iot", "sensors", "analytics", "gis"],
    application_count: 12,
    created_at: "2026-08-27T09:00:00Z",
    created_by: 1,
    match_rubric_id: 1,
    evaluation_rubric_id: 5,
    eligibility_rules: {
      registered_startup: true,
      required_certification: "ISO 9001:2015",
      min_experience_years: 2,
      min_technology_overlap: 1,
      max_quote: 1000000,
      security_baseline: true
    },
    kpi_targets: [
      { name: "Water wastage", unit: "%", baseline: 30, target: 20, category: "impact", direction: "lower_is_better" },
      { name: "Leak detection time", unit: "hours", baseline: 72, target: 6, category: "technical", direction: "lower_is_better" }
    ],
    statement: {
      problem: "High non-revenue water loss caused by undetected pipeline leakages across municipal distribution zones.",
      background: "Aging underground water pipeline infrastructure in District A suffers from recurring pressure drops and physical fractures.",
      existing_system: "Manual acoustic stick inspections conducted reactively after citizen complaints or surface flooding.",
      identified_gap: "Absence of real-time continuous telemetry and predictive acoustic anomaly monitoring.",
      desired_solution: "Deploy IoT sensor nodes and AI-driven pressure and acoustic analytics to pinpoint leaks within 6 hours.",
      target_users: "Municipal water supply engineers, field maintenance crews, and district administration.",
      technical_requirements: "Battery-powered acoustic/pressure sensors, cellular/LoRaWAN telemetry, GIS map dashboard, REST APIs.",
      constraints: "Sensors must fit existing valve chambers without interrupting municipal water supply during deployment.",
      budget: "₹10,00,000 all-inclusive for hardware, cloud infrastructure, and 90-day pilot validation.",
      timeline: "90 calendar days across 4 phased milestone deliveries.",
      expected_outcomes: "Reduction in non-revenue water loss from 30% to under 20% across the pilot distribution zone.",
      kpis: "Leak detection time < 6 hrs; water wastage <= 20%; uptime >= 95%; cost per km <= ₹25,000.",
      eligibility_requirements: "DPIIT-recognized startup with ISO 9001:2015 certification and at least 2 years operational track record.",
      data_requirements: "Daily pressure and acoustic time-series logs exported securely in CSV/JSON format.",
      security_requirements: "End-to-end encrypted telemetry transmission, role-based access control, and adherence to municipal data guidelines.",
      generated_by: "template"
    }
  },
  {
    id: 2,
    title: "AI-Based Hospital OPD Queue and Patient Triage Management",
    department: "District Health Administration",
    district: "District A",
    sector: "healthcare",
    budget: 750000,
    timeline_days: 120,
    deadline: "2026-09-28",
    status: "open",
    required_tech: ["ai", "analytics", "cloud", "mobile-app"],
    application_count: 8,
    created_at: "2026-08-28T10:30:00Z",
    created_by: 1,
    match_rubric_id: 3,
    evaluation_rubric_id: 6,
    eligibility_rules: {
      registered_startup: true,
      required_certification: "ISO 27001",
      min_experience_years: 1,
      min_technology_overlap: 1,
      max_quote: 750000,
      security_baseline: true
    },
    kpi_targets: [
      { name: "Average OPD wait time", unit: "mins", baseline: 110, target: 35, category: "impact", direction: "lower_is_better" }
    ],
    statement: {
      problem: "Severe OPD congestion in civil hospitals resulting in long patient waiting times and delayed emergency triage.",
      background: "District civil hospitals manage high daily patient volumes without automated queue orchestration.",
      existing_system: "Physical token counters and manual triage registries.",
      identified_gap: "No digital dynamic load balancing across clinical departments.",
      desired_solution: "Implement AI-powered digital token dispatch, doctor OPD slot prediction, and multilingual mobile queues.",
      target_users: "OPD patients, hospital administrators, nursing staff, and consulting physicians.",
      technical_requirements: "Cloud-hosted triage dispatch engine, digital display signage APIs, SMS/WhatsApp gateway.",
      constraints: "Must support low-literacy patient touchpoints and non-smartphone digital tokens.",
      budget: "₹7,50,000 for cloud platform, kiosk integration, and 120-day validation pilot.",
      timeline: "120 calendar days across pilot hospital wards.",
      expected_outcomes: "OPD wait time reduction by over 65% and zero patient dropouts.",
      kpis: "Average wait time <= 35 mins; kiosk uptime >= 98%; patient satisfaction >= 85%.",
      eligibility_requirements: "DPIIT-recognized health-tech startup with ISO 27001 data compliance.",
      data_requirements: "Encrypted patient queue metadata without storing personal health records permanently.",
      security_requirements: "HIPAA/DISHA compliant data processing and role-based doctor authentication.",
      generated_by: "template"
    }
  },
  {
    id: 3,
    title: "Automated Municipal Solid Waste Collection Route Optimization",
    department: "Municipal Solid Waste Department",
    district: "District B",
    sector: "waste",
    budget: 600000,
    timeline_days: 90,
    deadline: "2026-10-05",
    status: "open",
    required_tech: ["iot", "gps", "optimization", "analytics"],
    application_count: 17,
    created_at: "2026-08-29T11:00:00Z",
    created_by: 1,
    match_rubric_id: 4,
    evaluation_rubric_id: 5,
    eligibility_rules: {
      registered_startup: true,
      required_certification: "ISO 9001:2015",
      min_experience_years: 1,
      min_technology_overlap: 1,
      max_quote: 600000,
      security_baseline: true
    },
    kpi_targets: [
      { name: "Fuel consumption per ton", unit: "litres", baseline: 14.5, target: 9.8, category: "cost", direction: "lower_is_better" }
    ],
    statement: {
      problem: "Inefficient static waste pickup truck routes causing high diesel expenses and overflowing bins.",
      background: "Municipal solid waste collection vehicles travel fixed schedules regardless of bin fill levels.",
      existing_system: "Fixed manual routes logged on paper logsheets.",
      identified_gap: "Lack of ultrasonic bin fill telemetry and dynamic dynamic routing algorithms.",
      desired_solution: "Install ultrasonic fill sensors and provide automated daily dynamic dispatch routes to drivers.",
      target_users: "Sanitation supervisors, municipal truck drivers, and zonal waste commissioners.",
      technical_requirements: "Ruggedized IoT fill sensors, GPS driver navigation app, web supervisor portal.",
      constraints: "Hardware sensors must withstand outdoor weather, moisture, and rough bin handling.",
      budget: "₹6,00,000 for 100 bin sensors, driver tablets, and 90-day pilot deployment.",
      timeline: "90 calendar days across pilot municipal ward.",
      expected_outcomes: "25% reduction in diesel expenditure and zero uncollected overflow bins.",
      kpis: "Fuel consumption <= 9.8 L/ton; bin overflow incidents <= 2/month.",
      eligibility_requirements: "DPIIT-registered waste-tech or IoT startup.",
      data_requirements: "Real-time telemetry stream of GPS positions and bin fill percentages.",
      security_requirements: "Secure API access and encrypted GPS vehicle track logs.",
      generated_by: "template"
    }
  }
];

export const startups = [
  {
    id: 1,
    user_id: 3,
    name: "AquaSense Systems",
    sector: "water",
    technologies: ["iot", "sensors", "ai", "analytics", "gis"],
    tech_tags: ["iot", "sensors", "ai", "analytics", "gis"],
    dpiit_number: "DIPP48291",
    incorporation_year: 2021,
    turnover: 6500000,
    team_size: 18,
    past_projects: [
      { name: "Pune Municipal Smart Water Pilot - Ward 7", sector: "water", year: 2024 },
      { name: "PCMC DMA Leakage Reduction Project", sector: "water", year: 2023 }
    ],
    certifications: ["ISO 9001:2015", "ISO 27001", "CPRI Certified Hardware"],
    description: "End-to-end smart municipal water distribution monitoring platform with acoustic sensor nodes, GIS pressure mapping, and ML-based non-revenue water (NRW) leak detection algorithms.",
  },
  {
    id: 2,
    user_id: 3,
    name: "PipeAI Technologies",
    sector: "water",
    technologies: ["ai", "analytics", "gis", "iot", "scada"],
    tech_tags: ["ai", "analytics", "gis", "iot"],
    dpiit_number: "DIPP51902",
    incorporation_year: 2022,
    turnover: 4200000,
    team_size: 12,
    past_projects: [
      { name: "Nashik Industrial Corridor Pipeline Pressure Twin", sector: "water", year: 2024 }
    ],
    certifications: ["ISO 9001:2015"],
    description: "Predictive pipe burst and transient surge analysis platform for water utilities.",
  },
  {
    id: 3,
    user_id: 3,
    name: "HydroTrack Telemetry",
    sector: "water",
    technologies: ["sensors", "iot", "telemetry"],
    tech_tags: ["sensors", "iot"],
    dpiit_number: "DIPP63114",
    incorporation_year: 2023,
    turnover: 2800000,
    team_size: 8,
    past_projects: [],
    certifications: ["ISO 9001:2015"],
    description: "Low-cost water flow and reservoir level telemetry for district distribution.",
  }
];

export const evaluations = [
  { startup: "AquaSense Systems", challenge: "Reduce Municipal Water Leakage in Distribution Networks", status: "pending" },
  { startup: "PipeAI Technologies", challenge: "Reduce Municipal Water Leakage in Distribution Networks", status: "pending" },
  { startup: "MedQueue Solutions", challenge: "AI-Based Hospital OPD Queue and Patient Triage Management", status: "evaluated" }
];

export const rubrics = [
  {
    id: 1,
    name: "Default (PS baseline)",
    kind: "match",
    version: 1,
    is_default: true,
    active: true,
    weights: {
      technology_match: 30,
      domain_experience: 20,
      past_projects: 15,
      eligibility: 15,
      cost_fit: 10,
      scalability: 10
    },
    criteria: [
      {
        key: "technology_match",
        label: "Technology match",
        weight: 30,
        help: "Overlap between the challenge's required technologies and the startup's tech_tags."
      },
      {
        key: "domain_experience",
        label: "Domain experience",
        weight: 20,
        help: "How closely the startup's sector matches the challenge's sector."
      },
      {
        key: "past_projects",
        label: "Past projects",
        weight: 15,
        help: "Number and relevance of the startup's prior deployments in this sector."
      },
      {
        key: "eligibility",
        label: "Eligibility",
        weight: 15,
        help: "Score from the eligibility gate checks, 100 if all six passed."
      },
      {
        key: "cost_fit",
        label: "Cost fit",
        weight: 10,
        help: "How closely the startup's quote fits within the challenge budget."
      },
      {
        key: "scalability",
        label: "Scalability",
        weight: 10,
        help: "Team size and prior deployment count as a proxy for scale-up capacity."
      }
    ]
  },
  {
    id: 2,
    name: "Infrastructure / IoT",
    kind: "match",
    version: 1,
    is_default: false,
    active: true,
    weights: {
      technology_match: 35,
      domain_experience: 15,
      past_projects: 15,
      eligibility: 15,
      cost_fit: 5,
      scalability: 15
    },
    criteria: [
      {
        key: "technology_match",
        label: "Technology match",
        weight: 35,
        help: "Overlap between required technologies and the startup's tech_tags. Weighted higher for hardware-heavy IoT deployments."
      },
      {
        key: "domain_experience",
        label: "Domain experience",
        weight: 15,
        help: "How closely the startup's sector matches the challenge's sector."
      },
      {
        key: "past_projects",
        label: "Past projects",
        weight: 15,
        help: "Number and relevance of the startup's prior deployments in this sector."
      },
      {
        key: "eligibility",
        label: "Eligibility",
        weight: 15,
        help: "Score from the eligibility gate checks, 100 if all six passed."
      },
      {
        key: "cost_fit",
        label: "Cost fit",
        weight: 5,
        help: "How closely the startup's quote fits within the challenge budget. Lower weight, since infrastructure pilots tolerate cost variance more."
      },
      {
        key: "scalability",
        label: "Scalability",
        weight: 15,
        help: "Team size and prior deployment count. Weighted higher, since IoT rollouts need to scale across many sites."
      }
    ]
  },
  {
    id: 3,
    name: "Healthcare",
    kind: "match",
    version: 1,
    is_default: false,
    active: true,
    weights: {
      technology_match: 25,
      domain_experience: 20,
      past_projects: 25,
      eligibility: 15,
      cost_fit: 5,
      scalability: 10
    },
    criteria: [
      {
        key: "technology_match",
        label: "Technology match",
        weight: 25,
        help: "Overlap between required technologies and the startup's tech_tags."
      },
      {
        key: "domain_experience",
        label: "Domain experience",
        weight: 20,
        help: "How closely the startup's sector matches the challenge's sector."
      },
      {
        key: "past_projects",
        label: "Past projects",
        weight: 25,
        help: "Weighted higher for healthcare, prior clinical or hospital deployments matter more than raw tech fit."
      },
      {
        key: "eligibility",
        label: "Eligibility",
        weight: 15,
        help: "Score from the eligibility gate checks, 100 if all six passed."
      },
      {
        key: "cost_fit",
        label: "Cost fit",
        weight: 5,
        help: "How closely the startup's quote fits within the challenge budget. Lower weight, patient outcomes matter more than cost here."
      },
      {
        key: "scalability",
        label: "Scalability",
        weight: 10,
        help: "Team size and prior deployment count as a proxy for scale-up capacity."
      }
    ]
  },
  {
    id: 4,
    name: "Low-budget municipal",
    kind: "match",
    version: 1,
    is_default: false,
    active: true,
    weights: {
      technology_match: 25,
      domain_experience: 15,
      past_projects: 10,
      eligibility: 15,
      cost_fit: 25,
      scalability: 10
    },
    criteria: [
      {
        key: "technology_match",
        label: "Technology match",
        weight: 25,
        help: "Overlap between required technologies and the startup's tech_tags."
      },
      {
        key: "domain_experience",
        label: "Domain experience",
        weight: 15,
        help: "How closely the startup's sector matches the challenge's sector."
      },
      {
        key: "past_projects",
        label: "Past projects",
        weight: 10,
        help: "Number and relevance of the startup's prior deployments. Lower weight, smaller municipalities have less prior work to point to."
      },
      {
        key: "eligibility",
        label: "Eligibility",
        weight: 15,
        help: "Score from the eligibility gate checks, 100 if all six passed."
      },
      {
        key: "cost_fit",
        label: "Cost fit",
        weight: 25,
        help: "How closely the startup's quote fits within the challenge budget. Weighted highest, since a tight municipal budget is the binding constraint."
      },
      {
        key: "scalability",
        label: "Scalability",
        weight: 10,
        help: "Team size and prior deployment count as a proxy for scale-up capacity."
      }
    ]
  },
  {
    id: 5,
    name: "Default expert panel",
    kind: "evaluation",
    version: 1,
    is_default: true,
    active: true,
    weights: {
      technical_feasibility: 25,
      innovation: 15,
      cost_effectiveness: 15,
      scalability: 15,
      security: 10,
      implementation_capability: 10,
      social_impact: 10
    },
    criteria: [
      {
        key: "technical_feasibility",
        label: "Technical feasibility",
        weight: 25,
        help: "Can this actually be built and deployed within the pilot timeline?"
      },
      {
        key: "innovation",
        label: "Innovation",
        weight: 15,
        help: "How novel is the approach compared to existing solutions in this space?"
      },
      {
        key: "cost_effectiveness",
        label: "Cost effectiveness",
        weight: 15,
        help: "Value delivered per rupee against the proposed budget."
      },
      {
        key: "scalability",
        label: "Scalability",
        weight: 15,
        help: "Can this be replicated across other districts without redesign?"
      },
      {
        key: "security",
        label: "Security",
        weight: 10,
        help: "Does the proposal meet baseline data protection and cybersecurity expectations?"
      },
      {
        key: "implementation_capability",
        label: "Implementation capability",
        weight: 10,
        help: "Does the team have the experience and capacity to execute this pilot?"
      },
      {
        key: "social_impact",
        label: "Social impact",
        weight: 10,
        help: "Expected benefit to end users and the public if the pilot succeeds."
      }
    ]
  },
  {
    id: 6,
    name: "Security-weighted panel",
    kind: "evaluation",
    version: 1,
    is_default: false,
    active: true,
    weights: {
      technical_feasibility: 20,
      innovation: 10,
      cost_effectiveness: 15,
      scalability: 15,
      security: 25,
      implementation_capability: 10,
      social_impact: 5
    },
    criteria: [
      {
        key: "technical_feasibility",
        label: "Technical feasibility",
        weight: 20,
        help: "Can this actually be built and deployed within the pilot timeline?"
      },
      {
        key: "innovation",
        label: "Innovation",
        weight: 10,
        help: "How novel is the approach compared to existing solutions in this space?"
      },
      {
        key: "cost_effectiveness",
        label: "Cost effectiveness",
        weight: 15,
        help: "Value delivered per rupee against the proposed budget."
      },
      {
        key: "scalability",
        label: "Scalability",
        weight: 15,
        help: "Can this be replicated across other districts without redesign?"
      },
      {
        key: "security",
        label: "Security",
        weight: 25,
        help: "Weighted highest, for challenges handling sensitive citizen data (health records, biometric, financial)."
      },
      {
        key: "implementation_capability",
        label: "Implementation capability",
        weight: 10,
        help: "Does the team have the experience and capacity to execute this pilot?"
      },
      {
        key: "social_impact",
        label: "Social impact",
        weight: 5,
        help: "Expected benefit to end users. Lower weight here, security compliance is the gating concern for this panel."
      }
    ]
  }
];

export const mockApplicationsList = [
  {
    application_id: 14,
    challenge_id: 1,
    challenge_title: "Reduce Municipal Water Leakage in Distribution Networks",
    challenge_sector: "water",
    startup_id: 3,
    startup_name: "AquaSense",
    quote: 850000,
    pitch: "We deploy real-time acoustic sensors and IoT pressure transducers with predictive leak mapping.",
    eligible: true,
    eligibility_report: {
      registered_startup: { passed: true, note: "DIPP12345" },
      required_certification: { passed: true, note: "ISO 9001:2015 present" },
      min_experience_years: { passed: true, note: "4 years, needs 2" },
      technology_overlap: { passed: true, note: "3 of 3 matched" },
      budget_within_range: { passed: true, note: "quote 8.5L of 10L" },
      security_baseline: { passed: true, note: "self-declared" }
    },
    match_score: 91.2,
    match_breakdown: {
      technology_match: 94.0,
      domain_experience: 90.0,
      past_projects: 85.0,
      eligibility: 100.0,
      cost_fit: 80.0,
      scalability: 92.0
    },
    rubric_snapshot: {
      technology_match: 30,
      domain_experience: 20,
      past_projects: 15,
      eligibility: 15,
      cost_fit: 10,
      scalability: 10
    },
    explanation: "Recommended because the startup has IoT expertise, municipal infrastructure experience and two previous water-management deployments.",
    status: "applied",
    applied_at: "2026-08-30T10:00:00Z"
  }
];
