# ProcuraAI (SIH 26136) — Live Demo Script (Day 3 Working Draft)

**Scenario:** Municipal Water Department creates an AI-structured challenge to tackle 35% non-revenue water leakage, discovers and screens startups, evaluates candidates via an expert panel under a shared rubric, and selects the winning innovation.

**Total Time:** 4–5 minutes  
**Audience:** SIH Evaluation Panel / Jury

---

## Pre-Demo Checklist (1 Minute Before Going on Stage)
1. Backend running: `uvicorn backend.app.main:app --reload --port 8000`
2. Frontend running: `npm run dev` (serving at `http://localhost:5173`)
3. Fresh seed data: `python backend/seed.py` (resets to known clean state)
4. Chrome opened at `http://localhost:5173`

---

## Act 1: Authentication & Problem Ingestion (0:00 – 1:15)

### Step 1: Officer Login
* **Action:** Navigate to `http://localhost:5173/login`.
* **Click:** Select role shortcut **"Government Officer"** (prefills `officer@water.gov.in` / `secret123`).
* **Click:** **"Sign In"** button.
* **What Audience Sees:** Redirects to `/government` dashboard showing active municipal challenges, budget allocations, and status summary cards ("Draft", "Active", "Evaluation").

### Step 2: Create New Problem Challenge
* **Action:** Click **"Create Challenge"** in the top navigation or dashboard button.
* **What Audience Sees:** The Challenge Creation wizard form.
* **Action:** Fill in basic department info:
  * Title: `Smart Municipal Water Leak Detection & Flow Telemetry`
  * Sector: `Water Management`
  * Department: `Urban Water Supply Authority`
  * District: `District A`
  * Budget (INR): `1000000` (₹10 Lakhs)
  * Timeline (Days): `90`
  * Required Technologies: `IoT, Pressure Sensors, Acoustic Sensors, AI Anomaly Detection`
  * Raw Problem Description:
    > *"Our municipal distribution network experiences 35% non-revenue water losses due to undetected subterranean pipeline bursts. We currently only find out when roads flood or citizen complaints arrive days later. We need real-time pressure sensor nodes and acoustic anomaly detection to pinpoint leaks within 2 hours."*

### Step 3: AI Problem Statement Generation (Live LLM)
* **Click:** **"Generate Structured Statement with AI"** button.
* **What Audience Sees:** 1.5-second loading animation followed by the complete **15-section standardized problem statement** automatically populated:
  * 1. Problem Definition
  * 2. Background & Administrative Context
  * 3. Existing System & Current Practices
  * 4. Identified Operational Gap
  * 5. Desired Innovation Solution
  * 6. Target Users & Stakeholders
  * 7. Technical Architecture & System Requirements
  * 8. Operational Constraints & Field Limitations
  * 9. Budget Allocation & Financial Framework
  * 10. Pilot Implementation Timeline & Phasing
  * 11. Expected Outcomes & Deliverables
  * 12. Key Performance Indicators (KPIs)
  * 13. Startup Eligibility Requirements
  * 14. Data Governance & Integration Requirements
  * 15. Cybersecurity & Compliance Requirements
* **Spoken Point:** *"In 2 seconds, our platform transforms a 3-line complaint into a 15-section, tender-compliant specification that adheres to public procurement standards."*

### Step 4: Configure Scoring Rubric & Publish
* **Action:** In the Rubric dropdown, view available rubrics:
  * `Default (PS baseline)` (30/20/15/15/10/10)
  * `Infrastructure / IoT` (Technology: 35%, Scalability: 15%, Cost: 5%)
* **Click:** Select `Infrastructure / IoT` rubric.
* **Click:** **"Publish Challenge"** button.
* **What Audience Sees:** Success toast and redirect to `/challenges/1` showing the published challenge in `open` status.

---

## Act 2: Startup Discovery, Screening & AI Matching (1:15 – 2:30)

### Step 5: Run Automated Discovery & Eligibility Gate
* **Action:** From the challenge page, click **"Discover Startups"** (or navigate to `/recommendations/1`).
* **What Audience Sees:** The platform scans all 20 empanelled startups and executes two deterministic engines:
  1. **Eligibility Gate (Pass/Fail):** Verifies DPIIT recognition, ISO certifications, experience years, tech tag overlap, and budget ceiling.
  2. **TF-IDF + Weighted Match Engine:** Computes cosine similarity across required technologies and evaluates domain experience, past projects, and scalability.

### Step 6: Inspect Ranking & Explainability Breakdown
* **What Audience Sees:** Ranked table of startup candidates:
  * **#1 AquaSense Systems** — **91.2% Match** (Eligible: `True`)
  * **#2 PipeAI Technologies** — **84.5% Match** (Eligible: `True`)
  * **#3 HydroTrack Telemetry** — **78.0% Match** (Eligible: `True`)
  * **Ineligible Startups** (e.g. *CleanHazard Systems* or *LastMile Micro*) listed at the bottom with greyed badges and explicit failure tags (e.g., *"0/4 Required Tech Overlap"*, *"Missing ISO 27001"*).
* **Click:** Click on **"AquaSense Systems"** to expand the **Score Breakdown**:
  * Technology Match: `94%`
  * Domain Experience: `100%` (Water sector exact match)
  * Past Projects: `100%` (3 relevant municipal projects)
  * Cost Fit: `90%` (Quote fits within ₹10L ceiling)
  * Scalability: `85%`
  * **AI Explanation:** *"Recommended because the startup holds acoustic sensor patents, 3 prior municipal SCADA deployments in Maharashtra, and certified DPIIT recognition."*

---

## Act 3: Shortlisting & Expert Evaluation (2:30 – 3:45)

### Step 7: Shortlist Top Candidates
* **Click:** Check the top 2 startups (**AquaSense Systems** and **PipeAI Technologies**).
* **Click:** **"Shortlist for Expert Panel"** button.
* **What Audience Sees:** Status transitions to `shortlisted`. Applications are now dispatched to the independent technical expert pool.

### Step 8: Expert Review & Scoring (Expert Persona)
* **Action:** Log out and log in as **Technical Expert** (`expert1@gov.in` / `secret123`).
* **What Audience Sees:** `/evaluator` dashboard showing assigned applications waiting for review.
* **Click:** Click **"Evaluate AquaSense Systems"**.
* **What Audience Sees:** The Dynamic Evaluation Form populated from the active **"Default expert panel"** rubric (7 criteria):
  * Technical Feasibility (Weight: 25%): Enter `92`
  * Innovation (Weight: 15%): Enter `88`
  * Cost Effectiveness (Weight: 15%): Enter `85`
  * Scalability (Weight: 15%): Enter `90`
  * Security (Weight: 10%): Enter `95`
  * Implementation Capability (Weight: 10%): Enter `90`
  * Social Impact (Weight: 10%): Enter `88`
* **Click:** **"Submit Evaluation"**.
* **What Audience Sees:** Weighted Total computed instantly: `89.4 / 100`. Rubric weights snapshot frozen to prevent retroactive tampering.

---

## Act 4: Selection & Formal Procurement Documents (3:45 – 4:30)

### Step 9: Final Selection (Officer Persona)
* **Action:** Log back in as Government Officer (`officer@water.gov.in`).
* **Action:** Open `/challenges/1/applications`.
* **What Audience Sees:** Consensus average across expert evaluations:
  * **AquaSense Systems:** Average Score **89.4** $\rightarrow$ Status: `evaluated`
  * **PipeAI Technologies:** Average Score **81.0** $\rightarrow$ Status: `evaluated`
* **Click:** Click **"Select Winner"** on AquaSense Systems.
* **What Audience Sees:** AquaSense marked as **Selected** (`selected`), challenge status updated, and pilot drafting enabled.

### Step 10: Legal & Governance Document Preview
* **Action:** Click **"View Official Documents"** $\rightarrow$ **"Evaluation Rubric & Criteria"** (`/documents/evaluation_criteria/1`).
* **What Audience Sees:** A formal, government-branded HTML document rendering all 7 evaluation dimensions, percentage weights, and statutory audit notice ready for browser printing/PDF export.
* **Spoken Point:** *"Every step from raw statement to scoring weights and final selection is fully documented, legally compliant with GFR 2017 public procurement rules, and audit-ready."*

---

## Transition to Days 4 & 5 (Closing Pitch)
* *"In Days 4 and 5, this selected startup enters the structured Pilot Phase: 4 milestone-based deliverables, real-time IoT validation by field inspectors, automated mock escrow disbursements, and the final 4-way Scale-Up procurement decision."*
