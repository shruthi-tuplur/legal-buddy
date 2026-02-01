import React, { useMemo, useState } from "react";

/**
 * SimulatorCard
 * payload shape:
 * {
 *   stage_label: string,
 *   tree: { version, default_root_id, roots_by_stage, nodes },
 * }
 */
export default function SimulatorCard({ payload }) {
  const safe = payload || {};
  const stageLabel = safe.stage_label || "";
  const tree = safe.tree || {};

  const nodes = tree.nodes || {};

  const rootId = useMemo(() => {
    if (safe.root_id) return safe.root_id;   // ✅ use backend-picked root first
  
    const stage = String(stageLabel).toLowerCase();
    const roots = Array.isArray(tree.roots_by_stage) ? tree.roots_by_stage : [];
    for (const r of roots) {
      const matches = Array.isArray(r.match) ? r.match : [];
      const ok = matches.every((m) => stage.includes(String(m).toLowerCase()));
      if (ok && r.root_id) return r.root_id;
    }
    return tree.default_root_id || "general_root";
  }, [safe.root_id, stageLabel, tree.roots_by_stage, tree.default_root_id]);

  const [stack, setStack] = useState(() => [rootId]);
    React.useEffect(() => { setStack([rootId]); }, [rootId]);

  const currentId = stack[stack.length - 1];
  const node = nodes[currentId];

  const canBack = stack.length > 1;

  function goTo(id) {
    if (!id || !nodes[id]) return;
    setStack((prev) => [...prev, id]);
  }

  function goBack() {
    if (!canBack) return;
    setStack((prev) => prev.slice(0, -1));
  }

  if (!node) {
    return (
      <div className="simCard">
        <div className="simHeader">
          <div className="simTitle">Procedural Simulator</div>
          {stageLabel ? <div className="simStage">{stageLabel}</div> : null}
        </div>
        <div className="simBody">
          Simulator data missing or malformed.
        </div>
      </div>
    );
  }

  const choices = Array.isArray(node.choices) ? node.choices : [];

  return (
    <div className="simCard">
      <div className="simHeader">
        <div className="simTitle">Procedural Simulator</div>
        {stageLabel ? <div className="simStage">{stageLabel}</div> : null}
      </div>

      <div className="simNode">
        <div className="simNodeTitle">{node.title}</div>
        {node.body ? <div className="simNodeBody">{node.body}</div> : null}
      </div>

      <div className="simChoices">
        {choices.map((c, i) => {
          const label = c?.label || "Option";
          const isBack = c?.back === true;

          return (
            <button
              key={`${currentId}-${i}`}
              className={`simChoiceBtn ${isBack ? "secondary" : ""}`}
              onClick={() => (isBack ? goBack() : goTo(c.to))}
              disabled={isBack ? !canBack : !c?.to}
              type="button"
            >
              {label}
            </button>
          );
        })}
      </div>

      <div className="simFooter">
        <button className="simNavBtn" onClick={goBack} disabled={!canBack} type="button">
          Back
        </button>
        <div className="simCrumb">
          {stack.length > 0 ? `${stack.length} step${stack.length === 1 ? "" : "s"} deep` : ""}
        </div>
      </div>
    </div>
  );
}
