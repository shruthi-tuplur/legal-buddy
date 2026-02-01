import "./App.css";
import { useEffect, useMemo, useRef, useState } from "react";
import TimelineCard from "./timelinecard";
import SimulatorCard from "./simulatorcard";
import StatsCard from "./StatsCard";

function makeId(prefix = "msg") {
  return `${prefix}_${Date.now()}_${Math.random().toString(16).slice(2)}`;
}

export default function App() {
  const [messages, setMessages] = useState([]);
  const [caseId, setCaseId] = useState("");
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(false);
  const [stageLabel, setStageLabel] = useState("");
  const [error, setError] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [activeCaseId, setActiveCaseId] = useState(null);
  const [isDark, setIsDark] = useState(false);
  const [isPinkMode, setIsPinkMode] = useState(false);


  const [isAnalyzingStats, setIsAnalyzingStats] = useState(false);

  const trimmedCaseId = useMemo(() => caseId.trim(), [caseId]);
  const trimmedDraft = useMemo(() => draft.trim(), [draft]);

  useEffect(() => {
    const existing = localStorage.getItem("lb_session_id");
    if (existing) setSessionId(existing);

    // IMPORTANT: do NOT auto-restore activeCaseId on refresh
    setActiveCaseId(null);
    localStorage.removeItem("lb_active_case_id");
  }, []);

  const bottomRef = useRef(null);
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length, loading]);

  async function postChat({ case_id, user_message, wantsStats = false }) {
    const res = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: sessionId,
        case_id,
        user_message,
        wantsStats,
      }),
    });

    const data = await res.json();
    if (!res.ok || data.error) {
      throw new Error(data.error || `Request failed (${res.status})`);
    }

    if (data.session_id && data.session_id !== sessionId) {
      setSessionId(data.session_id);
      localStorage.setItem("lb_session_id", data.session_id);
    }

    if (data.stage_label) setStageLabel(data.stage_label);

    return data;
  }

  async function handleSendMessage() {
    if (!activeCaseId || !trimmedDraft || loading) return;

    const cmd = trimmedDraft.toLowerCase();

      if (cmd === "pink mode") {
        // show the user message (so it feels real)
        setMessages((prev) => [
          ...prev,
          {
            id: makeId("user"),
            role: "user",
            content: trimmedDraft,
            ui_cards: [],
          },
        ]);

        setDraft("");
        setIsPinkMode(true);

        // optional subtle acknowledgement
        setMessages((prev) => [
          ...prev,
          {
            id: makeId("assistant"),
            role: "assistant",
            content: "💖",
            ui_cards: [],
          },
        ]);

        return; // 🚨 DO NOT hit the API
      }


    const wantsStats =
      /similar cases|how (do|did)|statistics|usually turn out|outcome|dismissed|convicted|acquitted/i.test(
        trimmedDraft.toLowerCase()
      );

    setLoading(true);
    setError("");

    const userMsg = {
      id: makeId("user"),
      role: "user",
      content: trimmedDraft,
      ui_cards: [],
    };
    setMessages((prev) => [...prev, userMsg]);
    setDraft("");

    const analyzingId = makeId("analyzing");
    if (wantsStats) {
      setIsAnalyzingStats(true);
      setMessages((prev) => [
        ...prev,
        {
          id: analyzingId,
          role: "assistant",
          content: "Analyzing similar cases…",
          ui_cards: [],
        },
      ]);
    }

    try {
      const data = await postChat({
        case_id: null,
        user_message: trimmedDraft,
        wantsStats,
      });

      const assistantMsg = {
        id: makeId("assistant"),
        role: "assistant",
        content: data.explanation || "",
        ui_cards: data.ui_cards || [],
      };

      if (wantsStats) {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === analyzingId
              ? { ...m, content: assistantMsg.content, ui_cards: assistantMsg.ui_cards }
              : m
          )
        );
      } else {
        setMessages((prev) => [...prev, assistantMsg]);
      }
    } catch (e) {
      const msg = String(e.message || e);
      setError(msg);

      if (wantsStats) {
        setMessages((prev) =>
          prev.map((m) => (m.id === analyzingId ? { ...m, content: msg, ui_cards: [] } : m))
        );
      } else {
        setMessages((prev) => [
          ...prev,
          { id: makeId("assistant_err"), role: "assistant", content: msg, ui_cards: [] },
        ]);
      }
    } finally {
      setLoading(false);
      setIsAnalyzingStats(false);
    }
  }

  async function handleSetCase() {
    if (!trimmedCaseId || loading) return;

    setLoading(true);
    setError("");

    setMessages((prev) => [
      ...prev,
      {
        id: makeId("user"),
        role: "user",
        content: `Case ID: ${trimmedCaseId}`,
        ui_cards: [],
      },
    ]);

    try {
      const data = await postChat({
        case_id: trimmedCaseId,
        user_message: `Explain case ${trimmedCaseId}. Give me a clear stage + plain-language summary.`,
      });

      setActiveCaseId(trimmedCaseId);
      localStorage.setItem("lb_active_case_id", trimmedCaseId);

      setMessages((prev) => [
        ...prev,
        {
          id: makeId("assistant"),
          role: "assistant",
          content: data.explanation || "",
          ui_cards: data.ui_cards || [],
        },
      ]);

      setCaseId("");
    } catch (e) {
      const msg = String(e.message || e);
      setError(msg);
      setMessages((prev) => [
        ...prev,
        { id: makeId("assistant_err"), role: "assistant", content: msg, ui_cards: [] },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={`page ${isDark ? "dark" : ""} ${isPinkMode ? "pink" : ""}`}>

      <div className="phoneFrame">
        <div className="content">
          {!activeCaseId && (
            <div className="landingCenter">
              <div className="landingText">
                Ask me about
                <br />
                your case
              </div>
            </div>
          )}

          {activeCaseId && stageLabel && (
            <div className="stageHeader">
              <div className="stageTitle">Stage: {stageLabel}</div>
            </div>
          )}

          <button
            className="themeToggle"
            onClick={() => setIsDark((d) => !d)}
            aria-label="Toggle theme"
          >
            <span className="themeIcon">
              {isDark ? (
                <svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true">
                  <circle cx="12" cy="12" r="4.2" fill="currentColor" />
                  <g stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                    <line x1="12" y1="1.5" x2="12" y2="4.2" />
                    <line x1="12" y1="19.8" x2="12" y2="22.5" />
                    <line x1="1.5" y1="12" x2="4.2" y2="12" />
                    <line x1="19.8" y1="12" x2="22.5" y2="12" />
                    <line x1="4.2" y1="4.2" x2="6.1" y2="6.1" />
                    <line x1="17.9" y1="17.9" x2="19.8" y2="19.8" />
                    <line x1="17.9" y1="6.1" x2="19.8" y2="4.2" />
                    <line x1="4.2" y1="19.8" x2="6.1" y2="17.9" />
                  </g>
                </svg>
              ) : (
                <svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true">
                  <path
                    d="M21 12.8A9 9 0 1111.2 3a7 7 0 109.8 9.8z"
                    fill="currentColor"
                  />
                </svg>
              )}
            </span>

            <span className={`toggleTrack ${isDark ? "on" : ""}`}>
              <span className="toggleThumb" />
            </span>
          </button>

          {/* Scrollable thread */}
          <div className="thread">
            {messages.map((m, idx) => {
              const cards = Array.isArray(m.ui_cards) ? m.ui_cards : [];
              const statsCards = cards.filter((c) => c?.type === "stats_card");
              const timelineCards = cards.filter((c) => c?.type === "timeline_card");
              const simulatorCards = cards.filter((c) => c?.type === "simulator_card");
              const otherCards = cards.filter(
                (c) => c?.type !== "timeline_card" && c?.type !== "simulator_card"
              );

              return (
                <div key={m.id || idx}>
                  {/* ✅ Timeline graphic FIRST (before assistant bubble) */}
                  {m.role === "assistant" && timelineCards.length > 0 && (
                    <div style={{ marginBottom: 10 }}>
                      {timelineCards.map((card, cIdx) => (
                        <TimelineCard key={`tl-${idx}-${cIdx}`} payload={card.payload} />
                      ))}
                    </div>
                  )}

                    {m.role === "assistant" && statsCards.length > 0 && (
                      <div style={{ marginBottom: 10 }}>
                        {statsCards.map((card, cIdx) => (
                          <StatsCard key={`st-${idx}-${cIdx}`} payload={card.payload} />
                        ))}
                      </div>
                    )}


                  {/* Bubble (wordy explanation) */}
                  <div className={m.role === "user" ? "bubble userBubble" : "bubble botBubble"}>
                    {m.content}
                  </div>

                  {/* ✅ Simulator card AFTER bubble (so it feels like “try it now”) */}
                  {m.role === "assistant" && simulatorCards.length > 0 && (
                    <div style={{ marginTop: 10 }}>
                      {simulatorCards.map((card, cIdx) => (
                        <SimulatorCard key={`sim-${idx}-${cIdx}`} payload={card.payload} />
                      ))}
                    </div>
                  )}

                  {/* Any future card types */}
                  {m.role === "assistant" && otherCards.length > 0 && (
                    <div style={{ marginTop: 10 }}>
                      {otherCards.map((card, cIdx) => null)}
                    </div>
                  )}
                </div>
              );
            })}

            {loading && !isAnalyzingStats && (
              <div className="bubble botBubble subtle">Thinking…</div>
            )}
            <div ref={bottomRef} />
          </div>
        </div>

        {/* Dock */}
        <div className="dock">
          {error && <div className="errorInline">{error}</div>}

          {!activeCaseId && (
            <div className="dockRow">
              <input
                className="dockInput"
                value={caseId}
                onChange={(e) => setCaseId(e.target.value)}
                placeholder="Enter case ID"
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleSetCase();
                }}
              />
              <button
                className="sendBtn"
                onClick={handleSetCase}
                disabled={loading || !trimmedCaseId}
                title="Set case"
              >
                <svg className="sendIcon" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
                  <path
                    d="M3 12L21 12M15 6L21 12L15 18"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </button>
            </div>
          )}

          {activeCaseId && (
            <>
              <div className="dockRow activeCaseRow">
                <div className="activeCasePill">Active case: {activeCaseId}</div>
                <div />
              </div>

              <div className="dockRow">
                <input
                  className="dockInput"
                  value={draft}
                  onChange={(e) => setDraft(e.target.value)}
                  placeholder="Ask a follow-up…"
                  onKeyDown={(e) => {
                    if (e.key === "Enter") handleSendMessage();
                  }}
                />
                <button
                  className="sendBtn"
                  onClick={handleSendMessage}
                  disabled={loading || !trimmedDraft}
                  title="Send"
                >
                  <svg className="sendIcon" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">
                    <path
                      d="M3 12L21 12M15 6L21 12L15 18"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
