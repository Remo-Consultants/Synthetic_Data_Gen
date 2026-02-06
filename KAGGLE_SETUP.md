# Running on Kaggle - Step-by-Step Guide

## Prerequisites
- Kaggle account
- Project files (this repository)

## Step 1: Prepare Your Project

### Option A: Upload as Kaggle Dataset (Recommended)
1. Go to [Kaggle Datasets](https://www.kaggle.com/datasets)
2. Click **New Dataset**
3. Zip your project files:
   ```bash
   cd c:\Users\dines\Learning\Capstone\P4\Synthetic_Data_Gen\Synthetic-Data-Self-Distillation
   # Exclude .git and .venv folders
   tar -czf synthetic-data-gen.tar.gz --exclude=.git --exclude=.venv --exclude=__pycache__ .
   ```
4. Upload the tar.gz file
5. Set title: "COT Synthetic Data Generator"
6. Make it **Private** or **Public** as needed
7. Click **Create**

### Option B: Use GitHub Integration
1. Push your code to GitHub (see Colab guide)
2. You'll clone it in the notebook

## Step 2: Create a New Kaggle Notebook

1. Go to [Kaggle Notebooks](https://www.kaggle.com/code)
2. Click **New Notebook**
3. Configure settings:
   - Click **Settings** (gear icon on right)
   - **Accelerator**: Select **GPU T4 x2** (free tier)
   - **Internet**: Turn **ON** (required for Ollama)
   - **Persistence**: Turn **ON** (to save outputs)
   - Click **Save**

## Step 3: Setup Code in Kaggle

Add the following cells to your Kaggle notebook:

### Cell 1: Import Dataset and Setup
```python
import os
import shutil

# If you uploaded as Kaggle dataset:
# Your dataset will be in /kaggle/input/your-dataset-name/
dataset_path = '/kaggle/input/cot-synthetic-data-generator/'

# Create working directory
!mkdir -p /kaggle/working/project
%cd /kaggle/working/project

# Extract if tar.gz
if os.path.exists(f'{dataset_path}synthetic-data-gen.tar.gz'):
    !tar -xzf {dataset_path}synthetic-data-gen.tar.gz -C /kaggle/working/project

# OR if using GitHub:
# !git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git .

# List files to verify
!ls -la
```

### Cell 2: Install Ollama
```bash
%%bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama server in background
nohup ollama serve > /kaggle/working/ollama.log 2>&1 &

# Wait for server to start
sleep 10

# Verify Ollama is running
curl http://localhost:11434/api/tags || echo "Ollama not ready yet, waiting..."
sleep 5
curl http://localhost:11434/api/tags
```

### Cell 3: Install Python Dependencies
```python
!pip install -q pyyaml jinja2 pandas pyarrow
```

### Cell 4: Pull Models
```bash
%%bash
# Pull models - Kaggle has 2x T4 GPUs (16GB each)
# You can use larger models than Colab!

# Recommended for Kaggle
ollama pull qwen3:4b          # 2.6 GB - fast and good quality
ollama pull deepseek-r1:8b    # 4.9 GB - best for reasoning

# Optional: Add more for diversity
# ollama pull qwen3:8b        # 5.2 GB
# ollama pull phi4-mini       # 2.5 GB

# List available models
ollama list
```

### Cell 5: Test Run (Dry Run)
```python
!python run_pipeline.py --max-seeds 2 --dry-run
```

### Cell 6: Generate Data (Small Test)
```python
# Test with small batch
!python run_pipeline.py \
    --model-strategy fixed \
    --model qwen3-4b \
    --ctx-mode fixed \
    --fixed-tokens 2048 \
    --max-seeds 5 \
    --samples-per-seed 2
```

### Cell 7: Full Generation
```python
# Full generation - Kaggle allows 9 hours GPU time per session
!python run_pipeline.py \
    --model-strategy random \
    --ctx-mode profile \
    --max-seeds 50 \
    --samples-per-seed 3 \
    --output-format both \
    --output-dir /kaggle/working/output
```

### Cell 8: Save Outputs
```python
# Kaggle automatically saves files in /kaggle/working/
# You can download them from the Output tab

# Check output files
!ls -lh /kaggle/working/output/

# Optionally, create a summary
import pandas as pd
import os

output_dir = '/kaggle/working/output'
for file in os.listdir(output_dir):
    if file.endswith('.parquet'):
        df = pd.read_parquet(os.path.join(output_dir, file))
        print(f"\n{file}:")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {list(df.columns)}")
        print(f"  Sample:\n{df.head(2)}")
```

## Step 4: Download Results

### Method 1: From Output Tab
1. Click **Output** tab on the right
2. Your files in `/kaggle/working/` will appear
3. Click download icon next to each file

### Method 2: Create Dataset
```python
# This creates a Kaggle dataset from your outputs
# Run this in a cell:
from kaggle import api

# Your outputs will be saved as a new dataset version
# Configure in Notebook settings → Output
```

## Important Notes for Kaggle

### ⏰ Session Limits
- **GPU quota**: 30 hours/week (free tier)
- **Session limit**: 9 hours per session
- **Internet**: Required for Ollama (enable in settings)

### 💾 Storage
- **Working directory**: `/kaggle/working/` (saved as output)
- **Input datasets**: `/kaggle/input/` (read-only)
- **Disk space**: ~100GB available

### 🚀 Performance Advantages Over Colab
1. **Dual T4 GPUs** (16GB total VRAM)
2. **Longer sessions** (9 hours vs Colab's 12 hours)
3. **Better CPU** (more cores)
4. **Persistent outputs** (auto-saved)

## Recommended Kaggle Configuration

For **Maximum Throughput** (2x T4 GPUs):
```bash
python run_pipeline.py \
    --model-strategy random \
    --ctx-mode profile \
    --max-seeds 100 \
    --samples-per-seed 3 \
    --output-format both \
    --output-dir /kaggle/working/output
```

For **Quality Focus** (using 8B models):
```bash
python run_pipeline.py \
    --model-strategy fixed \
    --model deepseek-r1-8b \
    --ctx-mode long_cot \
    --max-seeds 50 \
    --samples-per-seed 3 \
    --output-dir /kaggle/working/output
```

For **Speed** (smaller models):
```bash
python run_pipeline.py \
    --model-strategy fixed \
    --model qwen3-4b \
    --ctx-mode fixed \
    --fixed-tokens 1024 \
    --max-seeds 200 \
    --samples-per-seed 2 \
    --output-dir /kaggle/working/output
```

## Troubleshooting

### Ollama Not Starting
```bash
# Check if Ollama is running
!ps aux | grep ollama

# Check logs
!cat /kaggle/working/ollama.log

# Restart Ollama
!pkill ollama
!nohup ollama serve > /kaggle/working/ollama.log 2>&1 &
!sleep 10
```

### Internet Not Working
1. Go to **Settings** (gear icon)
2. Ensure **Internet** is **ON**
3. Click **Save**
4. Restart the notebook

### Out of Memory
```python
# Use smaller models or reduce context
!python run_pipeline.py \
    --model qwen3-4b \
    --ctx-mode fixed \
    --fixed-tokens 1024 \
    --max-seeds 10
```

### Session Timeout
```python
# Use --resume to continue from checkpoint
!python run_pipeline.py \
    --resume \
    --max-seeds 100 \
    --output-dir /kaggle/working/output
```

## Complete Kaggle Notebook Template

```python
# ========================================
# COT Synthetic Data Generator - Kaggle
# ========================================

# Cell 1: Setup Project
import os
dataset_path = '/kaggle/input/cot-synthetic-data-generator/'
!mkdir -p /kaggle/working/project
%cd /kaggle/working/project
!tar -xzf {dataset_path}synthetic-data-gen.tar.gz -C /kaggle/working/project

# Cell 2: Install Ollama
%%bash
curl -fsSL https://ollama.com/install.sh | sh
nohup ollama serve > /kaggle/working/ollama.log 2>&1 &
sleep 10

# Cell 3: Install Dependencies
!pip install -q pyyaml jinja2 pandas pyarrow

# Cell 4: Pull Models
!ollama pull qwen3:4b
!ollama pull deepseek-r1:8b
!ollama list

# Cell 5: Dry Run Test
!python run_pipeline.py --max-seeds 2 --dry-run

# Cell 6: Generate Data
!python run_pipeline.py \
    --model-strategy random \
    --max-seeds 50 \
    --samples-per-seed 3 \
    --output-format both \
    --output-dir /kaggle/working/output

# Cell 7: View Results
!ls -lh /kaggle/working/output/
import pandas as pd
df = pd.read_parquet('/kaggle/working/output/synthetic_dataset.parquet')
print(f"Generated {len(df)} samples")
df.head()
```

## Kaggle vs Colab Comparison

| Feature | Kaggle | Google Colab (Free) | Google Colab Pro |
|---------|--------|---------------------|------------------|
| GPU | 2x T4 (16GB) | 1x T4 (16GB) | 1x A100 (40GB) |
| Session | 9 hours | 12 hours | 24 hours |
| Weekly Quota | 30 GPU hours | Unlimited (with limits) | Unlimited |
| Internet | Yes (toggle) | Yes | Yes |
| Persistence | Auto-save outputs | Manual download | Auto-save |
| Best For | Large batches | Quick tests | Production runs |

## Tips for Maximum Efficiency

1. **Use both platforms**: Run on Kaggle for large batches, Colab for quick tests
2. **Checkpoint frequently**: Use `--resume` flag
3. **Monitor GPU usage**: Check Kaggle's GPU quota in settings
4. **Batch processing**: Generate in chunks of 50-100 seeds
5. **Model selection**: Use 4B-8B models for best speed/quality balance

## Publishing Results

After generation, you can:
1. **Download** from Output tab
2. **Create Kaggle Dataset** from outputs
3. **Push to HuggingFace Hub**:
   ```python
   !python run_pipeline.py \
       --push-to-hub your-username/dataset-name \
       --hf-token YOUR_HF_TOKEN \
       --max-seeds 100
   ```
