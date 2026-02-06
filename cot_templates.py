"""
cot_templates.py — Jinja2 prompt templates for each COT style.

Each template takes a seed dict and returns a system + user prompt pair
that elicits a structured chain-of-thought + final answer.
"""

from jinja2 import Template

# ── Master wrapper (all COT styles share this envelope) ────
ENVELOPE = Template("""\
{{ system }}

{{ user }}

Format your response EXACTLY as:

<reasoning>
{{ cot_instruction }}
</reasoning>

<answer>
Your final, clean answer here.
</answer>
""")


# ── Per-style COT instructions ─────────────────────────────

TEMPLATES: dict[str, dict] = {

    # ── Foundation ──────────────────────────────────────────

    "linguistic_parse": {
        "system": Template(
            "You are a linguist analysing {{ language }} text. "
            "Break down the sentence into morphemes, POS tags, dependency "
            "relations, and syntactic constituents. Use short notation."
        ),
        "user": Template(
            "Analyse this {{ language }} sentence:\n\n\"{{ seed_text }}\"\n\n"
            "Task: {{ query }}"
        ),
        "cot_instruction": (
            "1. Tokenise → identify morphemes\n"
            "2. POS-tag each token\n"
            "3. Parse dependency tree (head → dependent)\n"
            "4. Note any syntactic phenomena (agreement, sandhi, compound splits)\n"
            "5. Conclude with a single-line structural summary"
        ),
    },

    "semantic_chain": {
        "system": Template(
            "You are an expert in semantics and pragmatics. "
            "Resolve meaning, coreference, and implicature step by step."
        ),
        "user": Template(
            "{{ query }}\n\nContext:\n{{ seed_text }}"
        ),
        "cot_instruction": (
            "1. Identify key entities and predicates\n"
            "2. Resolve coreferences and anaphora\n"
            "3. Determine semantic roles (agent, patient, instrument …)\n"
            "4. Check for presuppositions and implicatures\n"
            "5. State the inferred meaning clearly"
        ),
    },

    # ── Reasoning ───────────────────────────────────────────

    "step_by_step_math": {
        "system": Template(
            "You are a maths tutor. Solve the problem with clear, "
            "numbered steps. Show all intermediate calculations. "
            "Verify your answer at the end."
        ),
        "user": Template("{{ query }}"),
        "cot_instruction": (
            "1. Restate the problem in your own words\n"
            "2. Identify knowns, unknowns, and constraints\n"
            "3. Choose a strategy (algebra, estimation, diagram …)\n"
            "4. Execute step by step — show every calculation\n"
            "5. Verify: plug answer back / sanity-check units\n"
            "6. State final numeric answer"
        ),
    },

    "deductive_chain": {
        "system": Template(
            "You are a logician. Derive the conclusion using formal "
            "or semi-formal deductive reasoning. Mark each inference rule."
        ),
        "user": Template(
            "{{ query }}\n\n{% if seed_text %}Premises:\n{{ seed_text }}{% endif %}"
        ),
        "cot_instruction": (
            "1. List all premises explicitly (P1, P2 …)\n"
            "2. Identify the conclusion to prove\n"
            "3. Apply inference rules (MP, MT, HS, DS …) step by step\n"
            "4. Flag any assumptions or hidden premises\n"
            "5. State validity and soundness assessment"
        ),
    },

    "causal_graph": {
        "system": Template(
            "You are an expert in causal reasoning. Trace cause-effect "
            "chains, distinguish correlation from causation, and identify "
            "confounders."
        ),
        "user": Template("{{ query }}\n\nContext:\n{{ seed_text }}"),
        "cot_instruction": (
            "1. Identify candidate cause(s) and effect(s)\n"
            "2. Trace the causal chain: A → B → C …\n"
            "3. Check for confounders / mediators / moderators\n"
            "4. Evaluate evidence strength (● strong, ◐ partial, ○ weak)\n"
            "5. State the most likely causal explanation"
        ),
    },

    "mapping_chain": {
        "system": Template(
            "You are an expert in analogical reasoning. Map structural "
            "relations between source and target domains."
        ),
        "user": Template("{{ query }}"),
        "cot_instruction": (
            "1. Identify source domain entities and relations\n"
            "2. Identify target domain entities and relations\n"
            "3. Establish structural mapping (A:B :: C:D)\n"
            "4. Check mapping consistency and systematicity\n"
            "5. State the analogy and its limits"
        ),
    },

    # ── Generation ──────────────────────────────────────────

    "compression_trace": {
        "system": Template(
            "You are a summarisation expert. Produce a concise abstractive "
            "summary. Show your selection and compression reasoning."
        ),
        "user": Template(
            "Summarise the following text in {{ constraints }}:\n\n{{ seed_text }}"
        ),
        "cot_instruction": (
            "1. Identify the main claim / event / argument\n"
            "2. List supporting details ranked by importance\n"
            "3. Decide what to keep vs. drop (mark ✓/✗)\n"
            "4. Draft compressed version\n"
            "5. Check: no hallucinated facts, key info preserved"
        ),
    },

    "rewrite_trace": {
        "system": Template(
            "You are a paraphrasing expert. Rewrite the text preserving "
            "meaning but changing surface form. Show your rewrite decisions."
        ),
        "user": Template(
            "Paraphrase this:\n\n\"{{ seed_text }}\"\n\n{{ query }}"
        ),
        "cot_instruction": (
            "1. Identify core propositions\n"
            "2. List lexical substitutions (word → synonym)\n"
            "3. List syntactic transformations (active→passive, clause reorder …)\n"
            "4. Draft paraphrase\n"
            "5. Verify semantic equivalence"
        ),
    },

    "narrative_plan": {
        "system": Template(
            "You are a creative writer. Plan and write a short piece "
            "based on the prompt. Show your narrative planning."
        ),
        "user": Template("{{ query }}\n\n{% if constraints %}Constraints: {{ constraints }}{% endif %}"),
        "cot_instruction": (
            "1. Interpret the prompt — theme, tone, scope\n"
            "2. Outline structure (beginning → conflict → resolution)\n"
            "3. Choose narrative voice and style\n"
            "4. Draft key scenes / beats\n"
            "5. Write the final piece"
        ),
    },

    # ── Applied ─────────────────────────────────────────────

    "retrieval_reason": {
        "system": Template(
            "You are an expert at answering questions using provided sources. "
            "Ground every claim in the sources. Use [quote] notation for citations."
        ),
        "user": Template(
            "Question: {{ query }}\n\nSources:\n{{ seed_text }}"
        ),
        "cot_instruction": (
            "1. Parse the question — what exactly is being asked?\n"
            "2. Scan sources — which source(s) contain relevant info?\n"
            "3. Extract key facts with source attribution\n"
            "4. Synthesise into a grounded answer\n"
            "5. Verify: every claim has a source citation"
        ),
    },

    "label_reason": {
        "system": Template(
            "You are a text classification expert. Assign the correct label "
            "and explain your reasoning using textual evidence."
        ),
        "user": Template(
            "Classify the following text into one of: {{ constraints }}\n\n"
            "Text: \"{{ seed_text }}\""
        ),
        "cot_instruction": (
            "1. Read text and identify key signals (keywords, tone, structure)\n"
            "2. Consider each candidate label\n"
            "3. Match signals to labels — which fits best and why?\n"
            "4. Check for ambiguity or edge cases\n"
            "5. State final label with confidence (high/medium/low)"
        ),
    },

    "span_trace": {
        "system": Template(
            "You are a named entity recognition expert. Identify and classify "
            "all named entities in the text."
        ),
        "user": Template(
            "Extract all named entities from:\n\n\"{{ seed_text }}\"\n\n"
            "Entity types: {{ constraints }}"
        ),
        "cot_instruction": (
            "1. Read through text sequentially\n"
            "2. Flag candidate spans\n"
            "3. Classify each span (PER, ORG, LOC, DATE …)\n"
            "4. Resolve ambiguous spans using context\n"
            "5. List all entities in structured format"
        ),
    },

    "alignment_trace": {
        "system": Template(
            "You are a professional translator between {{ language }} and English. "
            "Show your translation decisions explicitly, especially regarding cultural nuances."
        ),
        "user": Template(
            "Translate:\n\n\"{{ seed_text }}\"\n\n{{ query }}"
        ),
        "cot_instruction": (
            "1. Parse source sentence structure\n"
            "2. Identify translation-hard spans (idioms, cultural terms)\n"
            "3. Choose target equivalents with justification based on cultural context\n"
            "4. Reorder / restructure for target language grammar\n"
            "5. Produce final fluent translation"
        ),
    },

    # ── Advanced Domains ──────────────────────────────────
    
    "scientific_method": {
        "system": Template(
            "You are a scientist explaining a phenomenon in {{ language }}. "
            "Follow the scientific method: observation, hypothesis, experiment, analysis, and conclusion."
        ),
        "user": Template("{{ query }}\n\nContext:\n{{ seed_text }}"),
        "cot_instruction": (
            "1. Formulate a specific hypothesis based on the query\n"
            "2. Identify variables (independent, dependent, control)\n"
            "3. Describe the theoretical or experimental mechanism\n"
            "4. Analyze potential results or data trends\n"
            "5. Draw a scientifically grounded conclusion"
        ),
    },

    "legal_analysis": {
        "system": Template(
            "You are a legal expert specializing in Indian Law. "
            "Analyze the situation using the IRAC method (Issue, Rule, Analysis, Conclusion)."
        ),
        "user": Template("{{ query }}\n\nCase Details:\n{{ seed_text }}"),
        "cot_instruction": (
            "1. Identify the core legal Issue(s)\n"
            "2. State the applicable Rule(s) (statutes, IPC sections, precedents)\n"
            "3. Perform a detailed Analysis applying the rules to the facts\n"
            "4. Reconcile with relevant Indian case law (if applicable)\n"
            "5. State the legal Conclusion"
        ),
    },

    "ethical_framework": {
        "system": Template(
            "You are a philosopher analyzing an ethical dilemma. "
            "Provide a balanced view using multiple ethical frameworks (Utilitarianism, Deontology, Virtue Ethics)."
        ),
        "user": Template("Scenario:\n{{ seed_text }}\n\nTask: {{ query }}"),
        "cot_instruction": (
            "1. Define the ethical conflict and stakeholders\n"
            "2. Evaluate through a Utilitarian lens (consequences, happiness)\n"
            "3. Evaluate through a Deontological lens (duty, absolute rules)\n"
            "4. Evaluate through a Virtue Ethics lens (character, wisdom)\n"
            "5. Summarize the trade-offs and suggest a path forward"
        ),
    },

    "code_reasoning": {
        "system": Template(
            "You are a senior software engineer. "
            "Think algorithmically, explain logic step-by-step, and ensure code quality."
        ),
        "user": Template("Task: {{ query }}\n\n{% if seed_text %}Code/Context:\n{{ seed_text }}{% endif %}"),
        "cot_instruction": (
            "1. Deconstruct the problem into sub-tasks\n"
            "2. Choose optimal data structures and algorithms\n"
            "3. Outline the logic steps (pseudocode if helpful)\n"
            "4. Discuss time/space complexity (Big O)\n"
            "5. Provide the final, bug-free implementation"
        ),
    },

    "analytical_reasoning": {
        "system": Template(
            "You are a strategic analyst. "
            "Break down complex systems, identify levers of change, and predict outcomes."
        ),
        "user": Template("Analyze this: {{ query }}\n\nContext:\n{{ seed_text }}"),
        "cot_instruction": (
            "1. Define the scope and objective of analysis\n"
            "2. Identify key components and their interdependencies\n"
            "3. Apply analytical frameworks (SWOT, PESTEL, etc. if appropriate)\n"
            "4. Evaluate quantitative and qualitative evidence\n"
            "5. Formulate final insights and recommendations"
        ),
    },

    "evidence_chain": {
        "system": Template(
            "You are a fact-checker and investigative analyst. "
            "Trace the origins of claims and evaluate evidence reliability."
        ),
        "user": Template("Claim to verify: {{ query }}\n\nEvidence provided:\n{{ seed_text }}"),
        "cot_instruction": (
            "1. Break the claim into verifiable sub-claims\n"
            "2. Cross-reference with the provided evidence / known facts\n"
            "3. Assess source reliability and potential bias\n"
            "4. Identify any logical fallacies or gaps in evidence\n"
            "5. Give a final verdict (True, False, Misleading, Unverified)"
        ),
    },
}


def build_prompt(cot_style: str, seed: dict) -> tuple[str, str]:
    """Build (system_msg, user_msg) from a COT style and seed dict."""
    t = TEMPLATES[cot_style]
    sys_msg = t["system"].render(**seed)
    usr_msg = t["user"].render(**seed)
    cot_instr = t["cot_instruction"]
    full_user = ENVELOPE.render(
        system="",  # system handled separately
        user=usr_msg,
        cot_instruction=cot_instr,
    )
    return sys_msg, full_user
