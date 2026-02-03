"""
seed_generator.py — Create seed data for each skill.

Seeds are the raw material fed into the COT generation pipeline.
Each seed is a dict with at minimum: query, seed_text, language, constraints.
"""

import json
import random
import hashlib
from pathlib import Path

# ────────────────────────────────────────────────────────────
# Built-in seed banks per source type
# ────────────────────────────────────────────────────────────

MATH_SEEDS = [
    {
        "query": "A shopkeeper buys 45 notebooks at ₹12 each and sells them at ₹18 each. What is the total profit?",
        "seed_text": "",
        "language": "en",
        "constraints": "Show all arithmetic steps.",
        "seed_url": "synthetic/math",
    },
    {
        "query": "A train travels 360 km in 4 hours. It then travels another 240 km in 3 hours. What is the average speed for the entire journey?",
        "seed_text": "",
        "language": "en",
        "constraints": "Use distance = speed × time.",
        "seed_url": "synthetic/math",
    },
    {
        "query": "If 3x + 7 = 22, what is the value of x?",
        "seed_text": "",
        "language": "en",
        "constraints": "Solve step by step.",
        "seed_url": "synthetic/math",
    },
    {
        "query": "एक दुकानदार ने 200 रुपये में 5 किलो चावल खरीदे और 250 रुपये में बेच दिए। लाभ प्रतिशत क्या है?",
        "seed_text": "",
        "language": "hi",
        "constraints": "सभी गणना चरण दिखाएं।",
        "seed_url": "synthetic/math",
    },
    {
        "query": "A rectangular garden is 15m long and 8m wide. A path 2m wide is built around it. What is the area of the path?",
        "seed_text": "",
        "language": "en",
        "constraints": "Draw conceptual diagram in text. Show all steps.",
        "seed_url": "synthetic/math",
    },
    {
        "query": "Three friends split a bill of $147 equally. They each leave a 15% tip on their share. How much does each person pay in total?",
        "seed_text": "",
        "language": "en",
        "constraints": "",
        "seed_url": "synthetic/math",
    },
    {
        "query": "A tank is filled by pipe A in 6 hours and pipe B in 8 hours. If both pipes are opened together, how long to fill the tank?",
        "seed_text": "",
        "language": "en",
        "constraints": "Use rate = 1/time approach.",
        "seed_url": "synthetic/math",
    },
    {
        "query": "Find the compound interest on ₹10,000 at 10% per annum for 2 years, compounded annually.",
        "seed_text": "",
        "language": "en",
        "constraints": "Use CI = P(1+r/n)^(nt) - P",
        "seed_url": "synthetic/math",
    },
]

LOGIC_SEEDS = [
    {
        "query": "All roses are flowers. Some flowers fade quickly. Can we conclude that some roses fade quickly?",
        "seed_text": "P1: All roses are flowers.\nP2: Some flowers fade quickly.",
        "language": "en",
        "constraints": "",
        "seed_url": "synthetic/logic",
    },
    {
        "query": "If it rains, the ground is wet. The ground is not wet. What can we conclude?",
        "seed_text": "P1: Rain → Wet ground\nP2: ¬Wet ground",
        "language": "en",
        "constraints": "Name the inference rule used.",
        "seed_url": "synthetic/logic",
    },
    {
        "query": "Either the butler or the gardener committed the crime. The gardener was in another city. Who committed the crime?",
        "seed_text": "P1: Butler ∨ Gardener\nP2: ¬Gardener (alibi confirmed)",
        "language": "en",
        "constraints": "",
        "seed_url": "synthetic/logic",
    },
    {
        "query": "No mammals are cold-blooded. All whales are mammals. Are any whales cold-blooded?",
        "seed_text": "P1: Mammal → ¬Cold-blooded\nP2: Whale → Mammal",
        "language": "en",
        "constraints": "Use syllogistic reasoning.",
        "seed_url": "synthetic/logic",
    },
]

HINDI_LEX_SEEDS = [
    {
        "query": "इस वाक्य का वाक्य-विश्लेषण करें और कर्ता, क्रिया, कर्म पहचानें।",
        "seed_text": "राम ने बाजार से पाँच किलो आम खरीदे।",
        "language": "hi",
        "constraints": "",
        "seed_url": "synthetic/hindi_lex",
    },
    {
        "query": "Identify the sandhi and samas in this Hindi compound word and break it down.",
        "seed_text": "विद्यालय (विद्या + आलय)",
        "language": "hi",
        "constraints": "Show morpheme boundaries.",
        "seed_url": "synthetic/hindi_lex",
    },
    {
        "query": "Parse the postpositions and case markers in this sentence.",
        "seed_text": "लड़की ने किताब को मेज पर रखा।",
        "language": "hi",
        "constraints": "",
        "seed_url": "synthetic/hindi_lex",
    },
    {
        "query": "Identify verb forms and tense/aspect/mood markers.",
        "seed_text": "वह कल स्कूल जा रहा होगा।",
        "language": "hi",
        "constraints": "Mark TAM morphemes.",
        "seed_url": "synthetic/hindi_lex",
    },
]

SEMANTIC_SEEDS = [
    {
        "query": "The trophy doesn't fit into the brown suitcase because it is too [large/small]. Which entity does 'it' refer to in each case?",
        "seed_text": "Sentence 1: The trophy doesn't fit into the brown suitcase because it is too large.\nSentence 2: The trophy doesn't fit into the brown suitcase because it is too small.",
        "language": "en",
        "constraints": "This is a Winograd-style coreference problem.",
        "seed_url": "synthetic/semantic",
    },
    {
        "query": "The town councillors refused the demonstrators a permit because they feared violence. Who feared violence?",
        "seed_text": "The town councillors refused the demonstrators a permit because they feared violence.",
        "language": "en",
        "constraints": "Resolve the pronoun 'they'.",
        "seed_url": "synthetic/semantic",
    },
    {
        "query": "The man planted the tree because it was Arbor Day. What is the cause and what is the effect?",
        "seed_text": "",
        "language": "en",
        "constraints": "COPA-style causal reasoning.",
        "seed_url": "synthetic/semantic",
    },
]

SUMMARIZATION_SEEDS = [
    {
        "query": "Summarise this passage.",
        "seed_text": (
            "The Indian Space Research Organisation (ISRO) successfully launched "
            "the Chandrayaan-3 mission on July 14, 2023. The spacecraft entered "
            "lunar orbit on August 5 and the Vikram lander made a successful soft "
            "landing near the lunar south pole on August 23, making India the "
            "fourth country to land on the Moon and the first to land near the "
            "south pole. The Pragyan rover was deployed shortly after landing and "
            "conducted experiments on the lunar surface for about two weeks."
        ),
        "language": "en",
        "constraints": "2-3 sentences",
        "seed_url": "wikipedia/Chandrayaan-3",
    },
]

PARAPHRASE_SEEDS = [
    {
        "query": "Rewrite preserving meaning, changing at least 60% of words.",
        "seed_text": "The rapid advancement of artificial intelligence has raised concerns about job displacement across multiple industries.",
        "language": "en",
        "constraints": "",
        "seed_url": "synthetic/paraphrase",
    },
]

RAG_SEEDS = [
    {
        "query": "What was the primary cause of the fall of the Western Roman Empire?",
        "seed_text": (
            "[Source 1] The fall of the Western Roman Empire in 476 AD was driven by "
            "a combination of internal decay and external pressures. Economic troubles, "
            "including heavy taxation and inflation, weakened the empire from within.\n\n"
            "[Source 2] Barbarian invasions, particularly by the Visigoths, Vandals, and "
            "Ostrogoths, put enormous military pressure on Roman borders. The sack of "
            "Rome in 410 AD by Alaric I was a pivotal moment.\n\n"
            "[Source 3] Political instability, with over 20 emperors in 75 years during "
            "the Crisis of the Third Century, prevented effective governance."
        ),
        "language": "en",
        "constraints": "Cite sources using [Source N] notation.",
        "seed_url": "wikipedia/Fall_of_Roman_Empire",
    },
]

CLASSIFICATION_SEEDS = [
    {
        "query": "",
        "seed_text": "I absolutely loved this restaurant! The pasta was cooked to perfection and the service was outstanding.",
        "language": "en",
        "constraints": "positive, negative, neutral",
        "seed_url": "synthetic/classification",
    },
    {
        "query": "",
        "seed_text": "The flight was delayed by 3 hours and nobody at the counter could give us any information.",
        "language": "en",
        "constraints": "positive, negative, neutral",
        "seed_url": "synthetic/classification",
    },
]

NER_SEEDS = [
    {
        "query": "",
        "seed_text": "Sundar Pichai, CEO of Google, announced new AI features at the I/O conference in Mountain View, California on May 14, 2024.",
        "language": "en",
        "constraints": "PER, ORG, LOC, DATE, EVENT",
        "seed_url": "synthetic/ner",
    },
    {
        "query": "",
        "seed_text": "नरेंद्र मोदी ने 15 अगस्त 2024 को लाल किले से भाषण दिया।",
        "language": "hi",
        "constraints": "PER, LOC, DATE",
        "seed_url": "synthetic/ner",
    },
]

TRANSLATION_SEEDS = [
    {
        "query": "Translate to Hindi. Preserve technical terms.",
        "seed_text": "Machine learning models require large amounts of labeled data for supervised training.",
        "language": "en",
        "constraints": "",
        "seed_url": "synthetic/translation",
    },
    {
        "query": "Translate to English. Keep cultural context.",
        "seed_text": "दीपावली भारत का सबसे बड़ा त्योहार है जो बुराई पर अच्छाई की जीत का प्रतीक है।",
        "language": "hi",
        "constraints": "",
        "seed_url": "synthetic/translation",
    },
]

CREATIVE_SEEDS = [
    {
        "query": "Write a short story (200-300 words) about an AI that discovers it can dream.",
        "seed_text": "",
        "language": "en",
        "constraints": "Include: a moment of self-doubt, a sensory detail, dialogue.",
        "seed_url": "synthetic/creative",
    },
]

CAUSAL_SEEDS = [
    {
        "query": "Why does deforestation lead to increased flooding in downstream areas?",
        "seed_text": (
            "Forests act as natural sponges, absorbing rainfall through their root "
            "systems and releasing water slowly into streams. Tree canopies intercept "
            "rain, reducing the impact on soil. When forests are removed, soil becomes "
            "compacted and less able to absorb water."
        ),
        "language": "en",
        "constraints": "Trace the full causal chain.",
        "seed_url": "wikipedia/Deforestation",
    },
]

ANALOGY_SEEDS = [
    {
        "query": "Doctor is to Hospital as Teacher is to ___. Explain the analogical mapping.",
        "seed_text": "",
        "language": "en",
        "constraints": "",
        "seed_url": "synthetic/analogy",
    },
    {
        "query": "Photosynthesis is to Plants as Digestion is to ___. Complete and explain.",
        "seed_text": "",
        "language": "en",
        "constraints": "Map the structural relations.",
        "seed_url": "synthetic/analogy",
    },
]

# ── Seed source → bank mapping ─────────────────────────────
SEED_BANKS = {
    "math_problems":    MATH_SEEDS,
    "logic_puzzles":    LOGIC_SEEDS,
    "hindi_wikipedia":  HINDI_LEX_SEEDS,
    "wikipedia_vital":  SEMANTIC_SEEDS + CAUSAL_SEEDS + SUMMARIZATION_SEEDS + PARAPHRASE_SEEDS + RAG_SEEDS,
    "news_articles":    SUMMARIZATION_SEEDS,
    "story_seeds":      CREATIVE_SEEDS,
    "labeled_text":     CLASSIFICATION_SEEDS,
    "concept_pairs":    ANALOGY_SEEDS,
    "wiktionary":       HINDI_LEX_SEEDS,
    "parallel_corpus":  TRANSLATION_SEEDS,
}


def get_seeds(skill_cfg: dict, limit: int | None = None) -> list[dict]:
    """Return seeds for a skill config, optionally limited."""
    source = skill_cfg["seed_source"]
    bank = SEED_BANKS.get(source, [])
    if not bank:
        print(f"  [WARN] No seeds for source '{source}', using fallback.")
        bank = SEMANTIC_SEEDS  # safe fallback
    seeds = []
    for s in bank:
        seed = {**s}  # copy
        seed["skill_id"] = skill_cfg["id"]
        seed["category"] = skill_cfg["category"]
        seed["band"] = skill_cfg["band"]
        seed["benchmarks"] = skill_cfg["benchmarks"]
        seed["cot_style"] = skill_cfg["cot_style"]
        seed["stages"] = skill_cfg["stages"]
        # generate deterministic ID
        h = hashlib.md5(
            f"{skill_cfg['id']}_{s.get('query','')}_{s.get('seed_text','')}".encode()
        ).hexdigest()[:12]
        seed["synth_id"] = f"{skill_cfg['id']}_{h}"
        seeds.append(seed)
    if limit:
        seeds = seeds[:limit]
    return seeds


def load_custom_seeds(jsonl_path: str, skill_cfg: dict) -> list[dict]:
    """Load seeds from a user-provided JSONL file."""
    seeds = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            raw = json.loads(line.strip())
            seed = {
                "query": raw.get("query", ""),
                "seed_text": raw.get("seed_text", raw.get("text", "")),
                "language": raw.get("language", "en"),
                "constraints": raw.get("constraints", ""),
                "seed_url": raw.get("source", "custom"),
                "skill_id": skill_cfg["id"],
                "category": skill_cfg["category"],
                "band": skill_cfg["band"],
                "benchmarks": skill_cfg["benchmarks"],
                "cot_style": skill_cfg["cot_style"],
                "stages": skill_cfg["stages"],
            }
            h = hashlib.md5(
                f"{skill_cfg['id']}_{seed['query']}_{seed['seed_text']}".encode()
            ).hexdigest()[:12]
            seed["synth_id"] = f"{skill_cfg['id']}_{h}"
            seeds.append(seed)
    return seeds
