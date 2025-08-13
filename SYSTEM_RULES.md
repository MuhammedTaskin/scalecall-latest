Alright—clean slate, in English, no canvas. Here’s a from-scratch blueprint you can hand to a coding agent and build in 2–3 days on an M3 Pro, offline-first.

Telco Agent — Blueprint (M3 Pro · React · Offline-First)

0) Goals & Constraints
	•	Goal (demo): End-to-end eSIM flow in Turkish: verify → device check → issue LPA code → guided activation → status “active”.
	•	Device: MacBook M3 Pro. No paid/closed services. Everything local/offline.
	•	Model: Single LLM orchestrator with Function Calling + Prompt-Swap Handoff (persona switch, same context).
	•	Voice: XTTS-v2 only (no Piper). Press-to-Talk (PTT) for STT; Interrupt button to stop TTS.
	•	UI: Minimal/premium React; right-side event feed; persona badge & handoff animation.
	•	Latency targets: first token ≤1.5s (best-effort), post-tool reply ≤2.5s.

⸻

1) Tech Stack
	•	Backend: Python 3.11, FastAPI (ASGI), WebSocket streaming.
	•	LLM: Gemma-3 4B Instruct (MLX, 4-bit) as primary (on-device), streaming.
	•	Optional alt: Gemma-3n E4B (Transformers, 4-bit) behind the same ABI.
	•	STT: whisper.cpp (CoreML) or faster-whisper (small/base). Triggered by PTT only.
	•	TTS: XTTS-v2; sentence/phrase chunks queued to the browser.
	•	Data: SQLite (seeded from JSON); easy swap to Supabase OSS later.
	•	Frontend: Vite + React + TypeScript, Tailwind (utility-only), Radix Primitives (a11y). No heavy UI kits.

⸻

2) Repository Layout

telecom-agent/
  backend/
    app.py                  # FastAPI + REST + WS
    orchestrator.py         # streaming, function-calls, prompt-swap handoff
    llm_abi.py              # provider-neutral LLM wrapper (mlx | hf)
    stt_service.py          # whisper.cpp or faster-whisper bridge
    tts_service.py          # XTTS-v2 server or local bridge
    tools/
      registry.py           # tool schemas, allowlist, adapters
      telecom.py            # your existing tool impls (normalized)
      esim_extra.py         # get_activation_status, get_activation_steps, etc.
    db.py                   # SQLite models + seed
    prompts.py              # system + persona prompts
    eval_runner.py          # >=100 scripted tests + KPI report
  frontend/
    index.html
    src/
      main.tsx
      App.tsx
      lib/ws.ts             # WS client
      lib/audio.ts          # audio queue: play(), stop(), enqueue()
      components/
        Chat.tsx            # user/agent bubbles, streaming text
        EventFeed.tsx       # tool_call/results, handoff tags, tts events
        PersonaBadge.tsx    # Router/Tech/Plan/Billing handoff
        MicButton.tsx       # PTT (hold to record) + visual state
        Interrupt.tsx       # Stop TTS now
      styles/tokens.css     # minimal design tokens
  data/
    users.json
    packages.json
  scripts/
    run_local.sh
  README.md


⸻

3) Orchestrator Contract

class Orchestrator:
    async def stream(self, messages: list[dict]) -> AsyncIterator[dict]:
        """
        Yields either:
          {"delta": "text"}  # partial model text
        or
          {"tool_call": {"id": "...", "name": "verify_user", "arguments": {...}}}
        or
          {"handoff": {"persona": "TechAgent"}}
        """

    def feed_tool_result(self, call_id: str, result: dict) -> None:
        """Inject tool result back into the ongoing conversation context."""

Function Calling (strict)
When the model needs a tool, it must emit only:

{"tool_call": {"id":"uuid","name":"<tool>","arguments":{...}}}

No prose. After backend calls the tool and replies:

{"tool_result": {"id":"same-uuid","name":"<tool>","result": {...}}}

the orchestrator continues streaming deltas or next tool calls.

Prompt-Swap Handoff
Model can request persona change:

{"handoff": {"persona":"TechAgent"}}

Backend swaps the system prompt to the persona prompt and continues with the same history.

⸻

4) Tools (distinct & minimal)

Keep yours, but normalize returns to a single type:
OperationResult { success: bool, data?: object, error?: string }

Required set for the eSIM demo:
	1.	verify_user(maiden_name, msisdn) → verificateUser
	2.	get_user_info(customer_id) → getUserInfo
	3.	check_device_registration(imei) → checkDeviceRegistration
	4.	reissue_activation_code(customer_id) → reissueActivationCode (returns LPA:1$…)
	5.	get_activation_steps(os_type) → (new) deterministic iOS/Android steps
	6.	get_activation_status(customer_id) → (new) state machine: pending→downloading→installing→active
	7.	get_available_packages(country_code|user_id) → getAvailablePackages
	8.	change_package(customer_id, package_id) → changePackage
	9.	create_support_ticket(customer_id, subject, description, priority) → createSupportTicket

Schema example (per tool)

{
  "name": "reissue_activation_code",
  "description": "Issue a new eSIM activation code (LPA).",
  "parameters": {
    "type": "object",
    "properties": { "customer_id": {"type":"string"} },
    "required": ["customer_id"]
  }
}

PII & Safety
	•	Mask MSISDN/IMEI in logs/UI. Never read tokens/OTP aloud.
	•	On tool failure: short apology + next best action.

⸻

5) Data Model (SQLite)
	•	users(id, name, msisdn, …) — seed from data/users.json.
	•	packages(id, name, price, data, …) — seed from data/packages.json.
	•	sessions(id, user_id, started_at, ended_at, transcript_json)
	•	tool_calls(id, session_id, name, args_json, result_json, ts)
	•	memories(user_id, tone_pref, last_intent, updated_at) (lightweight, optional)
	•	tickets(ticket_id, customer_id, subject, status, priority, created_at)

⸻

6) Voice Pipeline (simplified)
	•	No automatic barge-in.
	•	PTT flow: user holds MicButton → audio captured → STT → text sent; release ends segment.
	•	TTS flow: backend returns sentence/phrase chunks (URLs or PCM blobs) → audio.ts queue plays them.
	•	Interrupt: prominent button; stops any playing audio instantly.
	•	Web: enable echoCancellation/noiseSuppression/autoGainControl on getUserMedia.

⸻

7) WebSocket Protocol (frontend↔backend)

Client → Server

{"type":"user_text","text":"..."}            // text input
{"type":"user_audio_start"}                  // PTT pressed
{"type":"user_audio_chunk","pcm":"base64"}   // audio chunk
{"type":"user_audio_end"}                    // PTT released
{"type":"interrupt"}                         // stop TTS immediately

Server → Client

{"type":"model_delta","text":"..."}                  // token stream
{"type":"tool_call","id":"...","name":"...","args":{}} 
{"type":"tool_result","id":"...","name":"...","result":{}} 
{"type":"handoff","persona":"TechAgent"}
{"type":"tts_chunk","url":"/audio/<id>.wav"}         // or inline base64
{"type":"event","name":"kpi","data":{"first_token_ms":...}}


⸻

8) Frontend (React) — Components & Responsibilities
	•	App.tsx: layout, routes (single page), WS lifecycle, global state.
	•	Chat.tsx: message list + streaming tokens; submit text; show STT transcript on send.
	•	EventFeed.tsx: append tool_call/result, handoff, tts events in a collapsible list.
	•	PersonaBadge.tsx: current persona with subtle fade/slide on change.
	•	MicButton.tsx: PTT recording with waveform/ring; disabled while TTS playing (optional).
	•	Interrupt.tsx: big “Stop” button; sends interrupt.
	•	lib/ws.ts: auto-reconnect, message send helpers.
	•	lib/audio.ts: queue with enqueue(blob|url), play(), stop(), emits onStart/onEnd.

Design: monochrome + single accent, Inter/IBM Plex, large line-height, soft shadows, 120ms transitions. No gradients. No clutter.

⸻

9) System & Persona Prompts (English; model answers in Turkish)

System

You are RouterAgent, an on-device telecom assistant.
Use function calls to act. Keep replies in Turkish and ≤2 sentences.
Rules:
- Verify user first (verify_user) before revealing account data.
- Choose tools dynamically; avoid rigid flows.
- After each tool_call, wait for the tool_result before continuing.
- If the topic changes, suspend the old thread and handle the new intent.
- Never expose raw payloads, secrets, or tokens. Summarize politely.
- Fix obvious ASR confusions by context (e.g., “mevsim” → “eSIM” in SIM contexts).
- If a specialist is better, request HANDOFF(persona) and continue with the same context.
Allowed tools: verify_user, get_user_info, check_device_registration,
reissue_activation_code, get_activation_steps, get_activation_status,
get_available_packages, change_package, create_support_ticket.

Persona notes

TechAgent: device/coverage/activation; crisp diagnostics and steps.
PlanAgent: tariffs; list 2–3 options max, confirm before acting.
BillingAgent: payments/contract; explain constraints and alternatives.
FAQAgent: generic info; keep it tight.

Handoff policy

Emit {"handoff":{"persona":"TechAgent"}} to switch persona. Continue with same history.

Function-calling policy

Emit exactly {"tool_call":{"id":"...","name":"<tool>","arguments":{...}}}
Then wait for {"tool_result":...} before continuing.


⸻

10) KPIs & Eval
	•	Metrics: SuccessRate, ToolAccuracy, FirstTokenLatency, TaskLatency, Steps, ErrorRecovery.
	•	Dataset: eval/*.yaml with ≥100 varied cases (intent, interruptions, errors).
	•	Report: reports/benchmark.md aggregated stats.

⸻

11) Security & Ops
	•	Allowlist tool names; JSON-schema validate args.
	•	Mask PII in logs/UI; never output tokens/OTP.
	•	Rate-limit: reissue_activation_code ≤3/day per user.
	•	Daily JSON backup & audit logs.

⸻

12) Day-by-Day Plan

Day 1
	•	WS skeleton; Orchestrator (stream + tool_call parse + tool_result feed + handoff).
	•	Tool registry with schemas; adapt your existing tools to OperationResult.
	•	React shell (App, Chat, EventFeed, PersonaBadge) + minimal styles.

Day 2
	•	MLX Gemma-3 4B streaming provider; XTTS-v2 playback queue; PTT STT.
	•	eSIM flow end-to-end (verify → device → LPA → steps → status=active).
	•	PII masking + error messages.

Day 3 (buffer)
	•	100-case eval & KPI report; polish UI; short demo video recording.

⸻

13) Acceptance Criteria
	•	Single model does Function Calling and Prompt-Swap Handoff; events visible in EventFeed.
	•	eSIM flow completes end-to-end with realistic tool results.
	•	XTTS-v2 plays sentence chunks; Interrupt stops immediately.
	•	STT works via PTT; transcript is shown before send.
	•	All tools return OperationResult; errors summarized politely; PII masked.
	•	KPI report generated from ≥100 eval cases.

⸻

14) Runbook (local)

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
# then: npm create vite@latest frontend -- --template react-ts
# install tailwind + radix; run dev server; open http://localhost:5173

requirements.txt (core):

fastapi
uvicorn[standard]
sqlalchemy
pydantic
websockets
whispercpp-python  # or faster-whisper
coqui-tts          # XTTS-v2
numpy