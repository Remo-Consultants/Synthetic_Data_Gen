"""
run_pipeline.py — Main entry point for COT synthetic dataset generation.

v2 — FAST mode:
  • GGUF backend via llama-cpp-python (3-5x faster than transformers)
  • Context-length distribution: small models → short, big → long
  • True per-seed model rotation (no grouping that defeats randomness)
  • Smart model swapping: sorts seeds to minimise load/unload cycles

Usage:
  python run_pipeline.py                                    # all skills, random model
  python run_pipeline.py --max-seeds 3 --dry-run            # preview
  python run_pipeline.py --model-strategy fixed --model qwen3-4b-gguf
  python run_pipeline.py --ctx-mode long_cot                # model's full max_cot
  python run_pipeline.py --ctx-mode fixed --fixed-tokens 1024  # all seeds = 1024
  python run_pipeline.py --backend all                      # include HF models too
  python run_pipeline.py --verify --verifier qwen3-1.7b-gguf
  python run_pipeline.py --push-to-hub user/dataset
"""

import argparse
import itertools
import os
import random
import sys
import time
import yaml

from seed_generator import get_seeds, load_custom_seeds
from cot_generator import generate_cot_batch
from model_manager import ModelManager
from dataset_writer import (
    save_parquet,
    save_jsonl,
    append_checkpoint,
    load_checkpoint,
    print_stats,
    push_to_hub,
)


# ================================================================
# Model selection
# ================================================================

class ModelSelector:
    """Picks the next model based on strategy."""

    def __init__(self, eligible_models: list[dict], strategy: str):
        self.models = eligible_models
        self.strategy = strategy
        self._call_count = 0

    def pick(self, role: str = "generator") -> dict:
        pool = [m for m in self.models if role in m.get("roles", ["generator"])]
        if not pool:
            pool = self.models

        if self.strategy == "random":
            return random.choice(pool)
        elif self.strategy == "round_robin":
            idx = self._call_count % len(pool)
            self._call_count += 1
            return pool[idx]
        elif self.strategy == "weighted":
            weights = [m.get("max_cot", 4096) for m in pool]
            return random.choices(pool, weights=weights, k=1)[0]
        elif self.strategy == "fixed":
            return pool[0]
        else:
            return random.choice(pool)

    def describe(self) -> str:
        names = [m["id"] for m in self.models]
        return f"{self.strategy} over {len(names)} models: {names}"


# ================================================================
# Config helpers
# ================================================================

def load_config(path: str = "skills_config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def filter_models(models: list[dict], tier: str,
                  backend_filter: str = "ollama") -> list[dict]:
    """Filter models by tier and backend."""
    tier_order = ["consumer_8gb", "mid_16gb", "high_24gb", "datacenter_80gb"]
    if tier not in tier_order:
        tier = "consumer_8gb"
    max_idx = tier_order.index(tier)
    eligible_tiers = set(tier_order[:max_idx + 1])

    result = [m for m in models
              if m.get("gpu_tier", "consumer_8gb") in eligible_tiers]

    if backend_filter != "all":
        result = [m for m in result
                  if m.get("backend", "gguf") == backend_filter]

    return result


def resolve_model(models: list[dict], model_id: str) -> dict:
    for m in models:
        if m["id"] == model_id:
            return m
    raise ValueError(
        f"Model '{model_id}' not found. "
        f"Available: {[m['id'] for m in models]}"
    )


# ================================================================
# Main
# ================================================================

def main():
    parser = argparse.ArgumentParser(
        description="COT Synthetic Dataset Generator (v2 — FAST)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--config", default="skills_config.yaml")
    parser.add_argument("--skills", nargs="*", default=None)
    parser.add_argument("--gpu-tier", default=None,
                        choices=["consumer_8gb", "mid_16gb",
                                 "high_24gb", "datacenter_80gb"])
    parser.add_argument("--model-strategy", default=None,
                        choices=["random", "round_robin", "fixed", "weighted"])
    parser.add_argument("--model", default=None,
                        help="Fixed model ID (with --model-strategy fixed)")
    parser.add_argument("--backend", default=None,
                        choices=["ollama", "gguf", "hf", "all"],
                        help="Backend filter (default: ollama)")
    parser.add_argument("--ctx-mode", default=None,
                        choices=["profile", "fixed", "long_cot"],
                        help="Context distribution mode")
    parser.add_argument("--fixed-tokens", type=int, default=None,
                        help="Fixed max_new_tokens (with --ctx-mode fixed)")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--verifier", default=None)
    parser.add_argument("--max-seeds", type=int, default=None)
    parser.add_argument("--samples-per-seed", type=int, default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--output-format",
                        choices=["parquet", "jsonl", "both"],
                        default=None)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--push-to-hub", default=None)
    parser.add_argument("--hf-token", default=None)
    parser.add_argument("--custom-seeds", default=None)
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    # ── Load config ─────────────────────────────────────────
    config = load_config(args.config)
    gen = config["generation"]
    ctx_profiles = config.get("ctx_profiles", {})

    gpu_tier = args.gpu_tier or gen.get("gpu_tier", "consumer_8gb")
    strategy = args.model_strategy or gen.get("model_strategy", "random")
    backend_filter = args.backend or gen.get("backend_filter", "ollama")
    output_dir = args.output_dir or gen.get("output_dir", "./output")
    output_format = args.output_format or gen.get("output_format", "parquet")
    samples_per_seed = args.samples_per_seed or gen.get("samples_per_seed", 1)
    ctx_mode = args.ctx_mode or gen.get("ctx_mode", "profile")

    # Override fallback tokens if specified
    if args.fixed_tokens:
        gen["fallback_max_new_tokens"] = args.fixed_tokens

    # Pass ctx_mode into gen_settings
    gen["ctx_mode"] = ctx_mode

    # ── Filter skills ───────────────────────────────────────
    skills = config["skills"]
    if args.skills:
        skills = [s for s in skills if s["id"] in args.skills]
        if not skills:
            print(f"[ERROR] No matching skills. Available: "
                  f"{[s['id'] for s in config['skills']]}")
            sys.exit(1)

    # ── Filter models ───────────────────────────────────────
    all_models = config["models"]
    eligible = filter_models(all_models, gpu_tier, backend_filter)

    if args.model and strategy == "fixed":
        fixed = resolve_model(eligible, args.model)
        eligible = [fixed]

    if not eligible:
        print(f"[ERROR] No models for tier='{gpu_tier}', "
              f"backend='{backend_filter}'")
        print(f"  Tip: use --backend all to include HF models, "
              f"or --backend ollama")
        sys.exit(1)

    selector = ModelSelector(eligible, strategy)

    # Verifier
    verifier_cfg = None
    if args.verify:
        if args.verifier:
            verifier_cfg = resolve_model(all_models, args.verifier)
        else:
            verifier_cfg = min(eligible, key=lambda m: m.get("vram_est", 99))

    # ── Plan summary ────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  COT SYNTHETIC DATASET — GENERATION PLAN (v3 OLLAMA)")
    print("=" * 70)
    print(f"  Skills           : {[s['id'] for s in skills]}")
    print(f"  GPU tier         : {gpu_tier}")
    print(f"  Backend          : {backend_filter}")
    print(f"  Model strategy   : {selector.describe()}")
    print(f"  Context mode     : {ctx_mode}")
    if verifier_cfg:
        print(f"  Verifier         : {verifier_cfg['id']}")
    print(f"  Samples/seed     : {samples_per_seed}")
    print(f"  Max seeds/skill  : {args.max_seeds or 'all'}")
    print(f"  Output           : {output_dir} ({output_format})")
    print(f"  Resume           : {args.resume}")

    # Show ctx profiles
    if ctx_mode == "profile":
        print(f"\n  Context-length distributions:")
        size_classes_used = set(m.get("size_class", "8b") for m in eligible)
        for sc in sorted(size_classes_used):
            prof = ctx_profiles.get(sc, {})
            dist_str = "  ".join(
                f"{int(k)}tok:{v*100:.0f}%" for k, v in prof.items()
            )
            print(f"    {sc:>4s}: {dist_str}")

    # Show model pool
    print(f"\n  {'MODEL':<30} {'BACKEND':<6} {'SIZE':>4} "
          f"{'CTX':>7} {'MAX_COT':>8} {'VRAM':>6}")
    print(f"  {'─'*30} {'─'*6} {'─'*4} {'─'*7} {'─'*8} {'─'*6}")
    for m in eligible:
        print(f"  {m['id']:<30} {m.get('backend','?'):<6} "
              f"{m.get('size_class','?'):>4} {m['ctx']:>7,} "
              f"{m['max_cot']:>8,} {m['vram_est']:>5.1f}G")
    print("=" * 70)

    if args.dry_run:
        total_records = 0
        for skill in skills:
            seeds = get_seeds(skill, limit=args.max_seeds)
            n = len(seeds) * samples_per_seed
            total_records += n
            print(f"\n  {skill['id']:20s}  {len(seeds)} seeds × "
                  f"{samples_per_seed} = {n} records")
        print(f"\n  TOTAL: ~{total_records} records")
        print("\n  [DRY RUN] No generation performed.")
        return

    # ── Resume ──────────────────────────────────────────────
    all_records = []
    done_ids = set()
    if args.resume:
        all_records = load_checkpoint(output_dir)
        done_ids = {r["synth_id"] for r in all_records}

    # ── Generate ────────────────────────────────────────────
    mgr = ModelManager()
    checkpoint_every = gen.get("checkpoint_every", 50)
    total_start = time.time()

    for skill in skills:
        print(f"\n{'─'*70}")
        print(f"  SKILL: {skill['id']} — {skill['name']}")
        print(f"  COT style: {skill['cot_style']}  |  "
              f"Benchmarks: {skill['benchmarks']}")
        print(f"{'─'*70}")

        if args.custom_seeds:
            seeds = load_custom_seeds(args.custom_seeds, skill)
        else:
            seeds = get_seeds(skill, limit=args.max_seeds)

        seeds = [s for s in seeds if s["synth_id"] not in done_ids]
        if not seeds:
            print("  (all done, skipping)")
            continue

        # Expand for samples_per_seed
        expanded = []
        for s in seeds:
            for v in range(samples_per_seed):
                c = {**s}
                if v > 0:
                    c["synth_id"] = f"{s['synth_id']}_v{v}"
                expanded.append(c)

        # ── Assign model per seed ───────────────────────────
        # Each seed gets its own model pick. Then we sort by model
        # to minimise swap overhead, while preserving per-seed diversity.
        seed_assignments = []
        for seed in expanded:
            chosen = selector.pick(role="generator")
            seed_assignments.append((chosen["id"], seed))

        # Sort by model ID so consecutive seeds use same model
        seed_assignments.sort(key=lambda x: x[0])

        # Show distribution
        from collections import Counter
        dist = Counter(mid for mid, _ in seed_assignments)
        print(f"  Model assignments:")
        for mid, count in dist.most_common():
            print(f"    {mid:<30} → {count} seeds")

        # Generate in model-sorted order
        current_model_id = None
        current_model_cfg = None
        batch_seeds = []
        flush_count = 0

        def flush_batch():
            nonlocal all_records, done_ids, flush_count
            if not batch_seeds or current_model_cfg is None:
                return
            records = generate_cot_batch(
                seeds=batch_seeds,
                model_cfg=current_model_cfg,
                mgr=mgr,
                gen_settings=gen,
                ctx_profiles=ctx_profiles,
                verifier_cfg=verifier_cfg,
            )
            all_records.extend(records)
            done_ids.update(r["synth_id"] for r in records)
            flush_count += len(records)

            if flush_count >= checkpoint_every:
                append_checkpoint(
                    all_records[-flush_count:], output_dir
                )
                print(f"  [checkpoint] {len(all_records)} total records")
                flush_count = 0

        for mid, seed in seed_assignments:
            if mid != current_model_id:
                # Flush previous batch
                flush_batch()
                batch_seeds = []
                current_model_id = mid
                current_model_cfg = resolve_model(eligible, mid)

            batch_seeds.append(seed)

        # Flush last batch
        flush_batch()

        # Final checkpoint for any remaining
        if flush_count > 0:
            append_checkpoint(
                all_records[-flush_count:], output_dir
            )
            print(f"  [checkpoint] {len(all_records)} total records")

    # ── Final output ────────────────────────────────────────
    elapsed = time.time() - total_start
    print(f"\n[Pipeline] Done in {elapsed/60:.1f} min.")

    if not all_records:
        print("[Pipeline] No records generated.")
        return

    parquet_path = None
    if output_format in ("parquet", "both"):
        parquet_path = save_parquet(all_records, output_dir)
    if output_format in ("jsonl", "both"):
        save_jsonl(all_records, output_dir)

    print_stats(all_records)

    if args.push_to_hub and parquet_path:
        token = args.hf_token or os.environ.get("HF_TOKEN")
        push_to_hub(parquet_path, args.push_to_hub, token=token)


if __name__ == "__main__":
    main()
