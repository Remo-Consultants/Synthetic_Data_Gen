# Seed Generator Expansion Summary

## Overview
The `seed_generator.py` has been comprehensively expanded to support all newly added Indian languages and domain-specific skills from the updated `skills_config.yaml`.

---

## 📊 Expansion Statistics

| **Category** | **Before** | **After** | **Added** |
|--------------|------------|-----------|-----------|
| **Seed Banks** | 11 | 20 | +9 |
| **Languages Supported** | 2 (en, hi) | 7 (en, hi, ta, te, kn, bn, pa) | +5 |
| **Domain Coverage** | 8 | 15+ | +7 |
| **Total Seed Examples** | ~35 | ~95+ | +60 |

---

## 🌍 New Indian Language Seed Banks

### 1. **Tamil (ta)** - `TAMIL_LEX_SEEDS`
- **Source**: `tamil_wikipedia`
- **Seeds**: 3 examples
- **Focus**: Agglutinative morphology, sandhi (புணர்ச்சி), case markers
- **Example**: Analyzing "பள்ளிக்கூடத்திலிருந்து" (from the school)

### 2. **Telugu (te)** - `TELUGU_LEX_SEEDS`
- **Source**: `telugu_wikipedia`
- **Seeds**: 3 examples
- **Focus**: Vibhakti (విభక్తి) markers, compound word analysis
- **Example**: Breaking down "విద్యాలయం" (విద్య + ఆలయం)

### 3. **Kannada (kn)** - `KANNADA_LEX_SEEDS`
- **Source**: `kannada_wikipedia`
- **Seeds**: 3 examples
- **Focus**: Case markers, sandhi changes, grammatical analysis
- **Example**: Analyzing "ವಿದ್ಯಾಲಯ" (ವಿದ್ಯೆ + ಆಲಯ)

### 4. **Bengali (bn)** - `BENGALI_LEX_SEEDS`
- **Source**: `bengali_wikipedia`
- **Seeds**: 3 examples
- **Focus**: Vibhakti usage, sandhi compounds, syntactic parsing
- **Example**: Breaking down "বিদ্যালয়" (বিদ্যা + আলয়)

### 5. **Punjabi (pa)** - `PUNJABI_LEX_SEEDS`
- **Source**: `punjabi_wikipedia`
- **Seeds**: 3 examples
- **Focus**: Postpositions, case markers, morphological structure
- **Example**: Analyzing "ਵਿਦਿਆਲਾ" (ਵਿਦਿਆ + ਆਲਾ)

---

## 🔬 New Domain-Specific Seed Banks

### 1. **Mathematics** (Advanced)
- **Bank**: `MATH_TEXTBOOK_SEEDS`
- **Source**: `math_textbooks`
- **Seeds**: 4 examples
- **Topics**: 
  - Geometric proofs (triangle angle sum)
  - Algebraic derivations (quadratic formula)
  - Calculus (limits, derivatives from first principles)
- **Target**: 4K token deep mathematical reasoning

### 2. **Physics**
- **Bank**: `PHYSICS_SEEDS`
- **Source**: `physics_problems`
- **Seeds**: 4 examples
- **Topics**:
  - Kinematics (projectile motion)
  - Orbital mechanics (weightlessness)
  - Newton's laws (inclined plane)
  - Wave physics (electromagnetic waves)
- **Constraints**: Free body diagrams, step-by-step derivations

### 3. **Chemistry**
- **Bank**: `CHEMISTRY_SEEDS`
- **Source**: `chemistry_problems`
- **Seeds**: 4 examples
- **Topics**:
  - Chemical equations (balancing, conservation of mass)
  - Acid-base chemistry (pH calculations)
  - Bonding (ionic vs covalent)
  - Atomic structure (electron configuration)

### 4. **Biology**
- **Bank**: `BIOLOGY_SEEDS`
- **Source**: `biology_problems`
- **Seeds**: 4 examples
- **Topics**:
  - Photosynthesis (light-dependent/independent reactions)
  - DNA structure and replication
  - Cell division (mitosis vs meiosis)
  - Evolution (natural selection, Darwin's finches)

### 5. **Legal Reasoning**
- **Bank**: `LEGAL_SEEDS`
- **Source**: `legal_cases`, `legal_documents`
- **Seeds**: 4 examples (including 1 in Hindi)
- **Topics**:
  - Indian constitutional law (Basic Structure doctrine)
  - Contract law (consideration, Indian Contract Act 1872)
  - Criminal law (mens rea vs actus reus, IPC)
  - Fundamental rights (Article 21 - Right to Life)
- **Focus**: Case law citations, statutory interpretation

### 6. **Ethics**
- **Bank**: `ETHICS_SEEDS`
- **Source**: `ethical_dilemmas`
- **Seeds**: 3 examples
- **Topics**:
  - Trolley problem variants (self-driving cars)
  - Medical ethics (truth-telling, autonomy)
  - Professional ethics (whistleblowing)
- **Frameworks**: Utilitarian, deontological, virtue ethics

### 7. **Coding & Software**
- **Bank**: `CODING_SEEDS`
- **Source**: `github_repos`
- **Seeds**: 4 examples
- **Topics**:
  - Algorithm design (longest palindromic substring)
  - Debugging (factorial edge cases)
  - Data structures (binary search)
  - System design (REST API authentication)
- **Constraints**: Time/space complexity analysis, security best practices

### 8. **Politics**
- **Bank**: `POLITICS_SEEDS`
- **Source**: `political_texts`
- **Seeds**: 3 examples (including 1 in Hindi)
- **Topics**:
  - Separation of powers (parliamentary vs presidential)
  - Federalism (India vs USA)
  - Election Commission (भारत में चुनाव आयोग)

### 9. **News & Fact-Checking**
- **Bank**: `NEWS_SEEDS`
- **Source**: `news_articles`
- **Seeds**: 3 examples
- **Topics**:
  - Fact-checking (Chandrayaan-3 claims)
  - Bias detection (loaded language analysis)
  - 5W1H extraction (Who, What, When, Where, Why, How)

### 10. **Scientific Papers**
- **Bank**: `SCIENTIFIC_PAPER_SEEDS`
- **Source**: `scientific_papers`
- **Seeds**: 1 example
- **Topics**:
  - Research methodology analysis
  - CRISPR-Cas9 gene therapy abstract
- **Constraints**: Identify research question, methods, sample size, results, conclusion

---

## 🗺️ Updated SEED_BANKS Mapping

The `SEED_BANKS` dictionary now maps **20 seed sources** to their respective seed banks:

```python
SEED_BANKS = {
    # Mathematics (2)
    "math_problems": MATH_SEEDS,
    "math_textbooks": MATH_TEXTBOOK_SEEDS,
    
    # Logic & Reasoning (1)
    "logic_puzzles": LOGIC_SEEDS,
    
    # Science Domains (3)
    "physics_problems": PHYSICS_SEEDS,
    "chemistry_problems": CHEMISTRY_SEEDS,
    "biology_problems": BIOLOGY_SEEDS,
    
    # Legal & Ethics (3)
    "legal_cases": LEGAL_SEEDS,
    "legal_documents": LEGAL_SEEDS,
    "ethical_dilemmas": ETHICS_SEEDS,
    
    # Coding & Software (1)
    "github_repos": CODING_SEEDS,
    
    # Politics & News (2)
    "political_texts": POLITICS_SEEDS,
    "news_articles": NEWS_SEEDS + SUMMARIZATION_SEEDS,
    
    # Indian Languages (6)
    "hindi_wikipedia": HINDI_LEX_SEEDS,
    "tamil_wikipedia": TAMIL_LEX_SEEDS,
    "telugu_wikipedia": TELUGU_LEX_SEEDS,
    "kannada_wikipedia": KANNADA_LEX_SEEDS,
    "bengali_wikipedia": BENGALI_LEX_SEEDS,
    "punjabi_wikipedia": PUNJABI_LEX_SEEDS,
    
    # General Sources (6)
    "wikipedia_vital": SEMANTIC_SEEDS + CAUSAL_SEEDS + ...,
    "wiktionary": ALL_LANGUAGE_LEX_SEEDS,
    "story_seeds": CREATIVE_SEEDS,
    "labeled_text": CLASSIFICATION_SEEDS,
    "concept_pairs": ANALOGY_SEEDS,
    "parallel_corpus": TRANSLATION_SEEDS,
    "scientific_papers": SCIENTIFIC_PAPER_SEEDS,
}
```

---

## 🎯 Alignment with skills_config.yaml

All seed sources now align perfectly with the `seed_source` field in `skills_config.yaml`:

| **Skill ID** | **Seed Source** | **Seed Bank** | **Status** |
|--------------|-----------------|---------------|------------|
| FND-LEX-TA | tamil_wikipedia | TAMIL_LEX_SEEDS | ✅ Added |
| FND-LEX-TE | telugu_wikipedia | TELUGU_LEX_SEEDS | ✅ Added |
| FND-LEX-KN | kannada_wikipedia | KANNADA_LEX_SEEDS | ✅ Added |
| FND-LEX-BN | bengali_wikipedia | BENGALI_LEX_SEEDS | ✅ Added |
| FND-LEX-PA | punjabi_wikipedia | PUNJABI_LEX_SEEDS | ✅ Added |
| RSN-MATH-ADV | math_textbooks | MATH_TEXTBOOK_SEEDS | ✅ Added |
| RSN-PHYSICS | physics_problems | PHYSICS_SEEDS | ✅ Added |
| RSN-CHEMISTRY | chemistry_problems | CHEMISTRY_SEEDS | ✅ Added |
| RSN-BIOLOGY | biology_problems | BIOLOGY_SEEDS | ✅ Added |
| RSN-LEGAL | legal_cases | LEGAL_SEEDS | ✅ Added |
| RSN-ETHICS | ethical_dilemmas | ETHICS_SEEDS | ✅ Added |
| APP-CODE | github_repos | CODING_SEEDS | ✅ Added |
| APP-LAW | legal_documents | LEGAL_SEEDS | ✅ Added |
| APP-POLITICS | political_texts | POLITICS_SEEDS | ✅ Added |
| APP-NEWS | news_articles | NEWS_SEEDS | ✅ Added |
| APP-SCIENCE | scientific_papers | SCIENTIFIC_PAPER_SEEDS | ✅ Added |

---

## 🔑 Key Features

### 1. **Multilingual Support**
- All new language seeds include native script examples
- Grammatical analysis in both native language and English
- Focus on language-specific features (agglutination, sandhi, vibhakti)

### 2. **Domain Depth**
- Each domain has 3-4 seed examples covering different aspects
- Constraints guide the model toward 4K token generation
- Real-world examples (Indian law, JEE/NEET problems, etc.)

### 3. **4K Token Optimization**
- Seeds designed to encourage deep reasoning
- Complex problems requiring step-by-step solutions
- Multi-framework analysis (e.g., ethics: utilitarian + deontological)

### 4. **Indian Context**
- Legal seeds reference Indian law (IPC, Contract Act 1872, Constitution)
- Math problems use Indian currency (₹)
- Science problems reference Indian exams (JEE, NEET)
- Political analysis includes Indian governance structures

---

## 📝 Usage Example

```python
from seed_generator import get_seeds

# Load physics seeds for RSN-PHYSICS skill
skill_config = {
    "id": "RSN-PHYSICS",
    "seed_source": "physics_problems",
    "category": "Reasoning",
    "band": [3, 5],
    "benchmarks": ["SciQ", "GPQA-Physics"],
    "cot_style": "scientific_method",
    "stages": ["PRE", "SFT"]
}

seeds = get_seeds(skill_config, limit=10)
# Returns 4 physics problem seeds with skill metadata
```

---

## 🚀 Next Steps

1. **Test seed generation** for each new language and domain
2. **Validate** that seeds produce 4K token outputs with the configured models
3. **Expand seed banks** with more examples as needed
4. **Create custom seed JSONL files** for specific use cases using `load_custom_seeds()`

---

## 📚 References

- **skills_config.yaml**: Main configuration with all 26 skills
- **seed_generator.py**: Seed generation logic with 20 seed banks
- **Language codes**: ISO 639-1 (hi, ta, te, kn, bn, pa, en)
- **Benchmarks**: GSM8K, MATH, HumanEval, ILDC, SciQ, GPQA, etc.

---

**Last Updated**: 2026-02-06  
**Version**: v4.0 (Multi-Indian Language + Domain Expansion)
