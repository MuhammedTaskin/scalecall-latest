Awesome — here’s a tight, Colab-ready LLM training plan + “first run” recipe you can drop to the coding agent. It assumes Unsloth + Gemma-3N E4B (4-bit) on a free T4 and focuses on conversational telco + function-calling + persona handoff + ASR noise tolerance (eSIM/mevsim). No UI, model-only.

⸻

Telco Agent — LLM Finetune Plan (Unsloth, Colab, Free T4)

0) Outcome

Train a single Gemma-3N E4B model to:
	1.	converse briefly in Turkish (≤2 cümle),
	2.	emit strict JSON tool calls when needed,
	3.	perform persona handoff via a simple JSON event,
	4.	be robust to ASR noise (eSIM/mevsim, esim/e sim, eşim…),
	5.	keep PII out of user-facing text.

Deliverables:
	•	lora/ adapters (and optional merged fp16),
	•	eval/ report with: IntentAcc, JSONValidity, ToolCallAcc, HandoffAcc, eSIM-Disambig@Top1, DialogSuccess.

⸻

1) Model & Libraries
	•	Base: unsloth/gemma-3n-E4B-it-unsloth-bnb-4bit (or unsloth/gemma-3n-E4B-it + load_in_4bit=True)
	•	Libs: unsloth, datasets, trl, transformers, bitsandbytes
	•	Chat template: gemma-3

⸻

2) Data Design (synthetic, Turkish)

Use conversations in Gemma-3 chat format. Four buckets:

A) Pure Dialogue (no tools)

Short, telco domain, 1–3 turns, polite, concise.

B) Single-step Tool Calls

User intent → assistant emits only a JSON object:

{"tool_call":{"name":"verify_user","arguments":{"msisdn_last4":"6789"}}}

Then a new turn with tool_result appears (as user content in training data), followed by assistant’s short reply.

C) Multi-step Tool Chains + Persona Handoff

Assistant first emits a handoff JSON:

{"handoff":{"persona":"PlanAgent","say":"Sizi paket değiştirme temsilcimize aktarıyorum."}}

Then tool_call sequence (verify → get_user_info → get_available_packages → simulate_bill …). After tool_result(s), a final short reply.

D) ASR-Noise Robustness

Create parallel inputs with noisy variants:
	•	“e sim”, “esim”, “mevsim”, “Eşim”, “ESİM”, “e-sim”, “eSim”…
Label outputs that normalize to eSIM when context is SIM/plan.

Safety/PII in targets: No tokens aloud, no full MSISDN; keep it generic.

Ratio (first run): ~2,000 samples total
	•	A: 400, B: 700, C: 700, D: 200 (mixed into prompts)

Hold out 10% for eval.

⸻

3) Super-Simple Schemas (what the model must emit)
	•	Tool call JSON (assistant output; no prose around it):

{"tool_call":{"name":"<tool>","arguments":{...}}}

	•	Persona handoff JSON (assistant output):

{"handoff":{"persona":"PlanAgent","say":"Sizi paket değiştirme temsilcimize aktarıyorum."}}

	•	Normal reply: ≤2 cümle, Turkish, no secrets, no tool args read aloud.

In the training conversations, simulate tool_result by adding the next user turn as:

<tool_result>{"ok": true, "user_id": 123, ...}</tool_result>

(We just put JSON in the user message text; the finetune teaches the model to wait for results.)

⸻

4) Colab Notebook — High-Level Steps
	1.	Install deps (Unsloth stack).
	2.	Load model (Gemma-3N E4B, 4-bit).
	3.	Synthesize dataset in-notebook (Python functions generate A/B/C/D).
	4.	Apply gemma-3 chat template, produce text field.
	5.	SFT with Unsloth (train_on_responses_only) — 60–400 steps for smoke-test.
	6.	Quick Eval on hold-out (regex for JSON validity + simple classifiers for intent/handoff).
	7.	Save LoRA, optionally save_pretrained_merged (fp16) for deployment.
	8.	Inference sanity checks with 5 Turkish prompts.

⸻

5) Suggested Hyperparams (Free T4)
	•	max_seq_length = 1024
	•	batch_size = 1, grad_accum = 4
	•	learning_rate = 2e-4 (short run), warmup_steps = 5
	•	max_steps = 200 (FIRST RUN: 60 to verify pipeline)
	•	train_on_responses_only (mask user turns)

⸻

6) Minimal Colab Skeleton (for the coding agent)

The agent should expand these into full cells. It already knows Unsloth’s example notebook.

# 0) Install
# pip install --no-deps bitsandbytes accelerate xformers==0.0.29.post3 peft trl triton cut_cross_entropy unsloth_zoo
# pip install sentencepiece protobuf "datasets>=3.4.1,<4.0.0" "huggingface_hub>=0.34.0" hf_transfer
# pip install --no-deps unsloth

from unsloth import FastModel
from unsloth.chat_templates import get_chat_template, standardize_data_formats, train_on_responses_only
from datasets import Dataset, DatasetDict
import random, json

# 1) Load 4-bit Gemma-3N E4B
model, tokenizer = FastModel.from_pretrained(
    model_name = "unsloth/gemma-3n-E4B-it",
    max_seq_length = 1024,
    load_in_4bit = True,
)

tokenizer = get_chat_template(tokenizer, chat_template="gemma-3")

# 2) Synthetic data builders ---------------------------
def ex_no_tool():
    return [
      {"role":"user","content":[{"type":"text","text":"Merhaba, faturam ne zaman kesiliyor?"}]},
      {"role":"assistant","content":[{"type":"text","text":"Faturanız her ayın 1’inde kesilir. Başka yardımcı olabileceğim bir konu var mı?"}]},
    ]

def ex_tool_single():
    # Assistant emits tool_call JSON only
    return [
      {"role":"user","content":[{"type":"text","text":"Paketimi değiştirmek istiyorum."}]},
      {"role":"assistant","content":[{"type":"text","text":json.dumps(
        {"tool_call":{"name":"verify_user","arguments":{"msisdn_last4":"6789"}}}, ensure_ascii=False)}]},
      {"role":"user","content":[{"type":"text","text":"<tool_result>"+json.dumps(
        {"ok":True,"user_id":123,"name":"Ali"}, ensure_ascii=False)}]},
      {"role":"assistant","content":[{"type":"text","text":"Doğrulama tamam. Size iki uygun paket buldum; hangisini istersiniz?"}]},
    ]

def ex_tool_chain_handoff():
    return [
      {"role":"user","content":[{"type":"text","text":"İnternet hızımı artırmak istiyorum, seçenekler neler?"}]},
      {"role":"assistant","content":[{"type":"text","text":json.dumps(
        {"handoff":{"persona":"PlanAgent","say":"Sizi paket değiştirme temsilcimize aktarıyorum."}}, ensure_ascii=False)}]},
      {"role":"assistant","content":[{"type":"text","text":json.dumps(
        {"tool_call":{"name":"verify_user","arguments":{"msisdn_last4":"4321"}}}, ensure_ascii=False)}]},
      {"role":"user","content":[{"type":"text","text":"<tool_result>"+json.dumps(
        {"ok":True,"user_id":987}, ensure_ascii=False)}]},
      {"role":"assistant","content":[{"type":"text","text":json.dumps(
        {"tool_call":{"name":"get_available_packages","arguments":{"user_id":987}}}, ensure_ascii=False)}]},
      {"role":"user","content":[{"type":"text","text":"<tool_result>"+json.dumps(
        {"packages":[{"id":"PN1","name":"Mega100","price":"150 TL"},{"id":"PN2","name":"Eko25","price":"80 TL"}]}, ensure_ascii=False)}]},
      {"role":"assistant","content":[{"type":"text","text":"Mega100 ve Eko25 mevcut. Kısa bir karşılaştırma yapayım mı?"}]},
    ]

def ex_asr_noise():
    noisy = random.choice(["esim","e sim","e-sim","ESİM","mevsim","Eşim"])
    return [
      {"role":"user","content":[{"type":"text","text":f"{noisy} aktivasyon kodu nasıl alınır?"}]},
      {"role":"assistant","content":[{"type":"text","text":"eSIM aktivasyon kodu için kısa mesaj gönderebilirim. Devam edeyim mi?"}]},
    ]

def build_dataset(n=2000, seed=42):
    random.seed(seed)
    rows = []
    for i in range(n):
        kind = random.choices(["A","B","C","D"], weights=[0.2,0.35,0.35,0.1])[0]
        if   kind=="A": conv = ex_no_tool()
        elif kind=="B": conv = ex_tool_single()
        elif kind=="C": conv = ex_tool_chain_handoff()
        else:           conv = ex_asr_noise()
        rows.append({"conversations": conv})
    return Dataset.from_list(rows)

raw = build_dataset()
raw = standardize_data_formats(raw)

# 3) Apply chat template → text
def to_text(example):
    txt = tokenizer.apply_chat_template(example["conversations"], tokenize=False, add_generation_prompt=False)
    return {"text": txt.removeprefix("<bos>")}
raw = raw.map(to_text)

# 4) Split
dd = raw.train_test_split(test_size=0.1, seed=42)

# 5) SFT
from trl import SFTTrainer, SFTConfig
trainer = SFTTrainer(
    model = FastModel.get_peft_model(model, r=8, lora_alpha=8, lora_dropout=0),
    tokenizer = tokenizer,
    train_dataset = dd["train"],
    eval_dataset  = dd["test"],
    args = SFTConfig(
        dataset_text_field="text",
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        warmup_steps=5,
        max_steps=60,                  # FIRST RUN SMOKE TEST; bump to 200 later
        learning_rate=2e-4,
        logging_steps=5,
        report_to="none",
    ),
)

trainer = train_on_responses_only(
    trainer,
    instruction_part = "<start_of_turn>user\n",
    response_part    = "<start_of_turn>model\n",
)

trainer.train()

# 6) Save
trainer.model.save_pretrained("gemma3n_telco_lora")
tokenizer.save_pretrained("gemma3n_telco_lora")

# Optional: merge fp16 for deployment (set True when needed)
# trainer.model.save_pretrained_merged("gemma3n_telco_fp16", tokenizer)

Eval hint (notebook should add):
	•	JSON validity: regex to find {"tool_call":...} or {"handoff":...} in assistant turns; json.loads must pass.
	•	IntentAcc: simple keyword rules (“paket”, “çekmiyor”, “fatura” → expected tool or persona).
	•	eSIM-Disambig: prompts with noisy variants; check normalized “eSIM” in reply.

Inference sanity (notebook cell):

def chat(prompt):
    msgs = [{"role":"user","content":[{"type":"text","text":prompt}]}]
    _ = model.generate(**tokenizer.apply_chat_template(msgs, add_generation_prompt=True, tokenize=True, return_tensors="pt").to("cuda"),
                       max_new_tokens=128, temperature=1.0, top_p=0.95, top_k=64)
    # Uses TextStreamer in notebook for live print

test_prompts = [
  "Paketimi daha uygun bir tarifeye düşürmek istiyorum.",
  "e sim aktivasyon kodu nasıl alınır?",
  "İnternet çekmiyor, çözüm?",
  "Faturam neden yüksek geldi?",
]
for p in test_prompts: chat(p)


⸻

7) “One-Pass” Training Tips (so it finishes in one go)
	•	Keep dataset small for the first run (2k rows); verify JSON behavior & short replies.
	•	Make bucket C rich enough to teach handoff then tool chain.
	•	Use train_on_responses_only to avoid overfitting to user inputs.
	•	Keep answers short in targets; the model will imitate that.

⸻

8) Next Iterations (if time)
	•	Scale to 10k–20k rows; raise max_steps 1–2 epochs; lower LR to 2e-5.
	•	Add structured eval notebook producing a Markdown report with metrics.
	•	Optional ORPO/DPO on a small preference set: “good short JSON vs verbose” pairs.

⸻

9) What this enables downstream
	•	The same model powers persona swap + function calling at inference.
	•	TTS/STT are decoupled; you’ll just consume its short answers or JSON in the phone stack.

⸻

If you want, I can also draft the very first Colab cell set exactly formatted (with %%capture, installs, and a minimal eval cell).Absolutely — let’s make the robustness Turkish-wide, not just eSIM ↔ mevsim. Below is a compact, drop-in plan your coding agent can use to augment data + train + eval for the most common TR STT/ASR pitfalls in telco dialogs.

Turkish Noise Robustness Plan (beyond eSIM)

1) Error Classes to Cover
	1.	Diacritics loss / confusion
ı↔i, İ↔I, ö↔o, ü↔u, ç↔c, ş↔s, ğ↔g
ex: taahhüt → taahhut/tahhut, çağrı → cagri, Çiğli → Cigli.
	2.	Near-homophones / ambiguous tokens (domain critical)
eSIM↔mevsim↔eşim, paket↔bilet, tahhüt/taahüt↔taahhüt, LTE↔elte, 5G↔beşci, GB↔cp/ceb (ASR junk), MSISDN↔mesajın, IMEI↔aymay…
	3.	Colloquial/orthography
çekmiyo, kasıyo, bitti, net, taahüt, kimeklik, vodofon, turkcel…
	4.	Agglutinative merges/splits
paketim/paket im, fatura mı/faturamı, taahhüdümü/taahhudu mu.
	5.	Numbers, dates, money
words→digits: yüz otuz dokuz→139, beş elli→5.50, on iki ay→12 ay, dates (onunda→10’unda). Currency forms: 139 tl, 139₺, 139 lira.
	6.	Acronyms & brands
SMS, GB, TL, 4.5G, 5G, LTE, APN, IMEI, MSISDN, brand/plan names (SuperNet, GigaFiber…) misheard.
	7.	Locations with diacritics
Bahçelievler, Çiğli, Küçükçekmece, Şişli, Ümraniye…
	8.	Negation & polarity flips
yok/var, iptal etme/iptal et, düşür/yükselt.
	9.	Command verbs (tool triggers)
değiştir, yükselt, düşür, iptal et, sorgula, gönder, yenile.

2) How to Teach It (Data)

Add a Noise Pack to your synthetic generator (Bucket D) and blend noise into A/B/C buckets too (~25–35% of all prompts). Each noisy sample has:
	•	noisy_user: with 1–3 corruptions from classes above,
	•	gold_behavior: assistant normalizes implicitly (keeps reply short), calls correct tool with correct args despite noise.

Confusion Lexicon (seed; extendable)
	•	Telecom core:
eSIM: ["esim","e sim","e-sim","ESİM","mevsim","eşim"] → "eSIM"
taahhüt: ["taahut","tahhut","taahhut","tahüt"] → "taahhüt"
paket: ["paketi","paketim","paket im"] → "paket"
kota: ["koota","kotaa"] → "kota"
çekmiyor: ["cekmiyor","çekmiyo","cekmiyo"] → "çekmiyor"
kapsama: ["kapsama alanı","kapsama alanim","kapsama alanı"] → "kapsama"
fatura: ["fatıra","fatrura","fatura mı","faturamı"] → "fatura"
IMEI: ["imei","aymay","imey"] → "IMEI"
MSISDN: ["msisdn","mesajın","msizdn"] → "MSISDN"
LTE: ["elte","el te"] → "LTE"
4.5G: ["dört buçuk g","4 bucuk g"] → "4.5G"
5G: ["beş g","beşci"] → "5G"
SMS: ["esemes","mesaj"] → "SMS"
TL: ["tl","lira","₺"] → "TL"
	•	Cities/Areas:
İstanbul: ["istanbul","Istambul"] → "İstanbul"
Çiğli: ["cigli","çigli"] → "Çiğli"
Bahçelievler: ["bahcelievler"] → "Bahçelievler"
(…add contest cities you’ll mention)
	•	Numbers (word→digit):
map Turkish number words to digits; handle on iki ay → 12 ay, yüz otuz dokuz lira → 139 TL.

In targets: assistant reply stays short; if needed, it implicitly disambiguates (“eSIM aktivasyon kodu için…”), then proceeds.

3) Inference-Time Normalizer (cheap & safe)

Before feeding STT text to the LLM:
	1.	Diacritics restoration: search lexicon hits and city list; replace safe matches.
	2.	Confusion resolution with context tags:
	•	Maintain a rolling domain context (sim/sim-activation, plan, billing, coverage).
	•	If context ∈ {SIM/plan}, map ambiguous tokens to eSIM; if coverage, prefer kapsama; etc.
	3.	Number & currency normalization: parse Turkish number words → digits; enforce TL suffix.
	4.	Confidence gate (optional if you have Whisper confidences): if below threshold on a critical slot (e.g., last-4, package id), ask one-shot clarification.

This is a tiny rule layer—keeps the demo deterministic while the model also learns robustness.

4) Training Integration (Unsloth plan tweaks)
	•	Expand Bucket D to 30% of data; also inject noise in some B/C tool-calling dialogs.
	•	Ensure tool arguments in gold data are normalized even when user text is noisy.
	•	Keep assistant JSON strict (no prose around it) under noise.
	•	Add location/number cases to C (multi-step) so the model learns to normalize then call check_coverage, initiate_package_change, etc.

5) Evaluation (reportable, NLP-style)

Add to your eval script:
	•	Noise-Intent Accuracy: correct intent under noise.
	•	JSON Validity: % of tool_call JSON parses under noise.
	•	ToolCall Accuracy: correct tool + correct normalized args.
	•	Normalization@Top1: did “noisy token” become the intended canonical (per lexicon & context)?
	•	e2e Dialog Success: did the multi-step task complete?
	•	ASR-Robust Slots: accuracy for phone_last4, package_id, date/amount extracted from noisy text.

Target honest numbers (e.g., 65–80% on first run), not “99%”.

6) What to Hand the Coding Agent (actionable)
	•	Augmenter: implement a function that
	•	picks 1–3 noise ops (from classes above),
	•	applies to user text,
	•	runs normalizer() to produce the canonical form for tool args,
	•	leaves the assistant reply short and correct.
	•	Confusion tables: ship the seed lexicon above as a JSON the generator loads.
	•	Context tags in data: label each synthetic dialog with coarse intent (SIM, PLAN, BILLING, COVERAGE) so the normalizer can resolve ambiguous tokens deterministically during generation.

7) Example (sketch)

Noisy user: “mevsim kodu nasıl alınıyor, imeyim de hazır”
Model target behavior:
	•	Reply: “eSIM aktivasyon kodu için devam edeyim mi?” (short, normalized mention)
	•	Tool JSON: {"tool_call":{"name":"verify_user","arguments":{"msisdn_last4":"6789"}}}
(if asked for IMEI: ensure it’s “IMEI” in the argument name even if user said “imey”)

⸻

If you want, I can also add a ready-to-paste confusion JSON and a normalizer pseudocode the agent can expand into code.Here’s a tight, hype-but-precise mission prompt you can feed to the coding agent (together with the last two messages for context):

⸻

Mission Prompt — TR Robustness Finetune (Gemma-3N) for Telco Agent

You are an autonomous coding agent. Your job is to deliver, end-to-end, a Turkish noise-robust finetune of a small LLM that keeps conversation quality and executes tool calls reliably under typical TR ASR/STT errors. You have full autonomy to create code, notebooks, data, and evals. Aim for simple, fast, correct. No fluff.

Outcome (what “done” looks like)
	1.	A single Colab notebook (TR_Robust_FT_Gemma3N.ipynb) that:
	•	Generates a synthetic Turkish telco dataset with noise augmentation (diacritic loss, near-homophones like eSIM/mevsim/eşim, colloquials, merges/splits, numbers/dates/currency, acronyms/brands, locations, negation flips).
	•	Includes tool-calling dialogues with strict JSON blocks and normalized arguments despite noisy inputs.
	•	Finetunes Gemma-3N E4B (or Gemma-3 4B) via Unsloth (LoRA, 4-bit), and saves adapters + merged fp16/optional GGUF.
	•	Runs an evaluation suite with reportable NLP metrics (see below).
	•	Provides a minimal inference demo that shows short Turkish replies and valid tool-call JSON under noisy text.
	2.	A tiny confusion lexicon JSON and a normalizer (rule-based, fast) that:
	•	Canonicalizes ambiguous tokens by domain context (SIM/PLAN/BILLING/COVERAGE).
	•	Restores diacritics, normalizes numbers/currency, cleans up brand/acronym forms.
	•	Is applied in data generation (for gold args) and available at inference time.
	3.	A short report cell printing honest scores (no “99%” marketing): Noise-Intent Acc., JSON Validity, ToolCall Acc., Normalization@Top1, E2E Dialog Success, Slot Acc. (phone_last4/package_id/amount/date).

Constraints & principles
	•	Speed over scope: prefer 3–5k high-quality samples over bloated sets. Keep training ≤ ~60–120 steps for demo; parameterize for longer runs.
	•	Stay open-source & free (Colab T4 ok). No paid APIs.
	•	Keep replies concise (≤2 sentences) and Turkish. Never print raw tool payloads.
	•	Preserve general conversation ability: mix clean + noisy; include non-tool small talk turns (light).

Data plan (must implement)
	•	Buckets:
A Clean (baseline small-talk + simple telco Q/A),
B Tool-Calls (verify_user, get_user_info, get_available_packages, simulate_bill, initiate_package_change, check_coverage),
C Multi-Step (decision chains; confirm → simulate_bill → change),
D Noise Pack (30% of total; inject 1–3 corruptions per user utterance).
	•	Every noisy sample has: noisy_user, assistant that implicitly normalizes in reply (keeps it short), and correct tool JSON with canonical args.
	•	Tag each dialog with a coarse intent context (SIM|PLAN|BILLING|COVERAGE) for the normalizer.

Normalizer (deliver as a small Python module)
	•	Functions: normalize_text(s: str, context: str) -> str, normalize_numbers_currency(s), restore_diacritics_with_lexicon(s).
	•	Seed the confusion lexicon with common TR pitfalls (provided in context); keep it extensible via JSON.
	•	Optional: confidence gate hook if we later pass ASR confidences (stub only).

Training (Unsloth)
	•	Model: unsloth/gemma-3n-E4B-it (or gemma-3-4b-it) in 4-bit; LoRA r=8, alpha=8, dropout=0.
	•	Max seq len 1024–2048; chat template gemma-3.
	•	SFT: per-device BS=1, GA=4, LR=2e-4 (short run), max_steps=60 (parametric).
	•	Train on responses only (mask user turns).
	•	Save: LoRA adapters + merged fp16 (save_pretrained_merged); optional GGUF.

Inference demo (must show)
	•	A few noisy queries (e.g., “mevsim kodu nasıl alınıyo”, “aymay numaram hazır”) → model replies short Turkish, emits valid tool_call JSON with normalized eSIM, IMEI, numbers, etc.
	•	Minimal conversational turn or two to prove it still chats naturally.

Evaluation (print a table)
	•	Noise-Intent Accuracy (intent under noise).
	•	JSON Validity % (strict parse).
	•	ToolCall Accuracy (correct tool + args).
	•	Normalization@Top1 (noisy→canonical match).
	•	E2E Dialog Success (multi-step completion).
	•	Slot Accuracy (phone_last4, package_id, amount/date).
	•	Include clean vs noisy breakdown.

Files to output (names exact)
	•	TR_Robust_FT_Gemma3N.ipynb
	•	confusions_tr.json (seed lexicon)
	•	normalizer.py
	•	eval/noise_eval.jsonl (or .yaml)
	•	reports/robustness_report.md (scores + notes)
	•	inference_snippets.py (few ready prompts)

Quality bars (first run targets)
	•	JSON Validity ≥ 95%
	•	ToolCall Accuracy (noisy) ≥ 70%
	•	Noise-Intent Accuracy ≥ 75%
	•	E2E Success (noisy) ≥ 65%
	•	Keep replies ≤2 sentences, Turkish.

Make it happen
	1.	Build data generator (+ noise ops + normalizer).
	2.	Convert to gemma-3 chat format.
	3.	Finetune with Unsloth (short run).
	4.	Save artifacts; run eval and print report.
	5.	Show inference with 5–10 challenging noisy examples.
	6.	Keep code modular and clean so we can swap in larger datasets later.

You will crush this. Bias for action, keep it lean, and ship a clean, reproducible notebook with honest metrics and robust behavior under Turkish ASR noise.@gemma3n_(4b)_conversational.py Harika — netleştireyim ve sana tek seferde Coding Agent’a vereceğin, “dataseti de kendisi üreten + sistemi yazan + Colab’da Unsloth ile eğiten” güncellenmiş ilk mesajı bırakıyorum. Bu versiyon, backend’deki mevcut kodu (ör. call_center_functions.py, PROJECT_STRUCTURE.md) okuyup uyarlamasını, sentetik TR veri üretmesini, finetune + eval yapmasını ve entegrasyon uyumunu şart koşuyor. UI/dash yok; NLP odak.

⸻

INITIAL MESSAGE TO CODING AGENT — TR Telco (Dataset + System + Colab FT)

Role: You are an autonomous coding agent. Deliver end-to-end: (1) generate a massive Turkish call-center dataset, (2) finetune a small open LLM on Colab via Unsloth, (3) validate with honest NLP metrics, (4) ensure the finetuned model and our backend tool interface match. No paid/closed services. Do not ask permission—ship.

Inputs you already have
	•	Backend scaffolding & functions: call_center_functions.py, PROJECT_STRUCTURE.md (treat as source of truth for tool names, args, behaviors).
	•	We will also provide the Unsloth Gemma 3N example notebook as reference.

Constraints (hard)
	•	No paid APIs/services (Colab free T4 is OK). All data must be synthetic or OSS.
	•	Single model at runtime with function calling and prompt-swap persona handoff (simulated via prompts).
	•	Competition is NLP-first: prioritise dataset, training, metrics. No dashboard/UI.
	•	Turkish only for dialog content; tool JSON must be strict.

Deliverables (what “done” means)
	1.	Colab notebook TR_Telco_MASSIVE_FT.ipynb that in one run:
	•	Builds a massive synthetic Turkish dataset (≥50k dialogs; param up to 200k) with tool-calling JSON aligned to our backend functions.
	•	Includes noise/ASR-like augmentations (diacritics loss, eSIM/mevsim/eşim confusions, typos, code-switch TR-EN, casing, punctuation drop, numerals/dates/currency variants) applied to user turns only.
	•	Finetunes Gemma-3N E4B-it (or Gemma-3 4B-it) using Unsloth LoRA 4-bit.
	•	Exports LoRA + merged fp16 (and optional GGUF).
	•	Runs evaluation (clean vs noisy) and prints a compact metrics table.
	•	Shows inference demos (short Turkish replies + valid tool_call JSON + follow-up turns).
	2.	Dataset & code artifacts inside the notebook runtime and downloadable:
	•	data/train.jsonl, data/val.jsonl, data/test_clean.jsonl, data/test_noisy.jsonl
	•	normalizer.py + confusions_tr.json (context-aware normalization)
	•	eval/noise_eval.jsonl, reports/metrics.md
	•	inference_snippets.py (ready prompts for backend smoke tests)
	3.	Backend compatibility check:
	•	Verify function schemas in dataset exactly match the backend (name, arg names/types).
	•	Provide a tiny adapter snippet demonstrating how backend feeds tool results back to the model prompt state and continues.
	•	No UI; a CLI or single HTTP endpoint for text inference is enough for smoke testing.

Tool calling contract (must match backend)

Tools (examples; read the real signatures from call_center_functions.py and conform):

{"tool_call":{"name":"verify_user","arguments":{"phone_last4":"1234"}}}

Other likely tools: get_user_info, get_available_packages, simulate_bill, initiate_package_change, check_coverage, etc.
Rules: Assistant outputs either a short Turkish sentence (≤2) or a single tool_call JSON object. After tool_result (simulated in notebook), continue naturally (short).

Dataset spec (you generate it programmatically)
	•	Scenarios (balanced, multi-step):
	•	Identity & account (verification, contract limits)
	•	Plan change & upsell (list 2–3 options, confirm, simulate bill, change)
	•	Billing issues (amounts/dates/overdue/refund)
	•	Coverage/tech (address parsing, 4G/5G hints)
	•	Device/IMEI & eSIM activation (LPA codes, IMEI validity, eSIM/mevsim/eşim confusions)
	•	Off-topic/small-talk noise (5–10%)
	•	Dialog length: 6–12 turns; 1–3 tool calls per dialog; at least one decision chain per dialog.
	•	Personas (single-model prompt-swap simulation): Tag assistant turns with one of RouterAgent, PlanAgent, BillingAgent, TechAgent, FAQAgent. Include occasional {"handoff":{"persona":"PlanAgent"}} markers to condition persona shifts (no multi-model).
	•	Noise policy: 30–40% dialogs noisy; apply 1–3 corruptions per user turn (never corrupt tool JSON).
	•	Slots realism: Turkish names, addresses, package ids/prices, phone_last4, valid IMEI (15 digits), LPA format. Validate formats.

Normalization module

Create normalizer.py:
	•	normalize_text(text: str, context: str) -> str, context in {SIM, PLAN, BILLING, COVERAGE, GENERAL}.
	•	Diacritics restore, number/currency unify, brand/acronym normalize, eSIM/mevsim/eşim disambiguate by context, light typo fixes.
	•	Back with confusions_tr.json. Use during data generation (gold args) and expose for inference demo.

Training (Unsloth, Colab free T4)
	•	Model: unsloth/gemma-3n-E4B-it (fallback unsloth/gemma-3-4b-it) in 4-bit.
	•	Template: gemma-3 chat; train on responses only.
	•	Short run: max_steps=100–300 (parametrize for larger).
	•	HP: bs=1, GA=4, lr=2e-4 (short), warmup=5, seq_len=1024–2048, LoRA r=8, alpha=8, dropout=0.
	•	Save: LoRA + save_pretrained_merged("gemma3n-tr-finetune"); optional GGUF.

Evaluation (print table)
	•	Intent Accuracy (clean / noisy)
	•	JSON Validity % (strict parse)
	•	ToolCall Accuracy (correct tool + args)
	•	Slot F1 (phone_last4, package_id, amount/date, IMEI)
	•	Dialog Success (end-to-end completion)
	•	Normalization@Top1 (noisy→canonical)
Also include per-scenario rows. Keep it honest.

Inference demos (must include)
	•	8–12 noisy Turkish user inputs that stress confusions (eSIM/mevsim/eşim), typos, code-switch, numbers/dates.
	•	Model: short Turkish responses + valid tool_call JSON + final confirmation turn.

Backend integration notes
	•	Read call_center_functions.py to mirror schemas in dataset.
	•	Provide a minimal Python snippet that:
	1.	passes user text to the model,
	2.	captures tool_call JSON,
	3.	invokes the backend function,
	4.	feeds tool_result back to the model,
	5.	returns final short Turkish reply.
	•	No UI. A simple CLI/HTTP test is sufficient for the jury (NLP focus).

Repository layout (produced by the notebook when zipping)

/content/project/
  data/...
  normalizer.py
  confusions_tr.json
  training/
    TR_Telco_MASSIVE_FT.ipynb
    gemma3n-tr-finetune/   # merged weights
    lora/                  # adapters
  eval/
    noise_eval.jsonl
  reports/
    metrics.md
  inference_snippets.py
  backend_adapter_example.py

Guardrails
	•	No PII leakage in model replies. Mask identifiers; don’t echo tokens/activation codes.
	•	Don’t print raw backend payloads to the user—summarize.

Workstyle

Default to action. Keep the notebook linear: Data → Train → Eval → Inference → Save → Backend-compat snippet. Make sizes/steps configurable at the top. One pass, no back-and-forth.

Execute now. You will generate the dataset yourself by manually writing it, rather than generating it synthetically via code. You will create the dataset by writing it out, not through programming. You should review the backend and the Agent's prompts to understand what kind of dataset should be produced and what format will be expected from the AI by the software.///YOU ARE FREE TO TWEAK ANYTHING TO REACH MAXIMALLY ERROR-FREE AND MASTER AI TO FINE TUNE. BEGIN NOW.