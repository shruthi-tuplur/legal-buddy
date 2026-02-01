// simulator_tree_v1.js (shape you’ll embed in payload OR build server-side)
export const SIM_TREE_V1 = {
    version: "v1",
    roots_by_stage: [
      { match: ["pretrial", "arraignment"], root_id: "pretrial_root" },
      { match: ["arraignment"], root_id: "arraignment_root" },
    ],
    default_root_id: "general_root",
  
    nodes: {
      general_root: {
        id: "general_root",
        title: "Procedural Simulator",
        body:
          "This is a guided, educational ‘choose-your-path’ based on common court procedure. It’s not a prediction — it’s a way to learn the usual forks from here.",
        choices: [
          { label: "Pretrial (overview)", to: "pretrial_overview" },
          { label: "Discovery", to: "discovery_root" },
          { label: "Motions", to: "motions_root" },
          { label: "Plea discussions", to: "plea_root" },
        ],
      },
  
      arraignment_root: {
        id: "arraignment_root",
        title: "Arraignment stage",
        body:
          "Arraignment is when charges are formally read and a defendant enters a plea (often ‘not guilty’ initially). After that, cases typically move into pretrial scheduling and evidence exchange.",
        choices: [
          { label: "What usually happens next", to: "pretrial_overview" },
          { label: "Discovery", to: "discovery_root" },
          { label: "Motions", to: "motions_root" },
          { label: "Plea discussions", to: "plea_root" },
        ],
      },
  
      pretrial_root: {
        id: "pretrial_root",
        title: "Pretrial (current stage)",
        body:
          "Pretrial is the ‘working’ phase: scheduling, discovery, negotiations, and motions. Most forks come from: evidence review, motions outcomes, or plea negotiations.",
        choices: [
          { label: "Discovery (evidence exchange)", to: "discovery_root" },
          { label: "Motions (judge decisions)", to: "motions_root" },
          { label: "Plea discussions", to: "plea_root" },
          { label: "Trial-setting path (high level)", to: "trial_setting_overview" },
        ],
      },
  
      pretrial_overview: {
        id: "pretrial_overview",
        title: "Pretrial — overview",
        body:
          "Common pretrial activity includes: setting dates, exchanging discovery, negotiating, and filing motions. The court may schedule status dates to check progress.",
        choices: [
          { label: "Discovery", to: "discovery_root" },
          { label: "Motions", to: "motions_root" },
          { label: "Plea discussions", to: "plea_root" },
          { label: "Back", back: true },
        ],
      },
  
      // -----------------------------
      // Discovery
      // -----------------------------
      discovery_root: {
        id: "discovery_root",
        title: "Discovery",
        body:
          "Discovery is the exchange of evidence and information (police reports, recordings, lab results, witness info, etc.). It shapes negotiations and what motions make sense.",
        choices: [
          { label: "What’s included in discovery?", to: "discovery_included" },
          { label: "How discovery changes the case", to: "discovery_changes_case" },
          { label: "After discovery is reviewed — what forks happen?", to: "discovery_after_review" },
          { label: "Back", back: true },
        ],
      },
  
      discovery_included: {
        id: "discovery_included",
        title: "What’s included in discovery?",
        body:
          "Often includes reports, bodycam/video, 911 calls, lab results, photographs, witness statements, and sometimes digital evidence. What’s required can vary by jurisdiction and charge type.",
        choices: [
          { label: "Common issues people run into", to: "discovery_issues" },
          { label: "Back to Discovery", to: "discovery_root" },
        ],
      },
  
      discovery_issues: {
        id: "discovery_issues",
        title: "Common discovery issues",
        body:
          "Common issues: delays, missing items, needing clarification, disputes about what must be shared, and requests for protective orders (limits on sensitive materials).",
        choices: [
          { label: "Discovery-related motions", to: "motions_discovery_related" },
          { label: "Back to Discovery", to: "discovery_root" },
        ],
      },
  
      discovery_changes_case: {
        id: "discovery_changes_case",
        title: "How discovery changes the case",
        body:
          "Discovery can strengthen or weaken positions. It affects: (1) whether a plea offer feels reasonable, (2) whether a motion could succeed, and (3) how trial prep looks.",
        choices: [
          { label: "Explore motions next", to: "motions_root" },
          { label: "Explore plea discussions next", to: "plea_root" },
          { label: "Back to Discovery", to: "discovery_root" },
        ],
      },
  
      discovery_after_review: {
        id: "discovery_after_review",
        title: "After discovery is reviewed",
        body:
          "Common forks after discovery review: plea negotiations, motions (like suppress/dismiss), additional investigation, or moving toward trial-setting.",
        choices: [
          { label: "Plea discussions", to: "plea_root" },
          { label: "Motions", to: "motions_root" },
          { label: "Trial-setting path", to: "trial_setting_overview" },
          { label: "Back to Discovery", to: "discovery_root" },
        ],
      },
  
      // -----------------------------
      // Motions
      // -----------------------------
      motions_root: {
        id: "motions_root",
        title: "Motions",
        body:
          "Motions are requests asking the judge to do something specific (exclude evidence, dismiss charges, order discovery, set deadlines, etc.). Motions often have clear outcomes: granted, denied, continued, or partially granted.",
        choices: [
          { label: "Motion to suppress", to: "motion_suppress_root" },
          { label: "Motion to dismiss", to: "motion_dismiss_root" },
          { label: "Discovery-related motion", to: "motions_discovery_related" },
          { label: "What happens at a motions hearing?", to: "motions_hearing" },
          { label: "Back", back: true },
        ],
      },
  
      motions_hearing: {
        id: "motions_hearing",
        title: "Motions hearing",
        body:
          "A motions hearing is when the judge considers arguments (and sometimes evidence) about a motion. Some motions are decided on briefing; others involve testimony (for example, suppression issues).",
        choices: [
          { label: "Go to Motion to suppress", to: "motion_suppress_root" },
          { label: "Back to Motions", to: "motions_root" },
        ],
      },
  
      motions_discovery_related: {
        id: "motions_discovery_related",
        title: "Discovery-related motions",
        body:
          "These ask the judge to order disclosure, set deadlines, resolve disputes about what must be produced, or apply protective limits for sensitive material.",
        choices: [
          { label: "Common outcomes (what changes?)", to: "motions_discovery_outcomes" },
          { label: "Back to Motions", to: "motions_root" },
        ],
      },
  
      motions_discovery_outcomes: {
        id: "motions_discovery_outcomes",
        title: "Discovery motion — common outcomes",
        body:
          "Common outcomes include: ordering production by a date, narrowing requests, setting schedules, or granting protective terms. The case usually continues with updated deadlines.",
        choices: [
          { label: "Back to Discovery", to: "discovery_root" },
          { label: "Back to Motions", to: "motions_root" },
        ],
      },
  
      // Motion to suppress
      motion_suppress_root: {
        id: "motion_suppress_root",
        title: "Motion to suppress",
        body:
          "This argues certain evidence shouldn’t be used because of how it was obtained (for example, search/seizure issues or statement/admission issues). If key evidence is excluded, negotiations and trial strategy often shift.",
        choices: [
          { label: "Outcome: Granted", to: "suppress_granted" },
          { label: "Outcome: Denied", to: "suppress_denied" },
          { label: "Outcome: Partially granted", to: "suppress_partial" },
          { label: "Outcome: Continued / not decided yet", to: "suppress_continued" },
          { label: "Back to Motions", to: "motions_root" },
        ],
      },
  
      suppress_granted: {
        id: "suppress_granted",
        title: "Suppression granted",
        body:
          "If suppression is granted, the excluded evidence generally can’t be used the same way at trial. That can change leverage and next steps.",
        choices: [
          { label: "Common next forks", to: "after_suppress_granted" },
          { label: "Back to Motion to suppress", to: "motion_suppress_root" },
        ],
      },
  
      after_suppress_granted: {
        id: "after_suppress_granted",
        title: "After suppression is granted — common forks",
        body:
          "Common forks: the prosecution reassesses strength, negotiations may shift, charges may be reduced, or (sometimes) dismissal discussions happen. The case can still continue, just under a different evidence posture.",
        choices: [
          { label: "Explore plea discussions", to: "plea_root" },
          { label: "Back to Motion to suppress", to: "motion_suppress_root" },
          { label: "Back to Pretrial", to: "pretrial_root" },
        ],
      },
  
      suppress_denied: {
        id: "suppress_denied",
        title: "Suppression denied",
        body:
          "If suppression is denied, the evidence usually remains available for use. That doesn’t end the case — it just means this motion didn’t change the evidence landscape.",
        choices: [
          { label: "Common next forks", to: "after_suppress_denied" },
          { label: "Back to Motion to suppress", to: "motion_suppress_root" },
        ],
      },
  
      after_suppress_denied: {
        id: "after_suppress_denied",
        title: "After suppression is denied — common forks",
        body:
          "Common forks: negotiations continue, other motions may be considered, and trial prep continues. Some cases move toward trial-setting if unresolved.",
        choices: [
          { label: "Explore plea discussions", to: "plea_root" },
          { label: "Explore other motions", to: "motions_root" },
          { label: "Trial-setting path", to: "trial_setting_overview" },
        ],
      },
  
      suppress_partial: {
        id: "suppress_partial",
        title: "Suppression partially granted",
        body:
          "Sometimes only part of the evidence is excluded (for example, a portion of a statement, or certain items from a search).",
        choices: [
          { label: "Common next forks", to: "after_suppress_granted" },
          { label: "Back to Motion to suppress", to: "motion_suppress_root" },
        ],
      },
  
      suppress_continued: {
        id: "suppress_continued",
        title: "Suppression continued",
        body:
          "A ‘continued’ motion usually means no final decision yet. The court may want more briefing, a future hearing, or additional information before ruling.",
        choices: [
          { label: "What usually happens next", to: "motions_hearing" },
          { label: "Back to Motion to suppress", to: "motion_suppress_root" },
        ],
      },
  
      // Motion to dismiss
      motion_dismiss_root: {
        id: "motion_dismiss_root",
        title: "Motion to dismiss",
        body:
          "This argues the case (or certain charges) should be thrown out for legal reasons (for example: procedural issues, insufficient allegations, timing issues, or other legal defects).",
        choices: [
          { label: "Outcome: Granted", to: "dismiss_granted" },
          { label: "Outcome: Denied", to: "dismiss_denied" },
          { label: "Outcome: Partially granted", to: "dismiss_partial" },
          { label: "Outcome: Continued / not decided yet", to: "dismiss_continued" },
          { label: "Back to Motions", to: "motions_root" },
        ],
      },
  
      dismiss_granted: {
        id: "dismiss_granted",
        title: "Dismissal granted",
        body:
          "If dismissal is granted, a charge (or the whole case) may end in court. Separate processes like sealing/expungement (if available) are usually different steps.",
        choices: [
          { label: "What people often ask next", to: "post_dismissal_questions" },
          { label: "Back to Motion to dismiss", to: "motion_dismiss_root" },
        ],
      },
  
      post_dismissal_questions: {
        id: "post_dismissal_questions",
        title: "After dismissal — common questions",
        body:
          "Common questions include: what records remain public, whether sealing/expungement exists, and whether any conditions apply. Those details vary by jurisdiction and case type.",
        choices: [
          { label: "Back to Motion to dismiss", to: "motion_dismiss_root" },
          { label: "Back to Pretrial", to: "pretrial_root" },
        ],
      },
  
      dismiss_denied: {
        id: "dismiss_denied",
        title: "Dismissal denied",
        body:
          "If dismissal is denied, the case continues. That doesn’t mean there are no defenses — it just means the court didn’t end the case on these legal grounds.",
        choices: [
          { label: "Common next forks", to: "after_dismiss_denied" },
          { label: "Back to Motion to dismiss", to: "motion_dismiss_root" },
        ],
      },
  
      after_dismiss_denied: {
        id: "after_dismiss_denied",
        title: "After dismissal is denied — common forks",
        body:
          "Common forks: negotiations continue, other motions may be filed, or the case moves toward trial-setting if unresolved.",
        choices: [
          { label: "Explore plea discussions", to: "plea_root" },
          { label: "Explore other motions", to: "motions_root" },
          { label: "Trial-setting path", to: "trial_setting_overview" },
        ],
      },
  
      dismiss_partial: {
        id: "dismiss_partial",
        title: "Dismissal partially granted",
        body:
          "Sometimes only certain counts/charges are dismissed while others remain. That can change strategy and negotiations.",
        choices: [
          { label: "Common next forks", to: "after_dismiss_denied" },
          { label: "Back to Motion to dismiss", to: "motion_dismiss_root" },
        ],
      },
  
      dismiss_continued: {
        id: "dismiss_continued",
        title: "Dismissal continued",
        body:
          "A continued motion typically means the court hasn’t ruled yet — more briefing, a later hearing date, or additional review may be needed.",
        choices: [
          { label: "What happens at a motions hearing?", to: "motions_hearing" },
          { label: "Back to Motion to dismiss", to: "motion_dismiss_root" },
        ],
      },
  
      // -----------------------------
      // Pleas + Trial setting (light v1)
      // -----------------------------
      plea_root: {
        id: "plea_root",
        title: "Plea discussions",
        body:
          "Plea discussions are negotiations about resolving a case without trial. They can happen at many points in pretrial, often influenced by discovery and motions outcomes.",
        choices: [
          { label: "What a plea offer can include", to: "plea_includes" },
          { label: "If plea talks don’t resolve it", to: "plea_no_resolution" },
          { label: "Back", back: true },
        ],
      },
  
      plea_includes: {
        id: "plea_includes",
        title: "What a plea offer can include",
        body:
          "Plea offers can involve charge reductions, sentencing recommendations, dismissal of some counts, conditions (classes, probation terms), or time served terms — depending on the case and jurisdiction.",
        choices: [
          { label: "Back to Plea discussions", to: "plea_root" },
          { label: "Explore motions", to: "motions_root" },
        ],
      },
  
      plea_no_resolution: {
        id: "plea_no_resolution",
        title: "If plea talks don’t resolve it",
        body:
          "If a case doesn’t resolve through plea discussions, it often proceeds through motions/trial prep and may move toward a trial-setting path.",
        choices: [
          { label: "Trial-setting path", to: "trial_setting_overview" },
          { label: "Back to Plea discussions", to: "plea_root" },
        ],
      },
  
      trial_setting_overview: {
        id: "trial_setting_overview",
        title: "Trial-setting path (high level)",
        body:
          "If unresolved, a case can move toward trial-setting: deadlines, witness lists, exhibits, and final pretrial hearings. Many cases still resolve before the trial date, but the court prepares for trial as a possible outcome.",
        choices: [
          { label: "Back to Pretrial", to: "pretrial_root" },
          { label: "Explore motions", to: "motions_root" },
          { label: "Explore plea discussions", to: "plea_root" },
        ],
      },
    },
  };
  