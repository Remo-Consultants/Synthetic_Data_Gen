# COT Synthetic Dataset Generator (Multilingual & Multi-Domain)

Local pipeline for generating high-quality **4K token** Chain-of-Thought synthetic training data for **7 Indian languages** and **15+ specialized domains**.

**v4** — Expanded support for **Hindi, Tamil, Telugu, Kannada, Bengali, Punjabi**, and **English**. Includes **Semantic Reasoning**, **Legal (IRAC)**, **Science (JEE/NEET level)**, and a new **Validation Framework**.

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

# Fixed model, profile distribution + VALIDATION
python run_pipeline.py --model-strategy fixed --model qwen3-8b --max-seeds 5 --validate --judge deepseek-r1-8b

# Specific Multilingual Skills only (e.g., Tamil & Telugu)
python run_pipeline.py --skills FND-LEX-TA FND-LEX-TE --max-seeds 5

# Deep Reasoning Domains (Physics, Legal)
python run_pipeline.py --skills RSN-PHYSICS RSN-LEGAL --ctx-mode long_cot --max-seeds 3

# With verification (per-trace scoring)
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

## 26 Skills across 4 Layers

### 🏛️ Foundation Layer (Language & Syntax)
| ID | Name | Languages | COT Style |
|---|---|---|---|
| FND-LEX-HI | Hindi Lexical & Syntactic | hi, en | linguistic_parse |
| FND-LEX-TA | Tamil Lexical & Syntactic | ta, en | linguistic_parse |
| FND-LEX-TE | Telugu Lexical & Syntactic | te, en | linguistic_parse |
| FND-LEX-KN | Kannada Lexical & Syntactic | kn, en | linguistic_parse |
| FND-LEX-BN | Bengali Lexical & Syntactic | bn, en | linguistic_parse |
| FND-LEX-PA | Punjabi Lexical & Syntactic | pa, en | linguistic_parse |
| FND-SEM | Semantic Understanding | Multilingual | semantic_chain |
| FND-MORPH | Morphological Analysis | Multilingual | linguistic_parse |

### 🧠 Reasoning Layer (Logic & STEM)
| ID | Name | Domains | COT Style |
|---|---|---|---|
| RSN-MATH-ADV | Advanced Mathematics | Math | step_by_step_math |
| RSN-PHYSICS | Physics Reasoning | Science | scientific_method |
| RSN-CHEMISTRY| Chemistry Reasoning | Science | scientific_method |
| RSN-BIOLOGY  | Biology Reasoning | Science | scientific_method |
| RSN-LEGAL    | Legal Reasoning | Law | legal_analysis |
| RSN-ETHICS   | Ethical Reasoning | Ethics | ethical_framework |
| RSN-LOGIC    | Logical Deduction | Logic | deductive_chain |
| RSN-CAUSAL   | Causal Reasoning | Logic | causal_graph |

### ✍️ Generation Layer
| ID | Name | Categories | COT Style |
|---|---|---|---|
| GEN-SUMM | Abstractive Summarization | Gen | compression_trace |
| GEN-PARA | Paraphrase Generation | Gen | rewrite_trace |
| GEN-CREATIVE | Creative Writing | Gen | narrative_plan |

### 🛠️ Applied Layer
| ID | Name | Domains | COT Style |
|---|---|---|---|
| APP-CODE | Code Gen & Debugging | Code | code_reasoning |
| APP-LAW  | Legal Doc Analysis | Law | legal_analysis |
| APP-POLITICS | Political Analysis | Social | analytical_reasoning |
| APP-NEWS | Fact-Checking | Social | evidence_chain |
| APP-SCIENCE | Sci-Lit Analysis | STEM | analytical_reasoning |
| APP-RAG | Grounded Retrieval | RAG | retrieval_reason |
| APP-TRANSLATE| Translation | Multi | alignment_trace |

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
  --validate                 Run quality & diversity validation suite
  --judge ID                 Model ID used as LLM-as-a-Judge (default: deepseek-r1-8b)
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
