"""
Unified Evaluator: Combines v3.py and edubench.py evaluators.
Single clean function that takes request + questions and runs both evaluations.
"""

INCEPTBENCH_VERSION = "1.4.2"

import sys
import uuid
import time
import logging
from pathlib import Path
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from pydantic import BaseModel, ConfigDict, Field
from typing import Any, List, Optional, Literal, Dict
import os
import json
import re
import requests
import asyncio
import anthropic
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add submodules to path
_submodules_base = Path(__file__).parent / "submodules"
_submodule_paths = [
    _submodules_base,  # For incept_core imports
    _submodules_base / "reading-question-qc",
    _submodules_base / "EduBench" / "code" / "evaluation",
    _submodules_base / "agentic-incept-reasoning",  # For utils imports
    _submodules_base / "agentic-incept-reasoning" / "src",  # For edu_agents imports
]

# Add all submodule paths to sys.path
for path in _submodule_paths:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

# Import from incept_core (extracted minimal files from incept-multilingual-generation)
from incept_core.evaluator.v3 import (
    call_single_shot_evaluator,
    build_single_shot_messages,
    EvaluationDimension,
    clip01
)
from incept_core.evaluator.llm_interface import simple_solve_with_llm
from incept_core.evaluator.edubench import verify_answer_with_gpt4, get_normal_answer
from evaluation import TASK_PROMPT_TEMPLATES
from qc_pipeline import QuestionQCAnalyzer

# Import evaluate_content using importlib to bypass package __init__.py files
# This avoids triggering the full dependency chain (tools, cairosvg, etc.)
def _import_evaluate_content():
    """Import evaluate_content directly without triggering package __init__.py files."""
    import importlib.util
    import sys

    try:
        # Get path to content_evaluator.py
        _agentic_src = Path(__file__).parent / "submodules" / "agentic-incept-reasoning" / "src"
        content_eval_path = _agentic_src / "edu_agents" / "eval" / "content_evaluator.py"

        if not content_eval_path.exists():
            return None

        # Create empty parent module namespaces to allow proper imports
        # This prevents triggering __init__.py files while allowing Pydantic to work
        if 'edu_agents' not in sys.modules:
            sys.modules['edu_agents'] = type(sys)('edu_agents')
        if 'edu_agents.core' not in sys.modules:
            sys.modules['edu_agents.core'] = type(sys)('edu_agents.core')
        if 'edu_agents.eval' not in sys.modules:
            sys.modules['edu_agents.eval'] = type(sys)('edu_agents.eval')

        # Load api_key_manager with proper module name
        api_key_path = _agentic_src / "edu_agents" / "core" / "api_key_manager.py"
        if api_key_path.exists() and 'edu_agents.core.api_key_manager' not in sys.modules:
            api_spec = importlib.util.spec_from_file_location("edu_agents.core.api_key_manager", api_key_path)
            if api_spec and api_spec.loader:
                api_module = importlib.util.module_from_spec(api_spec)
                sys.modules['edu_agents.core.api_key_manager'] = api_module
                api_spec.loader.exec_module(api_module)

        # Load content_evaluator with proper module name for Pydantic to work
        if 'edu_agents.eval.content_evaluator' not in sys.modules:
            spec = importlib.util.spec_from_file_location("edu_agents.eval.content_evaluator", content_eval_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules['edu_agents.eval.content_evaluator'] = module
                spec.loader.exec_module(module)

                # Rebuild Pydantic models after loading
                if hasattr(module, 'ComparisonResult'):
                    module.ComparisonResult.model_rebuild()
                if hasattr(module, 'PassFailResult'):
                    module.PassFailResult.model_rebuild()
                if hasattr(module, 'EvaluationResult'):
                    module.EvaluationResult.model_rebuild()

                return module.evaluate_content

        return sys.modules.get('edu_agents.eval.content_evaluator', {}).get('evaluate_content')

    except Exception:
        return None

evaluate_content = _import_evaluate_content()


# ============================================================================
# Article Markdown Parsing Utilities
# ============================================================================

def parse_article_markdown(content: str) -> Dict[str, Any]:
    """
    Parse markdown article content to extract:
    - Text content (combined from all text sections)
    - Embedded questions (with options, answers, explanations)
    - Images (URLs from markdown image syntax)
    - Structure metadata (headings, sections)

    Returns a dictionary with:
    - text_content: Combined text for text evaluators
    - embedded_questions: List of parsed question dicts
    - images: List of image URLs
    - structure: Metadata about article structure
    """
    result = {
        "text_content": "",
        "embedded_questions": [],
        "images": [],
        "structure": {
            "headings": [],
            "sections_count": 0
        }
    }

    lines = content.split('\n')
    text_parts = []
    current_question = None
    in_question_block = False
    question_lines = []

    for line in lines:
        # Extract images: ![alt](url)
        image_matches = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', line)
        for alt_text, url in image_matches:
            result["images"].append(url)

        # Extract headings: # Title, ## Subtitle, etc.
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading_match:
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()
            result["structure"]["headings"].append({"level": level, "title": title})
            text_parts.append(line)  # Include headings in text
            continue

        # Detect embedded questions
        # Pattern: **Question:** followed by options **A)** or A), etc.
        # Answer marked with ✓, followed by **Explanation:**

        if re.match(r'^\*\*Question:\*\*', line):
            in_question_block = True
            question_lines = [line]
            current_question = {"options": {}, "answer": None, "question": line.replace('**Question:**', '').strip()}
            continue

        if in_question_block:
            question_lines.append(line)

            # Extract options: **A)** text, A) text, or any variation
            # Pattern matches: **A)** text, A) text, etc.
            option_match = re.match(r'^\*\*([A-D])\)\*\*\s+(.+)$', line)
            if not option_match:
                option_match = re.match(r'^([A-D])\)\s+(.+)$', line)

            if option_match:
                option_letter = option_match.group(1)
                option_text = option_match.group(2).strip()
                # Check if this is the correct answer (marked with ✓)
                if '✓' in option_text:
                    option_text = option_text.replace('✓', '').strip()
                    current_question["answer"] = option_text
                    current_question["answer_letter"] = option_letter
                current_question["options"][option_letter] = option_text

            # Extract answer line: **Answer:** C) 35 riyals
            if line.startswith('**Answer:**'):
                answer_text = line.replace('**Answer:**', '').strip()
                if not current_question.get("answer"):
                    current_question["answer"] = answer_text

            # Extract explanation
            if line.startswith('**Explanation:**'):
                current_question["explanation"] = line.replace('**Explanation:**', '').strip()
                current_question["explanation_lines"] = []
            elif current_question and "explanation_lines" in current_question:
                # Continue collecting explanation until we hit a separator or specific end marker
                if line.strip() and not line.startswith('**Step'):
                    current_question["explanation_lines"].append(line.strip())
                elif line.startswith('**Step'):
                    # Step-by-step explanations are part of the explanation
                    current_question["explanation_lines"].append(line.strip())

            # End of question block (separator ---  or double newline after we have explanation)
            if line.strip() == '---':
                # Combine explanation lines
                if current_question.get("explanation_lines"):
                    full_explanation = current_question["explanation"] + "\n\n" + "\n".join(current_question["explanation_lines"])
                    current_question["explanation"] = full_explanation
                    del current_question["explanation_lines"]

                # Only add if we have valid question data
                if current_question.get("question") and current_question.get("options"):
                    result["embedded_questions"].append(current_question)

                in_question_block = False
                current_question = None
                question_lines = []
                continue
        else:
            # Regular text content (not in question block)
            if line.strip() and not line.strip().startswith('---'):
                # Remove markdown image syntax from text content
                clean_line = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'\1', line)
                text_parts.append(clean_line)

    # Combine all text parts
    result["text_content"] = '\n'.join(text_parts)
    result["structure"]["sections_count"] = len(result["structure"]["headings"])

    return result


class UniverslSkillInfoInput(BaseModel):
    title: str
    grade: str
    subject: str = "mathematics"
    difficulty: Optional[Literal["easy", "medium", "hard"]] = "medium"
    description: Optional[str] = None
    language: Literal['en', 'ar'] = 'en'

class UniversalGeneratedQuestionInput(BaseModel):
    id: str
    type: Literal["mcq", "fill-in"]  # MCQ and fill-in questions supported
    question: str
    answer: str
    answer_explanation: str
    answer_options: Optional[Dict[str, str]] = None  # Dict format for MCQ: {"A": "4 cm", "B": "0.4 cm", ...}
    skill: Optional[UniverslSkillInfoInput] = None
    image_url: Optional[str] = None
    additional_details: Optional[str] = None


class UniversalGeneratedTextInput(BaseModel):
    """
    Model for text/passage content (non-question formats)
    """
    id: str
    type: Literal["text", "passage", "explanation"]  # Text-based content types
    content: str  # Main text content
    title: Optional[str] = None  # Optional title
    skill: Optional[UniverslSkillInfoInput] = None
    image_url: Optional[str] = None
    additional_details: Optional[str] = None  # Context or metadata


class UniversalArticleInput(BaseModel):
    """
    Model for article content - a complete markdown-formatted educational article
    that can contain mixed content: headings, text, images, embedded questions.
    The entire article is stored as a single markdown string for semantic evaluation.
    """
    id: str
    type: Literal["article"] = "article"
    content: str  # Full markdown article with headings, text, images, embedded questions
    skill: Optional[UniverslSkillInfoInput] = None
    title: Optional[str] = None  # Article title (can be extracted from first h1 if not provided)
    language: Literal['en', 'ar'] = 'en'
    additional_details: Optional[str] = None  # Context or generation metadata


class UniversalEvaluationRequest(BaseModel):
    # At least one of these must be provided
    generated_questions: List[UniversalGeneratedQuestionInput] = Field(default_factory=list)
    generated_content: List[UniversalGeneratedTextInput] = Field(default_factory=list)
    generated_articles: List[UniversalArticleInput] = Field(default_factory=list)

    # User-facing parameters for automatic routing
    subject: Optional[Literal["math", "ela", "science", "social-studies", "history", "general"]] = None
    grade: Optional[str] = None  # e.g., "K", "1", "2", "3-5", "9-12", etc.
    type: Optional[Literal["mcq", "fill-in", "short-answer", "essay", "text-content", "passage", "article"]] = None

    # Internal parameter - auto-determined if not specified
    submodules_to_run: Optional[List[Literal["ti_question_qa", "answer_verification", "external_edubench", "reading_question_qc", "math_content_evaluator", "text_content_evaluator", "math_image_judge_evaluator", "image_quality_di_evaluator", "article_holistic_evaluator"]]] = None
    verbose: bool = False  # If False, returns only overall scores per module

    def model_post_init(self, __context):
        """Validate that at least one content type is provided and determine submodules"""
        if not self.generated_questions and not self.generated_content and not self.generated_articles:
            raise ValueError("At least one of 'generated_questions', 'generated_content', or 'generated_articles' must be provided")

        # Auto-determine submodules if not explicitly specified
        if self.submodules_to_run is None:
            self.submodules_to_run = self._determine_submodules()

    def _determine_submodules(self) -> List[str]:
        """
        Intelligently determine which submodules to run based on content type and parameters.
        PHILOSOPHY: Maximum coverage - run as many applicable evaluators as possible for
        comprehensive assessment from multiple perspectives.
        """
        modules = []
        has_questions = bool(self.generated_questions)
        has_content = bool(self.generated_content)
        has_articles = bool(self.generated_articles)

        # Check if content is math-related
        is_math_related = self._is_math_related()

        # Question-specific evaluators
        if has_questions:
            # Core question evaluator - ALWAYS run for ALL questions
            modules.append("ti_question_qa")

            # Answer verification - ONLY run for math-related questions
            if is_math_related:
                modules.append("answer_verification")

            # Content quality evaluator - ONLY run for math-related content
            # Checks: curriculum_alignment, cognitive_demand, accuracy_and_rigor,
            # misconceptions, engagement, instructional_support, clarity
            if is_math_related:
                modules.append("math_content_evaluator")

            # Reading QC - ALWAYS run for ALL questions
            # For MCQs: Full 11 checks (6 distractor + 5 question checks)
            # For fill-in/other: 5 universal question checks (alignment, clarity,
            #   single correct answer, passage accuracy, difficulty)
            # Maximum coverage approach: even partial checks add value!
            modules.append("reading_question_qc")

            # Educational benchmark - DISABLED BY DEFAULT (requires HuggingFace endpoint)
            # Users must explicitly request it via submodules_to_run parameter
            # modules.append("external_edubench")

        # Content-specific evaluators
        if has_content or self.type in ["text-content", "passage"]:
            # Text content evaluator - ALWAYS run for ALL text content
            modules.append("text_content_evaluator")

            # Content quality evaluator - ONLY run for math-related text content
            # The 9 criteria are universal: curriculum alignment, cognitive demand,
            # accuracy, engagement, clarity, etc. - apply to all subjects
            if is_math_related:
                modules.append("math_content_evaluator")

        # Article-specific evaluators
        if has_articles or self.type == "article":
            # Article holistic evaluator - ALWAYS run for articles (evaluates as unified experience)
            modules.append("article_holistic_evaluator")

            # Text content evaluator - ALWAYS run for articles (evaluates combined text)
            modules.append("text_content_evaluator")

            # Content quality evaluator - ONLY run for math-related articles
            if is_math_related:
                modules.append("math_content_evaluator")

            # Note: Articles may contain embedded questions and images which will be
            # extracted and evaluated separately by their respective evaluators

        # Remove duplicates and return
        return list(set(modules)) if modules else ["ti_question_qa"]

    def _is_math_related(self) -> bool:
        """
        Determine if content is math-related by checking:
        1. The subject parameter
        2. The skill.subject field in questions, content, or articles
        """
        # Check if subject parameter is math or mathematics
        if self.subject and self.subject.lower() in ["math", "mathematics"]:
            return True

        # Check skill.subject in questions
        if self.generated_questions:
            for question in self.generated_questions:
                if question.skill and question.skill.subject:
                    subject_lower = question.skill.subject.lower()
                    if "math" in subject_lower:
                        return True

        # Check skill.subject in content
        if self.generated_content:
            for content in self.generated_content:
                if content.skill and content.skill.subject:
                    subject_lower = content.skill.subject.lower()
                    if "math" in subject_lower:
                        return True

        # Check skill.subject in articles
        if self.generated_articles:
            for article in self.generated_articles:
                if article.skill and article.skill.subject:
                    subject_lower = article.skill.subject.lower()
                    if "math" in subject_lower:
                        return True

        return False

class EdubenchScores(BaseModel):
    qa_score: float
    ec_score: float
    ip_score: float
    ag_score: float
    qg_score: float
    tmg_score: float
    average_score: float


class InternalEvaluatorScores(BaseModel):
    correctness: float
    grade_alignment: float
    difficulty_alignment: float
    language_quality: float
    pedagogical_value: float
    explanation_quality: float
    instruction_adherence: float
    format_compliance: float
    query_relevance: float
    di_compliance: float


class DIScores(BaseModel):
    overall: float
    general_principles: float
    format_alignment: float
    grade_language: float


class SectionEvaluation(BaseModel):
    section_score: float
    issues: List[str]
    strengths: List[str]
    recommendation: str


class SectionEvaluations(BaseModel):
    question: SectionEvaluation
    scaffolding: SectionEvaluation


class InternalEvaluatorResult(BaseModel):
    scores: InternalEvaluatorScores
    issues: List[str]
    strengths: List[str]
    overall: float
    recommendation: str
    suggested_improvements: List[str]
    di_scores: DIScores
    section_evaluations: SectionEvaluations


class AnswerVerificationResult(BaseModel):
    is_correct: bool
    correct_answer: str
    confidence: int
    reasoning: str


class ReadingQuestionQCResult(BaseModel):
    overall_score: float
    distractor_checks: Dict[str, Any]
    question_checks: Dict[str, Any]
    passed: bool


# Simplified models for non-verbose mode
class SimplifiedInternalEvaluatorResult(BaseModel):
    overall: float


class SimplifiedAnswerVerificationResult(BaseModel):
    is_correct: bool


class SimplifiedEdubenchScores(BaseModel):
    average_score: float


class SimplifiedReadingQuestionQCResult(BaseModel):
    overall_score: float


class ContentEvaluatorResult(BaseModel):
    """Detailed content evaluation result"""
    overall_rating: str  # SUPERIOR, ACCEPTABLE, INFERIOR
    curriculum_alignment: str  # PASS or FAIL
    cognitive_demand: str
    accuracy_and_rigor: str
    image_quality: str
    reveals_misconceptions: str
    question_type_appropriateness: str
    engagement_and_relevance: str
    instructional_support: str
    clarity_and_accessibility: str
    pass_count: int
    fail_count: int
    overall_score: float  # 0-1 scale based on pass/fail ratio


class SimplifiedContentEvaluatorResult(BaseModel):
    """Simplified content evaluation result with just overall score"""
    overall_score: float


class TextContentEvaluatorResult(BaseModel):
    """Detailed text content pedagogical evaluation result using v3 dimensions"""
    correctness: float
    grade_alignment: float
    language_quality: float
    pedagogical_value: float
    explanation_quality: float
    di_compliance: float
    instruction_adherence: float
    query_relevance: float
    overall: float
    recommendation: str  # accept, revise, reject
    issues: List[str]
    strengths: List[str]
    suggested_improvements: List[str]
    di_scores: DIScores


class SimplifiedTextContentEvaluatorResult(BaseModel):
    """Simplified text content evaluation result with just overall score"""
    overall: float


class MathImageJudgeResult(BaseModel):
    """Detailed image quality evaluation result using image quality checker"""
    rating: str  # PASS, FAIL, or NO_ACCESS
    description: str
    selected_image_url: Optional[str] = None
    individual_image_ratings: Optional[Dict[str, str]] = None
    object_counts: Optional[List[Dict[str, Any]]] = None
    pass_score: float  # 1.0 for PASS, 0.0 for FAIL/NO_ACCESS


class SimplifiedMathImageJudgeResult(BaseModel):
    """Simplified image quality result with just pass score"""
    pass_score: float


class ImageDIRanking(BaseModel):
    """Single image evaluation from DI rubric checker"""
    rank: int
    image_index: int
    score: int  # 0-100 weighted score
    strengths: List[str]
    weaknesses: List[str]
    changes_required: List[str]
    recommendation: str  # ACCEPT or REJECT


class ImageQualityDIResult(BaseModel):
    """Detailed DI rubric-based image quality evaluation"""
    rankings: List[ImageDIRanking]
    best_image_index: int
    overall_feedback: str
    best_score: int  # Best image score for easy access
    normalized_score: float  # 0-1 scale for final scoring


class SimplifiedImageQualityDIResult(BaseModel):
    """Simplified DI quality result with just normalized score"""
    normalized_score: float  # 0-1 scale


class ArticleHolisticEvaluatorResult(BaseModel):
    """Result from article holistic evaluation"""
    pedagogical_coherence: float
    content_organization: float
    scaffolding_quality: float
    engagement: float
    mixed_media_integration: float
    learning_objectives_clarity: float
    grade_appropriateness: float
    completeness: float
    cognitive_load_management: float
    instructional_clarity: float
    overall: float
    recommendation: Literal["accept", "revise", "reject"]
    issues: List[str]
    strengths: List[str]
    suggested_improvements: List[str]


class SimplifiedArticleHolisticResult(BaseModel):
    """Simplified result showing only overall score"""
    overall: float
    recommendation: Literal["accept", "revise", "reject"]


class UniversalQuestionEvaluationScores(BaseModel):
    model_config = ConfigDict(
        # Exclude None values when serializing to JSON
        exclude_none=True
    )

    ti_question_qa: Optional[InternalEvaluatorResult | SimplifiedInternalEvaluatorResult] = None
    answer_verification: Optional[AnswerVerificationResult | SimplifiedAnswerVerificationResult] = None
    external_edubench: Optional[EdubenchScores | SimplifiedEdubenchScores] = None
    reading_question_qc: Optional[ReadingQuestionQCResult | SimplifiedReadingQuestionQCResult] = None
    math_content_evaluator: Optional[ContentEvaluatorResult | SimplifiedContentEvaluatorResult] = None
    text_content_evaluator: Optional[TextContentEvaluatorResult | SimplifiedTextContentEvaluatorResult] = None
    math_image_judge_evaluator: Optional[MathImageJudgeResult | SimplifiedMathImageJudgeResult] = None
    image_quality_di_evaluator: Optional[ImageQualityDIResult | SimplifiedImageQualityDIResult] = None
    article_holistic_evaluator: Optional[ArticleHolisticEvaluatorResult | SimplifiedArticleHolisticResult] = None
    score: Optional[float] = None  # Combined score from all evaluations (0-1 scale)
    final_score: Optional[float] = None  # Deprecated - use 'score' instead


class UniversalEvaluationResponse(BaseModel):
    request_id: str
    evaluations: Dict[str, UniversalQuestionEvaluationScores]
    evaluation_time_seconds: float
    inceptbench_version: str

# Configure logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def score_edubench_response_with_llm(task_type: str, response: str, prompt: str, question_context: Dict[str, Any] = None) -> float:
    """
    Score EduBench response using GPT-4 following EduBench's official evaluation methodology.

    Based on EduBench paper: https://arxiv.org/pdf/2505.16160
    Uses their 3 evaluation principles:
    1. Scenario Adaptability
    2. Factual & Reasoning Accuracy
    3. Pedagogical Application

    Args:
        task_type: The EduBench task type (QA, EC, IP, AG, QG, TMG)
        response: The model's response to evaluate
        prompt: The original prompt sent to the model

    Returns:
        Score from 0-10
    """
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        logger.warning("No OpenAI API key found, skipping LLM scoring")
        return 0.0

    # Build context information
    context_info = ""
    if question_context:
        if "question" in question_context:
            context_info += f"\nQuestion: {question_context['question']}"
        if "answer" in question_context:
            context_info += f"\nCorrect Answer: {question_context['answer']}"
        if "explanation" in question_context:
            context_info += f"\nExpected Explanation: {question_context['explanation'][:300]}"
        if "difficulty" in question_context:
            context_info += f"\nDifficulty Level: {question_context['difficulty']}"
        if "grade" in question_context:
            context_info += f"\nGrade Level: {question_context['grade']}"

    # EduBench official evaluation dimensions
    evaluation_prompt = f"""You are an expert evaluator following the EduBench evaluation methodology.

IMPORTANT: You are evaluating responses from EDU-Qwen2.5-7B, a 7B parameter model that tends to be:
- Verbose and repetitive (may repeat answers multiple times)
- Sometimes provides multiple JSON blocks instead of one
- May include extra explanations beyond what was asked
- May echo parts of the prompt in the response

DO NOT penalize these stylistic issues. Focus ONLY on the core educational content quality.

Evaluate the BEST interpretation of the response across these dimensions:

**1. Scenario Adaptability:**
- Instruction Following & Task Completion (did it accomplish the core task?)
- Role & Tone Consistency (appropriate educational tone?)
- Content Relevance & Scope Control (relevant to the question?)
- Scenario Element Integration (addresses the educational context?)

**2. Factual & Reasoning Accuracy:**
- Basic Factual Accuracy (is the core answer correct?)
- Domain Knowledge Accuracy (demonstrates subject understanding?)
- Reasoning Process Rigor (logical steps present?)
- Error Identification & Correction Precision (for EC tasks: correctly identifies issues?)

**3. Pedagogical Application:**
- Clarity, Simplicity & Inspiration (understandable despite verbosity?)
- Motivation, Guidance & Positive Feedback (supportive tone?)
- Personalization, Adaptation & Learning Support (helpful for learning?)
- Higher-Order Thinking & Skill Development (promotes understanding?)

**Context:**{context_info}

**Task Type:** {task_type}

**Prompt Sent to Model:**
{prompt}

**Model Response (may be verbose/repetitive):**
{response}

**Scoring Guidelines:**
Extract the BEST answer from the response (ignore repetitions). Score based on:
- 0-3: Factually wrong or completely missing the task
- 4-6: Partially correct but missing key elements or has significant errors
- 7-8: Correct and educationally sound despite verbosity
- 9-10: Excellent content with comprehensive, accurate pedagogical value

DO NOT deduct points for:
- Verbosity or repetition
- Multiple JSON blocks
- Extra explanations
- Formatting issues

DO deduct points for:
- Factual errors
- Missing required task elements
- Poor pedagogical approach
- Incorrect reasoning

Return ONLY a JSON object:
{{"score": <number 0-10>, "reasoning": "<brief explanation focusing on content quality>"}}"""

    try:
        headers = {
            "Authorization": f"Bearer {openai_key}",
            "Content-Type": "application/json"
        }

        response_obj = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            timeout=270,
            json={
                "model": "gpt-5",
                "messages": [{"role": "user", "content": evaluation_prompt}]
            }
        )

        if response_obj.status_code == 200:
            content = response_obj.json()['choices'][0]['message']['content']
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
                score = result.get('score', 0)
                logger.debug(f"{task_type} LLM score: {score}/10 - {result.get('reasoning', '')[:100]}")
                return float(score)

        logger.warning(f"Failed to get LLM score for {task_type}: {response_obj.status_code}")
        return 0.0

    except Exception as e:
        logger.error(f"Error scoring {task_type} with LLM: {e}")
        return 0.0

def _run_content_evaluation_task_sync(item_idx: int, item) -> Dict[str, Any]:
    """Synchronous wrapper for running content evaluation task.

    Accepts both UniversalGeneratedQuestionInput and UniversalGeneratedTextInput.
    """

    # Check if evaluate_content is available
    if evaluate_content is None:
        logger.warning(f"Content evaluator not available for item {item_idx} - skipping")
        return {
            'question_idx': item_idx,
            'result': None,
            'error': 'Content evaluator not available - edu_agents.eval.content_evaluator could not be imported'
        }

    async def _async_task():
        logger.debug(f"Running content evaluation for item {item_idx}")

        try:
            # Build content string based on item type
            content_parts = []

            # Check if this is a question or text content
            is_question = hasattr(item, 'question') and item.question is not None

            if is_question:
                # Question format
                content_parts = [
                    f"**Question:** {item.question}",
                    f"**Answer:** {item.answer}",
                ]

                if item.answer_explanation:
                    content_parts.append(f"**Explanation:** {item.answer_explanation}")

                if hasattr(item, 'answer_options') and item.answer_options:
                    options_str = "\n".join([f"{k}: {v}" for k, v in item.answer_options.items()])
                    content_parts.append(f"**Options:**\n{options_str}")
            else:
                # Text content format
                if hasattr(item, 'title') and item.title:
                    content_parts.append(f"**Title:** {item.title}")
                content_parts.append(f"**Content:** {item.content}")

            # Add common metadata
            if item.skill:
                content_parts.append(f"**Grade:** {item.skill.grade}")
                content_parts.append(f"**Subject:** {item.skill.subject}")
                if item.skill.difficulty:
                    content_parts.append(f"**Difficulty:** {item.skill.difficulty}")

            content = "\n\n".join(content_parts)

            # Evaluate content
            evaluation_json = await evaluate_content(content)

            # Parse the JSON response
            evaluation_data = json.loads(evaluation_json)

            return {
                'question_idx': item_idx,
                'result': evaluation_data
            }
        except Exception as e:
            logger.error(f"Error running content evaluation for item {item_idx}: {e}")
            return {
                'question_idx': item_idx,
                'result': None,
                'error': str(e)
            }

    # Run the async function in a new event loop
    return asyncio.run(_async_task())


def call_text_content_evaluator(text_content: UniversalGeneratedTextInput, total_items: int) -> Dict[str, Any]:
    """
    Evaluate text content using v3 evaluator's pedagogical dimensions.
    Adapted from call_single_shot_evaluator but for text/passage content.

    Returns normalized scores (0-1) across relevant dimensions:
    - CORRECTNESS: Factual accuracy of content
    - GRADE_ALIGNMENT: Appropriate for target grade level
    - LANGUAGE_QUALITY: Clarity, grammar, age-appropriate language
    - PEDAGOGICAL_VALUE: Educational impact and learning value
    - EXPLANATION_QUALITY: How well content explains concepts
    - DI_COMPLIANCE: Adherence to Direct Instruction principles
    - INSTRUCTION_ADHERENCE: Follows requirements/specifications
    - QUERY_RELEVANCE: Matches intended topic/skill
    """
    import time
    import json

    # Build evaluation messages for text content
    messages = _build_text_evaluation_messages(text_content, total_items)

    # Time the LLM call
    llm_start = time.time()

    # Use the same LLM interface as v3 evaluator
    data = simple_solve_with_llm(messages=messages)

    llm_time = time.time() - llm_start
    logger.debug(f"⏱️ Text content LLM evaluation call: {llm_time:.2f}s")

    # Normalize scores to 0..1 (same as v3)
    sr = data.get("scores", {})
    scores = {
        EvaluationDimension.CORRECTNESS: clip01(sr.get("correctness", 5) / 10.0),
        EvaluationDimension.GRADE_ALIGNMENT: clip01(sr.get("grade_alignment", 5) / 10.0),
        EvaluationDimension.LANGUAGE_QUALITY: clip01(sr.get("language_quality", 5) / 10.0),
        EvaluationDimension.PEDAGOGICAL_VALUE: clip01(sr.get("pedagogical_value", 5) / 10.0),
        EvaluationDimension.EXPLANATION_QUALITY: clip01(sr.get("explanation_quality", 5) / 10.0),
        EvaluationDimension.INSTRUCTION_ADHERENCE: clip01(sr.get("instruction_adherence", 5) / 10.0),
        EvaluationDimension.QUERY_RELEVANCE: clip01(sr.get("query_relevance", 5) / 10.0),
    }

    issues = list(data.get("issues", []))[:10]
    strengths = list(data.get("strengths", []))[:10]
    suggestions = list(data.get("suggested_improvements", []))[:10]
    recommendation = data.get("recommendation", "revise")
    if recommendation not in {"accept", "revise", "reject"}:
        recommendation = "revise"

    # Calculate overall score
    overall = sum(scores.values()) / max(1, len(scores))

    # DI scores
    di_scores_raw = data.get("di_scores", {}) or {}
    di_overall_raw = di_scores_raw.get("overall", sr.get("di_compliance", 5))
    di_scores = {
        "overall": clip01(float(di_overall_raw) / 10.0),
        "general_principles": clip01(float(di_scores_raw.get("general_principles", di_overall_raw)) / 10.0),
        "format_alignment": clip01(float(di_scores_raw.get("format_alignment", di_overall_raw)) / 10.0),
        "grade_language": clip01(float(di_scores_raw.get("grade_language", di_overall_raw)) / 10.0),
    }
    scores[EvaluationDimension.DI_COMPLIANCE] = di_scores["overall"]

    return {
        "scores": scores,
        "issues": issues,
        "strengths": strengths,
        "overall": overall,
        "recommendation": recommendation,
        "suggested_improvements": suggestions,
        "di_scores": di_scores,
        "section_evaluations": {
            "content": {
                "section_score": overall * 10.0,  # Convert back to 0-10 for consistency
                "issues": issues,
                "strengths": strengths,
                "recommendation": recommendation
            }
        }
    }


def _build_text_evaluation_messages(content: UniversalGeneratedTextInput, total_items: int) -> List[Dict[str, str]]:
    """
    Build LLM messages for evaluating text content (not questions).
    Adapted from build_single_shot_messages but focused on content evaluation.
    """
    from incept_core.direct_instruction.principles_constants import (
        DI_INDIVIDUAL_QUESTION_PRINCIPLES,
        DI_SCAFFOLDING_PRINCIPLES,
        GRADE_VOCABULARY_EXAMPLES_AR,
        GRADE_VOCABULARY_EXAMPLES_EN,
    )

    # Build request metadata
    req_meta = {
        "requested_grade": content.skill.grade if content.skill else None,
        "requested_language": content.skill.language if content.skill else "en",
        "content_type": content.type,
        "requested_difficulty": content.skill.difficulty if content.skill else "medium",
        "total_items": total_items,
        "topic": content.skill.title if content.skill else None,
        "subject": content.skill.subject if content.skill else "general",
        "additional_context": content.additional_details if content.additional_details else "",
    }

    language = str(req_meta.get("requested_language") or "english").lower()
    grade = req_meta.get("requested_grade")
    grade_examples = None
    if grade is not None:
        try:
            grade_key = f"Grade{int(grade)}"
            store = GRADE_VOCABULARY_EXAMPLES_AR if language.startswith("ar") else GRADE_VOCABULARY_EXAMPLES_EN
            grade_examples = store.get(grade_key)
        except Exception:
            grade_examples = None

    system = (
        "You are an expert educational content evaluator specializing in text-based educational materials. "
        "Your role is to assess the pedagogical value, accuracy, and appropriateness of educational text content.\n\n"
        "EVALUATION CONTEXT:\n"
        "You are evaluating TEXT CONTENT (passages, explanations, educational text) - NOT questions.\n"
        "Focus on content quality, educational value, and pedagogical effectiveness.\n\n"
        "KEY EVALUATION DIMENSIONS FOR TEXT CONTENT:\n\n"
        "1. **Correctness (0-10)**: Factual accuracy and reliability\n"
        "   - Are all facts, concepts, and examples accurate?\n"
        "   - Are there any misconceptions or errors?\n"
        "   - Is the information up-to-date and scientifically sound?\n\n"
        "2. **Grade Alignment (0-10)**: Age and grade appropriateness\n"
        "   - Is the complexity appropriate for the target grade?\n"
        "   - Are concepts introduced at the right developmental level?\n"
        "   - Are prior knowledge assumptions reasonable?\n\n"
        "3. **Language Quality (0-10)**: Clarity and linguistic appropriateness\n"
        "   - Is the language clear and grammatically correct?\n"
        "   - Is vocabulary appropriate for the grade level?\n"
        "   - Are sentences well-structured and easy to follow?\n\n"
        "4. **Pedagogical Value (0-10)**: Educational effectiveness\n"
        "   - Does the content promote meaningful learning?\n"
        "   - Are concepts explained in a way that builds understanding?\n"
        "   - Does it connect to real-world applications or prior knowledge?\n\n"
        "5. **Explanation Quality (0-10)**: How well concepts are explained\n"
        "   - Are explanations clear and well-structured?\n"
        "   - Does it use examples, analogies, or visuals effectively?\n"
        "   - Does it break down complex ideas into manageable parts?\n\n"
        "6. **DI Compliance (0-10)**: Direct Instruction principles\n"
        "   - Is the content structured and systematic?\n"
        "   - Does it follow explicit instruction principles?\n"
        "   - Is it appropriate for guided learning?\n\n"
        "7. **Instruction Adherence (0-10)**: Meets requirements\n"
        "   - Does content match the requested topic/subject?\n"
        "   - Is the length and depth appropriate?\n"
        "   - Does it follow any specified format or style?\n\n"
        "8. **Query Relevance (0-10)**: Topic alignment (VETO POWER)\n"
        "   - Does content directly address the intended topic?\n"
        "   - Is it focused and on-target?\n"
        "   - Score < 4.0 = AUTO-REJECT for off-topic content\n\n"
        "DIRECT INSTRUCTION (DI) EVALUATION:\n"
        "- Assess alignment with DI principles (clarity, structure, scaffolding)\n"
        "- Check for grade-appropriate language and vocabulary\n"
        "- Evaluate if content is suitable for explicit instruction\n\n"
        "RECOMMENDATION LOGIC:\n"
        "- REJECT if: query_relevance < 4.0 (off-topic), correctness < 4.0 (factually wrong), or major pedagogical issues\n"
        "- REVISE if: content is on-topic and accurate but needs improvement in clarity, structure, or pedagogical approach\n"
        "- ACCEPT if: content is accurate, on-topic, grade-appropriate, and pedagogically sound\n\n"
        "OUTPUT REQUIREMENTS:\n"
        "Return STRICT JSON with this schema:\n"
        "{\n"
        "  \"scores\": {\n"
        "    \"correctness\": 0-10,\n"
        "    \"grade_alignment\": 0-10,\n"
        "    \"language_quality\": 0-10,\n"
        "    \"pedagogical_value\": 0-10,\n"
        "    \"explanation_quality\": 0-10,\n"
        "    \"di_compliance\": 0-10,\n"
        "    \"instruction_adherence\": 0-10,\n"
        "    \"query_relevance\": 0-10\n"
        "  },\n"
        "  \"issues\": [string],\n"
        "  \"strengths\": [string],\n"
        "  \"suggested_improvements\": [string],\n"
        "  \"recommendation\": \"accept\" | \"revise\" | \"reject\",\n"
        "  \"di_scores\": {\n"
        "    \"overall\": 0-10,\n"
        "    \"general_principles\": 0-10,\n"
        "    \"format_alignment\": 0-10,\n"
        "    \"grade_language\": 0-10\n"
        "  }\n"
        "}"
    )

    user = {
        "content": {
            "type": content.type,
            "title": content.title if content.title else "Untitled",
            "text": content.content,
            "skill": content.skill.title if content.skill else None,
            "subject": content.skill.subject if content.skill else "general",
            "grade": content.skill.grade if content.skill else None,
            "difficulty": content.skill.difficulty if content.skill else "medium",
            "image_url": content.image_url if content.image_url else None,
        },
        "request_context": req_meta,
        "di_guidance": {
            "individual_principles": DI_INDIVIDUAL_QUESTION_PRINCIPLES.strip(),
            "scaffolding_principles": DI_SCAFFOLDING_PRINCIPLES.strip(),
            "grade_language_examples": grade_examples,
            "weighting": {
                "general_principles": 0.4,
                "format_alignment": 0.35,
                "grade_language": 0.25
            }
        },
        "evaluation_instructions": (
            "Evaluate this educational text content across all dimensions.\n"
            "Provide specific evidence for each score.\n"
            "Check factual accuracy carefully.\n"
            "Assess pedagogical effectiveness and grade appropriateness.\n"
            "Verify content matches the intended topic (query_relevance).\n"
            "Return ONLY valid JSON - no additional text."
        )
    }

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": json.dumps(user, ensure_ascii=False)}
    ]
    return messages


def _run_text_content_evaluator_task(item_idx: int, text_content: UniversalGeneratedTextInput, total_items: int) -> Dict[str, Any]:
    """
    Run text content pedagogical evaluation task.
    Evaluates text content for pedagogical value, DI alignment, and internal standards.
    """
    logger.debug(f"Running text content pedagogical evaluation for item {item_idx}")

    try:
        result_dict = call_text_content_evaluator(text_content, total_items)
        return {
            'question_idx': item_idx,
            'result': result_dict
        }
    except Exception as e:
        logger.error(f"Error running text content evaluation for item {item_idx}: {e}")
        return {
            'question_idx': item_idx,
            'result': None,
            'error': str(e)
        }


def _run_article_holistic_evaluator_task(item_idx: int, parsed_article: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run article holistic evaluation task.
    Evaluates the article as a unified pedagogical experience.

    Args:
        item_idx: Index of the article
        parsed_article: Dictionary with 'article' (UniversalArticleInput) and 'parsed' (parse results)

    Returns:
        Dictionary with evaluation results
    """
    logger.debug(f"Running article holistic evaluation for item {item_idx}")

    try:
        # Import the article evaluator
        from incept_core.evaluator.article_evaluator import evaluate_article_holistic

        article_obj = parsed_article['article']
        parsed_data = parsed_article['parsed']

        # Call evaluator
        result = evaluate_article_holistic(
            article_content=article_obj.content,
            structure=parsed_data['structure'],
            skill=article_obj.skill.model_dump() if article_obj.skill else None,
            title=article_obj.title,
            language=article_obj.language
        )

        return {
            'question_idx': item_idx,
            'result': result.model_dump()
        }

    except Exception as e:
        logger.error(f"Error running article holistic evaluation for item {item_idx}: {e}")
        import traceback
        traceback.print_exc()
        return {
            'question_idx': item_idx,
            'result': None,
            'error': str(e)
        }


def _run_math_image_judge_task(item_idx: int, item) -> Dict[str, Any]:
    """
    Run math image quality evaluation using Claude's image quality checker.
    Only evaluates items that have an image_url.

    Accepts both UniversalGeneratedQuestionInput and UniversalGeneratedTextInput.
    """
    logger.debug(f"Running math image quality evaluation for item {item_idx}")

    # Check if item has an image
    if not hasattr(item, 'image_url') or not item.image_url:
        logger.debug(f"Item {item_idx} has no image_url, skipping image evaluation")
        return {
            'question_idx': item_idx,
            'result': None,
            'skip_reason': 'no_image'
        }

    async def _async_task():
        try:
            # Import the image quality checker
            _agentic_src = Path(__file__).parent / "submodules" / "agentic-incept-reasoning" / "src"
            sys.path.insert(0, str(_agentic_src))

            from edu_agents.tools.image_quality_checker_claude import ImageQualityChecker

            # Create checker instance
            checker = ImageQualityChecker()

            # Build expected description and context
            # Check if this is a question or text content
            is_question = hasattr(item, 'question') and item.question is not None

            if is_question:
                # For questions, use question text as context
                educational_context = f"Grade {item.skill.grade if item.skill else 'unknown'} {item.skill.subject if item.skill else 'mathematics'}"
                question_prompt = item.question

                # Build expected description from answer explanation or question
                expected_description = item.answer_explanation if item.answer_explanation else item.question
            else:
                # For text content
                educational_context = f"Grade {item.skill.grade if item.skill else 'unknown'} {item.skill.subject if item.skill else 'general'}"
                question_prompt = item.title if hasattr(item, 'title') and item.title else ""
                expected_description = item.content[:500]  # First 500 chars of content

            # Run the image quality check
            logger.info(f"Checking image quality for item {item_idx}: {item.image_url}")
            result_json = await checker.check_image_quality(
                image_urls=item.image_url,
                expected_description=expected_description,
                educational_context=educational_context,
                question_prompt=question_prompt,
                delete_failed_images=False  # Don't delete images in evaluation mode
            )

            # Parse JSON result
            result_data = json.loads(result_json)

            return {
                'question_idx': item_idx,
                'result': result_data
            }

        except Exception as e:
            logger.error(f"Error running math image evaluation for item {item_idx}: {e}")
            return {
                'question_idx': item_idx,
                'result': None,
                'error': str(e)
            }

    # Run the async function
    return asyncio.run(_async_task())


def _run_image_quality_di_task(item_idx: int, item) -> Dict[str, Any]:
    """
    Run DI rubric-based image quality evaluation.
    Only evaluates items that have an image_url.

    Uses the advanced DI (Direct Instruction) rubric with weighted criteria
    and pedagogical hard-fail gates.

    Accepts both UniversalGeneratedQuestionInput and UniversalGeneratedTextInput.
    """
    logger.debug(f"Running DI image quality evaluation for item {item_idx}")

    # Check if item has an image
    if not hasattr(item, 'image_url') or not item.image_url:
        logger.debug(f"Item {item_idx} has no image_url, skipping DI image evaluation")
        return {
            'question_idx': item_idx,
            'result': None,
            'skip_reason': 'no_image'
        }

    try:
        # Import the DI quality checker
        _image_gen_pkg = Path(__file__).parent / "submodules" / "image_generation_package"
        sys.path.insert(0, str(_image_gen_pkg))

        from image_generation.image_quality_checker_di import ImageQualityChecker

        # Create checker instance
        checker = ImageQualityChecker()

        # Build expected description and context
        # Check if this is a question or text content
        is_question = hasattr(item, 'question') and item.question is not None

        if is_question:
            # For questions, use question text and answer explanation
            educational_context = f"Grade {item.skill.grade if item.skill else 'unknown'} {item.skill.subject if item.skill else 'mathematics'}"

            # Combine question and explanation for expected description
            expected_parts = [item.question]
            if item.answer_explanation:
                expected_parts.append(f"Answer: {item.answer}")
                expected_parts.append(f"Explanation: {item.answer_explanation}")
            expected_description = "\n".join(expected_parts)

            # Age group for DI rubric
            age_group = f"Grade {item.skill.grade if item.skill else 'unknown'} students"
        else:
            # For text content
            educational_context = f"Grade {item.skill.grade if item.skill else 'unknown'} {item.skill.subject if item.skill else 'general'}"
            expected_description = item.content[:1000]  # First 1000 chars
            age_group = f"Grade {item.skill.grade if item.skill else 'unknown'} students"

        # Determine image role: if question has text, image accompanies it; otherwise standalone
        if is_question and item.question:
            # Has question text - image is supporting material
            image_role = "accompaniment"
        else:
            # No question context - image must be standalone
            image_role = "standalone"

        logger.info(f"Checking DI image quality for item {item_idx} (role: {image_role}): {item.image_url}")

        # Handle both single URL and list of URLs
        image_urls = [item.image_url] if isinstance(item.image_url, str) else item.image_url

        result = checker.check_image_quality_batch(
            image_urls=image_urls,
            expected_description=expected_description,
            educational_context=educational_context,
            age_group=age_group,
            image_role=image_role
        )

        # Convert to dict for return
        result_dict = {
            'rankings': [
                {
                    'rank': r.rank,
                    'image_index': r.image_index,
                    'score': r.score,
                    'strengths': r.strengths,
                    'weaknesses': r.weaknesses,
                    'changes_required': r.changes_required,
                    'recommendation': r.recommendation
                }
                for r in result.rankings
            ],
            'best_image_index': result.best_image_index,
            'overall_feedback': result.overall_feedback,
            'best_score': result.rankings[0].score if result.rankings else 0
        }

        return {
            'question_idx': item_idx,
            'result': result_dict
        }

    except Exception as e:
        logger.error(f"Error running DI image evaluation for item {item_idx}: {e}")
        return {
            'question_idx': item_idx,
            'result': None,
            'error': str(e)
        }


def _run_reading_qc_task_sync(question_idx: int, question: UniversalGeneratedQuestionInput, claude_api_key: str, openai_api_key: str = None, max_retries: int = 3) -> Dict[str, Any]:
    """Synchronous wrapper for running reading question QC analysis with retry logic."""

    async def _async_task():
        logger.debug(f"Running reading QC for question {question_idx}")

        # Initialize clients
        claude_client = anthropic.AsyncAnthropic(api_key=claude_api_key)
        openai_client = AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None

        try:
            # Create analyzer
            analyzer = QuestionQCAnalyzer(
                claude_client=claude_client,
                openai_client=openai_client,
                claude_model="claude-sonnet-4-5-20250929",
                openai_model="gpt-4o"
            )

            # Convert question to the format expected by QuestionQCAnalyzer
            question_item = {
                'question_id': question.id,
                'question_type': 'MCQ' if question.type == 'mcq' else 'MP',
                'passage_text': question.additional_details or '',
                'grade': int(question.skill.grade) if question.skill and question.skill.grade.isdigit() else 5,
                'structured_content': {
                    'question': question.question,
                    'choices': question.answer_options or {},
                    'correct_answer': question.answer,
                    'CCSS': question.skill.title if question.skill else '',
                    'CCSS_description': question.skill.description if question.skill else '',
                    'DOK': question.skill.difficulty if question.skill else 'medium'
                }
            }

            # Retry logic for API failures
            last_error = None
            for attempt in range(max_retries):
                try:
                    result = await analyzer.analyze_question(question_item, semaphore=None)
                    return_value = {
                        'question_idx': question_idx,
                        'result': result
                    }
                    break
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                        logger.warning(f"Reading QC attempt {attempt + 1}/{max_retries} failed for question {question_idx}, retrying in {wait_time}s: {e}")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"Reading QC failed for question {question_idx} after {max_retries} attempts: {e}")
                        return_value = {
                            'question_idx': question_idx,
                            'result': None,
                            'error': str(e)
                        }
        finally:
            # Properly close clients before event loop teardown
            try:
                await claude_client.close()
                if openai_client:
                    await openai_client.close()
            except Exception as e:
                logger.debug(f"Error closing clients: {e}")

        return return_value

    # Run the async function in a new event loop
    return asyncio.run(_async_task())

def _run_edubench_task(question_idx: int, task_type: str, question: UniversalGeneratedQuestionInput) -> Dict[str, Any]:
    """Run single EduBench task - just returns raw response like batch_edubench."""
    logger.debug(f"Running {task_type} task for question {question_idx}")

    # Extract explanation - always present as required field
    detailed_explanation = question.answer_explanation

    # Build prompt based on task type
    if task_type == "QA":
        prompt = TASK_PROMPT_TEMPLATES["QA"](question.question)
    elif task_type == "EC":
        prompt = TASK_PROMPT_TEMPLATES["EC"](question.question, question.answer)
    elif task_type == "IP":
        base_prompt = TASK_PROMPT_TEMPLATES["IP"](question.question)
        prompt = f"{base_prompt}\n\nReference scaffolding (detailed step-by-step guidance):\n{detailed_explanation}"
    elif task_type == "AG":
        base_prompt = TASK_PROMPT_TEMPLATES["AG"](question.question, question.answer)
        prompt = f"{base_prompt}\n\nReference explanation:\n{detailed_explanation}"
    elif task_type == "QG":
        # Extract knowledge point from skill (optional field)
        if question.skill:
            knowledge_point = question.skill.title
            subject = question.skill.subject
            level = question.skill.difficulty
        else:
            # Fallback if no skill provided
            knowledge_point = question.question.split('.')[0] if '.' in question.question else question.question[:50]
            subject = "mathematics"
            level = "medium"

        question_type = question.type  # "mcq" or "fill-in"
        prompt = TASK_PROMPT_TEMPLATES["QG"](knowledge_point, subject, question_type, level)
    elif task_type == "TMG":
        # Extract knowledge point from skill (optional field)
        if question.skill:
            knowledge_point = question.skill.title
        else:
            # Fallback if no skill provided
            knowledge_point = "General educational content"

        base_prompt = TASK_PROMPT_TEMPLATES["TMG"](knowledge_point)
        prompt = f"{base_prompt}\n\nReference scaffolding example:\n{detailed_explanation}"
    else:
        prompt = ""

    response = get_normal_answer(prompt, 'EDU-Qwen2.5-7B')

    # an llm call to score the response
    evaluation = score_edubench_response_with_llm(task_type, response, prompt, question_context={
        "question": question.question,
        "answer": question.answer,
        "explanation": detailed_explanation,
        "difficulty": question.skill.difficulty if question.skill else "medium",
        "grade": question.skill.grade if question.skill else "unknown"
    })

    result = {
        "question_idx": question_idx,
        "task_type": task_type,
        "response": response,
        "evaluation": evaluation,
    }

    return result


def benchmark_parallel(request: UniversalEvaluationRequest, max_workers: int = 100) -> Dict[str, Any]:
    """
    Benchmark mode: Process all items (questions and content) in parallel for maximum throughput.

    Args:
        request: UniversalEvaluationRequest with questions and/or content
        max_workers: Number of parallel workers (default: 100)

    Returns:
        Dict with structure:
        {
            "request_id": str,
            "total_items": int,
            "successful": int,
            "failed": int,
            "scores": List[Dict] - one score per item,
            "failed_ids": List[str],
            "evaluation_time_seconds": float
        }
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())

    # Merge all items
    all_items = (request.generated_questions or []) + (request.generated_content or [])

    logger.info(f"🚀 Benchmark mode: Processing {len(all_items)} items ({len(request.generated_questions or [])} questions, {len(request.generated_content or [])} content) with {max_workers} workers")

    scores = []
    failed_ids = []

    def process_single_item(item):
        """Process a single item (question or content) and return result or error"""
        try:
            # Create a mini request with just this item
            # Determine if it's a question or content based on attributes
            is_question = hasattr(item, 'question') and item.question is not None

            if is_question:
                mini_request = UniversalEvaluationRequest(
                    submodules_to_run=request.submodules_to_run,
                    generated_questions=[item],
                    generated_content=[],
                    verbose=False  # Always use simplified mode for benchmarking
                )
            else:
                mini_request = UniversalEvaluationRequest(
                    submodules_to_run=request.submodules_to_run,
                    generated_questions=[],
                    generated_content=[item],
                    verbose=False  # Always use simplified mode for benchmarking
                )

            # Run evaluation
            response = universal_unified_benchmark(mini_request)

            # Extract the score
            if item.id in response.evaluations:
                eval_result = response.evaluations[item.id]

                # Convert Pydantic models to dicts for JSON serialization
                scores_dict = {}
                for module in request.submodules_to_run:
                    module_result = getattr(eval_result, module, None)
                    if module_result is not None:
                        # Convert Pydantic model to dict
                        scores_dict[module] = module_result.model_dump(exclude_none=True)
                    else:
                        scores_dict[module] = None

                return {
                    "id": item.id,
                    "success": True,
                    "score": eval_result.score,
                    "scores": scores_dict
                }
            else:
                return {
                    "id": item.id,
                    "success": False,
                    "error": "No evaluation result returned"
                }
        except Exception as e:
            logger.error(f"Failed to process item {item.id}: {e}")
            return {
                "id": item.id,
                "success": False,
                "error": str(e)
            }

    # Process all items in parallel with progress bar
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(tqdm(
            executor.map(process_single_item, all_items),
            total=len(all_items),
            desc="Evaluating items"
        ))

    # Collect results
    for result in results:
        if result["success"]:
            scores.append({
                "id": result["id"],
                "score": result["score"],
                "scores": result["scores"]
            })
        else:
            failed_ids.append(result["id"])
            logger.warning(f"Question {result['id']} failed: {result.get('error', 'Unknown error')}")

    evaluation_time = time.time() - start_time

    logger.info(f"✅ Benchmark complete: {len(scores)}/{len(all_items)} successful in {evaluation_time:.2f}s")

    return {
        "request_id": request_id,
        "total_items": len(all_items),
        "total_questions": len(request.generated_questions or []),
        "total_content": len(request.generated_content or []),
        "successful": len(scores),
        "failed": len(failed_ids),
        "scores": scores,
        "failed_ids": failed_ids,
        "evaluation_time_seconds": evaluation_time,
        "avg_score": sum(s["score"] for s in scores) / len(scores) if scores else 0.0
    }


def universal_unified_benchmark(request: UniversalEvaluationRequest) -> UniversalEvaluationResponse:
    """
    Main entry point for universal evaluation.
    Processes both questions and text content, organizing results by item ID.
    """

    start_time = time.time()
    request_id = str(uuid.uuid4())

    # Merge questions, content, and articles into unified list with type tracking
    all_items = []
    for q in (request.generated_questions or []):
        all_items.append(('question', q))
    for c in (request.generated_content or []):
        all_items.append(('content', c))

    # Parse articles and add them as special items
    parsed_articles = []
    for a in (request.generated_articles or []):
        parsed = parse_article_markdown(a.content)
        parsed_articles.append({
            'article': a,
            'parsed': parsed,
            'id': a.id
        })
        all_items.append(('article', a))

    logger.info(f"Universal evaluation request {request_id} with {len(request.generated_questions or [])} questions, {len(request.generated_content or [])} text content items, and {len(request.generated_articles or [])} articles")

    modules_to_use = list(request.submodules_to_run)  # Make a mutable copy
    evaluations = {}

    # AUTO-DETECT IMAGES: If any item has an image_url, automatically enable both image evaluators
    # Also check for images within parsed articles
    has_images = any(
        (hasattr(item, 'image_url') and item.image_url)
        for item_type, item in all_items
    ) or any(
        parsed_article['parsed']['images']
        for parsed_article in parsed_articles
    )

    if has_images:
        # Count items with images (including images from articles)
        items_with_images = sum(1 for item_type, item in all_items if hasattr(item, 'image_url') and item.image_url)
        items_with_images += sum(len(pa['parsed']['images']) for pa in parsed_articles)

        # Auto-enable DI image evaluator (minimal dependencies, evaluation-only)
        # Note: math_image_judge_evaluator (Claude) requires full generation dependencies
        auto_added = []
        if "image_quality_di_evaluator" not in modules_to_use:
            modules_to_use.append("image_quality_di_evaluator")
            auto_added.append("image_quality_di_evaluator")

        if auto_added:
            logger.info(f"🖼️  AUTO-ENABLED IMAGE EVALUATION: Detected {items_with_images} item(s) with images")
            logger.info(f"🖼️  Added evaluator: {', '.join(auto_added)} (DI rubric-based, 0-100 scoring)")
            logger.info(f"🖼️  Evaluating images automatically with pedagogical quality checker")
        else:
            logger.info(f"🖼️  IMAGE EVALUATION: {items_with_images} item(s) with images will be evaluated")

    # Initialize evaluations for all items
    for item_type, item in all_items:
        evaluations[item.id] = UniversalQuestionEvaluationScores()

    # Run all enabled modules in parallel
    questions = request.generated_questions or []
    text_content = request.generated_content or []
    effective_edubench_tasks = ["QA", "EC", "IP", "AG", "QG", "TMG"]

    # Prepare storage for results
    edubench_task_results = []
    internal_eval_results = []
    verification_results = []
    reading_qc_results = []
    content_eval_results = []
    text_content_eval_results = []
    math_image_judge_results = []
    image_quality_di_results = []
    article_holistic_results = []

    # Get API keys for reading QC
    claude_api_key = os.getenv('ANTHROPIC_API_KEY')
    openai_api_key = os.getenv('OPENAI_API_KEY')

    max_workers = 10
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        all_futures = []

        # Submit EduBench tasks if enabled (questions only)
        if "external_edubench" in modules_to_use and questions:
            logger.info(f"Submitting EduBench evaluation with {len(effective_edubench_tasks)} tasks for {len(questions)} questions")
            for i, q in enumerate(questions):
                for task_type in effective_edubench_tasks:
                    future = executor.submit(_run_edubench_task, i, task_type, q)
                    all_futures.append(('external_edubench', future))

        # Submit internal evaluator tasks if enabled (questions only for now)
        if "ti_question_qa" in modules_to_use and questions:
            logger.info(f"Submitting {len(questions)} internal evaluator tasks for questions")
            for i, q in enumerate(questions):
                future = executor.submit(call_single_shot_evaluator, q, len(questions))
                all_futures.append(('ti_question_qa', i, future))

        # Submit answer verification tasks if enabled (questions only - text has no answer)
        if "answer_verification" in modules_to_use and questions:
            logger.info(f"Submitting {len(questions)} answer verification tasks")
            for i, q in enumerate(questions):
                # For MCQ questions, resolve the answer choice to its actual text
                answer_to_verify = q.answer
                if q.type == "mcq" and q.answer_options and q.answer in q.answer_options:
                    answer_to_verify = q.answer_options[q.answer]
                    logger.debug(f"Q{i+1}: Resolved MCQ answer '{q.answer}' to '{answer_to_verify}'")

                future = executor.submit(verify_answer_with_gpt4, q.question, answer_to_verify, q.answer_explanation)
                all_futures.append(('answer_verification', i, future))

        # Submit reading QC tasks if enabled (questions only)
        if "reading_question_qc" in modules_to_use and questions:
            logger.info(f"Submitting {len(questions)} reading QC tasks")
            for i, q in enumerate(questions):
                future = executor.submit(_run_reading_qc_task_sync, i, q, claude_api_key, openai_api_key)
                all_futures.append(('reading_question_qc', i, future))

        # Submit content evaluation tasks if enabled
        # Works for both questions and text content
        if "math_content_evaluator" in modules_to_use:
            if questions:
                logger.info(f"Submitting {len(questions)} content evaluation tasks for questions")
                for i, q in enumerate(questions):
                    future = executor.submit(_run_content_evaluation_task_sync, i, q)
                    all_futures.append(('math_content_evaluator', i, future))
            if text_content:
                logger.info(f"Submitting {len(text_content)} content evaluation tasks for text")
                for i, c in enumerate(text_content):
                    # Offset index by number of questions to avoid collisions
                    idx = len(questions) + i
                    future = executor.submit(_run_content_evaluation_task_sync, idx, c)
                    all_futures.append(('math_content_evaluator', idx, future))

        # Submit text content pedagogical evaluator tasks if enabled (text content only)
        if "text_content_evaluator" in modules_to_use and text_content:
            logger.info(f"Submitting {len(text_content)} text content pedagogical evaluation tasks")
            total_items = len(all_items)
            for i, c in enumerate(text_content):
                # Offset index by number of questions to avoid collisions
                idx = len(questions) + i
                future = executor.submit(_run_text_content_evaluator_task, idx, c, total_items)
                all_futures.append(('text_content_evaluator', idx, future))

        # Submit article holistic evaluation tasks if enabled
        if "article_holistic_evaluator" in modules_to_use and parsed_articles:
            logger.info(f"Submitting {len(parsed_articles)} article holistic evaluation tasks")
            for i, parsed_article in enumerate(parsed_articles):
                idx = len(questions) + len(text_content) + i
                future = executor.submit(_run_article_holistic_evaluator_task, idx, parsed_article)
                all_futures.append(('article_holistic_evaluator', idx, future))

        # Submit article evaluation tasks if enabled
        # For articles, we evaluate the combined text content
        if "text_content_evaluator" in modules_to_use and parsed_articles:
            logger.info(f"Submitting {len(parsed_articles)} article text content evaluation tasks")
            total_items = len(all_items)
            for i, parsed_article in enumerate(parsed_articles):
                # Create a pseudo-content object with the article's combined text
                article_obj = parsed_article['article']
                pseudo_content = type('obj', (object,), {
                    'id': article_obj.id,
                    'type': 'article',
                    'content': parsed_article['parsed']['text_content'],
                    'title': article_obj.title,
                    'skill': article_obj.skill,
                    'image_url': None,  # Images handled separately
                    'additional_details': article_obj.additional_details
                })()

                # Offset index to avoid collisions
                idx = len(questions) + len(text_content) + i
                future = executor.submit(_run_text_content_evaluator_task, idx, pseudo_content, total_items)
                all_futures.append(('text_content_evaluator', idx, future))

        # Submit math content evaluator for articles if enabled and math-related
        if "math_content_evaluator" in modules_to_use and parsed_articles:
            logger.info(f"Submitting {len(parsed_articles)} article content evaluation tasks")
            for i, parsed_article in enumerate(parsed_articles):
                article_obj = parsed_article['article']
                # Create pseudo-content with article text
                pseudo_content = type('obj', (object,), {
                    'id': article_obj.id,
                    'type': 'article',
                    'content': parsed_article['parsed']['text_content'],
                    'title': article_obj.title,
                    'skill': article_obj.skill,
                    'image_url': None,
                    'additional_details': article_obj.additional_details
                })()

                idx = len(questions) + len(text_content) + i
                future = executor.submit(_run_content_evaluation_task_sync, idx, pseudo_content)
                all_futures.append(('math_content_evaluator', idx, future))

        # Submit math image judge evaluator tasks if enabled
        # Works for both questions and text content (only if they have images)
        if "math_image_judge_evaluator" in modules_to_use:
            if questions:
                questions_with_images = [(i, q) for i, q in enumerate(questions) if q.image_url]
                if questions_with_images:
                    logger.info(f"Submitting {len(questions_with_images)} math image judge tasks for questions")
                    for i, q in questions_with_images:
                        future = executor.submit(_run_math_image_judge_task, i, q)
                        all_futures.append(('math_image_judge_evaluator', i, future))
            if text_content:
                content_with_images = [(i, c) for i, c in enumerate(text_content) if c.image_url]
                if content_with_images:
                    logger.info(f"Submitting {len(content_with_images)} math image judge tasks for text content")
                    for i, c in content_with_images:
                        # Offset index by number of questions to avoid collisions
                        idx = len(questions) + i
                        future = executor.submit(_run_math_image_judge_task, idx, c)
                        all_futures.append(('math_image_judge_evaluator', idx, future))

        # Submit DI image quality evaluator tasks if enabled
        # Works for both questions and text content (only if they have images)
        if "image_quality_di_evaluator" in modules_to_use:
            if questions:
                questions_with_images = [(i, q) for i, q in enumerate(questions) if q.image_url]
                if questions_with_images:
                    logger.info(f"Submitting {len(questions_with_images)} DI image quality tasks for questions")
                    for i, q in questions_with_images:
                        future = executor.submit(_run_image_quality_di_task, i, q)
                        all_futures.append(('image_quality_di_evaluator', i, future))
            if text_content:
                content_with_images = [(i, c) for i, c in enumerate(text_content) if c.image_url]
                if content_with_images:
                    logger.info(f"Submitting {len(content_with_images)} DI image quality tasks for text content")
                    for i, c in content_with_images:
                        # Offset index by number of questions to avoid collisions
                        idx = len(questions) + i
                        future = executor.submit(_run_image_quality_di_task, idx, c)
                        all_futures.append(('image_quality_di_evaluator', idx, future))

        # Collect all results with a single progress bar
        if all_futures:
            logger.info(f"Running {len(all_futures)} total tasks in parallel")
            with tqdm(total=len(all_futures), desc="Running All Evaluation Tasks") as pbar:
                for future_info in all_futures:
                    module_type = future_info[0]

                    if module_type == 'external_edubench':
                        _, future = future_info
                        result = future.result()
                        edubench_task_results.append(result)
                    elif module_type == 'ti_question_qa':
                        _, question_idx, future = future_info
                        result = future.result()
                        internal_eval_results.append((question_idx, result))
                    elif module_type == 'answer_verification':
                        _, question_idx, future = future_info
                        result = future.result()
                        verification_results.append((question_idx, result))
                    elif module_type == 'reading_question_qc':
                        _, question_idx, future = future_info
                        result = future.result()
                        reading_qc_results.append((question_idx, result))
                    elif module_type == 'math_content_evaluator':
                        _, question_idx, future = future_info
                        result = future.result()
                        content_eval_results.append((question_idx, result))
                    elif module_type == 'text_content_evaluator':
                        _, item_idx, future = future_info
                        result = future.result()
                        text_content_eval_results.append((item_idx, result))
                    elif module_type == 'article_holistic_evaluator':
                        _, item_idx, future = future_info
                        result = future.result()
                        article_holistic_results.append((item_idx, result))
                    elif module_type == 'math_image_judge_evaluator':
                        _, item_idx, future = future_info
                        result = future.result()
                        math_image_judge_results.append((item_idx, result))
                    elif module_type == 'image_quality_di_evaluator':
                        _, item_idx, future = future_info
                        result = future.result()
                        image_quality_di_results.append((item_idx, result))

                    pbar.update(1)

    # Process EduBench results
    if "external_edubench" in modules_to_use and edubench_task_results:
        logger.info(f"Processing {len(edubench_task_results)} EduBench task results")

        # Organize results by question
        question_scores = {}  # {question_idx: {task_type: score}}

        for result in edubench_task_results:
            question_idx = result['question_idx']
            task_type = result['task_type']
            evaluation_score = result['evaluation']

            if question_idx not in question_scores:
                question_scores[question_idx] = {}

            question_scores[question_idx][task_type] = evaluation_score

        # Build EdubenchScores for each question
        for i, question in enumerate(questions):
            scores = question_scores.get(i, {})
            average_score = sum(scores.values()) / len(scores) if scores else 0.0

            if request.verbose:
                # Full detailed result
                edubench_scores = EdubenchScores(
                    qa_score=scores.get('QA', 0.0),
                    ec_score=scores.get('EC', 0.0),
                    ip_score=scores.get('IP', 0.0),
                    ag_score=scores.get('AG', 0.0),
                    qg_score=scores.get('QG', 0.0),
                    tmg_score=scores.get('TMG', 0.0),
                    average_score=average_score
                )
            else:
                # Simplified result - just average score
                edubench_scores = SimplifiedEdubenchScores(
                    average_score=average_score
                )

            if question.id in evaluations:
                evaluations[question.id].external_edubench = edubench_scores

        logger.info(f"Built EduBench scores for {len(question_scores)} questions")

    # Process internal evaluator results
    if "ti_question_qa" in modules_to_use and internal_eval_results:
        logger.info(f"Processing {len(internal_eval_results)} internal evaluation results")

        # Sort by question index to maintain order
        internal_eval_results.sort(key=lambda x: x[0])

        for question_idx, result_dict in internal_eval_results:
            question = questions[question_idx]
            if question.id in evaluations:
                # Convert dict to Pydantic model
                try:
                    if request.verbose:
                        # Full detailed result
                        # Convert EvaluationDimension keys to strings and extract scores
                        scores_dict = {
                            k.value if hasattr(k, 'value') else str(k): v
                            for k, v in result_dict['scores'].items()
                        }

                        internal_result = InternalEvaluatorResult(
                            scores=InternalEvaluatorScores(**scores_dict),
                            issues=result_dict.get('issues', []),
                            strengths=result_dict.get('strengths', []),
                            overall=result_dict.get('overall', 0.0),
                            recommendation=result_dict.get('recommendation', 'revise'),
                            suggested_improvements=result_dict.get('suggested_improvements', []),
                            di_scores=DIScores(**result_dict.get('di_scores', {})),
                            section_evaluations=SectionEvaluations(
                                question=SectionEvaluation(**result_dict['section_evaluations']['question']),
                                scaffolding=SectionEvaluation(**result_dict['section_evaluations']['scaffolding'])
                            )
                        )
                        evaluations[question.id].ti_question_qa = internal_result
                    else:
                        # Simplified result - just overall score
                        internal_result = SimplifiedInternalEvaluatorResult(
                            overall=result_dict.get('overall', 0.0)
                        )
                        evaluations[question.id].ti_question_qa = internal_result
                except Exception as e:
                    logger.error(f"Error converting internal evaluator result for question {question_idx}: {e}")
                    # Keep the raw dict if conversion fails
                    evaluations[question.id].ti_question_qa = None

        logger.info(f"Assigned internal evaluator results to {len(internal_eval_results)} questions")

    # Process answer verification results
    if "answer_verification" in modules_to_use and verification_results:
        logger.info(f"Processing {len(verification_results)} answer verification results")

        # Sort by question index to maintain order
        verification_results.sort(key=lambda x: x[0])

        for question_idx, result_dict in verification_results:
            question = questions[question_idx]
            if question.id in evaluations:
                # Convert dict to Pydantic model
                try:
                    if request.verbose:
                        # Full detailed result
                        verification_result = AnswerVerificationResult(
                            is_correct=result_dict.get('is_correct', False),
                            correct_answer=result_dict.get('correct_answer', ''),
                            confidence=result_dict.get('confidence', 0),
                            reasoning=result_dict.get('reasoning', '')
                        )
                        evaluations[question.id].answer_verification = verification_result
                    else:
                        # Simplified result - just is_correct
                        verification_result = SimplifiedAnswerVerificationResult(
                            is_correct=result_dict.get('is_correct', False)
                        )
                        evaluations[question.id].answer_verification = verification_result
                except Exception as e:
                    logger.error(f"Error converting answer verification result for question {question_idx}: {e}")
                    # Keep None if conversion fails
                    evaluations[question.id].answer_verification = None

        logger.info(f"Assigned answer verification results to {len(verification_results)} questions")

    # Process reading QC results
    if "reading_question_qc" in modules_to_use and reading_qc_results:
        logger.info(f"Processing {len(reading_qc_results)} reading QC results")

        # Sort by question index to maintain order
        reading_qc_results.sort(key=lambda x: x[0])

        for question_idx, result_dict in reading_qc_results:
            question = questions[question_idx]
            if question.id in evaluations:
                # Extract and convert the result
                try:
                    qc_result = result_dict.get('result')
                    if qc_result and 'error' not in result_dict:
                        # Extract scores
                        overall_score = qc_result.get('overall_score', 0.0)

                        if request.verbose:
                            # Full detailed result
                            # Extract checks - the 'checks' field contains all check results
                            all_checks = qc_result.get('checks', {})

                            # Separate distractor and question checks based on category
                            distractor_checks = {k: v for k, v in all_checks.items() if v.get('category') == 'distractor'}
                            question_checks = {k: v for k, v in all_checks.items() if v.get('category') == 'question'}

                            # Determine if passed (threshold: 0.8)
                            passed = overall_score >= 0.8

                            reading_qc_obj = ReadingQuestionQCResult(
                                overall_score=overall_score,
                                distractor_checks=distractor_checks,
                                question_checks=question_checks,
                                passed=passed
                            )
                            evaluations[question.id].reading_question_qc = reading_qc_obj
                        else:
                            # Simplified result - just overall score
                            reading_qc_obj = SimplifiedReadingQuestionQCResult(
                                overall_score=overall_score
                            )
                            evaluations[question.id].reading_question_qc = reading_qc_obj
                    else:
                        logger.warning(f"Reading QC result for question {question_idx} is None or has error")
                        evaluations[question.id].reading_question_qc = None
                except Exception as e:
                    logger.error(f"Error converting reading QC result for question {question_idx}: {e}")
                    evaluations[question.id].reading_question_qc = None

        logger.info(f"Assigned reading QC results to {len(reading_qc_results)} questions")

    # Process content evaluation results
    if "math_content_evaluator" in modules_to_use and content_eval_results:
        logger.info(f"Processing {len(content_eval_results)} content evaluation results")

        # Sort by item index to maintain order
        content_eval_results.sort(key=lambda x: x[0])

        for item_idx, result_dict in content_eval_results:
            # Determine which item this is (question, text content, or article)
            if item_idx < len(questions):
                item = questions[item_idx]
            elif item_idx < len(questions) + len(text_content):
                item = text_content[item_idx - len(questions)]
            else:
                # This is an article
                article_idx = item_idx - len(questions) - len(text_content)
                item = parsed_articles[article_idx]['article']

            if item.id in evaluations:
                try:
                    eval_result = result_dict.get('result')
                    if eval_result and 'error' not in result_dict:
                        # Count pass/fail
                        criteria = [
                            'curriculum_alignment', 'cognitive_demand', 'accuracy_and_rigor',
                            'image_quality', 'reveals_misconceptions', 'question_type_appropriateness',
                            'engagement_and_relevance', 'instructional_support', 'clarity_and_accessibility'
                        ]

                        pass_count = sum(1 for c in criteria if eval_result.get(c, {}).get('result') == 'PASS')
                        fail_count = len(criteria) - pass_count
                        overall_score = pass_count / len(criteria) if criteria else 0.0

                        if request.verbose:
                            # Full detailed result
                            content_eval_obj = ContentEvaluatorResult(
                                overall_rating=eval_result.get('overall', {}).get('result', 'UNKNOWN'),
                                curriculum_alignment=eval_result.get('curriculum_alignment', {}).get('result', 'UNKNOWN'),
                                cognitive_demand=eval_result.get('cognitive_demand', {}).get('result', 'UNKNOWN'),
                                accuracy_and_rigor=eval_result.get('accuracy_and_rigor', {}).get('result', 'UNKNOWN'),
                                image_quality=eval_result.get('image_quality', {}).get('result', 'UNKNOWN'),
                                reveals_misconceptions=eval_result.get('reveals_misconceptions', {}).get('result', 'UNKNOWN'),
                                question_type_appropriateness=eval_result.get('question_type_appropriateness', {}).get('result', 'UNKNOWN'),
                                engagement_and_relevance=eval_result.get('engagement_and_relevance', {}).get('result', 'UNKNOWN'),
                                instructional_support=eval_result.get('instructional_support', {}).get('result', 'UNKNOWN'),
                                clarity_and_accessibility=eval_result.get('clarity_and_accessibility', {}).get('result', 'UNKNOWN'),
                                pass_count=pass_count,
                                fail_count=fail_count,
                                overall_score=overall_score
                            )
                            evaluations[item.id].math_content_evaluator = content_eval_obj
                        else:
                            # Simplified result - just overall score
                            content_eval_obj = SimplifiedContentEvaluatorResult(
                                overall_score=overall_score
                            )
                            evaluations[item.id].math_content_evaluator = content_eval_obj
                    else:
                        logger.warning(f"Content evaluation result for item {item_idx} is None or has error")
                        evaluations[item.id].math_content_evaluator = None
                except Exception as e:
                    logger.error(f"Error converting content evaluation result for item {item_idx}: {e}")
                    evaluations[item.id].math_content_evaluator = None

        logger.info(f"Assigned content evaluation results to {len(content_eval_results)} items")

    # Process text content evaluator results
    if "text_content_evaluator" in modules_to_use and text_content_eval_results:
        logger.info(f"Processing {len(text_content_eval_results)} text content evaluator results")

        # Sort by item index to maintain order
        text_content_eval_results.sort(key=lambda x: x[0])

        for item_idx, result_dict in text_content_eval_results:
            # Text content evaluator applies to text content and articles (offset by questions count)
            if item_idx < len(questions) + len(text_content):
                item = text_content[item_idx - len(questions)]
            else:
                # This is an article
                article_idx = item_idx - len(questions) - len(text_content)
                item = parsed_articles[article_idx]['article']

            if item.id in evaluations:
                try:
                    eval_result = result_dict.get('result')
                    if eval_result and 'error' not in result_dict:
                        if request.verbose:
                            # Full detailed result
                            text_eval_obj = TextContentEvaluatorResult(
                                correctness=eval_result['scores'].get(EvaluationDimension.CORRECTNESS, 0.0),
                                grade_alignment=eval_result['scores'].get(EvaluationDimension.GRADE_ALIGNMENT, 0.0),
                                language_quality=eval_result['scores'].get(EvaluationDimension.LANGUAGE_QUALITY, 0.0),
                                pedagogical_value=eval_result['scores'].get(EvaluationDimension.PEDAGOGICAL_VALUE, 0.0),
                                explanation_quality=eval_result['scores'].get(EvaluationDimension.EXPLANATION_QUALITY, 0.0),
                                di_compliance=eval_result['scores'].get(EvaluationDimension.DI_COMPLIANCE, 0.0),
                                instruction_adherence=eval_result['scores'].get(EvaluationDimension.INSTRUCTION_ADHERENCE, 0.0),
                                query_relevance=eval_result['scores'].get(EvaluationDimension.QUERY_RELEVANCE, 0.0),
                                overall=eval_result.get('overall', 0.0),
                                recommendation=eval_result.get('recommendation', 'revise'),
                                issues=eval_result.get('issues', []),
                                strengths=eval_result.get('strengths', []),
                                suggested_improvements=eval_result.get('suggested_improvements', []),
                                di_scores=DIScores(**eval_result.get('di_scores', {}))
                            )
                            evaluations[item.id].text_content_evaluator = text_eval_obj
                        else:
                            # Simplified result - just overall score
                            text_eval_obj = SimplifiedTextContentEvaluatorResult(
                                overall=eval_result.get('overall', 0.0)
                            )
                            evaluations[item.id].text_content_evaluator = text_eval_obj
                    else:
                        logger.warning(f"Text content evaluation result for item {item_idx} is None or has error")
                        evaluations[item.id].text_content_evaluator = None
                except Exception as e:
                    logger.error(f"Error converting text content evaluation result for item {item_idx}: {e}")
                    evaluations[item.id].text_content_evaluator = None

        logger.info(f"Assigned text content evaluation results to {len(text_content_eval_results)} items")

    # Process article holistic evaluator results
    if "article_holistic_evaluator" in modules_to_use and article_holistic_results:
        logger.info(f"Processing {len(article_holistic_results)} article holistic evaluator results")

        # Sort by item index to maintain order
        article_holistic_results.sort(key=lambda x: x[0])

        for item_idx, result_dict in article_holistic_results:
            # Articles are offset by questions + text_content
            article_idx = item_idx - len(questions) - len(text_content)
            item = parsed_articles[article_idx]['article']

            if item.id in evaluations:
                try:
                    eval_result = result_dict.get('result')
                    if eval_result and 'error' not in result_dict:
                        if request.verbose:
                            # Full detailed result
                            article_eval_obj = ArticleHolisticEvaluatorResult(**eval_result)
                            evaluations[item.id].article_holistic_evaluator = article_eval_obj
                        else:
                            # Simplified result - just overall score and recommendation
                            article_eval_obj = SimplifiedArticleHolisticResult(
                                overall=eval_result.get('overall', 0.5),
                                recommendation=eval_result.get('recommendation', 'revise')
                            )
                            evaluations[item.id].article_holistic_evaluator = article_eval_obj
                    else:
                        logger.warning(f"Article holistic evaluation result for item {item_idx} is None or has error: {result_dict.get('error')}")
                        evaluations[item.id].article_holistic_evaluator = None
                except Exception as e:
                    logger.error(f"Error converting article holistic evaluation result for item {item_idx}: {e}")
                    evaluations[item.id].article_holistic_evaluator = None

        logger.info(f"Assigned article holistic evaluation results to {len(article_holistic_results)} items")

    # Process math image judge evaluator results
    if "math_image_judge_evaluator" in modules_to_use and math_image_judge_results:
        logger.info(f"Processing {len(math_image_judge_results)} math image judge evaluator results")

        # Sort by item index to maintain order
        math_image_judge_results.sort(key=lambda x: x[0])

        for item_idx, result_dict in math_image_judge_results:
            # Determine which item this is (question or text content)
            if item_idx < len(questions):
                item = questions[item_idx]
            else:
                item = text_content[item_idx - len(questions)]

            if item.id in evaluations:
                try:
                    # Skip items with no image
                    if result_dict.get('skip_reason') == 'no_image':
                        logger.debug(f"Skipping math image judge for item {item_idx} - no image")
                        evaluations[item.id].math_image_judge_evaluator = None
                        continue

                    eval_result = result_dict.get('result')
                    if eval_result and 'error' not in result_dict:
                        # Calculate pass score (1.0 for PASS, 0.0 for FAIL/NO_ACCESS)
                        rating = eval_result.get('rating', 'FAIL')
                        pass_score = 1.0 if rating == 'PASS' else 0.0

                        if request.verbose:
                            # Full detailed result
                            image_judge_obj = MathImageJudgeResult(
                                rating=rating,
                                description=eval_result.get('description', ''),
                                selected_image_url=eval_result.get('selected_image_url'),
                                individual_image_ratings=eval_result.get('individual_image_ratings'),
                                object_counts=eval_result.get('object_counts'),
                                pass_score=pass_score
                            )
                            evaluations[item.id].math_image_judge_evaluator = image_judge_obj
                        else:
                            # Simplified result - just pass score
                            image_judge_obj = SimplifiedMathImageJudgeResult(
                                pass_score=pass_score
                            )
                            evaluations[item.id].math_image_judge_evaluator = image_judge_obj
                    else:
                        logger.warning(f"Math image judge result for item {item_idx} is None or has error")
                        evaluations[item.id].math_image_judge_evaluator = None
                except Exception as e:
                    logger.error(f"Error converting math image judge result for item {item_idx}: {e}")
                    evaluations[item.id].math_image_judge_evaluator = None

        logger.info(f"Assigned math image judge results to {len(math_image_judge_results)} items")

    # Process DI image quality evaluator results
    if "image_quality_di_evaluator" in modules_to_use and image_quality_di_results:
        logger.info(f"Processing {len(image_quality_di_results)} DI image quality evaluator results")

        # Sort by item index to maintain order
        image_quality_di_results.sort(key=lambda x: x[0])

        for item_idx, result_dict in image_quality_di_results:
            # Determine which item this is (question or text content)
            if item_idx < len(questions):
                item = questions[item_idx]
            else:
                item = text_content[item_idx - len(questions)]

            if item.id in evaluations:
                try:
                    # Skip items with no image
                    if result_dict.get('skip_reason') == 'no_image':
                        logger.debug(f"Skipping DI image quality for item {item_idx} - no image")
                        evaluations[item.id].image_quality_di_evaluator = None
                        continue

                    eval_result = result_dict.get('result')
                    if eval_result and 'error' not in result_dict:
                        # Extract scores and rankings
                        best_score = eval_result.get('best_score', 0)
                        # Normalize score from 0-100 to 0-1
                        normalized_score = best_score / 100.0

                        if request.verbose:
                            # Full detailed result
                            rankings_objs = [
                                ImageDIRanking(
                                    rank=r['rank'],
                                    image_index=r['image_index'],
                                    score=r['score'],
                                    strengths=r['strengths'],
                                    weaknesses=r['weaknesses'],
                                    changes_required=r['changes_required'],
                                    recommendation=r['recommendation']
                                )
                                for r in eval_result.get('rankings', [])
                            ]

                            di_quality_obj = ImageQualityDIResult(
                                rankings=rankings_objs,
                                best_image_index=eval_result.get('best_image_index', 0),
                                overall_feedback=eval_result.get('overall_feedback', ''),
                                best_score=best_score,
                                normalized_score=normalized_score
                            )
                            evaluations[item.id].image_quality_di_evaluator = di_quality_obj
                        else:
                            # Simplified result - just normalized score
                            di_quality_obj = SimplifiedImageQualityDIResult(
                                normalized_score=normalized_score
                            )
                            evaluations[item.id].image_quality_di_evaluator = di_quality_obj
                    else:
                        logger.warning(f"DI image quality result for item {item_idx} is None or has error")
                        evaluations[item.id].image_quality_di_evaluator = None
                except Exception as e:
                    logger.error(f"Error converting DI image quality result for item {item_idx}: {e}")
                    evaluations[item.id].image_quality_di_evaluator = None

        logger.info(f"Assigned DI image quality results to {len(image_quality_di_results)} items")

    # Calculate final scores for each question
    logger.info("Calculating final combined scores for each question")
    for question_id, evaluation in evaluations.items():
        scores_to_combine = []

        # Debug: Log what we have for this question
        has_internal = evaluation.ti_question_qa is not None
        has_verification = evaluation.answer_verification is not None
        has_edubench = evaluation.external_edubench is not None
        has_reading_qc = evaluation.reading_question_qc is not None
        has_content_eval = evaluation.math_content_evaluator is not None
        has_text_content_eval = evaluation.text_content_evaluator is not None
        has_image_judge = evaluation.math_image_judge_evaluator is not None
        has_di_image = evaluation.image_quality_di_evaluator is not None
        has_article_holistic = evaluation.article_holistic_evaluator is not None

        logger.info(f"Question {question_id}: ti_question_qa={has_internal}, answer_verification={has_verification}, external_edubench={has_edubench}, reading_question_qc={has_reading_qc}, math_content_evaluator={has_content_eval}, text_content_evaluator={has_text_content_eval}, math_image_judge_evaluator={has_image_judge}, image_quality_di_evaluator={has_di_image}, article_holistic_evaluator={has_article_holistic}")

        # Internal evaluator: already on 0-1 scale
        if evaluation.ti_question_qa:
            # Works for both InternalEvaluatorResult and SimplifiedInternalEvaluatorResult
            internal_score = evaluation.ti_question_qa.overall
            scores_to_combine.append(internal_score)
            logger.info(f"  - Internal evaluator: {internal_score:.3f}")

        # Answer verification: gate check (not scored, only validates correctness)
        # If answer is incorrect, we set final score to 0 at the end (hard fail)
        if evaluation.answer_verification:
            # Works for both AnswerVerificationResult and SimplifiedAnswerVerificationResult
            if not evaluation.answer_verification.is_correct:
                logger.info(f"  - Answer verification: FAIL (is_correct=False - will set final score to 0)")
            else:
                logger.info(f"  - Answer verification: PASS (is_correct=True - gate passed)")

        # EduBench: convert from 0-10 to 0-1 scale
        if evaluation.external_edubench:
            # Works for both EdubenchScores and SimplifiedEdubenchScores
            edubench_normalized = evaluation.external_edubench.average_score / 10.0
            scores_to_combine.append(edubench_normalized)
            logger.info(f"  - EduBench: {edubench_normalized:.3f} (avg={evaluation.external_edubench.average_score:.2f}/10)")

        # Reading QC: already on 0-1 scale
        if evaluation.reading_question_qc:
            # Works for both ReadingQuestionQCResult and SimplifiedReadingQuestionQCResult
            reading_qc_score = evaluation.reading_question_qc.overall_score
            scores_to_combine.append(reading_qc_score)
            logger.info(f"  - Reading QC: {reading_qc_score:.3f}")

        # Content evaluator: already on 0-1 scale
        if evaluation.math_content_evaluator:
            # Works for both ContentEvaluatorResult and SimplifiedContentEvaluatorResult
            content_eval_score = evaluation.math_content_evaluator.overall_score
            scores_to_combine.append(content_eval_score)
            logger.info(f"  - Content evaluator: {content_eval_score:.3f}")

        # Text content pedagogical evaluator: already on 0-1 scale
        if evaluation.text_content_evaluator:
            # Works for both TextContentEvaluatorResult and SimplifiedTextContentEvaluatorResult
            text_content_score = evaluation.text_content_evaluator.overall
            scores_to_combine.append(text_content_score)
            logger.info(f"  - Text content evaluator: {text_content_score:.3f}")

        # Math image judge evaluator: already on 0-1 scale (pass_score)
        if evaluation.math_image_judge_evaluator:
            # Works for both MathImageJudgeResult and SimplifiedMathImageJudgeResult
            image_judge_score = evaluation.math_image_judge_evaluator.pass_score
            scores_to_combine.append(image_judge_score)
            rating_str = evaluation.math_image_judge_evaluator.rating if hasattr(evaluation.math_image_judge_evaluator, 'rating') else ('PASS' if image_judge_score == 1.0 else 'FAIL')
            logger.info(f"  - Math image judge: {image_judge_score:.3f} ({rating_str})")

        # DI image quality evaluator: already on 0-1 scale (normalized_score from 0-100)
        if evaluation.image_quality_di_evaluator:
            # Works for both ImageQualityDIResult and SimplifiedImageQualityDIResult
            di_image_score = evaluation.image_quality_di_evaluator.normalized_score
            scores_to_combine.append(di_image_score)
            score_100 = int(di_image_score * 100)
            recommendation = evaluation.image_quality_di_evaluator.rankings[0].recommendation if hasattr(evaluation.image_quality_di_evaluator, 'rankings') and evaluation.image_quality_di_evaluator.rankings else 'UNKNOWN'
            logger.info(f"  - DI image quality: {di_image_score:.3f} (score={score_100}/100, {recommendation})")

        # Article holistic evaluator: already on 0-1 scale
        if evaluation.article_holistic_evaluator:
            # Works for both ArticleHolisticEvaluatorResult and SimplifiedArticleHolisticResult
            article_holistic_score = evaluation.article_holistic_evaluator.overall
            scores_to_combine.append(article_holistic_score)
            recommendation = evaluation.article_holistic_evaluator.recommendation
            logger.info(f"  - Article holistic evaluator: {article_holistic_score:.3f} ({recommendation})")

        # Calculate weighted average of all available scores
        if scores_to_combine:
            evaluation.score = sum(scores_to_combine) / len(scores_to_combine)

            # Apply answer verification gate: if answer is incorrect, override score to 0
            if evaluation.answer_verification and not evaluation.answer_verification.is_correct:
                logger.info(f"Question {question_id}: calculated score = {evaluation.score:.3f} (from {len(scores_to_combine)} modules)")
                evaluation.score = 0.0
                logger.info(f"Question {question_id}: FINAL score = 0.000 (HARD FAIL due to incorrect answer)")
            else:
                logger.info(f"Question {question_id}: score = {evaluation.score:.3f} (from {len(scores_to_combine)} modules)")
        else:
            evaluation.score = None
            logger.warning(f"Question {question_id}: No scores available to calculate score - all evaluations are None!")

    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f"Universal evaluation request {request_id} completed in {elapsed_time:.2f} seconds")

    # Filter out evaluators that weren't requested
    filtered_evaluations = {}
    for question_id, evaluation in evaluations.items():
        # Build dict with only requested evaluators (and only non-None values)
        eval_dict = {}

        # If not verbose, only return score
        if not request.verbose:
            if evaluation.score is not None:
                eval_dict["score"] = evaluation.score
        else:
            # Verbose mode: include all detailed scores
            if "ti_question_qa" in modules_to_use and evaluation.ti_question_qa is not None:
                eval_dict["ti_question_qa"] = evaluation.ti_question_qa
            if "answer_verification" in modules_to_use and evaluation.answer_verification is not None:
                eval_dict["answer_verification"] = evaluation.answer_verification
            if "external_edubench" in modules_to_use and evaluation.external_edubench is not None:
                eval_dict["external_edubench"] = evaluation.external_edubench
            if "reading_question_qc" in modules_to_use and evaluation.reading_question_qc is not None:
                eval_dict["reading_question_qc"] = evaluation.reading_question_qc
            if "math_content_evaluator" in modules_to_use and evaluation.math_content_evaluator is not None:
                eval_dict["math_content_evaluator"] = evaluation.math_content_evaluator
            if "text_content_evaluator" in modules_to_use and evaluation.text_content_evaluator is not None:
                eval_dict["text_content_evaluator"] = evaluation.text_content_evaluator
            if "math_image_judge_evaluator" in modules_to_use and evaluation.math_image_judge_evaluator is not None:
                eval_dict["math_image_judge_evaluator"] = evaluation.math_image_judge_evaluator
            if "image_quality_di_evaluator" in modules_to_use and evaluation.image_quality_di_evaluator is not None:
                eval_dict["image_quality_di_evaluator"] = evaluation.image_quality_di_evaluator
            if "article_holistic_evaluator" in modules_to_use and evaluation.article_holistic_evaluator is not None:
                eval_dict["article_holistic_evaluator"] = evaluation.article_holistic_evaluator

            # Always include score if not None
            if evaluation.score is not None:
                eval_dict["score"] = evaluation.score

        # Create object from dict (Pydantic will only include provided keys)
        filtered_eval = UniversalQuestionEvaluationScores(**eval_dict)
        filtered_evaluations[question_id] = filtered_eval

    return UniversalEvaluationResponse(
        request_id=request_id,
        evaluations=filtered_evaluations,
        evaluation_time_seconds=elapsed_time,
        inceptbench_version=INCEPTBENCH_VERSION
    )


if __name__ == "__main__":
    import sys
    # Use command-line argument if provided, otherwise default to qs.json
    input_file = sys.argv[1] if len(sys.argv) > 1 else "qs.json"
    with open(input_file, "r", encoding="utf-8") as f:
        example_data = json.load(f)
    example_request = UniversalEvaluationRequest(**example_data)
    response = universal_unified_benchmark(example_request)
    print(response.model_dump_json(indent=2, exclude_none=True))