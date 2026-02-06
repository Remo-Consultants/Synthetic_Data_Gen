# ☁️ Cloud Setup Summary

## 📦 What You Have

A **COT Synthetic Data Generator** that:
- Uses **Ollama** for local LLM inference
- Generates **Chain-of-Thought** training data
- Supports **14 different skills** (reasoning, generation, etc.)
- Works with **multiple models** (1.7B to 70B parameters)

## 🎯 Your Goal

Run this on **Google Colab** or **Kaggle** to generate synthetic data without using your local machine.

---

## 📋 Complete Setup Guide

I've created **4 comprehensive resources** for you:

### 1. 📘 COLAB_SETUP.md
**Detailed Google Colab guide** with:
- Step-by-step setup instructions
- Session limits and tips
- Troubleshooting guide
- Performance recommendations

### 2. 📗 KAGGLE_SETUP.md
**Detailed Kaggle guide** with:
- Dataset upload instructions
- Configuration steps
- Advantages over Colab
- Production workflow

### 3. 📓 colab_notebook.ipynb
**Ready-to-use Colab notebook** with:
- All setup cells pre-configured
- Multiple generation configurations
- Automatic download
- Built-in troubleshooting

### 4. 📕 kaggle_notebook.ipynb
**Ready-to-use Kaggle notebook** with:
- Dataset extraction code
- Optimized for 2x T4 GPUs
- Auto-saved outputs
- Production-ready configs

### 5. 📊 PLATFORM_COMPARISON.md
**Quick reference guide** with:
- Platform comparison table
- Quick start commands
- Performance benchmarks
- Best practices

---

## 🚀 Quick Start (Choose Your Platform)

### Option A: Google Colab (Fastest to Start)

**Best for**: Quick tests, prototyping, learning

**Steps**:
1. Upload `colab_notebook.ipynb` to Google Colab
2. Change runtime to GPU (T4)
3. Update the GitHub URL in Cell 1
4. Run all cells
5. Download results

**Time**: 5 minutes setup + generation time

---

### Option B: Kaggle (Best for Production)

**Best for**: Large batches, production runs, better GPU

**Steps**:
1. Zip your project: `tar -czf project.tar.gz --exclude=.git --exclude=.venv .`
2. Upload to Kaggle Datasets
3. Upload `kaggle_notebook.ipynb` to Kaggle Notebooks
4. Configure: GPU T4 x2, Internet ON, Persistence ON
5. Add your dataset to the notebook
6. Run all cells
7. Download from Output tab

**Time**: 10 minutes setup + generation time

---

## 📊 Platform Comparison

| Feature | Google Colab Free | Kaggle | Winner |
|---------|------------------|--------|--------|
| **GPU** | 1x T4 (16GB) | 2x T4 (16GB) | 🏆 Kaggle |
| **Session** | 12 hours | 9 hours | Colab |
| **Setup** | Clone from GitHub | Upload dataset | 🏆 Colab |
| **Outputs** | Manual download | Auto-saved | 🏆 Kaggle |
| **Internet** | Always on | Toggle on | Colab |
| **Best for** | Testing | Production | Both! |

---

## 💡 Recommended Approach

### For First-Time Users:

1. **Start with Colab** (easier setup)
   - Test with 5-10 seeds
   - Verify quality
   - Understand the workflow

2. **Move to Kaggle** (better for scale)
   - Upload your project
   - Run larger batches (50-100 seeds)
   - Auto-saved outputs

### For Experienced Users:

**Use both in parallel**:
- **Colab**: Quick experiments, testing new configs
- **Kaggle**: Production runs, large batches

---

## 🎓 Step-by-Step: Your First Run

### Colab (Recommended for First Try)

```bash
# 1. Open Google Colab
Go to: https://colab.research.google.com/

# 2. Upload colab_notebook.ipynb
File → Upload notebook → Select colab_notebook.ipynb

# 3. Change Runtime
Runtime → Change runtime type → T4 GPU → Save

# 4. Update Cell 1
Replace: https://github.com/YOUR_USERNAME/YOUR_REPO.git
With your actual GitHub repo URL

# 5. Run All Cells
Runtime → Run all

# 6. Wait for Generation
Monitor progress in the output

# 7. Download Results
Last cell will download output.zip automatically
```

### Kaggle (For Production)

```bash
# 1. Prepare Project
cd c:\Users\dines\Learning\Capstone\P4\Synthetic_Data_Gen\Synthetic-Data-Self-Distillation
tar -czf project.tar.gz --exclude=.git --exclude=.venv --exclude=__pycache__ .

# 2. Upload to Kaggle
Go to: https://www.kaggle.com/datasets
Click: New Dataset
Upload: project.tar.gz
Title: "COT Synthetic Data Generator"
Click: Create

# 3. Create Notebook
Go to: https://www.kaggle.com/code
Click: New Notebook
Upload: kaggle_notebook.ipynb

# 4. Configure Settings
Click: Settings (gear icon)
- Accelerator: GPU T4 x2
- Internet: ON
- Persistence: ON
Click: Save

# 5. Add Dataset
Click: Add Data → Your Datasets
Select: "COT Synthetic Data Generator"

# 6. Update Cell 1
Verify dataset path matches your upload

# 7. Run All Cells
Cell → Run All

# 8. Download Results
Click: Output tab → Download files
```

---

## ⚙️ Recommended Configurations

### For Colab Free (Fast & Efficient)
```bash
python run_pipeline.py \
    --model-strategy fixed \
    --model qwen3-1.7b \
    --ctx-mode fixed \
    --fixed-tokens 1024 \
    --max-seeds 20 \
    --samples-per-seed 2
```
**Output**: ~40 samples in 20-30 minutes

### For Kaggle (Quality & Scale)
```bash
python run_pipeline.py \
    --model-strategy random \
    --ctx-mode profile \
    --max-seeds 50 \
    --samples-per-seed 3
```
**Output**: ~150 samples in 1-2 hours

### For Maximum Quality (Either Platform)
```bash
python run_pipeline.py \
    --model-strategy fixed \
    --model deepseek-r1-8b \
    --ctx-mode long_cot \
    --max-seeds 30 \
    --samples-per-seed 3
```
**Output**: ~90 high-quality samples in 2-3 hours

---

## 🔧 Common Issues

### ❌ Ollama Not Starting
```bash
# Check logs
!cat ollama.log

# Restart
!pkill ollama
!nohup ollama serve > ollama.log 2>&1 &
!sleep 10
```

### ❌ Out of Memory
```bash
# Use smaller model
--model qwen3-1.7b

# Reduce context
--fixed-tokens 512

# Reduce batch
--max-seeds 5
```

### ❌ Session Timeout
```bash
# Resume from checkpoint
python run_pipeline.py --resume --max-seeds 50
```

---

## 📈 Expected Performance

| Model | Context | Samples/Hour | Quality | Platform |
|-------|---------|--------------|---------|----------|
| qwen3:1.7b | 1024 | ~100 | Good | Colab Free |
| qwen3:4b | 2048 | ~50 | Better | Kaggle |
| deepseek-r1:8b | 4096 | ~20 | Best | Colab Pro/Kaggle |

---

## ✅ Success Checklist

Before you start:
- [ ] Choose platform (Colab or Kaggle)
- [ ] Read the relevant guide (COLAB_SETUP.md or KAGGLE_SETUP.md)
- [ ] Prepare your project (GitHub or zip)
- [ ] Have the notebook ready (colab_notebook.ipynb or kaggle_notebook.ipynb)

During setup:
- [ ] GPU enabled
- [ ] Internet enabled (Kaggle)
- [ ] Ollama installed and running
- [ ] Dependencies installed
- [ ] Model pulled successfully

Before full run:
- [ ] Dry run successful (`--dry-run`)
- [ ] Small test successful (5 seeds)
- [ ] Output format verified

After generation:
- [ ] Results downloaded/saved
- [ ] Quality verified
- [ ] Ready for next batch (if needed)

---

## 📚 Next Steps

1. **Read the detailed guide** for your chosen platform
2. **Upload the notebook** to Colab or Kaggle
3. **Run a small test** (5 seeds) to verify everything works
4. **Scale up** to your desired batch size
5. **Download and verify** your results

---

## 🆘 Need Help?

1. **Check the detailed guides**:
   - `COLAB_SETUP.md` for Colab-specific issues
   - `KAGGLE_SETUP.md` for Kaggle-specific issues
   - `PLATFORM_COMPARISON.md` for quick reference

2. **Review the notebooks**:
   - `colab_notebook.ipynb` has troubleshooting cells
   - `kaggle_notebook.ipynb` has monitoring tools

3. **Common fixes**:
   - Restart Ollama
   - Use smaller models
   - Reduce batch size
   - Check logs

---

## 🎉 You're Ready!

You now have everything you need to run your synthetic data generation on the cloud:

✅ **4 comprehensive guides**
✅ **2 ready-to-use notebooks**
✅ **Platform comparison**
✅ **Troubleshooting tips**
✅ **Performance benchmarks**

**Choose your platform and get started!** 🚀

---

## 📁 Files Created

```
Synthetic-Data-Self-Distillation/
├── COLAB_SETUP.md              # Detailed Colab guide
├── KAGGLE_SETUP.md             # Detailed Kaggle guide
├── PLATFORM_COMPARISON.md      # Quick reference
├── CLOUD_SETUP_SUMMARY.md      # This file
├── colab_notebook.ipynb        # Ready-to-use Colab notebook
└── kaggle_notebook.ipynb       # Ready-to-use Kaggle notebook
```

**Start with this file**, then dive into the detailed guides! 📖
