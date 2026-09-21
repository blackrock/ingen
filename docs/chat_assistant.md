# inChat — the local HuggingFace pipeline assistant

InGen Studio's chat ("inChat") lets you edit a pipeline in plain English. A small local model
(`Qwen/Qwen3-4B` by default, run in-process via HuggingFace `transformers`) does **one narrow job**:
read your request + the list of known columns, and return **two things** as JSON:

```json
{ "reply": "Adding three columns for you.", "ops": [ { "op": "add_columns", "cols": ["C1","C2","C3"] } ] }
```

- **`reply`** — one short, friendly sentence. Shown to you in the chat bubble. Conversation only.
- **`ops`** — a machine-readable list of edit operations. **This is the part that changes your config.**

### Two modes, one model (no separate agents)

The same model call covers both an "executor" and a "general queries" assistant — dispatched by
whether `ops` is empty, not by a second model or an orchestrator:

- **Edit mode** — the request maps to changes → `ops` is filled, applied deterministically.
- **Conversation mode** — a greeting or question ("hi", "what does this pipeline do?") → `ops: []`
  and `reply` carries the answer. The frontend shows the model's `reply` whenever an edit applied
  *or* there were no ops; it only falls back to the canned message when an edit was attempted but
  nothing changed (dedupe / unknown column) or the backend is down.

A true multi-agent setup (separate executor + router models) is overkill here — a 4B model handles
both jobs in a single round-trip.

## The model never writes YAML

This is the whole design. A 4B model is great at *classify-and-extract* ("which op, which columns")
and bad at authoring a strict YAML schema. So it never touches YAML. Instead:

1. The model emits `ops`. The backend parses the JSON out of the model's reply and drops any op that
   isn't in the known set, so callers always get a clean `{reply, ops}`.
2. The frontend's **rule-based applier** (`frontend/src/models/applyIntent.js`) maps each op onto the
   existing pure model mutators. `add_columns C1 C2 C3` → `listAdd('columns', ...)` for each, with
   dedupe and validation.
3. The existing **serializer** renders the YAML from the mutated model.

So the LLM picks the *intent*; deterministic Python/JS does the *construction*. If the model
hallucinates an unknown op or column, the applier drops/corrects it — the YAML can't be corrupted by
a bad model response.

## Supported ops

| op | args | effect |
|----|------|--------|
| `add_columns`   | `cols: [str]`        | add each column (deduped against existing) |
| `rename_column` | `from`, `to`         | rename, or add a src→dest mapping |
| `add_source`    | `name`, `type`       | type ∈ file, mysql, api, json |
| `add_filter`    | `col`, `val`         | drop rows where `col == val` (col must be a known column) |
| `set_output`    | `type`               | type ∈ delimited_file, excel, json, json_writer |
| `none`          | —                    | nothing matched |

One message can produce several ops, applied in order ("add columns A,B and drop status=inactive").

## Where the pieces live

| concern | file |
|---|---|
| model load + intent prompt + JSON extraction | `backend/app/chat.py` |
| HTTP routes (`/api/chat`, `/api/chat/warmup`) | `backend/app/main.py` |
| frontend client | `frontend/src/services/chatService.js` |
| op → model mutation (rule-based build) | `frontend/src/models/applyIntent.js` |
| regex fallback (used when backend is down) | `InterfaceChatEditor.jsx` |

## Running it

The model runs **inside the FastAPI backend process** — there's no separate model server. You only
need the InGen backend up:

```bash
pip install -r backend/requirements.txt
pip install torch --index-url https://download.pytorch.org/whl/cpu   # CPU build
uvicorn backend.app.main:app --reload --port 8000                    # from repo root
```

On first use the model weights download from the HuggingFace Hub (a few GB) and load into RAM. If the
backend is down, chat silently falls back to the regex parser (only a few exact patterns like
`add columns ...` work).

First message is slow (model load). The UI fires `/api/chat/warmup` when the chat opens, which loads
the model so subsequent messages are fast. The model stays resident for the life of the process.

### Model choice & RAM

Default is `Qwen/Qwen3-4B`. The model loads in **float32** (the fastest dtype on CPU — there are no
fast bf16/fp16 CPU kernels in transformers), so RAM ≈ params × 4 bytes. Budget for a 24–32 GB machine
at the default; 16 GB will swap. Override with `HF_CHAT_MODEL`:

| model | notes | RAM (fp32) |
|---|---|---|
| `Qwen/Qwen3-4B` | default, best open model for structured JSON | ~16 GB |
| `Qwen/Qwen2.5-7B-Instruct` | larger, higher quality | ~30 GB |
| `Qwen/Qwen2.5-3B-Instruct` | smaller, faster | ~12 GB |
| `Qwen/Qwen2.5-1.5B-Instruct` | fast, lightweight | ~6 GB |
| `HuggingFaceTB/SmolLM2-360M-Instruct` | smoke-test / very low RAM | ~1.4 GB |

All of the above are fully open and download automatically. Gemma models (`google/gemma-*`) are gated
and need an HF token + licence accept — avoid unless you have set that up.

### Getting good output from a small model

The model is a 4B running on CPU, so the invocation is tuned to make it reliable rather than relying on
raw capability (`backend/app/chat.py`):

- **Few-shot prompt** — the system turn is followed by worked input→JSON examples (multi-op edit,
  greeting, unsupported request) so the model copies the exact `{reply, ops}` shape.
- **Assistant prefill** — generation is seeded with `{"reply": "` so the model starts *inside* the JSON
  (no prose, no markdown fence, no stray `<think>`), then the prefill is stitched back before parsing.
- **Short generation** — `max_new_tokens=192` with `repetition_penalty=1.05`; payloads are tiny and this
  bounds latency and guards against greedy loops.
- **Bounded context** — the request carries the current YAML (capped at ~2.5 KB) plus the last few chat
  turns as plain-text context, so follow-ups ("now also add a filter") resolve without re-stating.

Recent dialogue is folded into the user turn as *text*, not replayed as real assistant turns — the stored
replies are human-facing prose, and feeding them back as assistant turns would teach the model to stop
emitting JSON. The few-shot pairs stay the only JSON exemplars.

### Config knobs (env)

| var | default | meaning |
|---|---|---|
| `HF_CHAT_MODEL` | `Qwen/Qwen3-4B` | HuggingFace model id to load |
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | backend base URL (frontend) |
