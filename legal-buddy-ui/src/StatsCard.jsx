import React, { useMemo } from "react";

function normalizeOutcomes(outcomesPct = {}) {
  // Keep a nice stable order
  const order = [
    "dismissed_or_nolle",
    "plea",
    "convicted",
    "acquitted",
    "other_or_unknown",
  ];

  const labelMap = {
    dismissed_or_nolle: "Dismissed / Nolle",
    plea: "Plea",
    convicted: "Convicted",
    acquitted: "Acquitted",
    other_or_unknown: "Other / Unknown",
  };

  return order
    .filter((k) => outcomesPct[k] != null)
    .map((k) => ({
      key: k,
      label: labelMap[k] || k,
      value: Number(outcomesPct[k]) || 0,
    }))
    .filter((x) => x.value > 0);
}

function pieSlices(data) {
  const total = data.reduce((s, x) => s + x.value, 0) || 1;
  let acc = 0;

  // We’ll render wedges with SVG arcs.
  // No fixed colors: we use currentColor + opacity bands (theme friendly).
  return data.map((d, i) => {
    const start = (acc / total) * Math.PI * 2;
    acc += d.value;
    const end = (acc / total) * Math.PI * 2;

    return { ...d, start, end, i };
  });
}

function arcPath(cx, cy, r, startAngle, endAngle) {
  const x1 = cx + r * Math.cos(startAngle);
  const y1 = cy + r * Math.sin(startAngle);
  const x2 = cx + r * Math.cos(endAngle);
  const y2 = cy + r * Math.sin(endAngle);
  const largeArc = endAngle - startAngle > Math.PI ? 1 : 0;

  return [
    `M ${cx} ${cy}`,
    `L ${x1} ${y1}`,
    `A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2}`,
    "Z",
  ].join(" ");
}

export default function StatsCard({ payload }) {
  const safe = payload || {};
  const skipped = !!safe.skipped;

  const rows = useMemo(
    () => normalizeOutcomes(safe.outcomes_pct || {}),
    [safe.outcomes_pct]
  );

  const slices = useMemo(() => pieSlices(rows), [rows]);

  return (
    <div className="statsCard">
      <div className="statsHeader">
        <div className="statsTitle">{safe.title || "Similar case outcomes"}</div>
        <div className="statsSub">{safe.subtitle || ""}</div>
      </div>

      {skipped ? (
        <div className="statsSkipped">
          {safe.reason || "Stats unavailable."}
        </div>
      ) : rows.length === 0 ? (
        <div className="statsSkipped">No outcome data found for this cohort.</div>
      ) : (
        <div className="statsBody">
          <div className="statsPieWrap" aria-label="Outcome distribution pie chart">
            <svg className="statsPie" viewBox="0 0 120 120" role="img">
              {/* base circle */}
              <circle cx="60" cy="60" r="46" className="statsPieBase" />
              {slices.map((s) => (
                <path
                  key={s.key}
                  d={arcPath(60, 60, 46, s.start, s.end)}
                  className="statsSlice"
                  style={{ opacity: 0.22 + s.i * 0.12 }}
                />
              ))}
              {/* donut hole */}
              <circle cx="60" cy="60" r="26" className="statsPieHole" />
            </svg>
          </div>

          <div className="statsLegend">
            {rows.map((r, i) => (
              <div key={r.key} className="statsLegendRow">
                <span className="statsDot" style={{ opacity: 0.22 + i * 0.12 }} />
                <span className="statsLabel">{r.label}</span>
                <span className="statsVal">{r.value.toFixed(1)}%</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Optional tiny footer for credibility */}
      {!skipped ? (
        <div className="statsFoot">
          Based on public Cook County disposition data (educational).
        </div>
      ) : null}
    </div>
  );
}
