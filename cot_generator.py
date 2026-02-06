"""
cot_generator.py — Core generation loop.

v2 changes:
  • Context-length distribution: each seed samples a max_new_tokens
    from the model's size_class profile (1b: mostly short, 8b: mixed)
  • Per-seed timing & speed tracking
  • Better fallback parsing
"""

import random
import re
import time
import traceback
from dataclasses import dataclass, field, asdict

from cot_templates import build_prompt
from model_manager import ModelManager


# ── Language Mapping ────────────────────────────────────────

LANGUAGE_MAP = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "bn": "Bengali",
    "pa": "Punjabi",
}


@dataclass
class SynthRecord:
    """One record in the output dataset (mirrors PleIAs/SYNTH columns)."""
    synth_id: str = ""
    language: str = "en"
    exercise: str = ""
    model: str = ""
    query: str = ""
    query_seed_url: str = ""
    query_seed_text: str = ""
    additional_seed_url: str = ""
    seed_license: str = "synthetic"
    constraints: str = ""
    script: str = ""
    synthetic_reasoning: str = ""
    synthetic_answer: str = ""
    words: int = 0
    max_new_tokens_used: int = 0
    generation_time_s: float = 0.0
    # extra columns
    skill_id: str = ""
    category: str = ""
    band: list = field(default_factory=list)
    benchmarks: list = field(default_factory=list)
    cot_style: str = ""
    stages: list = field(default_factory=list)
    verified: bool = False
    verification_score: float = 0.0


# ── Context-length distribution sampler ─────────────────────

def sample_max_tokens(model_cfg: dict, ctx_profiles: dict, ctx_mode: str,
                      fallback: int = 2048) -> int:
    """
    Pick max_new_tokens for this seed based on the model's size_class.

    ctx_mode:
      'profile' → weighted random from ctx_profiles[size_class]
      'fixed'   → always use fallback
      'long_cot'→ use model's max_cot
    """
    if ctx_mode == "fixed":
        return fallback

    if ctx_mode == "long_cot":
        return model_cfg.get("max_cot", fallback)

    # profile mode
    size_class = model_cfg.get("size_class", "8b")
    profile = ctx_profiles.get(size_class)

    if not profile:
        return fallback

    # profile is { token_count: probability }
    buckets = list(profile.keys())
    weights = list(profile.values())

    # buckets may be int or str — normalise
    buckets = [int(b) for b in buckets]

    chosen = random.choices(buckets, weights=weights, k=1)[0]

    # clamp to model's max_cot
    max_cot = model_cfg.get("max_cot", 8192)
    return min(chosen, max_cot)


# ── Parsing helpers ─────────────────────────────────────────

RE_REASONING = re.compile(
    r"<reasoning>(.*?)</reasoning>", re.DOTALL | re.IGNORECASE
)
RE_ANSWER = re.compile(
    r"<answer>(.*?)</answer>", re.DOTALL | re.IGNORECASE
)
# Also handle <think> tags from DeepSeek-R1 models
RE_THINK = re.compile(
    r"<think>(.*?)</think>", re.DOTALL | re.IGNORECASE
)


def parse_response(raw: str) -> tuple[str, str]:
    """Extract reasoning and answer blocks. Supports multiple tag formats."""
    reasoning, answer = "", ""

    # Try <reasoning>/<answer> first
    m_r = RE_REASONING.search(raw)
    m_a = RE_ANSWER.search(raw)

    if m_r:
        reasoning = m_r.group(1).strip()
    if m_a:
        answer = m_a.group(1).strip()

    # Try <think> tag (DeepSeek-R1 native)
    if not reasoning:
        m_t = RE_THINK.search(raw)
        if m_t:
            reasoning = m_t.group(1).strip()
            # answer is everything after </think>
            after_think = raw[m_t.end():].strip()
            if not answer and after_think:
                # strip any remaining tags
                answer = re.sub(r"</?answer>", "", after_think).strip()

    # Fallback: heuristic split
    if not reasoning and not answer:
        parts = re.split(r"(?i)(?:final\s+)?answer\s*:", raw, maxsplit=1)
        if len(parts) == 2:
            reasoning = parts[0].strip()
            answer = parts[1].strip()
        else:
            split_point = int(len(raw) * 0.7)
            reasoning = raw[:split_point].strip()
            answer = raw[split_point:].strip()

    return reasoning, answer


def count_words(text: str) -> int:
    return len(text.split())


# ── Main generator ──────────────────────────────────────────

def generate_cot_batch(
    seeds: list[dict],
    model_cfg: dict,
    mgr: ModelManager,
    gen_settings: dict,
    ctx_profiles: dict,
    verifier_cfg: dict | None = None,
) -> list[dict]:
    """
    Generate COT records for a batch of seeds.
    Each seed gets a RANDOM max_new_tokens from the model's ctx_profile.
    """
    mgr.load(model_cfg)
    records = []
    max_retries = gen_settings.get("max_retries", 2)
    ctx_mode = gen_settings.get("ctx_mode", "profile")
    fallback_tokens = gen_settings.get("fallback_max_new_tokens", 2048)

    for i, seed in enumerate(seeds):
        # Sample context length for THIS seed
        max_tokens = sample_max_tokens(
            model_cfg, ctx_profiles, ctx_mode, fallback_tokens
        )

        cot_style = seed["cot_style"]
        
        # Expand language code to full name for prompt quality
        lang_code = seed.get("language", "en")
        seed["language"] = LANGUAGE_MAP.get(lang_code, lang_code)
        
        sys_msg, usr_msg = build_prompt(cot_style, seed)

        messages = [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": usr_msg},
        ]

        raw = ""
        reasoning, answer = "", ""
        gen_time = 0.0

        for attempt in range(1, max_retries + 1):
            try:
                t0 = time.time()
                raw = mgr.generate(
                    messages,
                    max_new_tokens=max_tokens,
                    temperature=gen_settings.get("temperature", 0.7),
                    top_p=gen_settings.get("top_p", 0.9),
                    top_k=gen_settings.get("top_k", 50),
                    repetition_penalty=gen_settings.get(
                        "repetition_penalty", 1.1
                    ),
                )
                gen_time = time.time() - t0
                reasoning, answer = parse_response(raw)
                if reasoning and answer:
                    break
            except Exception:
                traceback.print_exc()
                time.sleep(1)

        total_words = count_words(reasoning) + count_words(answer)

        rec = SynthRecord(
            synth_id=seed["synth_id"],
            language=seed.get("language", "en"),
            exercise=seed.get("category", ""),
            model=model_cfg["id"],
            query=seed.get("query", ""),
            query_seed_url=seed.get("seed_url", ""),
            query_seed_text=seed.get("seed_text", ""),
            constraints=seed.get("constraints", ""),
            script=f"skill={seed['skill_id']} cot={cot_style}",
            synthetic_reasoning=reasoning,
            synthetic_answer=answer,
            words=total_words,
            max_new_tokens_used=max_tokens,
            generation_time_s=round(gen_time, 1),
            skill_id=seed["skill_id"],
            category=seed.get("category", ""),
            band=seed.get("band", []),
            benchmarks=seed.get("benchmarks", []),
            cot_style=cot_style,
            stages=seed.get("stages", []),
        )

        records.append(asdict(rec))

        # Per-seed progress with speed
        wps = total_words / gen_time if gen_time > 0 else 0
        print(
            f"  [{i+1}/{len(seeds)}] {rec.synth_id}  |  "
            f"{total_words} words  |  {max_tokens} tok budget  |  "
            f"{gen_time:.1f}s ({wps:.0f} w/s)  |  "
            f"model={model_cfg['id']}"
        )

    # ── Optional verification ───────────────────────────────
    if verifier_cfg and verifier_cfg["id"] != model_cfg["id"]:
        records = _verify_batch(records, verifier_cfg, mgr, gen_settings)

    return records


def _verify_batch(
    records: list[dict],
    verifier_cfg: dict,
    mgr: ModelManager,
    gen_settings: dict,
) -> list[dict]:
    """Ask a verifier model to score each COT trace (0-10)."""
    mgr.load(verifier_cfg)
    print(f"\n[Verifier] Scoring with {verifier_cfg['id']} ...")

    for rec in records:
        prompt = (
            f"Rate the quality of this chain-of-thought reasoning 0-10.\n"
            f"Consider: logical correctness, completeness, clarity.\n\n"
            f"Query: {rec['query']}\n\n"
            f"Reasoning:\n{rec['synthetic_reasoning'][:2000]}\n\n"
            f"Answer:\n{rec['synthetic_answer'][:500]}\n\n"
            f"Respond with ONLY a number 0-10."
        )
        messages = [{"role": "user", "content": prompt}]
        try:
            raw = mgr.generate(
                messages,
                max_new_tokens=16,
                temperature=0.1,
                top_p=0.9,
            )
            score = float(re.search(r"(\d+(?:\.\d+)?)", raw).group(1))
            score = min(10.0, max(0.0, score))
        except Exception:
            score = -1.0

        rec["verified"] = True
        rec["verification_score"] = score

    return records
