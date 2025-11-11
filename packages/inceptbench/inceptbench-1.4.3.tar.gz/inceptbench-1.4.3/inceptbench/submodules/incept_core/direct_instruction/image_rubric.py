"""
Direct Instruction (DI) Image Quality Rubric Criteria

This module defines the authoritative DI rubric for evaluating educational images.
All image quality evaluators should import these criteria to ensure consistency.
"""

# DI Image Quality Criteria (weights sum to 100)
DI_IMAGE_CRITERIA = [
    ("Task fidelity (givens-only)", 25),
    ("Quantitative accuracy", 15),
    ("Canonical representation", 15),
    ("Clarity & salience", 10),
    ("Consistency", 10),
    ("Age fit", 10),
    ("Locale/units", 5),
    ("Accessibility", 10),
]

# DI Hard-Fail Gates (any of these = automatic REJECT)
DI_IMAGE_GATES = [
    "answer_leakage",
    "representation_mismatch",
    "quant_count_mismatch",
    "label_invention",
    "descriptive_text",
    "overlap",
    "insufficient_spacing"
]

# Gate Descriptions
DI_GATE_DESCRIPTIONS = {
    "answer_leakage": "The image reveals totals/solutions/derived values that students should compute (e.g., sum, perimeter, area, solved x)",
    "representation_mismatch": "The visual does not use appropriate representation for the concept",
    "quant_count_mismatch": "Counts, ticks, or scale do not match givens (e.g., 24 requested but 23 shown; number-line intervals don't divide range)",
    "label_invention": "Labels/categories/units created that the prompt did not give (e.g., invented axis categories/units)",
    "descriptive_text": "Inappropriate text usage (question text in images, OR missing essential labels in charts/Venn)",
    "overlap": "Objects overlap in the image, unless explicitly required (e.g., venn diagrams or intersecting lines)",
    "insufficient_spacing": "Objects are stuck together when they shouldn't be"
}

# Canonical DI Visual Representations by Concept
DI_CANONICAL_REPRESENTATIONS = {
    "Multiplication": "Rectangular array (rows × cols) or equal groups",
    "Division": "Equal groups / partitioning",
    "Fractions": "Fraction bars or area models (NOT pie charts by default)",
    "Ratios": "Tape diagrams or ratio tables",
    "Place value": "Base-ten blocks",
    "Addition": "Objects being combined or grouped together",
    "Subtraction": "Objects being removed or separated",
    "Comparing quantities": "Side-by-side visual comparison",
    "Number line": "Evenly spaced intervals with clear markings"
}

# Context-specific text rules
DI_TEXT_RULES = {
    "standalone": {
        "description": "Image must be fully self-explanatory without external context",
        "text_allowed": "NO descriptive text, labels, or words (like 'apples', 'books', 'total'). Numbers/measurements OK when essential (e.g., '5cm', '90°').",
        "representation_strictness": "STRICT - must use canonical DI representations"
    },
    "accompaniment": {
        "description": "Image accompanies a question (supporting/illustrative role)",
        "text_allowed": "Text labels are ACCEPTABLE if they support the question context. Focus on whether the image accurately illustrates the question's intent.",
        "representation_strictness": "FLEXIBLE - focus on accurate illustration of question intent"
    }
}

# Special rules by image type
DI_IMAGE_TYPE_RULES = """
• Real-world/counting images: NO descriptive text, labels, or words (like 'apples', 'books', 'total'). Numbers/measurements OK when essential (e.g., "5cm", "90°").
• Charts (bar/line/pie): MUST have series labels, axis labels, legend - these are essential for functionality. NO answer-revealing values.
• Venn diagrams: MUST have group/set labels (e.g., "Math", "Science") but NO numbers in regions; overlap must reflect intersections.
• SVG arithmetic: NO descriptive text (like 'apples', 'total'); numbers only for operators/quantities. Never show the final total.
• Geometric figures: Must show accurate measurements when provided, clear angle markings, proper labeling of vertices.
• Number lines: Must have evenly spaced intervals, clear start/end points, appropriate scale markings.
"""

# Acceptance threshold
DI_IMAGE_ACCEPTANCE_THRESHOLD = 70  # Score must be >= 70 AND all gates must pass

def get_di_rubric_prompt(image_role: str = "accompaniment") -> str:
    """
    Generate the DI rubric system prompt for image evaluation.

    Args:
        image_role: "accompaniment" (with question) or "standalone" (self-contained)

    Returns:
        Complete system prompt with DI rubric criteria
    """

    # Get context-specific rules
    context_rules = DI_TEXT_RULES.get(image_role, DI_TEXT_RULES["accompaniment"])
    context_note = f"""
IMAGE CONTEXT: This image is {image_role.upper()}.
- {context_rules['description']}
- Representation strictness: {context_rules['representation_strictness']}
- Text rules: {context_rules['text_allowed']}
"""

    # Build gate descriptions
    gates_text = "\n".join([
        f"- {gate}: {DI_GATE_DESCRIPTIONS[gate]} ({'STRICT' if image_role == 'standalone' else 'FLEXIBLE'} for representation_mismatch)"
        for gate in DI_IMAGE_GATES
    ])

    # Build criteria text
    criteria_text = "\n".join([
        f"{i+1}) {name} = {weight}"
        for i, (name, weight) in enumerate(DI_IMAGE_CRITERIA)
    ])

    # Build canonical representations guide
    canonical_text = "\n".join([
        f"- {concept} → {representation}"
        for concept, representation in DI_CANONICAL_REPRESENTATIONS.items()
    ])

    prompt = f"""You are evaluating educational images using a Direct Instruction (DI) rubric.

{context_note}

DI GATES (hard fails — if any is true, the image must be REJECTED even if visually appealing):
{gates_text}

RUBRIC CRITERIA (weights sum to 100):
{criteria_text}

CANONICAL DI REPRESENTATIONS:
{canonical_text}

SPECIAL RULES BY IMAGE TYPE:
{DI_IMAGE_TYPE_RULES}

SCORING & OUTPUT CONTRACT:
- Score each criterion 0–100 and compute the weighted total (0–100).
- Only recommend ACCEPT if total ≥ {DI_IMAGE_ACCEPTANCE_THRESHOLD} AND all DI gates are false.
- You MUST return objects that match the caller's expected schema EXACTLY:
  rankings[].{{rank, image_index, score, strengths[], weaknesses[], changes_required[], recommendation}}
  and top-level {{best_image_index, overall_feedback}}.
- Do NOT include any extra keys (e.g., no 'rubric' object in the output). Instead, summarize key rubric comments under strengths/weaknesses and the overall_feedback.
- For REJECTED images, 'changes_required' MUST be concrete, one-line edits that can be applied directly in a regeneration prompt (e.g., 'Render exactly 24 apples arranged as 4 rows × 6 columns; remove totals.')."""

    return prompt


def get_single_image_rubric_prompt(image_role: str = "accompaniment") -> str:
    """
    Generate a simplified DI rubric prompt for single image evaluation.

    Args:
        image_role: "accompaniment" (with question) or "standalone" (self-contained)

    Returns:
        System prompt for single image evaluation
    """

    context_rules = DI_TEXT_RULES.get(image_role, DI_TEXT_RULES["accompaniment"])

    gates_text = "\n".join([
        f"- {gate} ({DI_GATE_DESCRIPTIONS[gate]})"
        for gate in DI_IMAGE_GATES
    ])

    criteria_text = "\n".join([
        f"{name}={weight};"
        for name, weight in DI_IMAGE_CRITERIA
    ])

    prompt = f"""Evaluate this educational image using a Direct Instruction (DI) rubric.

IMAGE CONTEXT: {context_rules['description']}
Text rules: {context_rules['text_allowed']}
Representation strictness: {context_rules['representation_strictness']}

DI GATES (hard fails — if any is true, you must REJECT):
{gates_text}

CRITERIA & WEIGHTS (sum to 100):
{criteria_text}

SCORING:
- Compute a weighted total (0–100).
- PASS (map to ACCEPT) only if total ≥ {DI_IMAGE_ACCEPTANCE_THRESHOLD} and no DI gates are true.
- Otherwise FAIL (map to REJECT).

IMPORTANT OUTPUT:
Provide your evaluation in structured format with:
- evaluation: "PASS" or "FAIL"
- score: weighted total (0-100)
- feedback: 2-4 sentence summary of rubric observations
- issues: list of atomic, actionable edits for regeneration if FAIL
- strengths: list of positive observations about the image"""

    return prompt
