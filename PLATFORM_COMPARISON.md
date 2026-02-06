# Platform Comparison & Quick Start Guide

## 🎯 Which Platform Should You Choose?

| Factor | Google Colab | Kaggle | Recommendation |
|--------|-------------|--------|----------------|
| **Quick Test** | ✅ Faster setup | ⚠️ Needs dataset upload | **Colab** |
| **Large Batches** | ⚠️ 12hr limit (free) | ✅ 9hr + auto-save | **Kaggle** |
| **GPU Power** | 1x T4 (16GB) | 2x T4 (16GB) | **Kaggle** |
| **Ease of Use** | ✅ Just clone repo | ⚠️ Upload dataset first | **Colab** |
| **Persistence** | ❌ Manual download | ✅ Auto-saved | **Kaggle** |
| **Best For** | Prototyping | Production | Both! |

## 🚀 Quick Start

### Google Colab (5 minutes)

1. **Open Colab**: [colab.research.google.com](https://colab.research.google.com/)
2. **Upload notebook**: `colab_notebook.ipynb` (or create new)
3. **Change runtime**: Runtime → Change runtime type → T4 GPU
4. **Run these commands**:

```python
# 1. Clone your repo
!git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
%cd YOUR_REPO

# 2. Install Ollama
!curl -fsSL https://ollama.com/install.sh | sh
!nohup ollama serve > ollama.log 2>&1 &
!sleep 5

# 3. Install deps
!pip install -q pyyaml jinja2 pandas pyarrow

# 4. Pull model
!ollama pull qwen3:1.7b

# 5. Generate!
!python run_pipeline.py --model qwen3-1.7b --max-seeds 20

# 6. Download
from google.colab import files
!zip -r output.zip output/
files.download('output.zip')
```

### Kaggle (10 minutes)

1. **Upload dataset**: 
   - Zip your project: `tar -czf project.tar.gz --exclude=.git --exclude=.venv .`
   - Upload to [kaggle.com/datasets](https://www.kaggle.com/datasets)

2. **Create notebook**: [kaggle.com/code](https://www.kaggle.com/code)

3. **Configure**:
   - Settings → GPU T4 x2
   - Settings → Internet ON
   - Settings → Persistence ON
   - Add your dataset

4. **Run these commands**:

```python
# 1. Extract dataset
!mkdir -p /kaggle/working/project
%cd /kaggle/working/project
!tar -xzf /kaggle/input/your-dataset/project.tar.gz

# 2. Install Ollama
!curl -fsSL https://ollama.com/install.sh | sh
!nohup ollama serve > /kaggle/working/ollama.log 2>&1 &
!sleep 10

# 3. Install deps
!pip install -q pyyaml jinja2 pandas pyarrow

# 4. Pull models
!ollama pull qwen3:4b
!ollama pull deepseek-r1:8b

# 5. Generate!
!python run_pipeline.py --max-seeds 50 --output-dir /kaggle/working/output

# 6. Download from Output tab →
```

## 📊 Performance Benchmarks

### Expected Generation Times

| Configuration | Colab Free | Kaggle | Samples/Hour |
|--------------|------------|--------|--------------|
| qwen3:1.7b, 1024 tokens | ~100 samples | ~120 samples | ~100-120 |
| qwen3:4b, 2048 tokens | ~50 samples | ~70 samples | ~50-70 |
| deepseek-r1:8b, 4096 tokens | ~20 samples | ~30 samples | ~20-30 |

### Recommended Configurations

#### Colab Free (T4, 12 hours)
```bash
python run_pipeline.py \
    --model-strategy fixed \
    --model qwen3-1.7b \
    --ctx-mode fixed \
    --fixed-tokens 1024 \
    --max-seeds 50 \
    --samples-per-seed 2
```
**Expected**: ~100 samples in 1 hour

#### Kaggle (2x T4, 9 hours)
```bash
python run_pipeline.py \
    --model-strategy random \
    --ctx-mode profile \
    --max-seeds 100 \
    --samples-per-seed 3
```
**Expected**: ~300 samples in 3-4 hours

#### Colab Pro (A100, 24 hours)
```bash
python run_pipeline.py \
    --model-strategy fixed \
    --model deepseek-r1-8b \
    --ctx-mode long_cot \
    --max-seeds 200 \
    --samples-per-seed 3
```
**Expected**: ~600 samples in 6-8 hours

## 🎓 Best Practices

### 1. Start Small
```bash
# Always test first!
python run_pipeline.py --max-seeds 2 --dry-run
python run_pipeline.py --max-seeds 5
```

### 2. Use Checkpoints
```bash
# Enable resume in case of disconnection
python run_pipeline.py --max-seeds 100 --resume
```

### 3. Monitor Progress
```bash
# Check outputs periodically
!ls -lh output/
!tail -f ollama.log
```

### 4. Download Frequently
- **Colab**: Download every 2-3 hours
- **Kaggle**: Auto-saved, but check Output tab

### 5. Optimize for Platform

**Colab Free** → Small models, short contexts
```bash
--model qwen3-1.7b --ctx-mode fixed --fixed-tokens 1024
```

**Kaggle** → Medium models, mixed contexts
```bash
--model qwen3-4b --ctx-mode profile
```

**Colab Pro** → Large models, long COT
```bash
--model deepseek-r1-8b --ctx-mode long_cot
```

## 🔧 Common Issues & Solutions

### Issue: Ollama Not Starting

**Solution**:
```bash
# Check if running
!ps aux | grep ollama

# Restart
!pkill ollama
!nohup ollama serve > ollama.log 2>&1 &
!sleep 10
```

### Issue: Out of Memory

**Solution**:
```bash
# Use smaller model
--model qwen3-1.7b

# Reduce context
--ctx-mode fixed --fixed-tokens 512

# Reduce batch
--max-seeds 10
```

### Issue: Session Timeout

**Solution**:
```bash
# Resume from checkpoint
python run_pipeline.py --resume --max-seeds 100
```

### Issue: Internet Not Working (Kaggle)

**Solution**:
1. Settings → Internet → ON
2. Save and restart notebook

## 📁 File Structure

After generation, you'll have:

```
output/
├── synthetic_dataset.parquet      # Main dataset
├── synthetic_dataset.jsonl        # JSONL format (if --output-format both)
├── metadata.json                  # Generation metadata
└── checkpoints/                   # Resume checkpoints
    └── checkpoint_*.json
```

## 🎯 Recommended Workflow

### For Quick Testing (Colab)
1. Clone repo → 2 min
2. Setup Ollama → 3 min
3. Pull small model → 2 min
4. Generate 20 seeds → 20 min
5. Download → 1 min
**Total: ~30 minutes**

### For Production (Kaggle)
1. Upload dataset → 5 min
2. Setup notebook → 3 min
3. Setup Ollama → 2 min
4. Pull models → 5 min
5. Generate 100 seeds → 2-3 hours
6. Download from Output tab → 1 min
**Total: ~3-4 hours**

### For Large Scale (Both)
1. **Day 1 (Colab)**: Test configuration, verify quality
2. **Day 2 (Kaggle)**: Run large batch (100-200 seeds)
3. **Day 3 (Kaggle)**: Resume for more if needed
4. **Combine**: Merge all outputs locally

## 💡 Pro Tips

1. **Use both platforms**: Test on Colab, produce on Kaggle
2. **Batch processing**: Generate in chunks of 50-100 seeds
3. **Model diversity**: Use random strategy for varied outputs
4. **Quality check**: Review first 10 samples before large runs
5. **Save configs**: Document successful configurations
6. **Monitor quota**: 
   - Colab: Unlimited sessions (with cooldowns)
   - Kaggle: 30 GPU hours/week

## 📚 Additional Resources

- **Colab Guide**: `COLAB_SETUP.md`
- **Kaggle Guide**: `KAGGLE_SETUP.md`
- **Colab Notebook**: `colab_notebook.ipynb`
- **Kaggle Notebook**: `kaggle_notebook.ipynb`
- **Main README**: `README.md`

## 🆘 Getting Help

If you encounter issues:

1. Check the troubleshooting sections in the guides
2. Review Ollama logs: `!cat ollama.log`
3. Check GPU usage: `!nvidia-smi`
4. Verify model availability: `!ollama list`
5. Test with minimal config: `--max-seeds 2 --dry-run`

## 🎉 Success Checklist

- [ ] Platform configured (GPU, Internet)
- [ ] Ollama installed and running
- [ ] Dependencies installed
- [ ] Model pulled successfully
- [ ] Dry run completed
- [ ] Small test (5 seeds) successful
- [ ] Full generation running
- [ ] Outputs verified
- [ ] Results downloaded

Good luck with your synthetic data generation! 🚀
