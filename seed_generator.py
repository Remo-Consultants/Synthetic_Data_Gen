"""
seed_generator.py — Create seed data for each skill.

Seeds are the raw material fed into the COT generation pipeline.
Each seed is a dict with at minimum: query, seed_text, language, constraints.
"""

import json
import random
import hashlib
from pathlib import Path

# ════════════════════════════════════════════════════════════
# Built-in seed banks per source type
# ════════════════════════════════════════════════════════════

# ── MATHEMATICS ──────────────────────────────────────────────

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

MATH_TEXTBOOK_SEEDS = [
    {
        "query": "Prove that the sum of angles in a triangle equals 180 degrees using Euclidean geometry.",
        "seed_text": "",
        "language": "en",
        "constraints": "Use formal proof structure with axioms and theorems.",
        "seed_url": "synthetic/math_textbook",
    },
    {
        "query": "Derive the quadratic formula from the general form ax² + bx + c = 0 using completing the square.",
        "seed_text": "",
        "language": "en",
        "constraints": "Show every algebraic step clearly.",
        "seed_url": "synthetic/math_textbook",
    },
    {
        "query": "Calculate the limit: lim(x→0) (sin(x)/x). Use L'Hôpital's rule or series expansion.",
        "seed_text": "",
        "language": "en",
        "constraints": "Justify each step mathematically.",
        "seed_url": "synthetic/math_textbook",
    },
    {
        "query": "Find the derivative of f(x) = x³ + 2x² - 5x + 7 from first principles.",
        "seed_text": "",
        "language": "en",
        "constraints": "Use the definition of derivative as a limit.",
        "seed_url": "synthetic/math_textbook",
    },
]

# ── LOGIC & REASONING ────────────────────────────────────────

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

# ── SCIENCE DOMAINS ──────────────────────────────────────────

PHYSICS_SEEDS = [
    {
        "query": "A ball is thrown upward with an initial velocity of 20 m/s. Calculate the maximum height reached and time to reach it. (g = 10 m/s²)",
        "seed_text": "",
        "language": "en",
        "constraints": "Use kinematic equations. Show all steps.",
        "seed_url": "synthetic/physics",
    },
    {
        "query": "Explain why astronauts feel weightless in orbit, even though Earth's gravity still acts on them.",
        "seed_text": "",
        "language": "en",
        "constraints": "Discuss free fall and orbital mechanics.",
        "seed_url": "synthetic/physics",
    },
    {
        "query": "A 5 kg block slides down a frictionless incline of 30°. Calculate the acceleration and force components.",
        "seed_text": "",
        "language": "en",
        "constraints": "Draw free body diagram. Use Newton's laws.",
        "seed_url": "synthetic/physics",
    },
    {
        "query": "Derive the relationship between wavelength, frequency, and wave speed for electromagnetic waves.",
        "seed_text": "",
        "language": "en",
        "constraints": "Include the fundamental wave equation.",
        "seed_url": "synthetic/physics",
    },
]

CHEMISTRY_SEEDS = [
    {
        "query": "Balance this chemical equation: C₃H₈ + O₂ → CO₂ + H₂O. Explain the law of conservation of mass.",
        "seed_text": "",
        "language": "en",
        "constraints": "Show step-by-step balancing process.",
        "seed_url": "synthetic/chemistry",
    },
    {
        "query": "Calculate the pH of a 0.01 M HCl solution. Explain the relationship between [H⁺] and pH.",
        "seed_text": "",
        "language": "en",
        "constraints": "Use pH = -log[H⁺]",
        "seed_url": "synthetic/chemistry",
    },
    {
        "query": "Explain why ionic compounds have high melting points while covalent compounds generally have lower melting points.",
        "seed_text": "",
        "language": "en",
        "constraints": "Discuss bonding and intermolecular forces.",
        "seed_url": "synthetic/chemistry",
    },
    {
        "query": "What is the electron configuration of Iron (Fe, atomic number 26)? Explain using Aufbau principle.",
        "seed_text": "",
        "language": "en",
        "constraints": "Show orbital filling order.",
        "seed_url": "synthetic/chemistry",
    },
]

BIOLOGY_SEEDS = [
    {
        "query": "Explain the process of photosynthesis, including light-dependent and light-independent reactions.",
        "seed_text": "",
        "language": "en",
        "constraints": "Include chemical equations and location in chloroplast.",
        "seed_url": "synthetic/biology",
    },
    {
        "query": "Describe the structure and function of DNA. How does DNA replication ensure genetic continuity?",
        "seed_text": "",
        "language": "en",
        "constraints": "Discuss double helix, base pairing, and semi-conservative replication.",
        "seed_url": "synthetic/biology",
    },
    {
        "query": "What is the difference between mitosis and meiosis? Why is meiosis important for sexual reproduction?",
        "seed_text": "",
        "language": "en",
        "constraints": "Compare stages and outcomes of both processes.",
        "seed_url": "synthetic/biology",
    },
    {
        "query": "Explain how natural selection leads to evolution. Use Darwin's finches as an example.",
        "seed_text": "",
        "language": "en",
        "constraints": "Discuss variation, inheritance, and differential survival.",
        "seed_url": "synthetic/biology",
    },
]

# ── LEGAL & ETHICS ───────────────────────────────────────────

LEGAL_SEEDS = [
    {
        "query": "Analyze the doctrine of 'Basic Structure' in Indian constitutional law. What are its key principles?",
        "seed_text": "The Basic Structure doctrine was established in Kesavananda Bharati v. State of Kerala (1973), holding that certain fundamental features of the Constitution cannot be amended by Parliament.",
        "language": "en",
        "constraints": "Cite relevant case law and constitutional provisions.",
        "seed_url": "synthetic/legal",
    },
    {
        "query": "What constitutes 'consideration' in contract law? Is past consideration valid?",
        "seed_text": "",
        "language": "en",
        "constraints": "Use Indian Contract Act, 1872 provisions.",
        "seed_url": "synthetic/legal",
    },
    {
        "query": "Explain the difference between 'mens rea' and 'actus reus' in criminal law with examples.",
        "seed_text": "",
        "language": "en",
        "constraints": "Provide case examples from Indian Penal Code.",
        "seed_url": "synthetic/legal",
    },
    {
        "query": "भारतीय संविधान के अनुच्छेद 21 में 'जीवन का अधिकार' की व्याख्या करें।",
        "seed_text": "",
        "language": "hi",
        "constraints": "प्रमुख मामलों का उल्लेख करें।",
        "seed_url": "synthetic/legal",
    },
]

ETHICS_SEEDS = [
    {
        "query": "A self-driving car must choose between hitting a pedestrian or swerving and harming its passenger. Analyze this using utilitarian and deontological frameworks.",
        "seed_text": "",
        "language": "en",
        "constraints": "Compare both ethical frameworks and their conclusions.",
        "seed_url": "synthetic/ethics",
    },
    {
        "query": "Is it ethical for a doctor to lie to a terminally ill patient about their prognosis if the truth might cause severe psychological harm?",
        "seed_text": "",
        "language": "en",
        "constraints": "Consider medical ethics principles: autonomy, beneficence, non-maleficence.",
        "seed_url": "synthetic/ethics",
    },
    {
        "query": "Discuss the ethics of whistleblowing. When is it morally justified to expose organizational wrongdoing?",
        "seed_text": "",
        "language": "en",
        "constraints": "Balance loyalty, public interest, and consequences.",
        "seed_url": "synthetic/ethics",
    },
]

# ── CODING & SOFTWARE ────────────────────────────────────────

CODING_SEEDS = [
    {
        "query": "Write a Python function to find the longest palindromic substring in a given string. Optimize for time complexity.",
        "seed_text": "",
        "language": "en",
        "constraints": "Include time/space complexity analysis. Provide test cases.",
        "seed_url": "synthetic/coding",
    },
    {
        "query": "Debug this code: Why does it produce incorrect output?\n\ndef factorial(n):\n    if n == 1:\n        return 1\n    return n * factorial(n-1)",
        "seed_text": "",
        "language": "en",
        "constraints": "Identify the bug and provide corrected version.",
        "seed_url": "synthetic/coding",
    },
    {
        "query": "Implement a binary search algorithm in Python. Explain why it's O(log n) time complexity.",
        "seed_text": "",
        "language": "en",
        "constraints": "Include edge cases and complexity proof.",
        "seed_url": "synthetic/coding",
    },
    {
        "query": "Design a REST API endpoint for user authentication. What HTTP methods and status codes would you use?",
        "seed_text": "",
        "language": "en",
        "constraints": "Consider security best practices (hashing, tokens).",
        "seed_url": "synthetic/coding",
    },
]

# ── POLITICS & NEWS ──────────────────────────────────────────

POLITICS_SEEDS = [
    {
        "query": "Analyze the separation of powers doctrine in parliamentary vs. presidential systems. Use India and USA as examples.",
        "seed_text": "",
        "language": "en",
        "constraints": "Compare executive-legislative relationships.",
        "seed_url": "synthetic/politics",
    },
    {
        "query": "What are the key differences between federalism in India and the United States?",
        "seed_text": "",
        "language": "en",
        "constraints": "Discuss distribution of powers and constitutional provisions.",
        "seed_url": "synthetic/politics",
    },
    {
        "query": "भारत में चुनाव आयोग की भूमिका और शक्तियों का विश्लेषण करें।",
        "seed_text": "",
        "language": "hi",
        "constraints": "संवैधानिक प्रावधानों का उल्लेख करें।",
        "seed_url": "synthetic/politics",
    },
]

NEWS_SEEDS = [
    {
        "query": "Fact-check this claim: 'India became the first country to land on the south pole of the Moon.'",
        "seed_text": "Chandrayaan-3's Vikram lander touched down near the lunar south pole on August 23, 2023.",
        "language": "en",
        "constraints": "Verify accuracy, provide sources, rate as True/False/Partially True.",
        "seed_url": "synthetic/news",
    },
    {
        "query": "Analyze potential bias in this news headline: 'Government's Bold Economic Reforms Set to Transform Nation'",
        "seed_text": "",
        "language": "en",
        "constraints": "Identify loaded language, missing context, and perspective.",
        "seed_url": "synthetic/news",
    },
    {
        "query": "Summarize the key points of this news article and identify the 5W1H (Who, What, When, Where, Why, How).",
        "seed_text": "The Reserve Bank of India raised the repo rate by 25 basis points to 6.75% on February 8, 2024, citing persistent inflation concerns. Governor Shaktikanta Das stated that the decision aims to anchor inflation expectations while supporting growth.",
        "language": "en",
        "constraints": "Extract factual information systematically.",
        "seed_url": "synthetic/news",
    },
]

# ── INDIAN LANGUAGES: LEXICAL & SYNTACTIC ────────────────────

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

TAMIL_LEX_SEEDS = [
    {
        "query": "இந்த வாக்கியத்தின் இலக்கண அமைப்பை பகுத்தாய்வு செய்யவும்.",
        "seed_text": "குழந்தை பள்ளிக்கு சென்றது.",
        "language": "ta",
        "constraints": "வினை, பெயர், வேற்றுமை உருபுகளை அடையாளம் காணவும்.",
        "seed_url": "synthetic/tamil_lex",
    },
    {
        "query": "Identify the agglutinative morphemes in this Tamil word.",
        "seed_text": "பள்ளிக்கூடத்திலிருந்து (from the school)",
        "language": "ta",
        "constraints": "Break down each suffix and its grammatical function.",
        "seed_url": "synthetic/tamil_lex",
    },
    {
        "query": "Analyze the sandhi (புணர்ச்சி) in this compound.",
        "seed_text": "கல்வி + நிலையம் = கல்வி நிலையம்",
        "language": "ta",
        "constraints": "Explain phonological changes.",
        "seed_url": "synthetic/tamil_lex",
    },
]

TELUGU_LEX_SEEDS = [
    {
        "query": "ఈ వాక్యంలో కర్త, క్రియ, కర్మను గుర్తించండి.",
        "seed_text": "రాము పుస్తకం చదివాడు.",
        "language": "te",
        "constraints": "వ్याకరణ విశ్లేషణ చేయండి.",
        "seed_url": "synthetic/telugu_lex",
    },
    {
        "query": "Analyze the case markers and postpositions in this Telugu sentence.",
        "seed_text": "పిల్లలు పాఠశాలకు వెళ్లారు.",
        "language": "te",
        "constraints": "Identify vibhakti (విభక్తి) markers.",
        "seed_url": "synthetic/telugu_lex",
    },
    {
        "query": "Break down this compound word into its morphological components.",
        "seed_text": "విద్యాలయం (విద్య + ఆలయం)",
        "language": "te",
        "constraints": "Show sandhi rules applied.",
        "seed_url": "synthetic/telugu_lex",
    },
]

KANNADA_LEX_SEEDS = [
    {
        "query": "ಈ ವಾಕ್ಯದ ವ್ಯಾಕರಣ ವಿಶ್ಲೇಷಣೆ ಮಾಡಿ.",
        "seed_text": "ಮಗು ಶಾಲೆಗೆ ಹೋಯಿತು.",
        "language": "kn",
        "constraints": "ಕರ್ತೃ, ಕ್ರಿಯಾಪದ, ಕರ್ಮವನ್ನು ಗುರುತಿಸಿ.",
        "seed_url": "synthetic/kannada_lex",
    },
    {
        "query": "Identify the vibhakti (case) markers in this Kannada sentence.",
        "seed_text": "ಅವನು ಪುಸ್ತಕವನ್ನು ಮೇಜಿನ ಮೇಲೆ ಇಟ್ಟನು.",
        "language": "kn",
        "constraints": "Explain each postposition's function.",
        "seed_url": "synthetic/kannada_lex",
    },
    {
        "query": "Analyze this compound word formation.",
        "seed_text": "ವಿದ್ಯಾಲಯ (ವಿದ್ಯೆ + ಆಲಯ)",
        "language": "kn",
        "constraints": "Show sandhi changes.",
        "seed_url": "synthetic/kannada_lex",
    },
]

BENGALI_LEX_SEEDS = [
    {
        "query": "এই বাক্যের ব্যাকরণগত বিশ্লেষণ করুন।",
        "seed_text": "ছেলেটি স্কুলে গিয়েছিল।",
        "language": "bn",
        "constraints": "কর্তা, ক্রিয়া, কর্ম চিহ্নিত করুন।",
        "seed_url": "synthetic/bengali_lex",
    },
    {
        "query": "Identify the case markers and postpositions in this Bengali sentence.",
        "seed_text": "আমি বাজার থেকে বই কিনেছি।",
        "language": "bn",
        "constraints": "Analyze vibhakti usage.",
        "seed_url": "synthetic/bengali_lex",
    },
    {
        "query": "Break down this sandhi compound.",
        "seed_text": "বিদ্যালয় (বিদ্যা + আলয়)",
        "language": "bn",
        "constraints": "Show morpheme boundaries.",
        "seed_url": "synthetic/bengali_lex",
    },
]

PUNJABI_LEX_SEEDS = [
    {
        "query": "ਇਸ ਵਾਕ ਦਾ ਵਿਆਕਰਣਿਕ ਵਿਸ਼ਲੇਸ਼ਣ ਕਰੋ।",
        "seed_text": "ਮੁੰਡਾ ਸਕੂਲ ਗਿਆ।",
        "language": "pa",
        "constraints": "ਕਰਤਾ, ਕਿਰਿਆ, ਕਰਮ ਪਛਾਣੋ।",
        "seed_url": "synthetic/punjabi_lex",
    },
    {
        "query": "Identify postpositions and case markers in this Punjabi sentence.",
        "seed_text": "ਉਹ ਕਿਤਾਬ ਮੇਜ਼ ਉੱਤੇ ਰੱਖੀ।",
        "language": "pa",
        "constraints": "Analyze vibhakti markers.",
        "seed_url": "synthetic/punjabi_lex",
    },
    {
        "query": "Analyze this compound word.",
        "seed_text": "ਵਿਦਿਆਲਾ (ਵਿਦਿਆ + ਆਲਾ)",
        "language": "pa",
        "constraints": "Show morphological structure.",
        "seed_url": "synthetic/punjabi_lex",
    },
]

# ── GENERAL SEEDS ────────────────────────────────────────────

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

SCIENTIFIC_PAPER_SEEDS = [
    {
        "query": "Summarize the methodology and key findings of this research abstract.",
        "seed_text": (
            "We investigated the efficacy of CRISPR-Cas9 gene editing in treating "
            "sickle cell disease. 45 patients received modified hematopoietic stem "
            "cells with corrected HBB gene. After 12 months, 93% showed normalized "
            "hemoglobin levels with no adverse effects. Results suggest gene therapy "
            "as a viable treatment option."
        ),
        "language": "en",
        "constraints": "Identify: research question, methods, sample size, results, conclusion.",
        "seed_url": "synthetic/scientific_papers",
    },
]

# ── MULTILINGUAL SEMANTIC REASONING ──────────────────────────

INDIAN_SEMANTIC_SEEDS = [
    # Winograd Schemas (Coreference)
    {
        "query": "The trophy won't fit into the brown suitcase because it is too [large/small]. What does 'it' refer to?",
        "seed_text": "Sentence A: ട്രോഫി തവിട്ടുനിറത്തിലുള്ള പെട്ടിയിൽ ഒതുങ്ങില്ല, കാരണം അത് വളരെ വലുതാണ്. (Tamil/Malayalam variant style)\nವಾಕ್ಯ: ಟ್ರೋಫಿಯು ಕಂದು ಬಣ್ಣದ ಪೆಟ್ಟಿಗೆಯಲ್ಲಿ ಹಿಡಿಯುವುದಿಲ್ಲ ಏಕೆಂದರೆ ಅದು ತುಂಬಾ ದೊಡ್ಡದಾಗಿದೆ.",
        "language": "kn",
        "constraints": "Resolve 'അത്/ಅದು' based on the adjective 'ದೊಡ್ಡದಾಗಿದೆ' (large).",
        "seed_url": "synthetic/semantic/winograd",
    },
    {
        "query": "The town councillors refused the demonstrators a permit because they [feared/advocated] violence. Who does 'they' refer to?",
        "seed_text": "বাক্য: নগর পরিষদ বিক্ষোভকারীদের অনুমতি দিতে অস্বীকার করেছিল কারণ তারা সহিংসতাকে ভয় পেয়েছিল।",
        "language": "bn",
        "constraints": "Explain why 'তারা' refers to the councillors in the context of fearing violence.",
        "seed_url": "synthetic/semantic/winograd",
    },
    # Cultural Idioms & Metaphors
    {
        "query": "Explain the metaphorical meaning of the phrase 'పెరటి చెట్టు వైద్యానికి పనికిరాదు' (The tree in the backyard is of no use for medicine).",
        "seed_text": "Telugu Proverb: పెరటి చెట్టు వైద్యానికి పనికిరాదు.",
        "language": "te",
        "constraints": "Provide the literal meaning and the deep semantic interpretation regarding familiarity and lack of appreciation.",
        "seed_url": "synthetic/semantic/idioms",
    },
    {
        "query": "Explain the semantic mapping of the Tamil proverb 'தொட்டில் பழக்கம் சுடுகாடு மட்டும்' (Habits formed in the cradle last until the crematorium).",
        "seed_text": "Tamil Proverb: தொட்டில் பழக்கம் சுடுகாடு மட்டும்.",
        "language": "ta",
        "constraints": "Analyze the permanence of early childhood habits and the lifecycle metaphor used.",
        "seed_url": "synthetic/semantic/idioms",
    },
    # Causal & Counterfactual
    {
        "query": "If the monsoon had arrived earlier this year, how would it have affected the agricultural economy in Punjab?",
        "seed_text": "ਜੇ ਇਸ ਸਾਲ ਮਾਨਸੂਨ ਜਲਦੀ ਆ ਜਾਂਦਾ, ਤਾਂ ਪੰਜਾਬ ਦੀ ਖੇਤੀਬਾੜੀ ਆਰਥਿਕਤਾ 'ਤੇ ਇਸਦਾ ਕੀ ਪ੍ਰਭਾਵ ਪੈਂਦਾ?",
        "language": "pa",
        "constraints": "Reason through the causal chain of crop cycles (Kharif), irrigation costs, and market prices.",
        "seed_url": "synthetic/semantic/causal",
    },
    {
        "query": "Analyze the cause-effect relationship: The rise of digital payments in rural India has decreased the reliance on local moneylenders.",
        "seed_text": "భారతదేశంలోని గ్రామీణ ప్రాంతాల్లో డిజిటల్ చెల్లింపుల పెరుగుదల స్థానిక వడ్డీ వ్యాపారులపై ఆధారపడటాన్ని తగ్గించింది.",
        "language": "te",
        "constraints": "Discuss accessibility, transparency, and financial inclusion as intermediary variables.",
        "seed_url": "synthetic/semantic/causal",
    }
]

# ════════════════════════════════════════════════════════════
# Seed source → bank mapping
# ════════════════════════════════════════════════════════════

SEED_BANKS = {
    # Mathematics
    "math_problems":        MATH_SEEDS,
    "math_textbooks":       MATH_TEXTBOOK_SEEDS,
    
    # Logic & Reasoning
    "logic_puzzles":        LOGIC_SEEDS,
    
    # Science Domains
    "physics_problems":     PHYSICS_SEEDS,
    "chemistry_problems":   CHEMISTRY_SEEDS,
    "biology_problems":     BIOLOGY_SEEDS,
    
    # Legal & Ethics
    "legal_cases":          LEGAL_SEEDS,
    "legal_documents":      LEGAL_SEEDS,
    "ethical_dilemmas":     ETHICS_SEEDS,
    
    # Coding & Software
    "github_repos":         CODING_SEEDS,
    
    # Politics & News
    "political_texts":      POLITICS_SEEDS,
    "news_articles":        NEWS_SEEDS + SUMMARIZATION_SEEDS,
    
    # Indian Languages - Lexical/Syntactic
    "hindi_wikipedia":      HINDI_LEX_SEEDS,
    "tamil_wikipedia":      TAMIL_LEX_SEEDS,
    "telugu_wikipedia":     TELUGU_LEX_SEEDS,
    "kannada_wikipedia":    KANNADA_LEX_SEEDS,
    "bengali_wikipedia":    BENGALI_LEX_SEEDS,
    "punjabi_wikipedia":    PUNJABI_LEX_SEEDS,
    
    # General Sources
    "wikipedia_vital":      SEMANTIC_SEEDS + CAUSAL_SEEDS + SUMMARIZATION_SEEDS + PARAPHRASE_SEEDS + RAG_SEEDS + INDIAN_SEMANTIC_SEEDS,
    "indian_semantics":     INDIAN_SEMANTIC_SEEDS,
    "wiktionary":           HINDI_LEX_SEEDS + TAMIL_LEX_SEEDS + TELUGU_LEX_SEEDS + KANNADA_LEX_SEEDS + BENGALI_LEX_SEEDS + PUNJABI_LEX_SEEDS,
    "story_seeds":          CREATIVE_SEEDS,
    "labeled_text":         CLASSIFICATION_SEEDS,
    "concept_pairs":        ANALOGY_SEEDS,
    "parallel_corpus":      TRANSLATION_SEEDS,
    "scientific_papers":    SCIENTIFIC_PAPER_SEEDS,
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
