"""
Article-specific evaluators for holistic and navigation assessment.

This module provides specialized evaluators for educational articles that assess:
1. Holistic quality - How well the article works as a unified learning experience
2. Navigation/flow - How well concepts progress and build upon each other

These evaluators complement the existing text_content_evaluator and math_content_evaluator
by focusing on article-specific pedagogical concerns.

DESIGN PRINCIPLE: Leverage existing evaluators for component assessment.
- Use text_content_evaluator for text portions (via main orchestrator)
- Use call_single_shot_evaluator for embedded questions (via main orchestrator)
- Use image_quality_di_evaluator for images (via main orchestrator)
- THIS evaluator focuses ONLY on article-level holistic concerns
"""

import json
from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel

# Import existing LLM infrastructure instead of direct API calls
try:
    from incept_core.evaluator.llm_interface import simple_solve_with_llm
    _has_llm_interface = True
except ImportError:
    _has_llm_interface = False


# ============================================================================
# Article Holistic Evaluator
# ============================================================================

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


def evaluate_article_holistic(
    article_content: str,
    structure: Dict[str, Any],
    skill: Optional[Dict[str, Any]] = None,
    title: Optional[str] = None,
    language: str = 'en'
) -> ArticleHolisticEvaluatorResult:
    """
    Evaluate article as unified pedagogical experience using Claude 3.5 Sonnet.

    Args:
        article_content: Full markdown article text
        structure: Parsed structure with headings, questions, images counts
        skill: Optional skill/topic metadata
        title: Optional article title
        language: Language code ('en' or 'ar')

    Returns:
        ArticleHolisticEvaluatorResult with scores and feedback
    """

    # Build skill context
    skill_context = ""
    if skill:
        skill_context = f"""
Topic: {skill.get('title', 'N/A')}
Subject: {skill.get('subject', 'N/A')}
Grade: {skill.get('grade', 'N/A')}
Difficulty: {skill.get('difficulty', 'medium')}
Language: {skill.get('language', language)}
"""

    # Build structure context
    structure_context = f"""
Number of headings: {structure.get('sections_count', 0)}
Number of embedded questions: {len(structure.get('embedded_questions', []))}
Number of images: {len(structure.get('images', []))}
"""

    # Heading hierarchy
    if structure.get('headings'):
        headings_text = "\n".join([
            f"{'  ' * (h['level'] - 1)}{'#' * h['level']} {h['title']}"
            for h in structure['headings'][:20]  # Limit to first 20
        ])
        structure_context += f"\n\nHeading hierarchy:\n{headings_text}"

    # Use well-tested prompt principles from existing evaluators
    # This prompt is inspired by v3.py and text_content_evaluator patterns
    system_prompt = """You are an expert educational content evaluator specializing in comprehensive article assessment. Your role is to evaluate educational articles as unified learning experiences, considering how all components work together to facilitate student learning.

**IMPORTANT**: Focus on ARTICLE-LEVEL holistic concerns. Individual text quality, question correctness, and image quality are evaluated separately by specialized evaluators. Your job is to assess how the article works as a UNIFIED pedagogical experience.

You evaluate articles across 10 pedagogical dimensions, providing scores from 0 to 10 for each:

1. **Pedagogical Coherence** (0-10): Does the article tell a coherent learning story? Do sections build upon each other logically? Are concepts introduced in appropriate order? Is there clear progression of ideas?

2. **Content Organization** (0-10): Clear logical structure with appropriate heading hierarchy? Sections properly segmented? Smooth transitions between topics? Easy to navigate?

3. **Scaffolding Quality** (0-10): Builds from simple to complex appropriately? Provides adequate support at each level? Appropriate challenge progression? Gradual release of responsibility?

4. **Engagement** (0-10): Maintains student interest throughout? Uses relatable examples and contexts? Varied content presentation? Hooks and maintains attention?

5. **Mixed Media Integration** (0-10): Images placed contextually near relevant text? Questions appear at pedagogically appropriate moments? Media supports rather than distracts? Coherent multi-modal experience?

6. **Learning Objectives Clarity** (0-10): Clear what students should learn? Objectives align with content? Outcomes measurable and achievable? Purpose evident?

7. **Grade Appropriateness** (0-10): Entire article appropriate for target grade? Overall complexity suitable? Length appropriate? Pacing matches developmental level?

8. **Completeness** (0-10): Covers topic comprehensively without gaps? No missing prerequisite explanations? Adequate depth for grade level? Addresses key concepts?

9. **Cognitive Load Management** (0-10): Appropriate information density? Not overwhelming or too sparse? Good balance of new vs. review? Breaks and processing time?

10. **Instructional Clarity** (0-10): Clear overall structure and instructions? Minimal ambiguity about learning path? Student knows what to do next? Clear expectations?

**Scoring Scale (0-10):**
- 9-10: Exceptional - Publishable quality, exemplary pedagogical design
- 7-8.9: Good - Minor revisions needed, solid foundation
- 5-6.9: Acceptable - Moderate revisions needed, some issues
- 3-4.9: Poor - Major revisions needed, significant problems
- 0-2.9: Unacceptable - Fundamental redesign needed

You must provide:
1. A score (0-10) for each of the 10 dimensions
2. Issues list (up to 10 specific problems with the ARTICLE STRUCTURE/FLOW, not individual components)
3. Strengths list (up to 10 specific positives about the HOLISTIC EXPERIENCE)
4. Suggested improvements (up to 5 actionable recommendations for ARTICLE-LEVEL improvements)

Be objective, specific, and constructive. Focus on pedagogical effectiveness of the UNIFIED ARTICLE EXPERIENCE."""

    user_prompt = f"""Evaluate this educational article holistically as a unified learning experience.

**Article Title:** {title or 'Untitled'}

**Target Audience:**
{skill_context}

**Article Structure:**
{structure_context}

**Article Content:**
{article_content[:8000]}  # Limit to ~8000 chars to fit in context

---

Focus on how the article works as a UNIFIED PEDAGOGICAL EXPERIENCE. Individual text/question/image quality is evaluated separately.

Please evaluate this article across all 10 dimensions. Provide your evaluation in the following JSON format:

{{
  "scores": {{
    "pedagogical_coherence": <score 0-10>,
    "content_organization": <score 0-10>,
    "scaffolding_quality": <score 0-10>,
    "engagement": <score 0-10>,
    "mixed_media_integration": <score 0-10>,
    "learning_objectives_clarity": <score 0-10>,
    "grade_appropriateness": <score 0-10>,
    "completeness": <score 0-10>,
    "cognitive_load_management": <score 0-10>,
    "instructional_clarity": <score 0-10>
  }},
  "issues": ["issue 1", "issue 2", ...],
  "strengths": ["strength 1", "strength 2", ...],
  "suggested_improvements": ["improvement 1", "improvement 2", ...]
}}

Provide ONLY the JSON output, no additional text."""

    # Use existing LLM interface infrastructure (same as v3.py and text_content_evaluator)
    try:
        if _has_llm_interface:
            # Build messages in the format expected by simple_solve_with_llm
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            # Use the same LLM interface as other evaluators for consistency
            eval_data = simple_solve_with_llm(messages=messages)
        else:
            # Fallback: Use direct Anthropic API call if llm_interface not available
            import anthropic
            import os

            client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.3,  # Lower temperature for more consistent scoring
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            # Extract JSON from response
            response_text = response.content[0].text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                lines = response_text.split('\n')
                response_text = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])
                if response_text.startswith('json'):
                    response_text = response_text[4:].strip()

            # Parse JSON
            eval_data = json.loads(response_text)

        # Extract scores (now nested under "scores" key, on 0-10 scale)
        scores_raw = eval_data.get('scores', {})

        # Normalize scores from 0-10 to 0-1 (consistent with other evaluators)
        def normalize_score(score: float) -> float:
            """Normalize score from 0-10 scale to 0-1 scale"""
            return max(0.0, min(1.0, score / 10.0))

        # Calculate normalized scores
        normalized_scores = {
            'pedagogical_coherence': normalize_score(scores_raw.get('pedagogical_coherence', 5.0)),
            'content_organization': normalize_score(scores_raw.get('content_organization', 5.0)),
            'scaffolding_quality': normalize_score(scores_raw.get('scaffolding_quality', 5.0)),
            'engagement': normalize_score(scores_raw.get('engagement', 5.0)),
            'mixed_media_integration': normalize_score(scores_raw.get('mixed_media_integration', 5.0)),
            'learning_objectives_clarity': normalize_score(scores_raw.get('learning_objectives_clarity', 5.0)),
            'grade_appropriateness': normalize_score(scores_raw.get('grade_appropriateness', 5.0)),
            'completeness': normalize_score(scores_raw.get('completeness', 5.0)),
            'cognitive_load_management': normalize_score(scores_raw.get('cognitive_load_management', 5.0)),
            'instructional_clarity': normalize_score(scores_raw.get('instructional_clarity', 5.0)),
        }

        # Calculate overall as weighted average (same weights as before)
        weights = {
            'pedagogical_coherence': 0.15,
            'content_organization': 0.12,
            'scaffolding_quality': 0.12,
            'engagement': 0.10,
            'mixed_media_integration': 0.10,
            'learning_objectives_clarity': 0.10,
            'grade_appropriateness': 0.10,
            'completeness': 0.08,
            'cognitive_load_management': 0.08,
            'instructional_clarity': 0.05
        }

        overall = sum(normalized_scores[dim] * weight for dim, weight in weights.items())

        # Determine recommendation (same thresholds as v3 evaluator)
        all_scores = list(normalized_scores.values())
        if overall >= 0.8 and all(score >= 0.6 for score in all_scores):
            recommendation = "accept"
        elif overall >= 0.5:
            recommendation = "revise"
        else:
            recommendation = "reject"

        # Build result with normalized scores
        result = ArticleHolisticEvaluatorResult(
            pedagogical_coherence=normalized_scores['pedagogical_coherence'],
            content_organization=normalized_scores['content_organization'],
            scaffolding_quality=normalized_scores['scaffolding_quality'],
            engagement=normalized_scores['engagement'],
            mixed_media_integration=normalized_scores['mixed_media_integration'],
            learning_objectives_clarity=normalized_scores['learning_objectives_clarity'],
            grade_appropriateness=normalized_scores['grade_appropriateness'],
            completeness=normalized_scores['completeness'],
            cognitive_load_management=normalized_scores['cognitive_load_management'],
            instructional_clarity=normalized_scores['instructional_clarity'],
            overall=overall,
            recommendation=recommendation,
            issues=eval_data.get('issues', [])[:10],
            strengths=eval_data.get('strengths', [])[:10],
            suggested_improvements=eval_data.get('suggested_improvements', [])[:5]
        )

        return result

    except Exception as e:
        # Return neutral scores on error
        return ArticleHolisticEvaluatorResult(
            pedagogical_coherence=0.5,
            content_organization=0.5,
            scaffolding_quality=0.5,
            engagement=0.5,
            mixed_media_integration=0.5,
            learning_objectives_clarity=0.5,
            grade_appropriateness=0.5,
            completeness=0.5,
            cognitive_load_management=0.5,
            instructional_clarity=0.5,
            overall=0.5,
            recommendation="revise",
            issues=[f"Evaluation error: {str(e)}"],
            strengths=[],
            suggested_improvements=["Re-run evaluation after resolving technical issues"]
        )


# Simplified result for non-verbose mode
class SimplifiedArticleHolisticResult(BaseModel):
    """Simplified result showing only overall score"""
    overall: float
    recommendation: Literal["accept", "revise", "reject"]


def simplify_article_holistic_result(result: ArticleHolisticEvaluatorResult) -> SimplifiedArticleHolisticResult:
    """Convert full result to simplified version"""
    return SimplifiedArticleHolisticResult(
        overall=result.overall,
        recommendation=result.recommendation
    )
