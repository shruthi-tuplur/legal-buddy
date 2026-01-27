flowchart LR
  U[User] --> FE[React Frontend]

  FE -->|POST /chat\n{session_id, case_id?, user_message}| API[FastAPI Backend]

  API -->|fetch_case_by_id(case_id)| CC1[Cook County Case API]
  API -->|build_llm_context_pack(case_data)| CTX[Context Pack Builder]
  CTX --> API

  API -->|call_llm_with_context_pack(context_pack + history)| LLM[LLM Provider]
  LLM -->|explanation text| API

  API -->|optional: build_timeline(context_pack)| TL[Timeline Builder]
  API -->|optional: get_sim_tree_v1 + pick_root_for_stage| SIM[Simulator Tree Loader]
  API -->|optional: compute_comparison_stats_for_user_context| STATS[Stats Service]
  STATS --> CC2[Socrata Dispositions API]

  API -->|JSON: explanation + ui_cards[]| FE
  FE -->|Render bubbles + cards| U
