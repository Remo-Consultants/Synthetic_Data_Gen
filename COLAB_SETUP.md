# Running on Google Colab - Step-by-Step Guide

## Prerequisites
- Google account
- Project files (this repository)

## Step 1: Upload Project to GitHub (Recommended) or Google Drive

### Option A: GitHub (Recommended)
1. Create a new repository on GitHub
2. Upload your project files or push from local:
```bash
cd c:\Users\dines\Learning\Capstone\P4\Synthetic_Data_Gen\Synthetic-Data-Self-Distillation
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Option B: Google Drive
1. Zip your project folder
2. Upload to Google Drive

## Step 2: Create a New Colab Notebook

1. Go to [Google Colab](https://colab.research.google.com/)
2. Click **File → New Notebook**
3. Change runtime to GPU:
   - Click **Runtime → Change runtime type**
   - Select **T4 GPU** (free tier)
   - Click **Save**

## Step 3: Setup Code in Colab

Copy and paste the following cells into your Colab notebook:

### Cell 1: Clone Repository (if using GitHub)
```python
# Clone your repository
!git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
%cd YOUR_REPO

# OR if using Google Drive:
# from google.colab import drive
# drive.mount('/content/drive')
# %cd /content/drive/MyDrive/path/to/your/project
```

### Cell 2: Install Ollama on Colab
```bash
%%bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama server in background
nohup ollama serve > ollama.log 2>&1 &

# Wait for server to start
sleep 5

# Verify Ollama is running
curl http://localhost:11434/api/tags
```

### Cell 3: Install Python Dependencies
```python
!pip install -q pyyaml jinja2 pandas pyarrow
```

### Cell 4: Pull Models
```bash
%%bash
# Pull recommended starter models (choose based on your needs)
# Small & Fast (recommended for Colab free tier)
ollama pull qwen3:1.7b
ollama pull gemma2:2b

# Medium (if you have Colab Pro)
# ollama pull qwen3:4b
# ollama pull deepseek-r1:8b

# List available models
ollama list
```

### Cell 5: Test Run (Dry Run)
```python
!python run_pipeline.py --max-seeds 2 --dry-run
```

### Cell 6: Generate Data (Small Test)
```python
# Start with a small test
!python run_pipeline.py \
    --model-strategy fixed \
    --model qwen3-1.7b \
    --ctx-mode fixed \
    --fixed-tokens 1024 \
    --max-seeds 3 \
    --samples-per-seed 2
```

### Cell 7: Full Generation (Adjust Parameters)
```python
# Full generation with multiple skills
!python run_pipeline.py \
    --max-seeds 10 \
    --samples-per-seed 3 \
    --output-format both
```

### Cell 8: Download Results
```python
from google.colab import files
import os

# Zip the output folder
!zip -r output.zip output/

# Download the zip file
files.download('output.zip')
```

## Step 4: Monitor Progress

You can monitor the generation in real-time:
```python
# View logs
!tail -f ollama.log

# Check output files
!ls -lh output/
```

## Important Notes for Colab

### ⏰ Session Limits
- **Free tier**: 12-hour session limit
- **Colab Pro**: 24-hour session limit
- Save your work frequently!

### 💾 Storage
- Colab provides ~100GB disk space
- Download results before session ends

### 🚀 Performance Tips
1. **Use smaller models** for free tier (1.7b, 2b)
2. **Reduce max-seeds** to avoid timeout
3. **Use fixed context mode** for faster generation
4. **Save checkpoints** using `--resume` flag

### 🔄 Resume After Disconnect
```python
# If your session disconnects, re-run setup cells and use:
!python run_pipeline.py --resume --max-seeds 10
```

## Recommended Colab Configuration

For **Free Tier** (T4 GPU, 12 hours):
```bash
python run_pipeline.py \
    --model-strategy fixed \
    --model qwen3-1.7b \
    --ctx-mode fixed \
    --fixed-tokens 1024 \
    --max-seeds 50 \
    --samples-per-seed 2 \
    --output-format parquet
```

For **Colab Pro** (A100 GPU, 24 hours):
```bash
python run_pipeline.py \
    --model-strategy random \
    --ctx-mode profile \
    --max-seeds 100 \
    --samples-per-seed 3 \
    --output-format both
```

## Troubleshooting

### Ollama Not Starting
```bash
# Check if Ollama is running
!ps aux | grep ollama

# Restart Ollama
!pkill ollama
!nohup ollama serve > ollama.log 2>&1 &
!sleep 5
```

### Out of Memory
```python
# Use smaller models or reduce batch size
!python run_pipeline.py \
    --model qwen3-1.7b \
    --ctx-mode fixed \
    --fixed-tokens 512 \
    --max-seeds 5
```

### Session Timeout
- Use `--resume` flag to continue from checkpoint
- Download intermediate results periodically

## Complete Colab Notebook Template

Save this as a `.ipynb` file or copy to Colab:

```python
# ========================================
# COT Synthetic Data Generator - Colab
# ========================================

# 1. Setup
!git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
%cd YOUR_REPO

# 2. Install Ollama
%%bash
curl -fsSL https://ollama.com/install.sh | sh
nohup ollama serve > ollama.log 2>&1 &
sleep 5

# 3. Install Dependencies
!pip install -q pyyaml jinja2 pandas pyarrow

# 4. Pull Model
!ollama pull qwen3:1.7b

# 5. Generate Data
!python run_pipeline.py \
    --model-strategy fixed \
    --model qwen3-1.7b \
    --max-seeds 20 \
    --output-format both

# 6. Download Results
from google.colab import files
!zip -r output.zip output/
files.download('output.zip')
```
