# COT Synthetic Dataset Generator

Local pipeline for generating Chain-of-Thought synthetic training data.

**v3** — Uses **Ollama** as primary backend. Zero Python build hassle. Same llama.cpp speed. Auto-pulls models.

## Quick Start (5 minutes)

```bash
# 1. Install Ollama — https://ollama.com (one-click installer)
#    It auto-detects your NVIDIA GPU + CUDA

# 2. Pull a model (pick any — pipeline auto-pulls if missing)
ollama pull deepseek-r1:8b

# 3. Install Python deps
pip install pyyaml jinja2 pandas pyarrow

# 4. Test run
python run_pipeline.py --max-seeds 2 --dry-run

# 5. Generate!
python run_pipeline.py --max-seeds 3
```

That's it. No CMAKE, no build tools, no llama-cpp-python wheels.

## Context-Length Distribution

Each seed randomly samples a token budget based on the model's size class:

```
1b:   1024: 70%   2048: 20%   4096: 10%
3b:   1024: 50%   2048: 30%   4096: 20%
8b:   1024: 20%   2048: 20%   4096: 40%   8192: 20%
14b:  1024: 10%   2048: 20%   4096: 40%   8192: 30%
```

Configurable in `skills_config.yaml → ctx_profiles`. Three modes:

| Mode | CLI | Use Case |
|---|---|---|
| `profile` (default) | (none) | Production — mixed token lengths |
| `fixed` | `--ctx-mode fixed --fixed-tokens 1024` | Speed testing |
| `long_cot` | `--ctx-mode long_cot` | Max depth traces |

## Models for RTX 3070 Laptop (8 GB)

Pull the ones you want. Pipeline randomly picks from whatever you have:

```bash
# Recommended starter set (pull these first)
ollama pull deepseek-r1:8b       # 4.9 GB — best for math/logic COT
ollama pull qwen3:4b             # 2.6 GB — fast, strong quality
ollama pull qwen3:1.7b           # 1.1 GB — ultra-fast, short outputs

# Full set for maximum diversity
ollama pull qwen3:8b             # 5.2 GB
ollama pull qwen2.5:7b           # 4.7 GB
ollama pull phi4-mini            # 2.5 GB
ollama pull llama3.1:8b          # 4.7 GB
ollama pull gemma2:9b            # 5.4 GB
ollama pull deepseek-r1:1.5b     # 1.1 GB
ollama pull gemma2:2b            # 1.6 GB
```

## Usage Examples

```bash
# Random models, profile distribution (default)
python run_pipeline.py --max-seeds 5

# Fixed model, short outputs — fastest
python run_pipeline.py --model-strategy fixed --model qwen3-4b --ctx-mode fixed --fixed-tokens 1024 --max-seeds 10

# Specific skills only
python run_pipeline.py --skills RSN-ARITH RSN-LOGIC --max-seeds 5

# Long COT traces for deep reasoning
python run_pipeline.py --model-strategy fixed --model deepseek-r1-8b --ctx-mode long_cot --max-seeds 3

# With verification
python run_pipeline.py --verify --verifier qwen3-1.7b --max-seeds 5

# HF fallback (if Ollama not available)
python run_pipeline.py --backend hf --model-strategy fixed --model deepseek-r1-qwen-7b-hf --max-seeds 3
```

## Model Catalog

| Model ID | Ollama Name | Size | VRAM | Max COT | Strength |
|---|---|---|---|---|---|
| `qwen3-8b` | `qwen3:8b` | 8b | 5.5G | 8K | Best all-rounder |
| `qwen2.5-7b` | `qwen2.5:7b` | 8b | 5.0G | 4K | Hindi/multilingual |
| `deepseek-r1-8b` | `deepseek-r1:8b` | 8b | 5.0G | 8K | Native COT, math |
| `phi4-mini` | `phi4-mini` | 3b | 2.8G | 4K | Reasoning/param |
| `llama3.1-8b` | `llama3.1:8b` | 8b | 5.5G | 4K | Clean format |
| `gemma2-9b` | `gemma2:9b` | 8b | 5.5G | 2K | Creative |
| `qwen3-4b` | `qwen3:4b` | 3b | 3.0G | 4K | Rivals 72B |
| `qwen3-1.7b` | `qwen3:1.7b` | 1b | 1.5G | 2K | Ultra-fast |
| `deepseek-r1-1.5b` | `deepseek-r1:1.5b` | 1b | 1.5G | 4K | Light reasoner |
| `gemma2-2b` | `gemma2:2b` | 1b | 2.0G | 1.5K | Fast scorer |

Larger tiers (16 GB+): `qwen3:14b`, `deepseek-r1:14b`, `qwen3:32b`, `deepseek-r1:32b`, `deepseek-r1:70b`

## 14 Skills, 4 Layers

| ID | Name | Category | COT Style |
|---|---|---|---|
| FND-LEX-HI | Hindi Lexical & Syntactic | Foundation | linguistic_parse |
| FND-SEM | Semantic Understanding | Foundation | semantic_chain |
| FND-MORPH | Morphological Analysis | Foundation | linguistic_parse |
| RSN-ARITH | Arithmetic & Numerical | Reasoning | step_by_step_math |
| RSN-LOGIC | Logical Deduction | Reasoning | deductive_chain |
| RSN-CAUSAL | Causal Reasoning | Reasoning | causal_graph |
| RSN-ANALOGICAL | Analogical Reasoning | Reasoning | mapping_chain |
| GEN-SUMM | Abstractive Summarization | Generation | compression_trace |
| GEN-PARA | Paraphrase Generation | Generation | rewrite_trace |
| GEN-CREATIVE | Creative Writing | Generation | narrative_plan |
| APP-RAG | RAG & Grounded QA | Applied | retrieval_reason |
| APP-CLASS | Text Classification | Applied | label_reason |
| APP-NER | Named Entity Recognition | Applied | span_trace |
| APP-TRANSLATE | Translation & Code-Switch | Applied | alignment_trace |

## Full CLI

```
python run_pipeline.py [OPTIONS]

  --config PATH              skills_config.yaml path
  --skills ID [ID ...]       Skill IDs (default: all)
  --gpu-tier TIER            consumer_8gb | mid_16gb | high_24gb | datacenter_80gb
  --backend BACKEND          ollama (default) | gguf | hf | all
  --model-strategy STRATEGY  random | round_robin | fixed | weighted
  --model ID                 Fixed model ID
  --ctx-mode MODE            profile (default) | fixed | long_cot
  --fixed-tokens N           Token budget for --ctx-mode fixed
  --verify                   Run verification pass
  --verifier ID              Verifier model
  --max-seeds N              Max seeds per skill
  --samples-per-seed N       Variants per seed (default: 3)
  --output-dir PATH          Output directory
  --output-format FORMAT     parquet | jsonl | both
  --resume                   Resume from checkpoint
  --push-to-hub REPO         Push to HuggingFace Hub
  --hf-token TOKEN           HF token
  --custom-seeds PATH        Custom seeds JSONL
  --dry-run                  Preview without generating
```

## Adding Models

Add to `models:` in `skills_config.yaml`:

```yaml
  - id: my-model
    backend: ollama
    ollama_model: "model-name:tag"    # exact ollama pull name
    size_class: 8b                    # determines ctx_profile
    ctx: 32768
    max_cot: 8192
    vram_est: 5.0
    gpu_tier: consumer_8gb
    strength: "Description"
    license: Apache-2.0
    roles: [generator]
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `HF_TOKEN` | (none) | HuggingFace token for push |
