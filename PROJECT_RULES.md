🚀 INITIAL PROMPT — BUILD & SHIP: Telco Agent (M3 Pro · React · Offline-First)

You are an elite, fully autonomous coding agent. Your mission: build a premium, minimal, end-to-end eSIM call-center agent in 2–3 days on an M3 Pro, offline-first, with no paid/closed services. You will design, implement, test, and polish. If anything is underspecified, decide fast, choose the simplest robust solution, and keep moving. Your north star: working demo that looks premium and “just works.” Crush it.

0) Non-negotiables (read carefully)
	•	Single LLM orchestrator with Function Calling + Prompt-Swap Handoff (persona switch, context preserved).
	•	Model: Gemma-3 4B Instruct via MLX, 4-bit, streaming on device (M3 Pro).
	•	STT: Whisper (either whisper.cpp/CoreML or faster-whisper). PTT (press-to-talk) only.
	•	TTS: XTTS-v2 only. No Piper fallback. Stream sentence/phrase chunks.
	•	Barge-in: No automatic barge-in. Provide a big Interrupt button that immediately stops TTS.
	•	Frontend: React + TypeScript (Vite), Tailwind (utility-only), Radix Primitives. Minimal, premium design.
	•	Tools: distinct capabilities, OperationResult shape. Realistic mock logic, graceful errors.
	•	PII: mask in logs/UI; never speak tokens/OTP.
	•	No paid/closed APIs. Everything runs local.
	•	Deliver a demo that does: verify → device check → LPA code → guided activation → status “active”.

1) Repo Layout (create now)

telecom-agent/
  backend/
    app.py                  # FastAPI + REST + WebSocket
    orchestrator.py         # streaming, function-calls, prompt-swap handoff
    llm_abi.py              # MLX Gemma-3 4B 4-bit provider (streaming)
    stt_service.py          # whisper.cpp or faster-whisper bridge (PTT)
    tts_service.py          # XTTS-v2 worker; chunked playback endpoints
    tools/
      registry.py           # JSON schemas + allowlist + dispatcher
      telecom.py            # tool implementations (OperationResult)
      esim_extra.py         # get_activation_steps/status (state machine)
    db.py                   # SQLite + seed from /data/*.json
    prompts.py              # system + persona prompts
    eval_runner.py          # >=100 eval cases + KPI report
  frontend/
    index.html
    src/
      main.tsx
      App.tsx
      lib/ws.ts             # WS client (auto-reconnect)
      lib/audio.ts          # queue: enqueue(blob|url), play(), stop()
      components/
        Chat.tsx            # streaming text bubbles (TR)
        EventFeed.tsx       # tool_call/result, handoff, tts events
        PersonaBadge.tsx    # Router/Tech/Plan/Billing (handoff animation)
        MicButton.tsx       # PTT (hold to record), ring/waveform
        Interrupt.tsx       # big STOP; kills TTS instantly
      styles/tokens.css     # typography/spacing/colors
  data/
    users.json
    packages.json
  scripts/
    run_local.sh
  README.md

2) Orchestrator ABI & Protocol
	•	Function Calling: Model emits only this JSON when it needs a tool:

{"tool_call":{"id":"uuid","name":"<tool>","arguments":{}}}

No prose around it. After you call the tool, feed:

{"tool_result":{"id":"same-uuid","name":"<tool>","result":{}}}

Then continue streaming deltas or the next tool_call.

	•	Prompt-Swap Handoff: Model can request persona change:

{"handoff":{"persona":"TechAgent"}}

Swap the system prompt to that persona, preserve chat history, continue.

	•	WebSocket messages
	•	Client→Server: user_text, user_audio_start/chunk/end, interrupt
	•	Server→Client: model_delta, tool_call, tool_result, handoff, tts_chunk, event{kpi|info}

3) System & Persona Prompts (English system; model replies Turkish)

System (RouterAgent)
	•	Keep Turkish replies ≤2 sentences.
	•	Always verify first (verify_user) before exposing account data.
	•	Choose tools dynamically; no hardcoded flows.
	•	After each tool_call, WAIT for tool_result.
	•	If topic changes, suspend old thread and handle new one.
	•	Never expose raw payloads/secrets; summarize politely.
	•	Fix obvious ASR mixups by context (e.g., “mevsim”→“eSIM” in SIM/plan contexts).
	•	If a specialist is better, emit {"handoff":{"persona":"TechAgent|PlanAgent|BillingAgent|FAQAgent"}} and continue.

Persona notes
	•	TechAgent: device/coverage/activation; crisp steps.
	•	PlanAgent: tariffs; list 2–3 options, confirm before acting.
	•	BillingAgent: payment/contract constraints; offer alternatives.
	•	FAQAgent: general info; be brief.

4) Tools (distinct; implement in backend/tools)

All must return:

OperationResult = {"success": bool, "data": dict|None, "error": str|None}

Required set
	1.	verify_user(maiden_name, msisdn) → checks credentials, returns {token, customer_id, name} (mask logs!)
	2.	get_user_info(customer_id) → package, contract_end, payment_status, device, metadata
	3.	check_device_registration(imei) → registered/unregistered + activation_status
	4.	reissue_activation_code(customer_id) → returns fresh LPA:1$...
	5.	get_activation_steps(os_type) → deterministic iOS/Android steps (plain text list)
	6.	get_activation_status(customer_id) → state machine pending→downloading→installing→active with timestamps
	7.	get_available_packages(country_code|user_id) → array of plans
	8.	change_package(customer_id, package_id) → price delta + confirmation
	9.	create_support_ticket(customer_id, subject, description, priority) → ticket id/status

JSON schema example (per tool)

{"name":"reissue_activation_code","description":"Issue new eSIM LPA code",
 "parameters":{"type":"object","properties":{"customer_id":{"type":"string"}},"required":["customer_id"]}}

Safety
	•	Mask MSISDN/IMEI in logs/UI; never output tokens/OTP.
	•	On errors: short apology + next step; never raw stack traces.

5) Data Layer
	•	SQLite via SQLAlchemy. Seed from data/users.json, data/packages.json.
	•	Tables: users, packages, sessions, tool_calls, tickets, memories(optional).

6) LLM Provider (MLX Gemma-3 4B 4-bit)
	•	llm_abi.py: expose async streaming with partial token deltas; detect function-call JSON; yield {delta} or {tool_call} or {handoff}.
	•	Keep provider-neutral ABI for future swap.

7) Voice Pipeline (simple & robust)
	•	STT: PTT only. On user_audio_start begin buffering; on user_audio_end decode via Whisper; send user_text.
	•	TTS: Backend sends sentence/phrase chunks from XTTS-v2 (URLs or base64 PCM).
	•	Interrupt: If client sends interrupt, stop playback immediately in lib/audio.ts and cancel any in-flight chunks.
	•	Enable echoCancellation, noiseSuppression, autoGainControl in getUserMedia.

8) Frontend (React)
	•	Minimal/premium: monochrome + single accent; Inter/IBM Plex; generous whitespace; subtle shadows; 120ms transitions.
	•	Components:
	•	Chat.tsx: stream tokens, show STT transcript, input box.
	•	EventFeed.tsx: every tool_call/result, handoff, tts event in a collapsible list.
	•	PersonaBadge.tsx: current persona; soft fade/slide on change.
	•	MicButton.tsx: hold-to-talk with waveform; disabled while sending.
	•	Interrupt.tsx: big STOP button visible during TTS.

9) KPIs & Eval
	•	Build eval_runner.py with ≥100 cases.
	•	Metrics: SuccessRate, ToolAccuracy, FirstTokenLatency, TaskLatency, Steps, ErrorRecovery.
	•	Output reports/benchmark.md with aggregates.

10) Acceptance Criteria (must pass)
	•	Single model performs Function Calling and Prompt-Swap Handoff; events visible in EventFeed.
	•	eSIM flow completes: verify → device → LPA → steps → status=active (all via tools).
	•	XTTS-v2 plays sentence/phrase chunks; Interrupt stops instantly.
	•	PTT STT works; transcript shown before send.
	•	All tools return OperationResult; PII masked; errors summarized politely.
	•	eval_runner.py produces KPI report over ≥100 cases.
	•	UI: premium/minimal; no clutter; persona handoff animation.

11) Runbook

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload

# frontend
cd frontend
npm i
npm run dev  # Vite dev server

requirements.txt (core)

fastapi
uvicorn[standard]
sqlalchemy
pydantic
websockets
faster-whisper    # or whispercpp-python
coqui-tts         # XTTS-v2
numpy

12) Autonomy Rules (go fast)
	•	You have full autonomy to create/rename files, add small deps, and restructure for clarity.
	•	If a spec detail is missing, pick the simplest solution that gets us to the demo today.
	•	Never wait for permission. Prefer working, clean, documented code over “perfect later.”
	•	When blocked, stub and move on, add a TODO with a small test.
	•	Produce concise commit messages and a crisp README.md.

13) Deliverables
	1.	Running backend + React frontend matching the spec.
	2.	README.md with setup/run instructions and 1-minute demo script.
	3.	reports/benchmark.md with KPI results.
	4.	Short list of future work (RAG, autoscaling, memory enrichment).

14) Demo Script (what the UI should showcase)
	•	User: “eSIM almak istiyorum.”
	•	Agent: verifies user (tool) → fetches user info (tool).
	•	TechAgent handoff → checks device by IMEI (tool).
	•	Issues LPA code (tool) → shows activation steps for iOS (tool).
	•	Polls activation status to “active” (tool).
	•	(Optional) PlanAgent suggests 2 plans; user confirms; change_package (tool).
	•	EventFeed shows every tool_call/result + handoff; persona badge animates.
	•	Interrupt button stops TTS instantly; PTT captures next utterance.

Now build. Ship fast. Keep it elegant.