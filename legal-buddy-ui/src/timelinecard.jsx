import React, { useMemo } from "react";

/**
 * TimelineCard
 * - Renders SVG timeline FIRST
 * - Then renders a short "explanation" / context BELOW the graphic
 * - Removes the "Typical next steps..." item from the timeline as a node
 *   and shows it as a separate context box instead.
 */
export default function TimelineCard({ payload }) {
  // ✅ IMPORTANT: do not early-return before hooks (eslint hooks rule)
  const safePayload = payload || {};

  const stage = safePayload.stage || "";
  const nowNodeId = safePayload.now_node_id || null;

  const nodes = useMemo(() => {
    const raw = Array.isArray(safePayload.nodes) ? safePayload.nodes : [];

    // Filter out the "Typical next steps..." placeholder so it doesn't appear as a node
    // We'll render it as a context box below the timeline instead.
    return raw.filter((n) => {
      const type = (n?.type || "").toUpperCase();
      const title = (n?.title || "").toLowerCase();
      if (type === "TYPICAL_STEP") return false;
      if (title.includes("typical next steps")) return false;
      return true;
    });
  }, [safePayload.nodes]);

  const contextBox = useMemo(() => {
    // Try to find your placeholder in future_placeholders first
    const fp = Array.isArray(safePayload.future_placeholders)
      ? safePayload.future_placeholders
      : [];

    const fromFuture = fp.find((x) => (x?.type || "").toUpperCase() === "TYPICAL_STEP")
      || fp.find((x) => (x?.title || "").toLowerCase().includes("typical next steps"));

    // If not found there, look for it in original nodes (in case your backend put it there)
    const rawNodes = Array.isArray(safePayload.nodes) ? safePayload.nodes : [];
    const fromNodes =
      rawNodes.find((x) => (x?.type || "").toUpperCase() === "TYPICAL_STEP") ||
      rawNodes.find((x) => (x?.title || "").toLowerCase().includes("typical next steps"));

    const picked = fromFuture || fromNodes;

    if (!picked) return null;

    // ✅ Better copy (humane + not prediction-y)
    const stageLower = String(stage).toLowerCase();

let bullets = [];

if (stageLower.includes("pretrial") && stageLower.includes("arraignment")) {
  bullets = [
    "Pretrial status dates / conferences get scheduled",
    "Discovery: both sides exchange evidence",
    "Negotiations: possible plea discussions",
    "Motions: requests the judge can rule on (e.g., evidence issues)",
    "Either a resolution OR a trial-setting path"
  ];
} else if (stageLower.includes("arraignment")) {
  bullets = [
    "Next court date is usually set",
    "Bond/bail conditions may be confirmed or adjusted",
    "Initial deadlines may be assigned"
  ];
} else {
  bullets = [
    "Next court date gets scheduled",
    "The court sets what the next procedural step is",
    "Your case moves forward based on what’s in the record"
  ];
}

return {
  title: "What usually happens next (at this stage)",
  subtitle: "Not a prediction — just the typical procedural steps people see here.",
  bullets,
};

  }, [safePayload.future_placeholders, safePayload.nodes]);

  const warnings = useMemo(() => {
    const w = Array.isArray(safePayload.warnings) ? safePayload.warnings : [];
    // Hide the redundant "Future steps..." warning if we already show the context box
    if (contextBox) {
      return w.filter((x) => !String(x).toLowerCase().includes("future steps"));
    }
    return w;
  }, [safePayload.warnings, contextBox]);

  // SVG layout constants
  const WIDTH = 340;
  const LEFT_X = 26;       // spine x
  const LABEL_X = 52;      // label start x
  const TOP_PAD = 14;
  const ROW_H = 62;        // spacing between events
  const LABEL_W = WIDTH - LABEL_X - 8;

  const HEIGHT = Math.max(160, TOP_PAD * 2 + nodes.length * ROW_H + 20);

  // Helpers
  const isNow = (id) => nowNodeId && String(id) === String(nowNodeId);

  return (
    <div className="timelineCardSvg">
      <div className="timelineHeader">
        <div className="timelineTitle">Timeline</div>
        {stage ? <div className="timelineStage">{stage}</div> : null}
      </div>

      {/* ✅ GRAPHIC FIRST */}
      <div className="timelineSvgWrap">
        <svg className="timelineSvg" viewBox={`0 0 ${WIDTH} ${HEIGHT}`} role="img" aria-label="Case timeline">
          {/* spine */}
          <line
            x1={LEFT_X}
            y1={TOP_PAD}
            x2={LEFT_X}
            y2={HEIGHT - TOP_PAD}
            className="tlSpine tlDrawSpine"
          />

          {/* rows */}
          {nodes.map((n, i) => {
            const y = TOP_PAD + i * ROW_H + 24;
            const now = isNow(n.id);

            return (
              <g
                key={n.id || i}
                className={`tlRow ${now ? "now" : ""}`}
                style={{ ["--i"]: i }}
              >
                {/* connector */}
                <line
                  x1={LEFT_X}
                  y1={y}
                  x2={LABEL_X - 6}
                  y2={y}
                  className="tlConnector"
                />

                {/* node */}
                <circle cx={LEFT_X} cy={y} r={6} className="tlNode" />

                {/* now ring */}
                {now ? (
                  <circle cx={LEFT_X} cy={y} r={12} className="tlNowRing" />
                ) : null}

                {/* label bubble */}
                <foreignObject
                  x={LABEL_X}
                  y={y - 22}
                  width={LABEL_W}
                  height={50}
                >
                  <div className="tlLabel">
                    <div className="tlLabelTop">
                      <div className="tlLabelTitle">{n.title || "Event"}</div>
                      {n.date ? <div className="tlLabelDate">{n.date}</div> : null}
                    </div>
                    {n.subtitle ? <div className="tlLabelSub">{n.subtitle}</div> : null}
                  </div>
                </foreignObject>
              </g>
            );
          })}
        </svg>
      </div>

      {/* ✅ WORDY EXPLANATION AFTER GRAPHIC */}
      {contextBox ? (
            <div className="timelineContextBox">
                <div className="timelineContextTitle">{contextBox.title}</div>
                <div className="timelineContextSub">{contextBox.subtitle}</div>

                {Array.isArray(contextBox.bullets) && contextBox.bullets.length > 0 ? (
                <ul className="timelineContextList">
                    {contextBox.bullets.map((b, i) => (
                    <li key={i} className="timelineContextItem">{b}</li>
                    ))}
                </ul>
                ) : null}
            </div>
            ) : null}


      {/* warnings */}
      {warnings.length > 0 ? (
        <div className="timelineWarnings">
          {warnings.map((w, i) => (
            <div key={i} className="timelineWarning">
              {w}
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}
