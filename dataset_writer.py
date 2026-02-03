"""
dataset_writer.py — Write generated records to Parquet / JSONL / HF.

Output schema mirrors PleIAs/SYNTH with added skill metadata columns.
"""

import json
import os
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


# SYNTH-compatible schema
SCHEMA = pa.schema([
    ("synth_id",            pa.string()),
    ("language",            pa.string()),
    ("exercise",            pa.string()),
    ("model",               pa.string()),
    ("query",               pa.string()),
    ("query_seed_url",      pa.string()),
    ("query_seed_text",     pa.string()),
    ("additional_seed_url", pa.string()),
    ("seed_license",        pa.string()),
    ("constraints",         pa.string()),
    ("script",              pa.string()),
    ("synthetic_reasoning", pa.string()),
    ("synthetic_answer",    pa.string()),
    ("words",               pa.int64()),
    ("max_new_tokens_used", pa.int64()),
    ("generation_time_s",   pa.float64()),
    # Extended columns
    ("skill_id",            pa.string()),
    ("category",            pa.string()),
    ("band",                pa.string()),      # JSON-encoded list
    ("benchmarks",          pa.string()),      # JSON-encoded list
    ("cot_style",           pa.string()),
    ("stages",              pa.string()),      # JSON-encoded list
    ("verified",            pa.bool_()),
    ("verification_score",  pa.float64()),
])


def _serialise_lists(records: list[dict]) -> list[dict]:
    """Convert list fields to JSON strings for Parquet storage."""
    out = []
    for r in records:
        row = {**r}
        for key in ("band", "benchmarks", "stages"):
            val = row.get(key, [])
            row[key] = json.dumps(val) if isinstance(val, list) else str(val)
        out.append(row)
    return out


def save_parquet(records: list[dict], output_dir: str, shard_name: str = "synth_001") -> str:
    """Save records as a single Parquet shard."""
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"{shard_name}.parquet")

    rows = _serialise_lists(records)
    table = pa.Table.from_pylist(rows, schema=SCHEMA)
    pq.write_table(table, path, compression="snappy")

    print(f"[Writer] Saved {len(records)} records → {path}")
    return path


def save_jsonl(records: list[dict], output_dir: str, filename: str = "synth.jsonl") -> str:
    """Save records as JSONL (good for streaming / inspection)."""
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, filename)

    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"[Writer] Saved {len(records)} records → {path}")
    return path


def append_checkpoint(records: list[dict], output_dir: str) -> str:
    """Append records to a running checkpoint JSONL."""
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "_checkpoint.jsonl")

    with open(path, "a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    return path


def load_checkpoint(output_dir: str) -> list[dict]:
    """Load existing checkpoint records (for resume)."""
    path = os.path.join(output_dir, "_checkpoint.jsonl")
    if not os.path.exists(path):
        return []
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    print(f"[Writer] Resumed {len(records)} records from checkpoint.")
    return records


def print_stats(records: list[dict]) -> None:
    """Print summary statistics for the generated dataset."""
    df = pd.DataFrame(records)
    print("\n" + "=" * 60)
    print("DATASET STATISTICS")
    print("=" * 60)
    print(f"Total records : {len(df)}")
    print(f"Total words   : {df['words'].sum():,}")
    print(f"Avg words/rec : {df['words'].mean():.0f}")
    print(f"\nBy skill:")
    for sid, grp in df.groupby("skill_id"):
        print(f"  {sid:20s}  {len(grp):5d} records  {grp['words'].sum():8,} words")
    print(f"\nBy model:")
    for mid, grp in df.groupby("model"):
        print(f"  {mid:20s}  {len(grp):5d} records")
    print(f"\nBy language:")
    for lang, grp in df.groupby("language"):
        print(f"  {lang:5s}  {len(grp):5d} records")
    if "verification_score" in df.columns and df["verified"].any():
        verified = df[df["verified"]]
        print(f"\nVerification scores:")
        print(f"  Mean  : {verified['verification_score'].mean():.1f}")
        print(f"  Median: {verified['verification_score'].median():.1f}")
        print(f"  <5    : {(verified['verification_score'] < 5).sum()} records")
    print("=" * 60)


def push_to_hub(
    parquet_path: str,
    repo_id: str,
    token: str | None = None,
) -> None:
    """Upload the dataset to HuggingFace Hub."""
    from datasets import Dataset

    table = pq.read_table(parquet_path)
    ds = Dataset(table)
    ds.push_to_hub(repo_id, token=token)
    print(f"[Writer] Pushed to https://huggingface.co/datasets/{repo_id}")
