<h1 align="center">Legal Buddy</h1>

<p align="center">
  An LLM-powered web application that helps justice-involved individuals understand their court cases,
  what’s happening now, and what typically comes next — using grounded data, visual explanations,
  and interactive procedural guidance.
</p>

<hr />

<h2>Overview</h2>

<p>
  Legal Buddy is designed to reduce confusion and anxiety around legal proceedings by translating
  fragmented court records into clear explanations, visual summaries, and structured timelines.
  Rather than predicting outcomes, the system focuses on procedural clarity and historical patterns
  from similar cases.
</p>

<hr />

<h2>Core Experiences</h2>

<p>
  Below are examples of key Legal Buddy workflows, including case entry, outcome statistics,
  timeline visualization, and procedural simulation.
</p>

<!-- ROW 1 -->
<p align="center">
  <img src="screenshots/home_light.png"
       width="280" height="560"
       style="object-fit: contain; margin: 0 12px;" />

  <img src="screenshots/stats1.png"
       width="280" height="560"
       style="object-fit: contain; margin: 0 12px;" />
</p>

<!-- ROW 2 -->
<p align="center">
  <img src="screenshots/timeline1.png"
       width="280" height="560"
       style="object-fit: contain; margin: 0 12px;" />

  <img src="screenshots/procedural1.png"
       width="280" height="560"
       style="object-fit: contain; margin: 0 12px;" />
</p>

<hr />

<h2>Case Overview (After Case ID Lookup)</h2>

<p>
  After a user submits a case ID, Legal Buddy retrieves relevant public court records and translates
  legal terminology and procedural status into clear, human-friendly language.
</p>

<p align="center">
  <img src="screenshots/initial_response.png"
       width="600"
       style="object-fit: contain;" />
</p>

<hr />

<h2>Similar Case Outcomes</h2>

<p>
  When users ask how similar cases typically turn out, Legal Buddy computes cohort-based outcome
  statistics and presents them visually alongside a plain-language explanation grounded in
  historical data.
</p>

<p align="center">
  <img src="screenshots/stats1.png"
       width="280" height="560"
       style="object-fit: contain; margin: 0 12px;" />

  <img src="screenshots/stats2.png"
       width="280" height="560"
       style="object-fit: contain; margin: 0 12px;" />
</p>

<hr />

<h2>Procedural Simulator: “What Usually Happens Next?”</h2>

<p>
  Legal Buddy includes an interactive procedural simulator that allows users to explore common
  next steps in their case. This simulator reflects typical procedural paths rather than making
  individualized predictions.
</p>

<p align="center">
  <img src="screenshots/procedural1.png"
       width="280" height="560"
       style="object-fit: contain; margin: 0 12px;" />

  <img src="screenshots/procedural2.png"
       width="280" height="560"
       style="object-fit: contain; margin: 0 12px;" />
</p>

<p align="center">
  <img src="screenshots/procedural3.png"
       width="280" height="560"
       style="object-fit: contain; margin: 0 12px;" />
</p>

<hr />

<h2>Case Timeline</h2>

<p>
  Users can view a structured timeline highlighting completed events, the current procedural stage,
  and likely upcoming milestones derived deterministically from court records.
</p>

<p align="center">
  <img src="screenshots/timeline1.png"
       width="280" height="560"
       style="object-fit: contain; margin: 0 12px;" />

  <img src="screenshots/timeline2.png"
       width="280" height="560"
       style="object-fit: contain; margin: 0 12px;" />
</p>

<p align="center">
  <img src="screenshots/timeline3.png"
       width="280" height="560"
       style="object-fit: contain; margin: 0 12px;" />
</p>

<hr />

<h2>Dark Mode</h2>

<p>
  All major workflows support dark mode for accessibility and visual comfort.
</p>

<!-- DARK MODE ROW 1 -->
<p align="center">
  <img src="screenshots/home_dark.png"
       width="280" height="560"
       style="object-fit: contain; margin: 0 12px;" />

  <img src="screenshots/stats_dark.png"
       width="280" height="560"
       style="object-fit: contain; margin: 0 12px;" />
</p>

<!-- DARK MODE ROW 2 -->
<p align="center">
  <img src="screenshots/timeline_dark.png"
       width="280" height="560"
       style="object-fit: contain; margin: 0 12px;" />

  <img src="screenshots/procedural_simulator_dark.png"
       width="280" height="560"
       style="object-fit: contain; margin: 0 12px;" />
</p>

<hr />

<h2>Key Features</h2>

<ul>
  <li>Grounded retrieval of public court records</li>
  <li>Plain-language explanations of legal status and procedure</li>
  <li>Visual outcome statistics for similar cases</li>
  <li>Interactive procedural simulator</li>
  <li>Deterministic case timeline generation</li>
  <li>Light and dark mode support</li>
</ul>

<hr />

<h2>Tech Stack</h2>

<ul>
  <li><strong>Frontend:</strong> React</li>
  <li><strong>Backend:</strong> FastAPI</li>
  <li><strong>LLMs:</strong> OpenAI and local models</li>
  <li><strong>Data:</strong> Public court records</li>
</ul>

<p>
  This project was built with a focus on clarity, accessibility, and procedural justice.
</p>
