#  InGen wrapper — inChat intent extraction via a local HuggingFace model (pure logic).
#
#  The model NEVER writes YAML. It returns a small, schema-constrained {"reply", "ops"} object which
#  the frontend applies through its existing model mutators (then the real serializer renders YAML).
#  Uses AutoTokenizer + AutoModelForCausalLM directly so chat templates are applied correctly.
#  The model is loaded once at first call and kept resident (lazy init).
#
#  Default model: Qwen/Qwen3-4B  (4B params, open licence, chat-template).
#  Loaded in float32 (fastest dtype on CPU), so RAM ~= params x 4 bytes: ~16 GB for the 4B default.
#  Budget for a 24-32 GB machine; 16 GB will swap.
#
#  Other options (set HF_CHAT_MODEL env var), RAM in float32:
#    Qwen/Qwen3-4B                    — default, best open model for structured JSON (~16 GB RAM)
#    Qwen/Qwen2.5-7B-Instruct         — larger, higher quality             (~30 GB RAM)
#    Qwen/Qwen2.5-3B-Instruct         — smaller, faster                    (~12 GB RAM)
#    Qwen/Qwen2.5-1.5B-Instruct       — fast, lightweight                  (~6 GB RAM)
#    HuggingFaceTB/SmolLM2-360M-Instruct — smoke-test / very low RAM       (~1.4 GB RAM)
#
#  NOTE: All Gemma models (google/gemma-*) are GATED and require an HF token + licence accept.
#  All models above are fully open and download automatically from HuggingFace Hub.

import json
import os
import re
import threading

HF_MODEL = os.environ.get("HF_CHAT_MODEL", "Qwen/Qwen3-4B")

# The ops the executor (frontend/src/models/applyIntent.js `switch (op?.op)`) actually implements.
# THAT FILE IS THE AUTHORITY — if you add/remove a case there, mirror it here and in the prompt below.
OPS = {
    "add_columns", "remove_column", "rename_column",
    "add_source", "remove_source",
    "add_transform", "remove_transform",
    "add_filter", "set_output", "explain", "none",
}

SYSTEM_PROMPT = (
    "You are inChat, a friendly assistant for building data pipelines in InGen Studio. "
    "You help by emitting small edit operations that the app applies to the pipeline — "
    "you never write or rewrite YAML yourself.\n\n"
    'Respond with a single JSON object: {"reply": "<1-2 sentence reply>", '
    '"ops": [<ops in order, or empty>]}. Plain JSON is best, but if you wrap it in a ```json fence '
    "or add a short note around it, that's fine — it will be parsed out.\n\n"
    "Available ops:\n"
    '  {"op": "add_columns", "cols": ["c1", "c2"]}                 - add output columns\n'
    '  {"op": "remove_column", "name": "col"}                       - drop an output column\n'
    '  {"op": "rename_column", "from": "old", "to": "new"}          - rename a column\n'
    '  {"op": "add_source", "name": "id", "type": "file|mysql|api|json"}  - add a data source\n'
    '  {"op": "remove_source", "name": "id"}                        - remove a source everywhere\n'
    '  {"op": "add_transform", "type": "merge|outer_join|mask|not_equals_filter|union|melt|'
    'aggregate|drop_duplicates|json_array_expander"}  - add a pre-processing step\n'
    '  {"op": "remove_transform", "type": "<transform type>"}       - remove a pre-processing step '
    '(or pass {"index": N})\n'
    '  {"op": "add_filter", "col": "column", "val": "value_to_drop"}  - drop rows where column == value\n'
    '  {"op": "set_output", "type": "delimited_file|excel|json|json_writer"}  - set the output format\n'
    '  {"op": "explain"}                                             - describe the current pipeline\n\n'
    "Guidelines:\n"
    "- Prefer column names from the provided known-columns list; if unsure, still emit the op and "
    "the app will guide the user.\n"
    "- A greeting or a question that is not an edit -> ops=[] and a helpful reply.\n"
    "- If the request is NOT one of the ops above (e.g. train a model, draw a chart, export a PDF), "
    "return ops=[] and a reply that names what you CAN do — don't invent an op.\n"
    "- One request may need several ops; emit them in order."
)

# A few worked examples, taught in-context. A 4B model extracts far more reliably from concrete
# input->JSON pairs than from the schema prose alone. Cover: multi-op edit, greeting, unsupported.
FEWSHOT = [
    {"role": "user", "content": "Known columns: ['id', 'status']\n\n"
        "Request: add columns amount and currency, then drop rows where status is inactive"},
    {"role": "assistant", "content": '{"reply": "Added two columns and a filter on status.", '
        '"ops": [{"op": "add_columns", "cols": ["amount", "currency"]}, '
        '{"op": "add_filter", "col": "status", "val": "inactive"}]}'},
    {"role": "user", "content": "Known columns: []\n\nRequest: hi, what can you do?"},
    {"role": "assistant", "content": '{"reply": "I can add or rename columns, add sources and '
        'filters, add transforms, and set the output format — just describe the change.", "ops": []}'},
    {"role": "user", "content": "Known columns: ['id']\n\nRequest: train a machine learning model"},
    {"role": "assistant", "content": '{"reply": "I can\'t train models — I edit pipelines. I can add '
        'columns, sources, filters, transforms, or set the output.", "ops": []}'},
]

# Prefill the assistant turn so generation starts inside the JSON object. Forces JSON-first output
# (no prose, no markdown fence, no stray <think>) and is stitched back on before parsing.
_PREFILL = '{"reply": "'

# Lazy-loaded model + tokenizer (thread-safe via lock)
_model = None
_tokenizer = None
_model_lock = threading.Lock()


def _load_model():
    """Load tokenizer + model once and cache globally. Thread-safe double-checked locking."""
    global _model, _tokenizer
    if _model is not None:
        return _tokenizer, _model
    with _model_lock:
        if _model is not None:
            return _tokenizer, _model
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM

        torch.set_num_threads(os.cpu_count() or 1)  # use all cores for CPU inference
        tok = AutoTokenizer.from_pretrained(HF_MODEL, trust_remote_code=False)
        mdl = AutoModelForCausalLM.from_pretrained(
            HF_MODEL,
            dtype=torch.float32,    # CPU-safe; use bfloat16 if CUDA available
            device_map="cpu",
            trust_remote_code=False,
        )
        mdl.eval()
        _tokenizer = tok
        _model = mdl
    return _tokenizer, _model


def _extract_json(text: str) -> dict:
    """Best-effort JSON extraction — handles markdown fences and leading/trailing prose."""
    text = text.strip()
    # Remove Qwen3 thinking block if present (<think>...</think>)
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    # Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Markdown code fence: ```json { ... } ``` — greedy so nested op objects aren't cut at the first }
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fenced:
        try:
            return json.loads(fenced.group(1))
        except json.JSONDecodeError:
            pass
    # First standalone { ... } block (greedy, handles nested braces via rfind)
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass
    return {}


_YAML_CAP = 2500  # chars — bounds CPU prefill cost; the model only needs the shape, not every row


def _build_user_content(
    message: str, columns: list, yaml: str, interface: str, history: list | None = None
) -> str:
    """Assemble the user turn content — context first, then the request.

    Recent dialogue is folded in as plain text (not as real assistant turns): the stored replies are
    human-facing prose, so replaying them as assistant turns would teach the model to stop emitting
    JSON. The few-shot pairs remain the only JSON exemplars."""
    parts = []
    if interface:
        parts.append(f"Active interface: {interface}")
    if history:
        lines = []
        for h in history[-6:]:  # last ~3 turns is plenty of context
            role = h.get("role", "user")
            content = str(h.get("content", "")).replace("\n", " ").strip()
            if content:
                lines.append(f"{role}: {content[:200]}")
        if lines:
            parts.append("Recent conversation:\n" + "\n".join(lines))
    if yaml and yaml.strip():
        y = yaml.strip()
        if len(y) > _YAML_CAP:
            y = y[:_YAML_CAP] + "\n# … (truncated)"
        parts.append(
            "Current pipeline YAML (reference only — do NOT rewrite; emit ops to modify it):\n" + y
        )
    parts.append(f"Known columns: {columns if columns else []}")
    parts.append(f"Request: {message}")
    return "\n\n".join(parts)


def _filter_ops(ops) -> list:
    """Keep only well-formed ops whose name the executor implements. Pure + model-free (testable)."""
    if not isinstance(ops, list):
        return []
    return [o for o in ops if isinstance(o, dict) and o.get("op") in OPS]


def interpret(
    message: str, columns: list, yaml: str = "", interface: str = "", history: list | None = None
) -> dict:
    """Ask the local HF model for a reply + ordered list of edit ops.
    Same public contract as chat.interpret(). Raises on load/inference errors so the
    FastAPI caller can return 502 and the frontend falls back to its regex parser."""
    if not message or not message.strip():
        return {"reply": "", "ops": []}  # warm-up ping — short-circuit

    tok, mdl = _load_model()
    import torch

    user_content = _build_user_content(message, columns, yaml, interface, history)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *FEWSHOT,
        {"role": "user", "content": user_content},
    ]

    # apply_chat_template — use enable_thinking=False for Qwen3 to skip CoT reasoning block
    # (faster + output goes straight to JSON). Falls back gracefully for other models.
    try:
        input_text = tok.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
    except TypeError:
        # model tokenizer doesn't support enable_thinking (non-Qwen3)
        input_text = tok.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

    input_text += _PREFILL  # prefill the assistant turn so generation starts inside the JSON

    inputs = tok(input_text, return_tensors="pt")
    input_len = inputs["input_ids"].shape[1]

    with torch.no_grad():
        output_ids = mdl.generate(
            **inputs,
            max_new_tokens=192,     # JSON payloads are tiny; 192 covers a multi-op reply with headroom
            do_sample=False,        # greedy — deterministic, no randomness
            temperature=None,       # must be None when do_sample=False (transformers 5.x)
            top_p=None,             # same
            repetition_penalty=1.05,  # cheap guard against greedy degenerate loops
            pad_token_id=tok.eos_token_id,
        )

    # Decode only the newly generated tokens (slice off the prompt), then stitch the prefill back on
    new_tokens = output_ids[0][input_len:]
    raw = tok.decode(new_tokens, skip_special_tokens=True)
    parsed = _extract_json(_PREFILL + raw)

    if not isinstance(parsed, dict):
        parsed = {}

    return {
        "reply": str(parsed.get("reply", "")),
        "ops": _filter_ops(parsed.get("ops")),
    }


def warmup() -> None:
    """Pre-load model weights into RAM. Best-effort — swallows all errors."""
    try:
        _load_model()
    except Exception:
        pass
