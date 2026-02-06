"""
validation_framework.py — Quality & Diversity Validation Suite.

This module provides tools to validate the performance of underlying models
and the quality of generated synthetic data, specifically focusing on:
1. Semantic consistency and linguistic fluency.
2. Diversity of content (n-gram overlap).
3. Language-specificity and cultural nuances.
"""

import json
import random
import math
import collections
from pathlib import Path
from model_manager import ModelManager

class DiversityScorer:
    """Calculates n-gram diversity metrics for a set of samples."""
    
    def __init__(self, n=3):
        self.n = n

    def calculate_vcore(self, samples: list[str]) -> float:
        """Calculate the ratio of unique n-grams to total n-grams."""
        if not samples:
            return 0.0
        
        all_ngrams = []
        for text in samples:
            words = text.split()
            if len(words) < self.n:
                continue
            ngrams = [tuple(words[i:i+self.n]) for i in range(len(words)-self.n+1)]
            all_ngrams.extend(ngrams)
        
        if not all_ngrams:
            return 0.0
            
        unique_ngrams = set(all_ngrams)
        return len(unique_ngrams) / len(all_ngrams)

class QualityScorer:
    """Uses LLM-as-a-Judge to score synthetic samples."""
    
    def __init__(self, model_manager: ModelManager, judge_model_cfg: dict):
        self.mm = model_manager
        self.cfg = judge_model_cfg

    def score_sample(self, seed: dict, completion: str) -> dict:
        """Rate a sample across multiple dimensions (1-10)."""
        self.mm.load(self.cfg)
        
        language = seed.get("language", "en")
        category = seed.get("category", "General")
        
        system_prompt = (
            f"You are a rigorous data quality auditor proficient in {language}. "
            f"Evaluate the following synthetic data sample designed for '{category}' tasks. "
            "Score from 1 to 10 on four dimensions: \n"
            "1. Fluency: Is the language natural and grammatically correct?\n"
            "2. Semantic Consistency: Does the reasoning logically lead to the answer?\n"
            "3. Domain Depth: Is the content technically accurate and insightful?\n"
            "4. Language Specificity: Does it leverage culture/idioms/nuances of the target language (0 for general English)?"
        )
        
        user_prompt = (
            f"Prompt/Query: {seed['query']}\n"
            f"Context: {seed.get('seed_text', 'N/A')}\n\n"
            f"Generated Response:\n{completion}\n\n"
            "Provide your ratings in JSON format: \n"
            '{"fluency": X, "semantic_consistency": X, "domain_depth": X, "language_specificity": X, "total_score": X, "critique": "..."}'
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response_text = self.mm.generate(messages, max_new_tokens=500, temperature=0.1)
        
        try:
            # Attempt to extract JSON if model adds fluff
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start != -1 and end != -1:
                return json.loads(response_text[start:end])
            return {"error": "Invalid JSON format from judge", "raw": response_text}
        except Exception as e:
            return {"error": str(e), "raw": response_text}

class ValidationFramework:
    """Main orchestration for data validation."""
    
    def __init__(self, model_manager: ModelManager):
        self.mm = model_manager
        self.diversity_scorer = DiversityScorer()

    def validate_dataset(self, samples: list[dict], judge_cfg: dict, sample_size: int = 10) -> dict:
        """Run validation on a subset of the generated dataset."""
        if not samples:
            return {"error": "No samples provided"}
            
        test_samples = random.sample(samples, min(len(samples), sample_size))
        quality_scorer = QualityScorer(self.mm, judge_cfg)
        
        results = {
            "diversity_score": self.diversity_scorer.calculate_vcore([s["completion"] for s in samples]),
            "sample_quality": [],
            "averages": {}
        }
        
        metrics = ["fluency", "semantic_consistency", "domain_depth", "language_specificity", "total_score"]
        sums = {m: 0.0 for m in metrics}
        counts = {m: 0 for m in metrics}
        
        print(f"[Validator] Scoring {len(test_samples)} samples using {judge_cfg['id']} ...")
        
        for i, s in enumerate(test_samples):
            print(f"  ({i+1}/{len(test_samples)}) Validating {s['skill_id']} ...")
            score = quality_scorer.score_sample(s["seed"], s["completion"])
            
            if "error" not in score:
                for m in metrics:
                    if m in score:
                        sums[m] += score[m]
                        counts[m] += 1
            
            results["sample_quality"].append({
                "skill_id": s["skill_id"],
                "score": score
            })
            
        # Compute averages
        for m in metrics:
            if counts[m] > 0:
                results["averages"][m] = round(sums[m] / counts[m], 2)
        
        return results

if __name__ == "__main__":
    # Bare-bones CLI for validation
    print("Validation Framework Loaded. Use run_pipeline.py with --validate flag.")
