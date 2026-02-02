<h1 align="center">Legal Buddy</h1>

<p align="center">
  An LLM-powered web application that helps justice-involved individuals understand their court cases,
  what’s happening now, and what typically comes next — using grounded data, visual explanations,
  and interactive procedural guidance.
</p>

<hr />

<h2>Overview</h2>

<p>
  Legal Buddy reduces confusion around legal proceedings by translating fragmented court records
  into clear explanations, visual summaries, and structured timelines. The system focuses on
  procedural clarity and historical patterns rather than outcome prediction.
</p>

<hr />

<h2>Core Experiences</h2>

<p>
  Below are key Legal Buddy workflows, shown side-by-side for easy comparison.
</p>

<table align="center">
  <tr>
    <td align="center">
      <img src="screenshots/home_light.png"
           width="260" height="520"
           style="object-fit: contain; border-radius: 24px;" />
    </td>
    <td align="center">
      <img src="screenshots/stats1.png"
           width="260" height="520"
           style="object-fit: contain; border-radius: 24px;" />
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="screenshots/timeline1.png"
           width="260" height="520"
           style="object-fit: contain; border-radius: 24px;" />
    </td>
    <td align="center">
      <img src="screenshots/procedural1.png"
           width="260" height="520"
           style="object-fit: contain; border-radius: 24px;" />
    </td>
  </tr>
</table>

<hr />

<h2>Case Overview (After Case ID Lookup)</h2>

<p>
  After a user submits a case ID, Legal Buddy retrieves relevant public court records and explains
  the current procedural status in clear, human-friendly language.
</p>

<p align="center">
  <img src="screenshots/initial_response.png"
       width="320"
       style="object-fit: contain; border-radius: 24px;" />
</p>

<hr />

<h2>Similar Case Outcomes</h2>

<p>
  Outcome statistics are computed from similar historical cases and presented visually alongside
  a plain-language explanation.
</p>

<table align="center">
  <tr>
    <td align="center">
      <img src="screenshots/stats1.png"
           width="260" height="520"
           style="object-fit: contain; border-radius: 24px;" />
    </td>
    <td align="center">
      <img src="screenshots/stats2.png"
           width="260" height="520"
           style="object-fit: contain; border-radius: 24px;" />
    </td>
  </tr>
</table>

<hr />

<h2>Procedural Simulator</h2>

<p>
  The procedural simulator allows users to explore common next steps in their case without making
  individualized predictions.
</p>

<table align="center">
  <tr>
    <td align="center">
      <img src="screenshots/procedural1.png"
           width="260" height="520"
           style="object-fit: contain; border-radius: 24px;" />
    </td>
    <td align="center">
      <img src="screenshots/procedural2.png"
           width="260" height="520"
           style="object-fit: contain; border-radius: 24px;" />
    </td>
    <td align="center">
      <img src="screenshots/procedural3.png"
           width="260" height="520"
           style="object-fit: contain; border-radius: 24px;" />
    </td>
  </tr>
</table>

<hr />

<h2>Case Timeline</h2>

<p>
  A structured timeline highlights completed events, the current procedural stage, and likely
  upcoming milestones.
</p>

<table align="center">
  <tr>
    <td align="center">
      <img src="screenshots/timeline1.png"
           width="260" height="520"
           style="object-fit: contain; border-radius: 24px;" />
    </td>
    <td align="center">
      <img src="screenshots/timeline2.png"
           width="260" height="520"
           style="object-fit: contain; border-radius: 24px;" />
    </td>
    <td align="center">
      <img src="screenshots/timeline3.png"
           width="260" height="520"
           style="object-fit: contain; border-radius: 24px;" />
    </td>
  </tr>
</table>

<hr />

<h2>Dark Mode</h2>

<table align="center">
  <tr>
    <td align="center">
      <img src="screenshots/home_dark.png"
           width="260" height="520"
           style="object-fit: contain; border-radius: 24px;" />
    </td>
    <td align="center">
      <img src="screenshots/stats_dark.png"
           width="260" height="520"
           style="object-fit: contain; border-radius: 24px;" />
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="screenshots/timeline_dark.png"
           width="260" height="520"
           style="object-fit: contain; border-radius: 24px;" />
    </td>
    <td align="center">
      <img src="screenshots/procedural_simulator_dark.png"
           width="260" height="520"
           style="object-fit: contain; border-radius: 24px;" />
    </td>
  </tr>
</table>

<hr />

<h2>Tech Stack</h2>

<ul>
  <li><strong>Frontend:</strong> React</li>
  <li><strong>Backend:</strong> FastAPI</li>
  <li><strong>LLMs:</strong> OpenAI and local models</li>
  <li><strong>Data:</strong> Public court records</li>
</ul>

<p>
  Built with a focus on clarity, accessibility, and procedural justice.
</p>
