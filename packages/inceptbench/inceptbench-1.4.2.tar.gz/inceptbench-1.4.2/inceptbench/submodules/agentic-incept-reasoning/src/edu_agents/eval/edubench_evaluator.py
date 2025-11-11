from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import time
from enum import Enum
from typing import Union

from anthropic import AsyncAnthropic
from google import genai
from google.genai import types
from pydantic import BaseModel
from scipy.stats import chisquare

from edu_agents.core.api_key_manager import get_async_openai_client
from edu_agents.tools.curriculum_search import search_curriculum_standards

logger = logging.getLogger(__name__)

# Configuration for curriculum deduplication model providers
OPENAI_DEDUP_PROVIDER = "openai"
CLAUDE_DEDUP_PROVIDER = "claude"
GEMINI_DEDUP_PROVIDER = "gemini"
CURRICULUM_DEDUP_MODEL = CLAUDE_DEDUP_PROVIDER


def extract_image_urls(content: str) -> list[str]:
    """
    Extract image URLs from content.
    
    Parameters
    ----------
    content : str
        The content to extract URLs from
        
    Returns
    -------
    list[str]
        List of image URLs found in the content
    """
    # Pattern to match common image URL formats
    # Matches URLs ending in common image extensions or containing image hosting domains
    url_pattern = r'https?://[^\s<>"]+?\.(?:jpg|jpeg|png|gif|bmp|svg|webp)(?:\?[^\s<>"]*)?'
    
    # Also match Supabase storage URLs (common in this codebase)
    supabase_pattern = r'https://[^\s<>"]*supabase[^\s<>"]*storage[^\s<>"]*'
    
    urls = []
    urls.extend(re.findall(url_pattern, content, re.IGNORECASE))
    urls.extend(re.findall(supabase_pattern, content, re.IGNORECASE))
    
    # Remove duplicates while preserving order
    seen = set()
    unique_urls = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
    
    return unique_urls

# Shared deduplication prompt (definitive version from Claude implementation)
DEDUPLICATION_SYSTEM_PROMPT = (
    """You are deduplicating curriculum standards retrieved from a RAG search.

Your task: Remove ONLY truly redundant/duplicate information while preserving ALL unique content.

CRITICAL RULES:
1. **NEVER add information**: You must NEVER add, infer, or generate any information that is not 
   explicitly present in the input. If all instances of a standard are truncated, keep the most 
   complete truncated version - do NOT fill in missing fields from patterns you observe in other 
   standards.
   
2. **Merge complementary truncations**: If the SAME standard (same standard ID) appears multiple 
   times with DIFFERENT truncation points, and together they would form a more complete version, 
   you MAY combine them by taking the union of all information present across those instances. 
   But ONLY if the information is actually present in at least one of the instances.
   
3. **Preserve completeness**: If a standard block appears multiple times with different levels of 
   completeness (e.g., one truncated, one complete), keep ONLY the most complete version.
   
4. **Literal duplicates only**: Only remove standard blocks that are EXACTLY the same or where one 
   is clearly a truncated/incomplete version of another for the SAME standard ID.
   
5. **DO NOT combine different standards**: Do NOT try to "smartly" combine related information. 
   If two standards are different (different standard IDs or different subjects/courses), keep 
   both even if they seem related.
   
6. **Preserve ALL formatting**: Keep the exact original formatting, including:
   - All "---" separator lines between standards
   - All line breaks and spacing within each standard block
   - All field names and structure (Key Concepts, Learning Objectives, etc.)
   
7. **Remove header blocks**: Remove all header blocks like "=== CURRICULUM SEARCH RESULT 1 ===" 
   entirely from the output. The output should start directly with the first standard block's 
   content (Key Concepts, Learning Objectives, etc.).
   
8. **When in doubt, keep it**: If you're unsure whether something is a duplicate, KEEP IT.

EXAMPLES:

REMOVE (exact duplicate):
- Standard "RI.3.2" appears twice with identical complete content
  → Keep one, remove the other

REMOVE (one is more complete):
- Standard "RI.3.2" ends at "Learning Objectives:" AND another "RI.3.2" has all fields
  → Remove the incomplete one, keep the complete one

MERGE (complementary truncations):
- Standard "RI.3.2" ends at "Assessment Boundaries: *None specified*"
- Another "RI.3.2" starts at "Learning Objectives:" and continues through all fields
  → Combine them to create the most complete version from information actually present

NEVER DO (adding information):
- Standard "RI.3.2" appears twice, both ending at "Learning Objectives:"
  → Do NOT add "Assessment Boundaries:", "Common Misconceptions:", etc. just because you see 
     that pattern in other standards. Keep one truncated version as-is.

KEEP (different standards):
- Standard "RI.3.1" and standard "RI.3.2"
  → Keep both, they are different standards

Your output must be the deduplicated text with NO additional commentary or explanation."""
)


class CurriculumStandardsExtraction(BaseModel):
    """Structured output for curriculum standards extraction"""
    has_explicit_standards: bool
    standards: list[str] = []


async def extract_explicit_curriculum_info(content: str) -> Union[list[str], None]:
    """
    Extract explicit curriculum standards mentioned in the content.
    
    Parameters
    ----------
    content : str
        The educational content to analyze for curriculum standards
        
    Returns
    -------
    Union[list[str], None]
        List of curriculum standards with descriptions if found, 
        None if no explicit standards present
    """
    try:
        client = get_async_openai_client(timeout=30.0)
        
        extraction_prompt = """
You are analyzing educational content to extract explicit curriculum standards. 
Look for standards like:
- CCSS (Common Core State Standards): e.g., CCSS.ELA-Literacy.RI.3.1, CCSS.Math.Content.5.NBT.A.1
- NGSS (Next Generation Science Standards): e.g., 3-LS1-1, MS-PS1-1
- State-specific standards that follow similar patterns
- Any other explicitly listed educational standards

IMPORTANT: 
- Only extract standards that are explicitly written out in the content
- Include the FULL text of each standard (code + description if provided)
- Do not infer or guess standards based on content topics

Examples:
- If you see "CCSS.ELA-Literacy.RI.3.1 – Ask and answer questions to demonstrate 
  understanding", extract: "CCSS.ELA-Literacy.RI.3.1 – Ask and answer questions 
  to demonstrate understanding"
- If you see just "CCSS.ELA-Literacy.RI.3.2", extract: "CCSS.ELA-Literacy.RI.3.2"

Set has_explicit_standards to true if any standards are found, false if none found.
If standards are found, include them in the standards array with their full text.
"""
        
        response = await client.responses.parse(
            model="gpt-4o",
            input=[
                {"role": "system", "content": extraction_prompt},
                {"role": "user", "content": f"Content to analyze:\n\n{content}"}
            ],
            text_format=CurriculumStandardsExtraction
        )
        
        # Extract the result from the structured response
        for output_item in response.output:
            if output_item.type == "message":
                for content_item in output_item.content:
                    if (content_item.type == "output_text" and 
                        hasattr(content_item, "parsed") and 
                        content_item.parsed is not None):
                        result = content_item.parsed
                        
                        if result.has_explicit_standards and result.standards:
                            logger.info(f"Extracted {len(result.standards)} explicit "
                                      f"curriculum standards")
                            return result.standards
                        else:
                            return None
        
        # Fallback if parsing fails
        logger.warning("Could not parse curriculum extraction result")
        return None
            
    except Exception as e:
        logger.warning(f"Error extracting explicit curriculum info: {e}")
        return None


async def _deduplicate_curriculum_context_openai(curriculum_results: list[str]) -> str:
    """
    Deduplicate curriculum search results using OpenAI GPT-4o.
    
    Parameters
    ----------
    curriculum_results : list[str]
        List of curriculum context strings from parallel searches
        
    Returns
    -------
    str
        Deduplicated curriculum context string with redundant information removed
    """
    try:
        if len(curriculum_results) == 1:
            return curriculum_results[0]
        
        client = get_async_openai_client(timeout=60.0)
        
        # Combine all results for deduplication
        combined_text = "".join(curriculum_results)

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": DEDUPLICATION_SYSTEM_PROMPT},
                {"role": "user", 
                 "content": "Deduplicate this curriculum content, being sure NEVER to add ANY "
                            "information that is not explicitly present in the input:\n\n" +
                            f"{combined_text}"}
            ],
            temperature=0.0
        )
        
        deduplicated_text = response.choices[0].message.content.strip()
        logger.info("Curriculum context deduplication completed using OpenAI GPT-4o")
        return deduplicated_text
        
    except Exception as e:
        logger.warning(f"Error deduplicating curriculum context with OpenAI: {e}")
        # Fallback to simple concatenation if deduplication fails
        return "\n\n".join(curriculum_results)


async def _deduplicate_curriculum_context_claude(curriculum_results: list[str]) -> str:
    """
    Deduplicate curriculum search results using Claude Sonnet 4.5.
    
    Parameters
    ----------
    curriculum_results : list[str]
        List of curriculum context strings from parallel searches
        
    Returns
    -------
    str
        Deduplicated curriculum context string with redundant information removed
    """
    try:
        if len(curriculum_results) == 1:
            return curriculum_results[0]
        
        client = AsyncAnthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        # Combine all results for deduplication
        combined_text = "".join(curriculum_results)

        user_prompt = f"""Deduplicate this curriculum content:

{combined_text}"""

        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=16384,
            system=DEDUPLICATION_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=0.0
        )
        
        # Extract text from response
        deduplicated_text = response.content[0].text.strip()
        logger.info("Curriculum context deduplication completed using Claude Sonnet 4.0")
        return deduplicated_text
        
    except Exception as e:
        logger.warning(f"Error deduplicating curriculum context with Claude: {e}")
        # Fallback to simple concatenation if deduplication fails
        return "\n\n".join(curriculum_results)


async def _deduplicate_curriculum_context_gemini(curriculum_results: list[str]) -> str:
    """
    Deduplicate curriculum search results using Gemini 2.5 Pro.
    
    Parameters
    ----------
    curriculum_results : list[str]
        List of curriculum context strings from parallel searches
        
    Returns
    -------
    str
        Deduplicated curriculum context string with redundant information removed
    """
    try:
        if len(curriculum_results) == 1:
            return curriculum_results[0]
        
        client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        
        # Combine all results for deduplication
        combined_text = "".join(curriculum_results)

        user_prompt = f"""Deduplicate this curriculum content:

{combined_text}"""

        # Generate response with Gemini using asyncio.to_thread
        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-2.5-pro",
            contents=[
                DEDUPLICATION_SYSTEM_PROMPT + "\n\n" + user_prompt
            ],
            config=types.GenerateContentConfig(
                temperature=0.0,
                max_output_tokens=16384
            )
        )
        
        # Extract text from response
        deduplicated_text = response.text.strip()
        logger.info("Curriculum context deduplication completed using Gemini 2.5 Pro")
        return deduplicated_text
        
    except Exception as e:
        logger.warning(f"Error deduplicating curriculum context with Gemini: {e}")
        # Fallback to simple concatenation if deduplication fails
        return "\n\n".join(curriculum_results)


async def _deduplicate_curriculum_context(curriculum_results: list[str]) -> str:
    """
    Deduplicate curriculum search results using the configured LLM.
    
    Parameters
    ----------
    curriculum_results : list[str]
        List of curriculum context strings from parallel searches
        
    Returns
    -------
    str
        Deduplicated curriculum context string with redundant information removed
    """
    if CURRICULUM_DEDUP_MODEL == CLAUDE_DEDUP_PROVIDER:
        return await _deduplicate_curriculum_context_claude(curriculum_results)
    elif CURRICULUM_DEDUP_MODEL == OPENAI_DEDUP_PROVIDER:
        return await _deduplicate_curriculum_context_openai(curriculum_results)
    elif CURRICULUM_DEDUP_MODEL == GEMINI_DEDUP_PROVIDER:
        return await _deduplicate_curriculum_context_gemini(curriculum_results)
    else:
        logger.warning(
            f"Unknown CURRICULUM_DEDUP_MODEL: {CURRICULUM_DEDUP_MODEL}. "
            f"Defaulting to Claude."
        )
        return await _deduplicate_curriculum_context_claude(curriculum_results)


async def get_curriculum_context(content: str) -> str:
    """
    Get curriculum context by first checking for explicit standards, then falling back to search.
    
    Parameters
    ----------
    content : str
        The educational content to analyze
        
    Returns
    -------
    str
        Formatted curriculum context string, or empty string if none found
    """
    curriculum_context = ""
    
    try:
        # First, try to extract explicit curriculum standards
        explicit_standards = await extract_explicit_curriculum_info(content)
        
        if explicit_standards:
            # If we found explicit standards, make parallel searches for each standard
            logger.info(f"Making parallel searches for {len(explicit_standards)} explicit "
                       f"curriculum standards")
            
            # Make parallel async searches for all standards
            tasks = [search_curriculum_standards(standard, k=1) for standard in explicit_standards]
            search_results = await asyncio.gather(*tasks)
            
            # Collect all results
            all_results = []
            for result in search_results:
                if result and result.text:
                    all_results.append(result.text)
            
            if all_results and len(all_results) > 1:
                # Deduplicate the results using LLM
                start_time = time.time()
                deduplicated_context = await _deduplicate_curriculum_context(all_results)
                logger.info(f"Deduplication completed in {time.time() - start_time} seconds")
                if deduplicated_context:
                    curriculum_context = f"\n\nRelevant Curriculum Context:\n{deduplicated_context}"
                else:
                    curriculum_context = "Relevant Curriculum Context:\n" + "\n".join(all_results)
            else:
                curriculum_context = "Relevant Curriculum Context:\n" + f"{search_results}"
        else:
            # Fall back to general content-based search with standard k
            logger.info("No explicit curriculum standards found, using general "
                       "content search")
            search_result = await search_curriculum_standards(content, k=3)
            
            if search_result and search_result.text:
                curriculum_context = f"\n\nRelevant Curriculum Context:\n{search_result.text}"
            
    except Exception as e:
        logger.warning(f"Could not retrieve curriculum context: {e}")
    
    return curriculum_context


class ContentType(Enum):
    QUESTION = "Question"
    QUIZ = "Quiz"
    READING_FICTION = "Reading Passage - Fiction"
    READING_NONFICTION = "Reading Passage - Nonfiction"
    OTHER = "Other"


class OverallRating(Enum):
    SUPERIOR = "SUPERIOR"
    ACCEPTABLE = "ACCEPTABLE"
    INFERIOR = "INFERIOR"


class OverallResult(BaseModel):
    rating: OverallRating
    rationale: str


class MetricResult(BaseModel):
    score: int
    rationale: str


# Evaluation result models for each content type
class QuestionEvaluationResult(BaseModel):
    overall: OverallResult
    curriculum_alignment: MetricResult
    reveals_misconceptions: MetricResult
    correctness: MetricResult
    difficulty_alignment: MetricResult
    mastery_learning_alignment: MetricResult
    stimulus_quality: MetricResult

    def to_json(self) -> str:
        """Convert to JSON string for API responses"""
        data = self.model_dump()
        # Convert enum to string value
        if 'overall' in data and 'rating' in data['overall']:
            data['overall']['rating'] = data['overall']['rating'].value
        return json.dumps(data, indent=2)

    def to_dict(self) -> dict:
        """Convert to dictionary for programmatic use"""
        data = self.model_dump()
        # Convert enum to string value
        if 'overall' in data and 'rating' in data['overall']:
            data['overall']['rating'] = data['overall']['rating'].value
        return data


class QuizEvaluationResult(BaseModel):
    overall: OverallResult
    concept_coverage: MetricResult
    difficulty_distribution: MetricResult
    non_repetitiveness: MetricResult
    test_preparedness: MetricResult
    answer_balance: MetricResult

    def to_json(self) -> str:
        """Convert to JSON string for API responses"""
        data = self.model_dump()
        # Convert enum to string value
        if 'overall' in data and 'rating' in data['overall']:
            data['overall']['rating'] = data['overall']['rating'].value
        return json.dumps(data, indent=2)

    def to_dict(self) -> dict:
        """Convert to dictionary for programmatic use"""
        data = self.model_dump()
        # Convert enum to string value
        if 'overall' in data and 'rating' in data['overall']:
            data['overall']['rating'] = data['overall']['rating'].value
        return data


class ReadingEvaluationResult(BaseModel):
    overall: OverallResult
    reading_level_match: MetricResult
    length_appropriateness: MetricResult
    topic_focus: MetricResult
    engagement: MetricResult
    accuracy_and_logic: MetricResult
    question_quality: MetricResult

    def to_json(self) -> str:
        """Convert to JSON string for API responses"""
        data = self.model_dump()
        # Convert enum to string value
        if 'overall' in data and 'rating' in data['overall']:
            data['overall']['rating'] = data['overall']['rating'].value
        return json.dumps(data, indent=2)

    def to_dict(self) -> dict:
        """Convert to dictionary for programmatic use"""
        data = self.model_dump()
        # Convert enum to string value
        if 'overall' in data and 'rating' in data['overall']:
            data['overall']['rating'] = data['overall']['rating'].value
        return data


class OtherEvaluationResult(BaseModel):
    overall: OverallResult
    educational_value: MetricResult
    direct_instruction_alignment: MetricResult
    content_appropriateness: MetricResult
    clarity_and_organization: MetricResult
    engagement: MetricResult

    def to_json(self) -> str:
        """Convert to JSON string for API responses"""
        data = self.model_dump()
        # Convert enum to string value
        if 'overall' in data and 'rating' in data['overall']:
            data['overall']['rating'] = data['overall']['rating'].value
        return json.dumps(data, indent=2)

    def to_dict(self) -> dict:
        """Convert to dictionary for programmatic use"""
        data = self.model_dump()
        # Convert enum to string value
        if 'overall' in data and 'rating' in data['overall']:
            data['overall']['rating'] = data['overall']['rating'].value
        return data


class ContentClassificationResult(BaseModel):
    content_type: ContentType
    confidence: str  # High, Medium, Low


async def classify_content(content: str) -> ContentType:
    """
    Classify the content type using a simple classification prompt.
    
    Parameters
    ----------
    content : str
        The content to classify
        
    Returns
    -------
    ContentType
        The classified content type
    """
    logger.info("Classifying content type...")
    
    client = get_async_openai_client(timeout=60.0)
    
    classification_prompt = """
You are a content classifier for educational materials. Analyze the following content and classify
it into one of these categories:

1. **Question** - Any single question (multiple choice, fill-in-the-blank, short answer, essay,
etc.)
2. **Quiz** - A collection of multiple questions (typically 3+ separate questions)
3. **Reading Passage - Fiction** - A fictional story or narrative text, possibly with comprehension
questions
4. **Reading Passage - Nonfiction** - An informational or factual text, possibly with comprehension
questions  
5. **Other** - Any other educational content (lessons, explanations, activities, etc.)

Guidelines:
- Look for question markers like "1.", "2.", "A)", "B)", etc. to identify multiple questions
- If it's primarily a story or narrative with characters and plot, classify as Fiction
- If it's primarily informational/factual text explaining concepts, classify as Nonfiction
- Reading passages may have comprehension questions at the end - focus on the main content type
- A single question with multiple parts is still just one Question
- Multiple distinct questions make it a Quiz
- Educational explanations, lessons, activities are Other

Provide your classification with confidence level.
"""
    
    try:
        response = await client.responses.parse(
            model="gpt-5",
            input=[
                {"role": "system", "content": classification_prompt},
                {"role": "user", "content": content}
            ],
            text_format=ContentClassificationResult
        )
        
        # Extract the classification from the structured response
        for output_item in response.output:
            if output_item.type == "message":
                for content_item in output_item.content:
                    if (content_item.type == "output_text" and 
                        hasattr(content_item, "parsed") and 
                        content_item.parsed is not None):
                        classified_type = content_item.parsed.content_type
                        logger.info(f"Content classified as: {classified_type.value}")
                        return classified_type
        
        # Fallback if parsing fails
        logger.warning("Could not parse classification result, defaulting to OTHER")
        return ContentType.OTHER
        
    except Exception as e:
        logger.error(f"Error classifying content: {str(e)}")
        return ContentType.OTHER


async def evaluate_question(content: str) -> QuestionEvaluationResult:
    """
    Evaluate a single question across 5 metrics.
    
    Parameters
    ----------
    content : str
        The question content to evaluate
        
    Returns
    -------
    QuestionEvaluationResult
        Evaluation results with scores and rationales for each metric
    """
    logger.info("Evaluating question...")
    
    # Get curriculum context using new extraction method
    curriculum_context = await get_curriculum_context(content)
    
    client = get_async_openai_client(timeout=300.0)
    
    evaluation_prompt = f"""
You are an expert educational evaluator. Evaluate questions across 5 key 
metrics and provide an overall holistic rating. Each metric should be scored 0-5 with 
detailed rationale.
{curriculum_context}

Rate each metric from 0-5. Ensure ALL rationales you provide for all metrics and the overall rating
are consistent with the curriculum context (if provided) and each other so that a content creator
could act upon your advice to improve the question without introducing contradictions.

If any URLs have alt text, read the alt text as part of your assessment, but do NOT guess or infer
what the alt text might contain. It's better to ignore the alt text or its possible content than to
base your assessment on hallucinations or guesses of what the alt text might contain.

**1. Curriculum Alignment (0-5)**
Evaluate how well this question aligns with educational standards, learning objectives, and 
assessment boundaries. Consider these specific factors:

- **Standard Alignment:** Does the question directly address relevant educational standards for 
its apparent subject/grade level? Does it reflect the concepts and skills described in the 
standards without deviating into unrelated topics?
- **Learning Objectives Alignment:** Does the question assess specific learning objectives in a 
clear and focused manner? Does it provide a meaningful opportunity to test student understanding?
- **Assessment Boundaries Compliance:** Does the question stay within appropriate boundaries? 
Does it avoid testing knowledge or skills beyond the scope of the standards? Does it maintain 
appropriate complexity without introducing irrelevant content?

If curriculum context is provided above, evaluate alignment with those specific standards. 
If no context provided, infer the subject area and evaluate against typical standards.

Scoring: 5 = Direct comprehensive alignment with standards and objectives, fully within boundaries; 
4 = Good alignment with minor irrelevant details; 3 = Partial alignment with some boundary issues; 
2 = Tangentially related but unclear assessment; 1 = Vague or insufficient alignment; 0 = No
alignment

**2. Reveals Misconceptions (0-5)**  
Evaluate how effectively this question reveals and addresses common student misconceptions through 
its design and answer choices. Consider these specific factors:

- **Plausibility of Distractors:** Are incorrect answer choices (if present) likely to 
be selected by students with imperfect mastery, particularly in light of common misconceptions and
the curriculum context (if available)? Do they represent misunderstandings students learning the
topic often make, instead of simple logical errors?
- **Connection to Common Misconceptions:** Are distractors aligned with known common misconceptions 
for the topic? If no specific misconceptions are known, do distractors logically reflect the most
likely misunderstandings?
- **Alignment with Question Context:** Are distractors relevant to the specific question and 
context? Do they avoid introducing unrelated or extraneous ideas that might confuse students?
- **Learning Opportunity Quality:** Are distractors designed to create meaningful learning 
opportunities by helping students reflect on their mistakes? Are they appropriately balanced in 
difficulty and avoid being obviously incorrect?
- **Diagnostic Value:** If a student provides an incorrect answer, does that help diagnose specific
areas of misunderstanding?  For open-ended questions, does the prompt allow misconceptions to
surface?
- **Assess Questions Based on the Capabilities of the Question Type**: Some question types are
inherently more diagnostically precise than others. For example, a multiple choice question is
typically more diagnostically precise than an open-ended question. Assess a question's ability to
reveal misconceptions based on how well it reveals misconceptions given the capabilities of the
question type. Do not penalize an open-ended question for being less diagnostically precise than a
multiple choice question, for example. Assess it based on its own capabilities and limitations as a
question type.

For questions that include distractors (multiple choice, true/false, matching, etc.):
Scoring: 5 = All distractors plausible, aligned with misconceptions, create meaningful learning 
opportunities; 4 = Most distractors effective with minor issues; 3 = Some distractors effective 
but others weak or irrelevant; 2 = Most distractors weak or unrelated to misconceptions; 
1 = Distractors implausible or fail to align with learning goals; 0 = Completely nonsensical 
or absent diagnostic value

For questions that do not include distractors (open-ended, fill-in-the-blank, short answer, etc.):
Scoring: 5 = The question is structured in a way that creates an excellent opportunity to reveal
misconceptions; 4 = The question is structured in a way that creates a good opportunity to reveal
misconceptions; 3 = The question is structured in a way that creates a moderate opportunity to
reveal misconceptions; 2 = The question is structured in a way that creates a minimal opportunity
to reveal misconceptions; 1 = The question is structured in a way that creates poor opportunity to
reveal misconceptions; 0 = The question is structured in a way that creates a no opportunity or
negative opportunity to reveal misconceptions.

**3. Correctness (0-5)**
Evaluate how well this question reflects correct information about the subject matter. Consider 
these specific factors:

- **Accuracy of Information:** Does the question accurately reflect the subject matter as expressed
in the curriculum context if provided, or generally if not provided? Does it avoid including
false, incorrect, or fabricated information?
- **Relevance to Standards:** Does the question stay on topic and avoid introducing information 
unrelated to the relevant educational standards?
  - **Note**: Curriculum vs. General Correctness: When curriculum context specifies pedagogical
  approaches that seem counter-intuitive (e.g., Common Core multiplication treating 3×4 and 4×3 as
  conceptually different for 3rd graders), prioritize curriculum alignment over general
  mathematical equivalence. Questions providing both pedagogically distinct but mathematically
  equivalent options demonstrate quality, not inaccuracy.
- **Appropriate Use of Context:** Does the question make appropriate use of learning objectives 
and assessment boundaries to maintain correctness? Does it avoid presenting misconceptions as 
factual information?
- **Avoidance of Hallucination:** Does the question avoid fabricating details or including 
unrelated concepts that are inconsistent with the subject matter?
- **Internal Consistency:** Does the question avoid contradictions within itself and answer 
choices? Is the correct answer actually correct and properly labeled? Questions with internal 
consistency issues should be severely penalized.
- **Be Aware of Intended Nuance**: Some questions may have intended nuance that is not explicitly
stated in the question, or even the curriculum, but is intended to assess a specific concept or
skill. For example, a question may ask a student to provide a multiplication equation that
demonstrates they understand multiplication in a curriculum-intended way. It may provide answer
choices that are mathematically correct, but not in the way the curriculum intended. For example,
it may show the student 3 groups of 4 circles and ask them for a multiplication equation that
represents this. "3 x 4" is the correct answer, but "4 x 3" is incorrect (because it does not
reflect the understanding of multiplication as "groups x objects") and "4 + 4 + 4" is incorrect
(because it is not a multiplication equation). In cases like this, do not penalize the question for
including these mathematically correct but not curriculum-intended answer choices, because the
presence of these answer choices is actually intentional and intended to assess the student's
understanding of the concept. Only penalize the question if its intent is not clear (either through
its wording or the curriculum context). For example, if it merely asked for "an equation" rather
than "a multiplication equation", then "4 + 4 + 4" would have been a plausibly correct answer in our
previous example.


Scoring: 5 = Entirely accurate, free from errors/hallucinations, completely relevant; 
4 = Accurate but may omit minor details or include slightly tangential information; 
3 = Mostly accurate but omits significant details or contains minor inaccuracies; 
2 = Contains noticeable inaccuracies that may confuse learners; 1 = Largely incorrect or 
misleading with significant errors; 0 = Entirely incorrect, fabricated, or unrelated

**4. Difficulty Alignment (0-5)**
Evaluate how well this question aligns with its intended difficulty level and cognitive demand. 
Consider these specific factors:

- **Difficulty Level Assessment:** First determine the apparent intended difficulty:
  • Easy: Basic recall or recognition of facts/concepts, straightforward foundational knowledge, 
    simple and clearly incorrect distractors
  • Medium: Application or analysis of concepts, applying understanding to familiar situations, 
    combining knowledge from multiple areas, moderately plausible distractors requiring reasoning
  • Hard: Advanced reasoning, evaluation, or synthesis, unfamiliar scenarios, multiple steps, 
    nuanced concepts, highly plausible distractors requiring careful analysis

- **Cognitive Demand Alignment:** Does the question appropriately challenge students based on 
its apparent difficulty level? Does it avoid unnecessary complexity (for Easy) or 
oversimplification (for Hard)?

- **Depth of Knowledge (DoK) Consistency:** Consider the cognitive demand:
  • DoK 1 (Recall): Basic recall of facts, definitions, procedures - single correct answer
  • DoK 2 (Skills/Concepts): Apply skills/concepts, interpret information, solve routine problems
  • DoK 3 (Strategic Thinking): Reasoning and planning, evaluate evidence, explain reasoning
  • DoK 4 (Extended Thinking): Extended analysis, synthesis, complex problem-solving over time

- **Contextual Appropriateness:** Does the difficulty align with the subject area, grade level, 
and learning objectives without introducing irrelevant complexity?

Scoring: 5 = Perfect difficulty match with intended level and appropriate cognitive demand; 
4 = Good alignment with minor elements that slightly exceed or fall short; 3 = Partial match 
with significant issues in complexity or cognitive demand; 2 = Limited alignment, mostly 
reflects different difficulty level; 1 = Poor alignment with clear difficulty mismatch; 
0 = Completely inappropriate for intended difficulty level

**5. Stimulus Quality (0-5)**
- **CRITICAL**: If the question contains a stimulus provided as a URL, you MUST download the
  stimulus and CAREFULLY examine the actual stimulus before scoring the stimulus quality.
- If images, diagrams, primary documents, or other stimulus elements are present, are they high
quality and necessary?
- Are stimulus elements clear, accurate, and well-integrated with the question?
- Do stimulus elements enhance a student's understanding of the question, or are they unnecessary
  or confusing?
- Would the question benefit from a stimulus element but lacks one?
- If separation or grouping of objects in the image is implied, are the objects clearly separated
in the image by spacing, dashed or solid lines, or other visual cues? Note: dashed rectangles around
objects constitute sufficient visual cues to separate the objects for all content types.
- Does the curriculum context provide any guidance on whether stimulus is required, or what features
  the stimulus should have?
  - If the curriculum context requires a stimulus, but a stimulus IS NOT present, score this as 0.
  - If the curriculum context forbids a stimulus, but a stimulus IS present, score this as 0.
  - If the curriculum context does say whether a stimulus is required or forbidden, base your score
  on the curriculum context's guidance and the other criteria for Stimulus Quality.

Scoring: 5 = Stimulus allowed/required and perfect stimulus quality with high-quality, necessary
stimulus elements, OR stimulus is forbidden and no stimulus is present; 4 = Stimulus
allowed/required and stimulus is good quality with minor issues; 3 = Stimulus allowed/required and
partial stimulus quality with significant issues; 2 = Stimulus allowed/required and limited stimulus
quality with clear issues; 1 = Stimulus allowed/required and poor stimulus quality with significant
issues; 0 = Stimulus forbidden and stimulus is present, OR stimulus required and no stimulus is
present, OR stimulus allowed/required and stimulus is present but of terrible quality.

**6. Mastery Learning Alignment (0-5)**
Evaluate how well this question supports mastery learning principles and deep understanding.
Consider these specific factors:

- **Conceptual Understanding Requirements:** Does the question require conceptual understanding, 
reasoning, and application rather than just recall? Does it go beyond simple recognition?
- **Non-trivial Application:** Does it present a non-trivial scenario where students must apply 
knowledge to solve problems, analyze situations, or make justified decisions?
- **Critical Thinking Emphasis:** Does it encourage critical thinking about relationships between 
key concepts and demonstrate deeper understanding? Does it require students to synthesize 
information, make connections, or explain reasoning?
- **Authentic Problem-Solving:** Does the question challenge students in ways that mirror 
authentic problem-solving in the field rather than testing isolated knowledge?
- **Diagnostic Learning Value:** Do incorrect answer choices help diagnose specific misconceptions 
and learning gaps? Does the question provide insight into whether students have achieved mastery?
- **Instructional Utility:** Would this question be useful for teachers to identify specific 
instructional needs and guide corrective learning?
- **Do Not Suggest Changing Question Types:** Do not suggest changing question types or adding
additional questions to further interrogate mastery learning principles. For example, do not suggest
a multiple choice question should be extended to include open-ended questions, add follow-up
questions, or be paired with other questions to further interrogate mastery learning principles.
Base your assessment solely on the limits of what the single question you have been given to
evaluate is capable of asking within the confines of the question type.

Scoring: 5 = Fully supports mastery learning with deep conceptual assessment, non-trivial 
application, and excellent diagnostic value; 4 = Promotes mastery learning with minor weaknesses; 
3 = Requires application but in straightforward ways, some diagnostic value; 2 = Primarily tests 
recall with minimal cognitive demand; 1 = Simple factual recall, no mastery support; 
0 = Completely misaligned with mastery learning principles

**OVERALL RATING**
After considering all individual metrics, provide a holistic overall rating by comparing this
question to the best available similar high-quality educational content that is typically available.
While your overall rating is independent of the individual metric scores, your rating should be
consistent with the individual metric scores and based on the curriculum context (if available). In
particular, do not suggest making changes to the content that are not consistent with the individual
metric rationales or the curriculum context.

- **SUPERIOR**: Better than typical high-quality educational questions relative to the curriculum
context if provided, or otherwise general pedagogical principles in the absence of curriculum
context. Exceptional design, engagement, and educational value that exceeds what is commonly
available.
- **ACCEPTABLE**: Comparable to typical high-quality educational questions relative to the
curriculum context if provided, or otherwise general pedagogical principles in the absence of
curriculum context. Good educational value that meets the standard expected from quality
educational materials.
- **INFERIOR**: Worse than typical high-quality educational questions relative to the curriculum
context if provided, or otherwise general pedagogical principles in the absence of curriculum
context. Falls short of the quality expected from good educational materials.

Note: It's possible for content to have low scores on some individual metrics but still be 
ACCEPTABLE or even SUPERIOR if it excels overall in ways that make it particularly valuable compared
to typical educational content. It's also possible for some content to score high on multiple
metrics yet still be INFERIOR overall if it is pedagogically unsound. Your overall rating should be
holistic, considering the full range of individual metric scores and pedagogical soundness.

**OUTPUT FORMAT**

For each metric AND the overall rating, provide:
- A score from 0 to 5 (for metrics) or SUPERIOR/ACCEPTABLE/INFERIOR rating (for overall)
- A detailed rationale that MUST include:
  (a) Clear Reasoning for the score/rating given, explaining why this specific score was assigned
      based on the evaluation criteria
  (b) If (1) the score is less than 5, or (2) the rating is less than SUPERIOR: Specific,
      actionable, and concrete Advice on how to improve the score/rating, including what changes
      should be made and what elements should be added, removed, or modified. Omit the Advice
      (including the "**Advice**:" line) if the score is 5 or the rating is SUPERIOR.
- Format the rationale like this, as a markdown string, but NOT inside a markdown code block:
```
**Reasoning**: [Detailed reasoning for the score/rating given]
\\n
**Advice**: [Specific, actionable, and concrete advice on how to improve the score/rating, including
what changes should be made and what elements should be added, removed, or modified; ONLY INCLUDE
THE "**Advice**:" line if the score is less than 5 OR the rating is less than SUPERIOR]
```

Remember to make all evaluations consistent with the curriculum context (if provided) and each other
so that a content creator could act upon your advice to improve the question without introducing
contradictions. Be strict in your evaluation - reserve high scores for truly excellent questions.
"""
    
    # Extract image URLs from content
    image_urls = extract_image_urls(content)
    
    # Build user content with proper structure for images
    user_content = [
        {"type": "input_text", "text": f"Please evaluate this question:\n\n{content}"}
    ]
    
    # Add images using proper vision API format
    for image_url in image_urls:
        user_content.append({"type": "input_image", "image_url": image_url})
        logger.info(f"Added image to evaluation: {image_url}")
        
    start_time = time.time()
    
    try:
        response = await client.responses.parse(
            model="gpt-5",
            input=[
                {"role": "system", "content": evaluation_prompt},
                {"role": "user", "content": user_content}
            ],
            text_format=QuestionEvaluationResult
        )
        logger.info(f"Question evaluation completed in {time.time() - start_time} seconds")
        
        # Extract the evaluation from the structured response
        for output_item in response.output:
            if output_item.type == "message":
                for content_item in output_item.content:
                    if (content_item.type == "output_text" and 
                        hasattr(content_item, "parsed") and 
                        content_item.parsed is not None):
                        result = content_item.parsed
                        
                        # AI now provides the overall rating directly, no calculation needed
                        return result
        
        # Fallback if parsing fails
        logger.error("Could not parse question evaluation results")
        return QuestionEvaluationResult(
            overall=OverallResult(rating=OverallRating.INFERIOR,
                                  rationale="Evaluation parsing failed"),
            curriculum_alignment=MetricResult(score=0, rationale="Evaluation parsing failed"),
            reveals_misconceptions=MetricResult(score=0, rationale="Evaluation parsing failed"), 
            correctness=MetricResult(score=0, rationale="Evaluation parsing failed"),
            difficulty_alignment=MetricResult(score=0, rationale="Evaluation parsing failed"),
            stimulus_quality=MetricResult(score=0, rationale="Evaluation parsing failed"),
            mastery_learning_alignment=MetricResult(score=0, rationale="Evaluation parsing failed")
        )
        
    except Exception as e:
        logger.error(f"Error evaluating question: {str(e)}")
        return QuestionEvaluationResult(
            overall=OverallResult(rating=OverallRating.INFERIOR,
                                  rationale=f"Evaluation failed: {str(e)}"),
            curriculum_alignment=MetricResult(score=0, rationale=f"Evaluation failed: {str(e)}"),
            reveals_misconceptions=MetricResult(score=0, rationale=f"Evaluation failed: {str(e)}"),
            correctness=MetricResult(score=0, rationale=f"Evaluation failed: {str(e)}"),
            difficulty_alignment=MetricResult(score=0, rationale=f"Evaluation failed: {str(e)}"),
            stimulus_quality=MetricResult(score=0, rationale=f"Evaluation failed: {str(e)}"),
            mastery_learning_alignment=MetricResult(score=0,
                                                    rationale=f"Evaluation failed: {str(e)}")
        )


async def _calculate_answer_balance(quiz_content: str) -> MetricResult:
    """
    Calculate answer balance using chi-square goodness of fit test.
    Extracts answer choices using GPT-5 and performs statistical analysis.
    """
    try:
        # Extract answer choices using GPT-5
        client = get_async_openai_client(timeout=60.0)
        prompt = (
            "Return a Python-formatted list of dictionaries indicating the correct/incorrect "
            "answer choices in the following quiz:\n"
            f'"""\n{quiz_content}\n"""\n'
            "The output should be formatted like this:\n"
            "[\n"
            '    {"A": "incorrect", "B": "correct", "C": "incorrect", "D": "incorrect"},\n'
            "    ...\n"
            "]"
            "DO NOT PLACE THE OUTPUT IN A CODE BLOCK, AND DO NOT INCLUDE ANY OTHER TEXT IN THE "
            "OUTPUT."
        )
        
        retries = 0
        answer_data = None
        while retries < 3:
            try:
                response = await client.chat.completions.create(
                    model="gpt-5",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0
                )
                answer_text = response.choices[0].message.content.strip()
                answer_data = eval(answer_text)  # Parse the Python list
                break
            except Exception as e:
                retries += 1
                await asyncio.sleep(2**retries)
                logger.warning(f"Retry {retries} for answer extraction: {e}")
        
        if not answer_data or len(answer_data) == 0 or retries >= 3:
            return MetricResult(
                score=0,
                rationale="Failed to extract answer choices from quiz"
            )

        # Analyze each question's correct answer position
        position_counts = []  # List of (position, total_choices) tuples
        for question_answers in answer_data:
            choices = sorted(question_answers.keys())  # Get available choices for this question
            n_choices = len(choices)
            
            # Find the position (0-based) of the correct answer
            correct_choice = next(
                (choice for choice, status in question_answers.items() 
                 if status.lower() == "correct"),
                None
            )
            
            if correct_choice and correct_choice in choices:
                position = choices.index(correct_choice)
                position_counts.append((position, n_choices))
        
        if not position_counts:
            return MetricResult(
                score=0,
                rationale="No valid correct answers found in quiz questions"
            )

        # Calculate chi-square statistic since questions may have different numbers of choices
        
        # Group questions by number of choices
        choice_groups = {}
        for pos, n_choices in position_counts:
            if n_choices not in choice_groups:
                choice_groups[n_choices] = []
            choice_groups[n_choices].append(pos)
        
        # Calculate chi-square contribution for each group
        observed_distributions = {}
        p_values = []
        
        for n_choices, positions in choice_groups.items():
            # Count occurrences of each position
            observed = [positions.count(i) for i in range(n_choices)]
            expected = [len(positions) / n_choices] * n_choices
            
            # Calculate chi-square test for this group
            try:
                stat, p_value = chisquare(observed, expected)
                p_values.append(p_value)
                observed_distributions[n_choices] = {
                    'positions': observed,
                    'p_value': p_value
                }
            except Exception as e:
                logger.warning(f"Failed to calculate chi-square for {n_choices} choices: {e}")
        
        # Use the minimum p-value across all groups
        p_value = min(p_values) if p_values else 0
        
        # Score based on p-value thresholds
        score = 0
        if p_value >= 0.90:
            score = 5
        elif p_value >= 0.80:
            score = 4
        elif p_value >= 0.60:
            score = 3
        elif p_value >= 0.40:
            score = 2
        elif p_value >= 0.20:
            score = 1
            
        # Build detailed explanation
        distributions = []
        for n_choices, data in observed_distributions.items():
            positions = data['positions']
            p_val = data['p_value']
            dist_str = (
                f"Questions with {n_choices} choices: "
                f"correct answer distribution {positions}, "
                f"probability this is random is {p_val*100:.1f}%"
            )
            distributions.append(dist_str)
        
        rationale = (
            "Questions include the following distributions of correct answers:\n\n" +
            "\n".join(distributions) +
            f"\n\nThe overall likelihood that this distribution is random is {p_value*100:.1f}%."
        )
        
        return MetricResult(score=score, rationale=rationale)
        
    except Exception as e:
        logger.error(f"Error calculating answer balance: {e}")
        return MetricResult(
            score=0,
            rationale=f"Error calculating answer balance: {str(e)}"
        )


async def evaluate_quiz(content: str) -> QuizEvaluationResult:
    """
    Evaluate a quiz across 5 metrics.
    
    Parameters
    ----------
    content : str
        The quiz content to evaluate
        
    Returns
    -------
    QuizEvaluationResult
        Evaluation results with scores and rationales for each metric
    """
    logger.info("Evaluating quiz...")
    
    # Calculate answer balance first so we can include it in the prompt
    answer_balance_result = await _calculate_answer_balance(content)
    
    # Get curriculum context using new extraction method
    curriculum_context = await get_curriculum_context(content)
    
    client = get_async_openai_client(timeout=300.0)
        
    # Include answer balance data in the prompt
    answer_balance_context = f"""

Answer Balance Analysis (Pre-computed based on chi-squared statistical analysis):
Score: {answer_balance_result.score}/5
{answer_balance_result.rationale}

Use this answer balance data to inform your reasoning and advice for the Answer Balance metric. 
You MUST use the provided score ({answer_balance_result.score}) but should enhance the reasoning
and advice based on the distribution data above and how it relates to the curriculum context and 
other aspects of the quiz content. Do not refer to the answer balance statistical analysis as if
it were provided to you. Speak about it as if you performed the analysis yourself (the analysis was
performed by code and provided to you, but the user is unaware of that process). You may refer to
the content of the statistical analysis in a manner that implies you performed the analysis
yourself."""
    
    evaluation_prompt = f"""
You are an expert educational evaluator. Evaluate quizzes across 5 key metrics and provide an
overall holistic rating. Each metric should be scored 0-5 with detailed rationale.
{curriculum_context}{answer_balance_context}

Rate each metric from 0-5. Ensure ALL rationales you provide for all metrics and the overall rating
are consistent with the curriculum context (if provided) and each other so that a content creator
could act upon your advice to improve the quiz without introducing contradictions.

If any URLs have alt text, read the alt text as part of your assessment, but do NOT guess or infer
what the alt text might contain. It's better to ignore the alt text or its possible content than to
base your assessment on hallucinations or guesses of what the alt text might contain.

**1. Concept Coverage (0-5)**
Evaluate how well this quiz achieves comprehensive concept coverage across all relevant 
educational standards. Follow this systematic approach:

- **Identify Key Concepts:** Extract the key concepts from the provided curriculum context or 
infer from the quiz content the major concepts that should be covered for the subject/grade level.
- **Analyze Concept Representation:** Review each quiz question and determine which key 
concept(s) it assesses. Track which standards are covered, underrepresented, or missing entirely.
- **Assess Balance and Distribution:** A well-balanced quiz should distribute questions across 
all major concepts so no important area is missing. If the quiz over-represents a few concepts 
while ignoring others, this significantly reduces effectiveness.

Consider these specific factors:
- Does the quiz cover **all major concepts** from relevant standards comprehensively?
- Are key learning objectives addressed across the questions with appropriate balance?
- Is there over-focus on some areas while neglecting other important concepts?
- Does each question serve a purpose in the overall coverage strategy?

Scoring: 5 = Covers all major concepts with appropriate balance, no significant gaps; 
4 = Covers most key concepts but one or two are underrepresented; 3 = Covers about half 
the key concepts with multiple missing areas; 2 = Heavily skewed, assesses only small 
subset while failing to address majority; 1 = Barely covers any key concepts; 
0 = Completely misaligned with expected standards

**2. Difficulty Distribution (0-5)**
Evaluate how well this quiz achieves an appropriate balance of difficulty levels. Follow this 
systematic approach:

- **Classify Each Question's Difficulty:** Determine whether each question is Easy, Medium, or Hard:
  • Easy: Simple recall or one-step problem-solving, basic foundational knowledge
  • Medium: Reasoning, multiple steps, moderate application, connecting concepts
  • Hard: Deep understanding, synthesis, higher-order thinking, advanced reasoning
- **Count and Assess Distribution:** Analyze the balance across difficulty levels and logical 
progression
- **Apply Scoring Criteria:** Use specific thresholds to determine the base score, then apply 
adjustments for progression and differentiation issues

Consider these specific factors:
- **Base Distribution:** Are all three difficulty levels present? What's the balance between 
most and least frequent levels?
- **Logical Progression:** Do difficulty levels progress logically or are they randomly mixed?
- **Student Differentiation:** Does the difficulty range allow students at different mastery 
levels to be meaningfully assessed?
- **Over-concentration:** Does more than 50% fall into a single difficulty level?

Scoring: 5 = All three levels present with ≤10% difference between most/least frequent; 
4 = All three levels, ≤20% difference; 3 = All three levels, ≤30% difference; 2 = Major 
imbalance or only two levels; 1 = Severe imbalance; 0 = All questions same difficulty.
Apply -1 penalties for poor progression or lack of differentiation.

**3. Non-Repetitiveness (0-5)**
Evaluate how well this quiz avoids repetitive or redundant questions. Follow this systematic 
approach:

- **Identify Core Concept of Each Question:** Extract the key concept being tested in each 
question. Note questions that assess the same skill, knowledge, or understanding in nearly 
identical ways.
- **Determine Substantial Repetition:** Consider questions redundant if they ask for the same 
factual recall multiple times, pose multiple variations of the same calculation without 
meaningful differences, or have only superficial wording differences while assessing the same idea.
- **Distinguish Valid Similarity:** Do NOT count as repetitive: questions that apply the same 
concept in different contexts, or require different levels of cognitive demand (e.g., one asks 
for definition, another applies it in problem).

Consider these specific factors:
- Does each question serve a **unique purpose** in assessing student understanding?
- Are there questions that feel **substantially the same** despite different wording?
- Do questions assess concepts in **diverse ways** or just repeat the same approach?
- Is repetition occurring within the same standard or across different standards?

Scoring: 5 = No redundant questions, each assesses distinct concept/skill; 4 = One pair of 
slightly repetitive questions with minimal impact; 3 = 2-3 noticeably redundant questions; 
2 = Heavily repetitive with 4-5 redundant questions; 1 = Dominated by repetition with 6+ 
similar questions; 0 = Almost entirely repetitive, functionally useless as assessment

**4. Test Preparedness (0-5)**
Evaluate how well this quiz aligns with expected standardized test composition for the subject 
area. Follow this systematic approach:

- **Analyze Expected Standardized Test Composition:** Identify the expected structure, cognitive 
demands, question relationships, and key features of standardized assessments for this subject.
- **Compare Quiz to Expected Composition:** Assess whether the quiz aligns with key elements 
such as question types, cognitive demand levels, question relationships, timing considerations, 
and question formations typical of standardized tests.
- **Focus on Specified Elements:** Determine how well the quiz follows what is typically 
expected in standardized testing without adding emphasis to elements not relevant to the format.

Consider these specific factors:
- Does the quiz structure **resemble standardized test formats** for the subject area?
- Are **question types and cognitive demands** appropriate for standardized test preparation?
- Does it include the **mix of question formats** typical of standardized assessments (e.g., 
stimulus-based questions, graph interpretation, scenario analysis)?
- Do the **relationships among questions** mirror what students would experience on real tests?
- Does the quiz prepare students for the **actual testing experience** they will encounter?

Scoring: 5 = Closely matches expected standardized test composition, maintains alignment with 
all key elements; 4 = Strong match with slight deviations that don't significantly impact 
resemblance; 3 = Partially aligns but contains noticeable differences in key areas; 2 = 
Significantly deviates, lacks important structural elements; 1 = Bears little resemblance 
to standardized test expectations; 0 = Fails completely to align, unsuitable for test preparation

**5. Answer Balance (0-5)**
Evaluate the distribution of correct answer positions across multiple-choice questions in the quiz.
The score and detailed distribution data have been pre-computed and provided above.

**CRITICAL INSTRUCTIONS:**
- You MUST use the exact score provided in the Answer Balance Analysis section above
- Enhance the reasoning by analyzing the distribution patterns in relation to:
  - The specific quiz content and question types
  - How answer position patterns might affect student performance or test-taking strategies
  - The curriculum context and any pedagogical implications
  - Consistency with the other metrics (concept coverage, difficulty, etc.)

**For your advice when the score is less than 5:**
- Base recommendations on the specific distribution data provided
- If certain positions (A, B, C, D) are over-represented, suggest which questions should have
  their correct answers moved to different positions
- Consider the quiz content when making specific suggestions (e.g., easier questions might
  benefit from varied answer positions to avoid patterns)
- Ensure advice is actionable and specific to this quiz's content and structure
- Make suggestions consistent with curriculum context and pedagogical goals

Scoring: Use the provided score from the Answer Balance Analysis above. DO NOT calculate or 
change this score - ONLY provide enhanced reasoning and advice based on the distribution data.

**OVERALL RATING**
After considering all individual metrics (including the answer balance analysis provided above),
provide a holistic overall rating by comparing this quiz to the best available similar
high-quality educational content that is typically available. While your overall rating is
independent of the individual metric scores, your rating should be consistent with the individual
metric scores and based on the curriculum context (if available). In particular, do not suggest
making changes to the content that are not consistent with the individual metric rationales or the
curriculum context.

- **SUPERIOR**: Better than typical high-quality educational quizzes relative to the curriculum
context if provided, or otherwise general pedagogical principles in the absence of curriculum
context. Exceptional design, engagement, and educational value that exceeds what is commonly
available.
- **ACCEPTABLE**: Comparable to typical high-quality educational quizzes relative to the
curriculum context if provided, or otherwise general pedagogical principles in the absence of
curriculum context. Good educational value that meets the standard expected from quality
educational materials.
- **INFERIOR**: Worse than typical high-quality educational quizzes relative to the curriculum
context if provided, or otherwise general pedagogical principles in the absence of curriculum
context. Falls short of the quality expected from good educational materials.

Note: It's possible for content to have low scores on some individual metrics but still be 
ACCEPTABLE or even SUPERIOR if it excels overall in ways that make it particularly valuable compared
to typical educational content. It's also possible for some content to score high on multiple
metrics yet still be INFERIOR overall if it is pedagogically unsound. Your overall rating should be
holistic, considering the full range of individual metric scores and pedagogical soundness.

For each metric AND the overall rating, provide:
- A score from 0 to 5 (for metrics) or SUPERIOR/ACCEPTABLE/INFERIOR rating (for overall)
- A detailed rationale that MUST include:
  (a) Clear justification and reasoning for the score/rating given, explaining why this specific 
      score was assigned based on the evaluation criteria
  (b) If (1) the score is less than 5, or (2) the rating is less than SUPERIOR: Specific,
      actionable, and concrete Advice on how to improve the score/rating, including what changes
      should be made and what elements should be added, removed, or modified. Omit the Advice
      (including the "**Advice**:" line) if the score is 5 or the rating is SUPERIOR.
- Format the rationale like this, as a markdown string, but NOT inside a markdown code block:
```
**Reasoning**: [Detailed reasoning for the score/rating given]
\\n
**Advice**: [Specific, actionable, and concrete advice on how to improve the score/rating, including
what changes should be made and what elements should be added, removed, or modified; ONLY INCLUDE
THE "**Advice**:" line if the score is less than 5 OR the rating is less than SUPERIOR]
```

Remember to make all evaluations consistent with the curriculum context (if provided) and each other
so that a content creator could act upon your advice to improve the quiz without introducing
contradictions. Be strict in your evaluation - reserve high scores for truly excellent quizzes.
"""
    
    # Extract image URLs from content
    image_urls = extract_image_urls(content)
    
    # Build user content with proper structure for images
    user_content = [{"type": "input_text", "text": f"Please evaluate this quiz:\n\n{content}"}]
    
    # Add images using proper vision API format
    for image_url in image_urls:
        user_content.append({"type": "input_image", "image_url": image_url})
        logger.info(f"Added image to evaluation: {image_url}")
        
    try:
        response = await client.responses.parse(
            model="gpt-5",
            input=[
                {"role": "system", "content": evaluation_prompt},
                {"role": "user", "content": user_content}
            ],
            text_format=QuizEvaluationResult
        )
        
        # Extract the evaluation from the structured response
        for output_item in response.output:
            if output_item.type == "message":
                for content_item in output_item.content:
                    if (content_item.type == "output_text" and 
                        hasattr(content_item, "parsed") and 
                        content_item.parsed is not None):
                        result = content_item.parsed
                        
                        # AI now provides the overall rating and all metrics directly
                        return result
        
        # Fallback if parsing fails
        logger.error("Could not parse quiz evaluation results")
        return QuizEvaluationResult(
            overall=OverallResult(rating=OverallRating.INFERIOR,
                                  rationale="Evaluation parsing failed"),
            concept_coverage=MetricResult(score=0, rationale="Evaluation parsing failed"),
            difficulty_distribution=MetricResult(score=0, rationale="Evaluation parsing failed"),
            non_repetitiveness=MetricResult(score=0, rationale="Evaluation parsing failed"),
            test_preparedness=MetricResult(score=0, rationale="Evaluation parsing failed"),
            answer_balance=MetricResult(score=0, rationale="Evaluation parsing failed")
        )
        
    except Exception as e:
        logger.error(f"Error evaluating quiz: {str(e)}")
        return QuizEvaluationResult(
            overall=OverallResult(rating=OverallRating.INFERIOR,
                                  rationale=f"Evaluation failed: {str(e)}"),
            concept_coverage=MetricResult(score=0, rationale=f"Evaluation failed: {str(e)}"),
            difficulty_distribution=MetricResult(score=0, rationale=f"Evaluation failed: {str(e)}"),
            non_repetitiveness=MetricResult(score=0, rationale=f"Evaluation failed: {str(e)}"),
            test_preparedness=MetricResult(score=0, rationale=f"Evaluation failed: {str(e)}"),
            answer_balance=MetricResult(score=0, rationale=f"Evaluation failed: {str(e)}")
        )


async def evaluate_reading_passage(content: str, is_fiction: bool) -> ReadingEvaluationResult:
    """
    Route to appropriate fiction or nonfiction reading passage evaluator.
    
    Parameters
    ----------
    content : str
        The reading passage content to evaluate
    is_fiction : bool
        Whether the passage is fiction (True) or nonfiction (False)
        
    Returns
    -------
    ReadingEvaluationResult
        Evaluation results with scores and rationales for each metric
    """
    if is_fiction:
        return await evaluate_fiction_reading_passage(content)
    else:
        return await evaluate_nonfiction_reading_passage(content)


async def evaluate_fiction_reading_passage(content: str) -> ReadingEvaluationResult:
    """
    Evaluate a fiction reading passage across 6 metrics.
    
    Parameters
    ----------
    content : str
        The fiction reading passage content to evaluate
        
    Returns
    -------
    ReadingEvaluationResult
        Evaluation results with scores and rationales for each metric
    """
    logger.info("Evaluating fiction reading passage...")
    
    # Get curriculum context using new extraction method
    curriculum_context = await get_curriculum_context(content)
    
    client = get_async_openai_client(timeout=300.0)
    
    evaluation_prompt = f"""
You are an expert educational evaluator. Evaluate fiction reading
passages across 6 key metrics and provide an overall holistic rating. Each metric should be scored 
0-5 with detailed rationale.
{curriculum_context}

Since specific parameters (grade level, target length, topic) may not be explicitly provided, make
educated guesses based on:
- Vocabulary complexity and sentence structure (to infer grade level)
- Content and themes (to infer topic)  
- Actual word count (to assess length appropriateness)

Rate each metric from 0-5. Ensure ALL rationales you provide for all metrics and the overall rating
are consistent with the curriculum context (if provided) and each other so that a content creator
could act upon your advice to improve the passage without introducing contradictions.

If any URLs have alt text, read the alt text as part of your assessment, but do NOT guess or infer
what the alt text might contain. It's better to ignore the alt text or its possible content than to
base your assessment on hallucinations or guesses of what the alt text might contain.

**1. Reading Level Match (0-5)**
Evaluate how well this passage aligns with the expected Lexile range and grade level. Use this 
systematic approach:

- **Identify Target Lexile Level:** Determine the appropriate Lexile level for the grade level:
  K: BR250L, 1st: 85L, 2nd: 355L, 3rd: 590L, 4th: 790L, 5th: 925L, 6th: 1010L, 
  7th: 1080L, 8th: 1140L, 9th: 1195L, 10th: 1240L, 11th/12th: 1285L
- **Assess Lexile Characteristics:** Evaluate against expected characteristics for that level:
  • Sentence Structure: Length, complexity, clause usage appropriate for level
  • Vocabulary: Academic/domain-specific words with appropriate context support
  • Inference Requirements: Level of implicit connections and background knowledge needed
  • Conceptual Complexity: Abstract vs. concrete ideas, real-world applications

Consider these specific factors:
- Does the **sentence structure** align with syntactic expectations (simple vs. complex sentences)?
- Is the **vocabulary** suitable for the Lexile level with appropriate context support?
- Are **inference requirements** appropriate for the grade level and topic?
- Do **concepts** match the expected abstraction level and cognitive demand?
- Would an average student at this grade level be **challenged appropriately** without frustration?

Scoring: 5 = Perfect match with expected Lexile level characteristics; 4 = Mostly aligns with 
minor deviations; 3 = Somewhat misaligned, too advanced or simple; 2 = Poorly aligned, 
requires significant adjustments; 1 = Entirely misaligned, far too difficult or easy; 
0 = Unusable at this grade level

**2. Length Appropriateness (0-5)**
- Count the approximate word count of the passage
- Based on the inferred grade level and type of passage, is the length appropriate?
- Typical ranges: Elementary (100-300 words), Middle (300-600 words), High School (500-1000+ words)
- Does the length support effective comprehension without being too short or overwhelming?

**3. Topic Focus (0-5)**
Evaluate how well this passage stays focused on the assigned topic without unnecessary tangents 
or unrelated details. Follow this systematic approach:

- **Direct Relevance Assessment:** Does the passage directly address the assigned topic? Does it 
explain key ideas, events, or concepts relevant to the topic?
- **Tangent Identification:** Does the passage stay on track, or does it introduce off-topic 
details? If background information is provided, does it serve a clear purpose?
- **Depth Evaluation:** Does the passage explore the topic with sufficient depth for the intended 
grade level? Is the topic fully developed or superficial?
- **Cohesion Analysis:** Does each part contribute logically to understanding the topic? Are 
transitions smooth and focused?

Consider these specific factors:
- Does every sentence **contribute meaningfully** to understanding the assigned topic?
- Are there **unnecessary tangents** or details that distract from the main focus?
- Is the topic **developed with appropriate depth** for the grade level without being superficial?
- Does the passage maintain **logical flow** and smooth transitions throughout?
- If comprehension questions are present, do they stay focused on the assigned topic?

Scoring: 5 = Fully focused with clear, structured, relevant discussion and no tangents; 
4 = Mostly on-topic with minor off-topic details that don't detract significantly; 3 = Covers 
topic but includes noticeable tangents or fails to develop key aspects; 2 = Only partially 
addresses topic, significant unrelated content, or lacks depth; 1 = Barely addresses topic, 
highly unfocused, long irrelevant sections; 0 = Entirely off-topic, no meaningful discussion

**4. Engagement (0-5)**
Evaluate how engaging and well-structured this fiction passage is. Follow this systematic approach:

- **Narrative Structure & Flow:** Clear beginning, middle, and end related to topic? Logical 
event progression? Appropriate pacing for grade level?
- **Character & Conflict Development:** Engaging, well-defined characters for age group and 
topic? Clear problem/conflict that drives interest? Meaningful resolution?
- **Reader Connection:** Would students find this interesting and want to keep reading? Does it 
spark curiosity, emotion, or imagination appropriately?
- **Sentence & Word Choice:** Varied sentence structures and engaging vocabulary appropriate for 
grade level? Avoids repetitive, simplistic, or monotonous phrasing?
- **Overall Appeal:** Would students at the grade level generally interested in the topic find 
this engaging and want to continue reading?

Scoring: 5 = Highly engaging, well-structured, captures interest from start to finish; 
4 = Mostly engaging with minor weaknesses; 3 = Somewhat engaging but parts may be dull or 
underdeveloped; 2 = Struggles to maintain engagement due to weak storytelling; 
1 = Lacks engagement, disjointed or tedious; 0 = Fails completely to be engaging, incoherent 
or extremely dull

**5. Accuracy & Logic (0-5)**
Evaluate the logical consistency of this fiction passage. Follow this systematic approach:

- **Logical Consistency:** Do events follow a clear cause-and-effect structure? Are character 
actions and decisions consistent with their motivations and setting?
- **Internal Coherence:** Does the story avoid contradictions (e.g., character knowing something 
they shouldn't, events occurring out of sequence)?
- **Internal Consistency & Coherence:** Does the passage maintain consistent tone, setting, and 
logic throughout? Are facts or events introduced and maintained logically?
- **Avoidance of Misleading Information:** Does it avoid misleading statements or ambiguities 
that could cause misunderstandings?

Scoring: 5 = Entirely logically sound with no errors or contradictions; 4 = Mostly logical with 
minor inconsistencies that don't significantly impact understanding; 3 = Notable inconsistencies 
that could reduce clarity; 2 = Multiple significant contradictions making it confusing; 1 = Major 
logical flaws undermining story coherence; 0 = Entirely unreliable with nonsensical content

**6. Question Quality (0-5)**
Evaluate the quality and appropriateness of comprehension questions (if present). Follow this 
systematic approach:

- **Question Clarity & Structure:** Are questions phrased clearly and unambiguously? Do they 
avoid vague wording, overly complex phrasing, or confusing grammar? Are they properly formatted?
- **Grade Level Appropriateness:** Are questions at a difficulty level that aligns with the 
cognitive abilities of students in the specified grade? Avoid being too simplistic or too difficult?
- **Balance of Question Types:** Do questions include:
  • Literal Recall Questions (Who? What? Where?) to test understanding of key details
  • Inferential Reasoning Questions (Why? How do you know?) to assess deeper comprehension
  • Applied Thinking Questions (How does this connect to real life?) for higher-order thinking
- **Alignment with Passage:** Does each question directly relate to the passage? Are correct 
answers truly correct and incorrect choices plausible yet clearly incorrect?
- **Cognitive Engagement & Depth:** Do questions encourage deeper thinking beyond surface-level 
recall? Do they help students make connections, analyze relationships, or draw conclusions?

Consider these specific factors:
- Is there a **balanced mix** of literal recall, inferential reasoning, and applied thinking?
- Are questions **clear, well-structured, and appropriately challenging** for the grade level?
- Do they **align well with the passage** with correct answers and plausible distractors?
- Do questions promote **deep comprehension and critical thinking**?

Scoring: 5 = Clear, well-structured, appropriately challenging with balanced mix of question 
types; 4 = Mostly strong with minor issues; 3 = Somewhat effective but notably unbalanced or 
some structural issues; 2 = Significant problems with clarity, answers, or difficulty; 1 = Poorly 
designed with little variety or major alignment issues; 0 = Entirely ineffective, fail to assess 
comprehension or contain major errors. If no questions present, score based on whether passage 
would lend itself well to good comprehension questions.

**OVERALL RATING**
After considering all individual metrics, provide a holistic overall rating by comparing this
fiction reading passage to the best available similar high-quality educational content that is
typically available. While your overall rating is independent of the individual metric scores, your
rating should be consistent with the individual metric scores and based on the curriculum context
(if available). In particular, do not suggest making changes to the content that are not consistent
with the individual metric rationales or the curriculum context.

- **SUPERIOR**: Better than typical high-quality educational fiction passages relative to the
curriculum context if provided, or otherwise general pedagogical principles in the absence of
curriculum context. Exceptional design, engagement, and educational value that exceeds what is
commonly available.
- **ACCEPTABLE**: Comparable to typical high-quality educational fiction passages relative to the
curriculum context if provided, or otherwise general pedagogical principles in the absence of
curriculum context. Good educational value that meets the standard expected from quality
educational materials.
- **INFERIOR**: Worse than typical high-quality educational fiction passages relative to the
curriculum context if provided, or otherwise general pedagogical principles in the absence of
curriculum context. Falls short of the quality expected from good educational materials.

Note: It's possible for content to have low scores on some individual metrics but still be 
ACCEPTABLE or even SUPERIOR if it excels overall in ways that make it particularly valuable compared
to typical educational content. It's also possible for some content to score high on multiple
metrics yet still be INFERIOR overall if it is pedagogically unsound. Your overall rating should be
holistic, considering the full range of individual metric scores and pedagogical soundness.

For each metric AND the overall rating, provide:
- A score from 0 to 5 (for metrics) or SUPERIOR/ACCEPTABLE/INFERIOR rating (for overall)
- A detailed rationale that MUST include:
  (a) Clear justification and reasoning for the score/rating given, explaining why this specific 
      score was assigned based on the evaluation criteria
  (b) If (1) the score is less than 5, or (2) the rating is less than SUPERIOR: Specific,
      actionable, and concrete Advice on how to improve the score/rating, including what changes
      should be made and what elements should be added, removed, or modified. Omit the Advice
      (including the "**Advice**:" line) if the score is 5 or the rating is SUPERIOR.
- Format the rationale like this, as a markdown string, but NOT inside a markdown code block:
```
**Reasoning**: [Detailed reasoning for the score/rating given]
\\n
**Advice**: [Specific, actionable, and concrete advice on how to improve the score/rating, including
what changes should be made and what elements should be added, removed, or modified; ONLY INCLUDE
THE "**Advice**:" line if the score is less than 5 OR the rating is less than SUPERIOR]
```

Remember to make all evaluations consistent with the curriculum context (if provided) and each other
so that a content creator could act upon your advice to improve the passage without introducing
contradictions. Be strict in your evaluation - reserve high scores for truly excellent passages.
"""
    
    # Extract image URLs from content
    image_urls = extract_image_urls(content)
    
    # Build user content with proper structure for images
    user_content = [
        {"type": "input_text", 
         "text": f"Please evaluate this fiction reading passage:\n\n{content}"}
    ]
    
    # Add images using proper vision API format
    for image_url in image_urls:
        user_content.append({"type": "input_image", "image_url": image_url})
        logger.info(f"Added image to evaluation: {image_url}")
        
    try:
        response = await client.responses.parse(
            model="gpt-5",
            input=[
                {"role": "system", "content": evaluation_prompt},
                {"role": "user", "content": user_content}
            ],
            text_format=ReadingEvaluationResult
        )
        
        # Extract the evaluation from the structured response
        for output_item in response.output:
            if output_item.type == "message":
                for content_item in output_item.content:
                    if (content_item.type == "output_text" and 
                        hasattr(content_item, "parsed") and 
                        content_item.parsed is not None):
                        result = content_item.parsed
                        
                        # AI now provides the overall rating directly, no calculation needed
                        return result
        
        # Fallback if parsing fails
        logger.error("Could not parse fiction reading passage evaluation results")
        return ReadingEvaluationResult(
            overall=OverallResult(rating=OverallRating.INFERIOR,
                                  rationale="Evaluation parsing failed"),
            reading_level_match=MetricResult(score=0, rationale="Evaluation parsing failed"),
            length_appropriateness=MetricResult(score=0, rationale="Evaluation parsing failed"),
            topic_focus=MetricResult(score=0, rationale="Evaluation parsing failed"),
            engagement=MetricResult(score=0, rationale="Evaluation parsing failed"),
            accuracy_and_logic=MetricResult(score=0, rationale="Evaluation parsing failed"),
            question_quality=MetricResult(score=0, rationale="Evaluation parsing failed")
        )
        
    except Exception as e:
        logger.error(f"Error evaluating fiction reading passage: {str(e)}")
        return ReadingEvaluationResult(
            overall=OverallResult(rating=OverallRating.INFERIOR,
                                  rationale=f"Evaluation failed: {str(e)}"),
            reading_level_match=MetricResult(score=0, rationale=f"Evaluation failed: {str(e)}"),
            length_appropriateness=MetricResult(score=0, rationale=f"Evaluation failed: {str(e)}"),
            topic_focus=MetricResult(score=0, rationale=f"Evaluation failed: {str(e)}"),
            engagement=MetricResult(score=0, rationale=f"Evaluation failed: {str(e)}"),
            accuracy_and_logic=MetricResult(score=0, rationale=f"Evaluation failed: {str(e)}"),
            question_quality=MetricResult(score=0, rationale=f"Evaluation failed: {str(e)}")
        )

async def evaluate_nonfiction_reading_passage(content: str) -> ReadingEvaluationResult:
    """
    Evaluate a nonfiction reading passage across 6 metrics.
    
    Parameters
    ----------
    content : str
        The nonfiction reading passage content to evaluate
        
    Returns
    -------
    ReadingEvaluationResult
        Evaluation results with scores and rationales for each metric
    """
    logger.info("Evaluating nonfiction reading passage...")
    
    # Get curriculum context using new extraction method
    curriculum_context = await get_curriculum_context(content)
    
    client = get_async_openai_client(timeout=300.0)
    
    evaluation_prompt = f"""
You are an expert educational evaluator. Evaluate nonfiction reading
passages across 6 key metrics and provide an overall holistic rating. Each metric should be scored 
0-5 with detailed rationale.
{curriculum_context}

Since specific parameters (grade level, target length, topic) may not be explicitly provided, make
educated guesses based on:
- Vocabulary complexity and sentence structure (to infer grade level)
- Content and themes (to infer topic)  
- Actual word count (to assess length appropriateness)

Rate each metric from 0-5. Ensure ALL rationales you provide for all metrics and the overall rating
are consistent with the curriculum context (if provided) and each other so that a content creator
could act upon your advice to improve the passage without introducing contradictions.

If any URLs have alt text, read the alt text as part of your assessment, but do NOT guess or infer
what the alt text might contain. It's better to ignore the alt text or its possible content than to
base your assessment on hallucinations or guesses of what the alt text might contain.

**1. Reading Level Match (0-5)**
Evaluate how well this passage aligns with the expected Lexile range and grade level. Use this 
systematic approach:

- **Identify Target Lexile Level:** Determine the appropriate Lexile level for the grade level:
  K: BR250L, 1st: 85L, 2nd: 355L, 3rd: 590L, 4th: 790L, 5th: 925L, 6th: 1010L, 
  7th: 1080L, 8th: 1140L, 9th: 1195L, 10th: 1240L, 11th/12th: 1285L
- **Assess Lexile Characteristics:** Evaluate against expected characteristics for that level:
  • Sentence Structure: Length, complexity, clause usage appropriate for level
  • Vocabulary: Academic/domain-specific words with appropriate context support
  • Inference Requirements: Level of implicit connections and background knowledge needed
  • Conceptual Complexity: Abstract vs. concrete ideas, real-world applications

Consider these specific factors:
- Does the **sentence structure** align with syntactic expectations (simple vs. complex sentences)?
- Is the **vocabulary** suitable for the Lexile level with appropriate context support?
- Are **inference requirements** appropriate for the grade level and topic?
- Do **concepts** match the expected abstraction level and cognitive demand?
- Would an average student at this grade level be **challenged appropriately** without frustration?

Scoring: 5 = Perfect match with expected Lexile level characteristics; 4 = Mostly aligns with 
minor deviations; 3 = Somewhat misaligned, too advanced or simple; 2 = Poorly aligned, 
requires significant adjustments; 1 = Entirely misaligned, far too difficult or easy; 
0 = Unusable at this grade level

**2. Length Appropriateness (0-5)**
- Count the approximate word count of the passage
- Based on the inferred grade level and type of passage, is the length appropriate?
- Typical ranges: Elementary (100-300 words), Middle (300-600 words), High School (500-1000+ words)
- Does the length support effective comprehension without being too short or overwhelming?

**3. Topic Focus (0-5)**
Evaluate how well this passage stays focused on the assigned topic without unnecessary tangents 
or unrelated details. Follow this systematic approach:

- **Direct Relevance Assessment:** Does the passage directly address the assigned topic? Does it 
explain key ideas, events, or concepts relevant to the topic?
- **Tangent Identification:** Does the passage stay on track, or does it introduce off-topic 
details? If background information is provided, does it serve a clear purpose?
- **Depth Evaluation:** Does the passage explore the topic with sufficient depth for the intended 
grade level? Is the topic fully developed or superficial?
- **Cohesion Analysis:** Does each part contribute logically to understanding the topic? Are 
transitions smooth and focused?

Consider these specific factors:
- Does every sentence **contribute meaningfully** to understanding the assigned topic?
- Are there **unnecessary tangents** or details that distract from the main focus?
- Is the topic **developed with appropriate depth** for the grade level without being superficial?
- Does the passage maintain **logical flow** and smooth transitions throughout?
- If comprehension questions are present, do they stay focused on the assigned topic?

Scoring: 5 = Fully focused with clear, structured, relevant discussion and no tangents; 
4 = Mostly on-topic with minor off-topic details that don't detract significantly; 3 = Covers 
topic but includes noticeable tangents or fails to develop key aspects; 2 = Only partially 
addresses topic, significant unrelated content, or lacks depth; 1 = Barely addresses topic, 
highly unfocused, long irrelevant sections; 0 = Entirely off-topic, no meaningful discussion

**4. Engagement (0-5)**
Evaluate how engaging and well-structured this nonfiction passage is. Follow this systematic
approach:

- **Clarity & Engagement of Presentation:** Information presented clearly and engagingly? 
Interesting examples, explanations, or relevant details? Engaging rather than dry tone?
- **Educational Appeal:** Does it spark curiosity about the topic? Are facts presented 
compellingly?
- **Sentence & Word Choice:** Varied sentence structures and engaging vocabulary appropriate for 
grade level? Avoids repetitive, simplistic, or monotonous phrasing?
- **Overall Appeal:** Would students at the grade level generally interested in the topic find 
this engaging and want to continue reading?

Scoring: 5 = Highly engaging, well-structured, captures interest from start to finish; 
4 = Mostly engaging with minor weaknesses; 3 = Somewhat engaging but parts may be dull or 
underdeveloped; 2 = Struggles to maintain engagement due to dry, unclear presentation; 
1 = Lacks engagement, disjointed or tedious; 0 = Fails completely to be engaging, incoherent 
or extremely dull

**5. Accuracy & Logic (0-5)**
Evaluate the factual accuracy of this nonfiction passage. Follow this systematic approach:

- **Factual Accuracy:** Are all statements factually correct based on established knowledge? 
Does it avoid misinformation, misinterpretations, or incorrect explanations?
- **Scientific/Historical Correctness:** If statistics, historical events, or scientific 
processes are mentioned, are they accurately described?
- **Simplification Appropriateness:** If complex ideas are simplified for younger readers, 
is the simplification still accurate rather than misleading?
- **Internal Consistency & Coherence:** Does the passage maintain consistent tone, setting, and 
logic throughout? Are facts or events introduced and maintained logically?
- **Avoidance of Misleading Information:** Does it avoid misleading statements or ambiguities 
that could cause misunderstandings?

Scoring: 5 = Entirely factually correct with no errors or contradictions; 4 = Mostly accurate 
with minor imprecisions that don't significantly impact understanding; 3 = Notable factual 
errors that could mislead or reduce clarity; 2 = Multiple significant errors making it misleading 
or confusing; 1 = Severe factual inaccuracies undermining educational value; 0 = Entirely 
unreliable with critical errors

**6. Question Quality (0-5)**
Evaluate the quality and appropriateness of comprehension questions (if present). Follow this 
systematic approach:

- **Question Clarity & Structure:** Are questions phrased clearly and unambiguously? Do they 
avoid vague wording, overly complex phrasing, or confusing grammar? Are they properly formatted?
- **Grade Level Appropriateness:** Are questions at a difficulty level that aligns with the 
cognitive abilities of students in the specified grade? Avoid being too simplistic or too difficult?
- **Balance of Question Types:** Do questions include:
  • Literal Recall Questions (Who? What? Where?) to test understanding of key details
  • Inferential Reasoning Questions (Why? How do you know?) to assess deeper comprehension
  • Applied Thinking Questions (How does this connect to real life?) for higher-order thinking
- **Alignment with Passage:** Does each question directly relate to the passage? Are correct 
answers truly correct and incorrect choices plausible yet clearly incorrect?
- **Cognitive Engagement & Depth:** Do questions encourage deeper thinking beyond surface-level 
recall? Do they help students make connections, analyze relationships, or draw conclusions?

Consider these specific factors:
- Is there a **balanced mix** of literal recall, inferential reasoning, and applied thinking?
- Are questions **clear, well-structured, and appropriately challenging** for the grade level?
- Do they **align well with the passage** with correct answers and plausible distractors?
- Do questions promote **deep comprehension and critical thinking**?

Scoring: 5 = Clear, well-structured, appropriately challenging with balanced mix of question 
types; 4 = Mostly strong with minor issues; 3 = Somewhat effective but notably unbalanced or 
some structural issues; 2 = Significant problems with clarity, answers, or difficulty; 1 = Poorly 
designed with little variety or major alignment issues; 0 = Entirely ineffective, fail to assess 
comprehension or contain major errors. If no questions present, score based on whether passage 
would lend itself well to good comprehension questions.

**OVERALL RATING**
After considering all individual metrics, provide a holistic overall rating by comparing this
nonfiction reading passage to the best available similar high-quality educational content that is
typically available. While your overall rating is independent of the individual metric scores, your
rating should be consistent with the individual metric scores and based on the curriculum context
(if available). In particular, do not suggest making changes to the content that are not consistent
with the individual metric rationales or the curriculum context.

- **SUPERIOR**: Better than typical high-quality educational nonfiction passages relative to the
curriculum context if provided, or otherwise general pedagogical principles in the absence of
curriculum context. Exceptional design, engagement, and educational value that exceeds what is
commonly available.
- **ACCEPTABLE**: Comparable to typical high-quality educational nonfiction passages relative to the
curriculum context if provided, or otherwise general pedagogical principles in the absence of
curriculum context. Good educational value that meets the standard expected from quality
educational materials.
- **INFERIOR**: Worse than typical high-quality educational nonfiction passages relative to the
curriculum context if provided, or otherwise general pedagogical principles in the absence of
curriculum context. Falls short of the quality expected from good educational materials.

Note: It's possible for content to have low scores on some individual metrics but still be 
ACCEPTABLE or even SUPERIOR if it excels overall in ways that make it particularly valuable compared
to typical educational content. It's also possible for some content to score high on multiple
metrics yet still be INFERIOR overall if it is pedagogically unsound. Your overall rating should be
holistic, considering the full range of individual metric scores and pedagogical soundness.

For each metric AND the overall rating, provide:
- A score from 0 to 5 (for metrics) or SUPERIOR/ACCEPTABLE/INFERIOR rating (for overall)
- A detailed rationale that MUST include:
  (a) Clear justification and reasoning for the score/rating given, explaining why this specific 
      score was assigned based on the evaluation criteria
  (b) If (1) the score is less than 5, or (2) the rating is less than SUPERIOR: Specific,
      actionable, and concrete Advice on how to improve the score/rating, including what changes
      should be made and what elements should be added, removed, or modified. Omit the Advice
      (including the "**Advice**:" line) if the score is 5 or the rating is SUPERIOR.
- Format the rationale like this, as a markdown string, but NOT inside a markdown code block:
```
**Reasoning**: [Detailed reasoning for the score/rating given]
\\n
**Advice**: [Specific, actionable, and concrete advice on how to improve the score/rating, including
what changes should be made and what elements should be added, removed, or modified; ONLY INCLUDE
THE "**Advice**:" line if the score is less than 5 OR the rating is less than SUPERIOR]
```

Remember to make all evaluations consistent with the curriculum context (if provided) and each other
so that a content creator could act upon your advice to improve the passage without introducing
contradictions. Be strict in your evaluation - reserve high scores for truly excellent passages.
"""
    
    # Extract image URLs from content
    image_urls = extract_image_urls(content)
    
    # Build user content with proper structure for images
    user_content = [
        {"type": "input_text", 
         "text": f"Please evaluate this nonfiction reading passage:\n\n{content}"}
    ]
    
    # Add images using proper vision API format
    for image_url in image_urls:
        user_content.append({"type": "input_image", "image_url": image_url})
        logger.info(f"Added image to evaluation: {image_url}")
        
    try:
        response = await client.responses.parse(
            model="gpt-5",
            input=[
                {"role": "system", "content": evaluation_prompt},
                {"role": "user", "content": user_content}
            ],
            text_format=ReadingEvaluationResult
        )
        
        # Extract the evaluation from the structured response
        for output_item in response.output:
            if output_item.type == "message":
                for content_item in output_item.content:
                    if (content_item.type == "output_text" and 
                        hasattr(content_item, "parsed") and 
                        content_item.parsed is not None):
                        result = content_item.parsed
                        
                        # AI now provides the overall rating directly, no calculation needed
                        return result
        
        # Fallback if parsing fails
        logger.error("Could not parse nonfiction reading passage evaluation results")
        return ReadingEvaluationResult(
            overall=OverallResult(rating=OverallRating.INFERIOR,
                                  rationale="Evaluation parsing failed"),
            reading_level_match=MetricResult(score=0, rationale="Evaluation parsing failed"),
            length_appropriateness=MetricResult(score=0, rationale="Evaluation parsing failed"),
            topic_focus=MetricResult(score=0, rationale="Evaluation parsing failed"),
            engagement=MetricResult(score=0, rationale="Evaluation parsing failed"),
            accuracy_and_logic=MetricResult(score=0, rationale="Evaluation parsing failed"),
            question_quality=MetricResult(score=0, rationale="Evaluation parsing failed")
        )
        
    except Exception as e:
        logger.error(f"Error evaluating nonfiction reading passage: {str(e)}")
        return ReadingEvaluationResult(
            overall=OverallResult(rating=OverallRating.INFERIOR,
                                  rationale=f"Evaluation failed: {str(e)}"),
            reading_level_match=MetricResult(score=0, rationale=f"Evaluation failed: {str(e)}"),
            length_appropriateness=MetricResult(score=0, rationale=f"Evaluation failed: {str(e)}"),
            topic_focus=MetricResult(score=0, rationale=f"Evaluation failed: {str(e)}"),
            engagement=MetricResult(score=0, rationale=f"Evaluation failed: {str(e)}"),
            accuracy_and_logic=MetricResult(score=0, rationale=f"Evaluation failed: {str(e)}"),
            question_quality=MetricResult(score=0, rationale=f"Evaluation failed: {str(e)}")
        )


async def evaluate_other(content: str) -> OtherEvaluationResult:
    """
    Evaluate generic educational content across 5 metrics.
    
    Parameters
    ----------
    content : str
        The educational content to evaluate
        
    Returns
    -------
    OtherEvaluationResult
        Evaluation results with scores and rationales for each metric
    """
    logger.info("Evaluating other educational content...")
    
    # Get curriculum context using new extraction method
    curriculum_context = await get_curriculum_context(content)
    
    client = get_async_openai_client(timeout=300.0)
    
    evaluation_prompt = f"""
You are an expert educational evaluator. Evaluate educational content across 
5 key metrics and provide an overall holistic rating. This content doesn't fit the standard 
categories of questions, quizzes, or reading passages, so evaluate it as general educational 
material. Each metric should be scored 0-5 with detailed rationale.
{curriculum_context}

Rate each metric from 0-5. Ensure ALL rationales you provide for all metrics and the overall rating
are consistent with the curriculum context (if provided) and each other so that a content creator
could act upon your advice to improve the content without introducing contradictions.

If any URLs have alt text, read the alt text as part of your assessment, but do NOT guess or infer
what the alt text might contain. It's better to ignore the alt text or its possible content than to
base your assessment on hallucinations or guesses of what the alt text might contain.

**1. Educational Value (0-5)**
Evaluate whether this content provides meaningful learning opportunities and aligns with 
educational goals. Follow this systematic approach:

- **Learning Opportunity Assessment:** Does this content provide meaningful learning opportunities? 
Are the concepts, skills, or knowledge presented genuinely worth learning and educationally
valuable?
- **Standards Alignment:** Does it align with educational goals and standards for its apparent 
subject area and grade level? Does it address important learning objectives?
- **Knowledge Acquisition:** Would students gain valuable understanding, skills, or insights from 
engaging with this content? Does it build upon or connect to existing knowledge?
- **Educational Relevance:** Is the content educationally significant rather than trivial or 
purely entertainment-focused?

Consider these specific factors:
- Does the content **address important educational concepts** or skills?
- Is the **knowledge presented valuable** for student development and learning?
- Does it **align with curriculum standards** and educational objectives?
- Would engagement with this content **meaningfully advance student learning**?

Scoring: 5 = Exceptional educational value, addresses crucial concepts, strong alignment with 
standards; 4 = Good educational value with clear learning benefits; 3 = Moderate educational 
value, some useful learning; 2 = Limited educational value, mostly superficial; 1 = Minimal 
educational benefit; 0 = No meaningful educational value

**2. Direct Instruction Alignment (0-5)**
Evaluate how well this content follows standard Direct Instruction pedagogical philosophy and 
methodology. Follow this systematic approach:

- **Structured Learning Sequence:** Does the content follow the classic Direct Instruction 
sequence: (1) Show/Present the concept clearly, (2) Provide worked examples and demonstrations, 
(3) Offer guided practice opportunities, (4) Provide independent practice when appropriate?
- **Clear Communication:** Is information presented with explicit, unambiguous language? Are 
concepts explained directly rather than requiring students to infer or discover them independently?
- **Scaffolding Implementation:** Does the content provide appropriate scaffolding that gradually 
releases responsibility from instructor guidance to student independence? Are supports
systematically reduced as competency increases?
- **Depth of Knowledge Alignment:** Does the content align with appropriate DoK levels?
  • DoK 1: Recall of facts, definitions, procedures with direct instruction
  • DoK 2: Application of skills/concepts with guided practice
  • DoK 3: Strategic thinking with structured problem-solving approaches
  • DoK 4: Extended thinking with systematic inquiry methods
- **Instructional vs. Decorative Elements:** Are visual elements, examples, and activities 
directly instructional and purposeful rather than merely decorative or entertaining?

Consider these specific factors:
- Does the content **explicitly present concepts** before expecting application?
- Are **worked examples provided** to demonstrate proper application of concepts?
- Is there **systematic progression** from guided to independent practice?
- Are **visual and interactive elements instructional** rather than merely decorative?
- Does the content **align with appropriate DoK levels** for systematic learning?

Scoring: 5 = Perfect Direct Instruction alignment with clear sequence, explicit teaching, and 
systematic scaffolding; 4 = Good DI alignment with minor deviations from methodology; 3 = Some 
DI elements but inconsistent application; 2 = Limited DI principles, mostly discovery-based or 
unclear; 1 = Poor alignment with DI methodology; 0 = No evidence of Direct Instruction principles

**3. Content Appropriateness (0-5)**
Evaluate how well this content is suited for its apparent target audience and context. 
Follow this systematic approach:

- **Audience Suitability:** Is the content suitable for its apparent target audience? Does the 
complexity, topics, and approach match the intended learners?
- **Difficulty Alignment:** Is the difficulty level appropriate for the intended learners? 
Neither too advanced nor too simplistic?
- **Relevance and Relatability:** Are topics, examples, and references relevant and relatable 
to the target audience? Do they connect to students' experiences and interests?
- **Bias and Appropriateness:** Does it avoid bias, stereotypes, or inappropriate material? 
Is content respectful and inclusive?
- **Scope Appropriateness:** Is the scope appropriate - neither too broad to be superficial 
nor too narrow to be useful?

Consider these specific factors:
- Does the **complexity match the target audience's** capabilities and knowledge level?
- Are **examples and references** relevant and accessible to intended learners?
- Does the content **avoid bias or inappropriate** material while being inclusive?
- Is the **scope well-balanced** for meaningful learning without overwhelming?

Scoring: 5 = Perfect appropriateness for target audience, excellent relevance and scope; 
4 = Good appropriateness with minor issues; 3 = Adequate appropriateness but some mismatches; 
2 = Poor appropriateness with significant issues; 1 = Largely inappropriate for audience; 
0 = Completely inappropriate or unsuitable

**4. Clarity & Organization (0-5)**
Evaluate how well-structured, clear, and organized this content is for effective learning. 
Follow this systematic approach:

- **Structural Organization:** Is the content well-structured and easy to follow? Does it have 
clear organization that supports understanding?
- **Explanation Clarity:** Are explanations clear, understandable, and accessible? Do they 
communicate concepts effectively?
- **Logical Flow:** Is there logical flow from one idea to the next? Do transitions make sense 
and support comprehension?
- **Key Point Emphasis:** Are key points emphasized appropriately? Do important concepts receive 
adequate attention and highlighting?
- **Complexity Management:** Does it avoid unnecessary complexity or confusion? Is information 
presented as simply as possible while remaining accurate?

Consider these specific factors:
- Is the **structure clear and logical** with good organization throughout?
- Are **explanations accessible** and easy to understand for the target audience?
- Does the content **flow logically** with smooth transitions between ideas?
- Are **important points highlighted** and given appropriate emphasis?

Scoring: 5 = Exceptionally clear and well-organized, excellent flow and structure; 4 = Good 
clarity and organization with minor issues; 3 = Adequate clarity but some organizational 
problems; 2 = Poor clarity with confusing organization; 1 = Very unclear and poorly organized; 
0 = Incomprehensible or completely disorganized

**5. Engagement (0-5)**
Evaluate how engaging, interesting, and motivating this content is for learners. Follow this 
systematic approach:

- **Interest and Motivation:** Would learners find this content interesting and motivating? 
Does it capture and maintain attention effectively?
- **Presentation Variety:** Does it use varied presentation methods, activities, or approaches 
to maintain attention and accommodate different preferences?
- **Engaging Elements:** Are examples, activities, illustrations, or interactive elements 
engaging and relevant? Do they enhance rather than distract from learning?
- **Active Participation:** Does it encourage active participation, thinking, or engagement 
rather than passive consumption?
- **Continued Interest:** Would students want to continue learning about this topic after 
engaging with this content? Does it spark curiosity?

Consider these specific factors:
- Would students find this content **interesting and want to engage** with it?
- Does it use **varied approaches** to maintain attention and interest?
- Are **examples and activities engaging** and relevant to learners?
- Does it **encourage active thinking** and participation rather than passive reading?

Scoring: 5 = Highly engaging, motivating, uses varied approaches effectively; 4 = Good 
engagement with effective interest-building; 3 = Moderate engagement but could be more 
compelling; 2 = Limited engagement, somewhat dry or uninteresting; 1 = Poor engagement, 
likely to lose student interest; 0 = No engaging elements, completely uninteresting

**OVERALL RATING**
After considering all individual metrics, provide a holistic overall rating by comparing this
educational content to the best available similar high-quality educational content that is
typically available. While your overall rating is independent of the individual metric scores, your
rating should be consistent with the individual metric scores and based on the curriculum context
(if available). In particular, do not suggest making changes to the content that are not consistent
with the individual metric rationales or the curriculum context.

- **SUPERIOR**: Better than typical high-quality educational content relative to the curriculum
context if provided, or otherwise general pedagogical principles in the absence of curriculum
context. Exceptional design, engagement, and educational value that exceeds what is commonly
available.
- **ACCEPTABLE**: Comparable to typical high-quality educational content relative to the
curriculum context if provided, or otherwise general pedagogical principles in the absence of
curriculum context. Good educational value that meets the standard expected from quality
educational materials.
- **INFERIOR**: Worse than typical high-quality educational content relative to the curriculum
context if provided, or otherwise general pedagogical principles in the absence of curriculum
context. Falls short of the quality expected from good educational materials.

Note: It's possible for content to have low scores on some individual metrics but still be 
ACCEPTABLE or even SUPERIOR if it excels overall in ways that make it particularly valuable compared
to typical educational content. It's also possible for some content to score high on multiple
metrics yet still be INFERIOR overall if it is pedagogically unsound. Your overall rating should be
holistic, considering the full range of individual metric scores and pedagogical soundness.

For each metric AND the overall rating, provide:
- A score from 0 to 5 (for metrics) or SUPERIOR/ACCEPTABLE/INFERIOR rating (for overall)
- A detailed rationale that MUST include:
  (a) Clear justification and reasoning for the score/rating given, explaining why this specific 
      score was assigned based on the evaluation criteria
  (b) If (1) the score is less than 5, or (2) the rating is less than SUPERIOR: Specific,
      actionable, and concrete Advice on how to improve the score/rating, including what changes
      should be made and what elements should be added, removed, or modified. Omit the Advice
      (including the "**Advice**:" line) if the score is 5 or the rating is SUPERIOR.
- Format the rationale like this, as a markdown string, but NOT inside a markdown code block:
```
**Reasoning**: [Detailed reasoning for the score/rating given]
\\n
**Advice**: [Specific, actionable, and concrete advice on how to improve the score/rating, including
what changes should be made and what elements should be added, removed, or modified; ONLY INCLUDE
THE "**Advice**:" line if the score is less than 5 OR the rating is less than SUPERIOR]
```

Remember to make all evaluations consistent with the curriculum context (if provided) and each other
so that a content creator could act upon your advice to improve the content without introducing
contradictions. Be strict in your evaluation - reserve high scores for truly excellent educational
content.
"""
    
    # Extract image URLs from content
    image_urls = extract_image_urls(content)
    
    # Build user content with proper structure for images
    user_content = [
        {"type": "input_text", 
         "text": f"Please evaluate this educational content:\n\n{content}"}
    ]
    
    # Add images using proper vision API format
    for image_url in image_urls:
        user_content.append({"type": "input_image", "image_url": image_url})
        logger.info(f"Added image to evaluation: {image_url}")
        
    start_time = time.time()
    
    try:
        response = await client.responses.parse(
            model="gpt-5",
            input=[
                {"role": "system", "content": evaluation_prompt},
                {"role": "user", "content": user_content}
            ],
            text_format=OtherEvaluationResult
        )
        logger.info(f"Other content evaluation completed in {time.time() - start_time} seconds")
        
        # Extract the evaluation from the structured response
        for output_item in response.output:
            if output_item.type == "message":
                for content_item in output_item.content:
                    if (content_item.type == "output_text" and 
                        hasattr(content_item, "parsed") and 
                        content_item.parsed is not None):
                        result = content_item.parsed
                        
                        # AI now provides the overall rating directly, no calculation needed
                        return result
        
        # Fallback if parsing fails
        logger.error("Could not parse other content evaluation results")
        return OtherEvaluationResult(
            overall=OverallResult(rating=OverallRating.INFERIOR,
                                  rationale="Evaluation parsing failed"),
            educational_value=MetricResult(score=0, rationale="Evaluation parsing failed"),
            direct_instruction_alignment=MetricResult(score=0,
                                                      rationale="Evaluation parsing failed"),
            content_appropriateness=MetricResult(score=0, rationale="Evaluation parsing failed"),
            clarity_and_organization=MetricResult(score=0, rationale="Evaluation parsing failed"),
            engagement=MetricResult(score=0, rationale="Evaluation parsing failed")
        )
        
    except Exception as e:
        logger.error(f"Error evaluating other content: {str(e)}")
        return OtherEvaluationResult(
            overall=OverallResult(rating=OverallRating.INFERIOR,
                                  rationale=f"Evaluation failed: {str(e)}"),
            educational_value=MetricResult(score=0, rationale=f"Evaluation failed: {str(e)}"),
            direct_instruction_alignment=MetricResult(score=0,
                                                      rationale=f"Evaluation failed: {str(e)}"),
            content_appropriateness=MetricResult(score=0, rationale=f"Evaluation failed: {str(e)}"),
            clarity_and_organization=MetricResult(score=0,
                                                  rationale=f"Evaluation failed: {str(e)}"),
            engagement=MetricResult(score=0, rationale=f"Evaluation failed: {str(e)}")
        )


async def comprehensive_evaluate(content: str) -> str:
    """
    Comprehensive two-step evaluation: classify content type, then evaluate accordingly.
    Returns JSON string with new evaluation format.
    
    Parameters
    ----------
    content : str
        The educational content to evaluate
        
    Returns
    -------
    str
        JSON string containing evaluation results specific to the content type
    """
    start_time = time.time()
    # Step 1: Classify content
    content_type = await classify_content(content)
    logger.info(f"Content classified as: {content_type.value}")
    
    # Step 2: Route to appropriate evaluator and return JSON
    if content_type == ContentType.QUESTION:
        result = await evaluate_question(content)
    elif content_type == ContentType.QUIZ:
        result = await evaluate_quiz(content)
    elif content_type == ContentType.READING_FICTION:
        result = await evaluate_reading_passage(content, is_fiction=True)
    elif content_type == ContentType.READING_NONFICTION:
        result = await evaluate_reading_passage(content, is_fiction=False)
    else:  # ContentType.OTHER
        result = await evaluate_other(content)
    duration = time.time() - start_time
    logger.info(f"Evaluation complete in {duration}s. Overall rating: {result.overall.rating}")
    return result.to_json()


async def comprehensive_evaluate_object(content: str) -> Union[QuestionEvaluationResult,
QuizEvaluationResult, ReadingEvaluationResult, OtherEvaluationResult]:
    """
    Comprehensive evaluation that returns Pydantic objects for programmatic use.
    
    Parameters
    ----------
    content : str
        The educational content to evaluate
        
    Returns
    -------
    Union[QuestionEvaluationResult, QuizEvaluationResult, ReadingEvaluationResult,
    OtherEvaluationResult]
        Evaluation results specific to the content type as Pydantic objects
    """
    # Step 1: Classify content
    content_type = await classify_content(content)
    logger.info(f"Content classified as: {content_type.value}")
    
    # Step 2: Route to appropriate evaluator
    if content_type == ContentType.QUESTION:
        return await evaluate_question(content)
    elif content_type == ContentType.QUIZ:
        return await evaluate_quiz(content)
    elif content_type == ContentType.READING_FICTION:
        return await evaluate_reading_passage(content, is_fiction=True)
    elif content_type == ContentType.READING_NONFICTION:
        return await evaluate_reading_passage(content, is_fiction=False)
    else:  # ContentType.OTHER
        return await evaluate_other(content)
