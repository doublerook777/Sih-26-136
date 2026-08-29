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
    match_score: 94.0,
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
    match_score: 76.5,
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
    match_score: 82.0,
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
    match_score: 94.0
  },
  {
    id: 2,
    user_id: 3,
    name: "PipeAI Technologies",
    sector: "water",
    technologies: ["ai", "analytics", "gis", "iot", "scada"],
    dpiit_number: "DIPP51902",
    incorporation_year: 2022,
    turnover: 4200000,
    team_size: 12,
    past_projects: [
      { name: "Nashik Industrial Corridor Pipeline Pressure Twin", sector: "water", year: 2024 }
    ],
    certifications: ["ISO 9001:2015"],
    description: "Predictive pipe burst and transient surge analysis platform for water utilities.",
    match_score: 87.0
  },
  {
    id: 3,
    user_id: 3,
    name: "HydroTrack Telemetry",
    sector: "water",
    technologies: ["sensors", "iot", "telemetry"],
    dpiit_number: "DIPP63114",
    incorporation_year: 2023,
    turnover: 2800000,
    team_size: 8,
    past_projects: [],
    certifications: ["ISO 9001:2015"],
    description: "Low-cost water flow and reservoir level telemetry for district distribution.",
    match_score: 81.0
  }
];

export const evaluations = [
  { startup: "AquaSense Systems", challenge: "Reduce Municipal Water Leakage in Distribution Networks", status: "pending" },
  { startup: "PipeAI Technologies", challenge: "Reduce Municipal Water Leakage in Distribution Networks", status: "pending" },
  { startup: "MedQueue Solutions", challenge: "AI-Based Hospital OPD Queue and Patient Triage Management", status: "evaluated" }
];
