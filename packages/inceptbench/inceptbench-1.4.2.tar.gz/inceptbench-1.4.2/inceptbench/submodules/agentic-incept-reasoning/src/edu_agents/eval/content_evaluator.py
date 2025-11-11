from __future__ import annotations

import asyncio
import json
import logging
import textwrap
import time
from enum import Enum

from pydantic import BaseModel

from edu_agents.core.api_key_manager import get_openai_client

logger = logging.getLogger(__name__)

guidance = textwrap.dedent("""
### Curriculum Alignment
- **Matches the standard**: The question should directly align with one or more grade-level
standards. It does not need to state the standard explicitly -- you should just check that it does
align with an appropriate standard.
- **Appropriate difficulty**: The question should reflect the complexity and skill expectations of
the grade.
- **Focus on key concepts**: The question avoids trivia or peripheral content; it focuses on
concepts central to mastery.

### Cognitive Demand
- **Conforms to specific DOK level**: If the question was supposed to be at a specified DOK level,
it is at that level. If no level is specified, infer the DOK level from the difficulty of the
question: easy=DOK 1, medium=DOK 2, hard=DOK 3 or higher. If, even after looking at difficulty, you
cannot infer a DOK level, assume the question should be at Level 2.
- **Depth of Knowledge (DOK)**:
    - **Level 1**: Recall (e.g., 6 x 4 = 24)
    - **Level 2**: Skill/Concept (e.g., solve a simple word problem)
    - **Level 3**: Strategic Thinking (e.g., create a bar graph from a data set)
- **Avoid rote-only questions** unless they are part of building fluency.

### Accuracy and Rigor
- **Accuracy**: All numbers, operations, logic, details, and answer options in the question are
correct and consistent.
- **Correctness**: The answer that is indicated as correct is indeed correct, verified by explicit,
separate calculations or reasoning you performed that prove it is the genuine correct answer. Don't
assume the indicated correct answer is correct. Be skeptical and evaluate it yourself from first
principles.

### Variety
- **Breadth of coverage**: Questions cover the full breadth of the curriculum, including all skills
and misconceptions.
- **Breadth of content**: Questions do not overly repeat the same structures or answer choices.
- **Does not apply to single questions**: This criterion is not applicable to single questions. If
you are only given a single question, give the rating of PASS.

### Image Quality
- **Use of images**: If the question would have benefited from images but did not contain any, it
must receive a FAIL rating.
- **Correctness**: Images are correct and free of logical errors.
- **Consistency**: Images included in the question are consistent with associated text.
- **Interpretability**: Images are not ambiguous or confusing.
- **Fidelity**: The content of the image is clear, centered, easy to read and understand, and
contains no elements which are cut off or overflow the edge of the image.
- **Simplicity**: Images included in the question enhance understanding of the question and do not
distract.
- **Grade-level appropriate**: Images included in the question are stylistically appropriate for a
typical student in the target grade.
- **Subdivision of Objects**: If the expected description includes subdivisions of objects (e.g., a
circle or number line divided into X sections), the correct number of subdivisions should be shown
in the image.
- **Placement of Special Markers**: If the expected description includes special markers (e.g.,
arrows, labels, ticks, etc.), these markers should be placed in a way that is not likely to confuse
students. For example, tick marks indicating the sides of a geometric shape are equal in length
should be placed centered and perpendicular to those sides of the shape. In another example,
right-angle markers should be placed at the right angle of a geometric shape and form a perfect
square with the right angle.
- **Label Placement**: Labels in the image should be consistently placed across all objects in the
image. Labels should be placed logically, for example centered on the object they are labeling or
just outside the object they are labeling (provided all labels are placed in the same way).
- **Centroid Object Alignment**: Centroids of objects in the image should be aligned consistently
across the image. For example, if the expected description indicates a particular grid alignment or
the image is visuallylaid out in an implied grid, the image should show that alignment precisely
relative to the centroids of objects in the image.
- **Color Use**: Unless intentionally specified in the expected description, the image should not
be black and white. It should use color to help students understand the content and make it more
engaging.
- **Hyperlinks accepted**: Using hyperlinks to images is completely acceptable. Do not penalize a
question for including hyperlinks to an images.
- **Review the actual image**: If the question includes an image, review the actual image to ensure
it is of high quality and is consistent with the associated text. If the image is provided as a URL,
download the image and review it.

### Reveals Misconceptions
- **Misconception-Driven**: The question is designed to reveal misconceptions and inform
instruction, either in its construction or by asking students to explain their reasoning.
- **Actionable**: Possible incorrect answers to a question should reveal understanding or
misconceptions to inform instruction.
- **Applicability on Open-Ended Questions**: Some open-ended questions, such as fill-in-the-blank or
short answer questions, don't provide obvious opportunities to reveal misconceptions. For these
questions, assess this criterion based on whether an incorrect answer provides a clear opportunity
to reveal some misconception related to the topic, not necessarily a specific misconceptition.
- **Diagnostic power**: Questions should assess both conceptual and procedural understanding. A
question that merely tests if a student can generate the correct answer should receive a FAIL
rating, unless the question is an open-ended question that provides a clear opportunity to reveal
general misconceptions even if the student does not provide a specific misconceptition.

### Question Type Appropriateness
- **Multiple Choice**:
    - One correct answer only
    - Plausible distractors
    - Avoids "all of the above"/"none of the above"
- **Open-ended**:
    - Encourags student reasoning and explanation
- **Visual**:
    - Clear, accurate diagrams (especially for geometry/fractions)

### Engagement and Relevance
- **Relatable context**: The question uses everyday or familiar settings.
- **Motivating framing**: The question is presented in a relatable way.
- **Avoids unnecessary complexity**: The question does not pursue engagement at the expense of
clarity or relatability.

### Instructional Support
- **Instructional guidance**: The question provides clear and specific guidance for teachers or
students, indicating the correct answer, how to solve the problem, and how to address incorrect
answers.
- **Clear rubric**: Especially for open-ended responses.
- **Feedback-ready**: The question enables teachers or systems to explain what was correct or
incorrect and why for students who struggle with the question's topic.
- **No extended depth requirement**: It is not required to provide extended instructional support,
additional activities, or deeper exploration of related concepts. Do not penalize a question for not
providing extended instructional support beyond the intended topic of the question.

### Clarity and Accessibility
- **Clear language**: The question uses age-appropriate vocabulary with no ambiguity.
- **Simple structure**: Especially for struggling readers, the question should not include
grammatical clutter.
- **Avoid bias**: The question uses inclusive names, situations, and references. Images use
alt-text.""")

system_prompt = textwrap.dedent(f"""
You are an education expert tasked with evaluating the quality of educational content, providing
both a rating and your reasoning. Your evaluation consists of two parts:

## 1. Guidance-based Evaluation
Evaluate the content against the Provided Guidance. Rate each Provided Guidance category
independently, providing a PASS or FAIL based on whether the content COMPLETELY meets the Provided
Guidance category or not. Do not give questions "the benefit of the doubt" when assessing whether
they meet the Provided Guidance. PASS or FAIL should always be upper-cased.

Here is the Provided Guidance:

{guidance}

## 2. Overall Assessment
An Overall Assessment of the quality of the content relative to the highest quality content
typically available for the given content type, **independent of the Provided Guidance**. Your
rating MUST be one of three categories:

  - **SUPERIOR**: The content is superior to the highest quality content typically available.
  - **ACCEPTABLE**: The content is comparable to the highest quality content typically available.
  - **INFERIOR**: The content is inferior to the highest quality content typically available.

Be strict with your Overall Assessment, comparing the content to the best examples of the content
type available. Keep your standards high. Content must be better than the highest quality content
readily available to receive a SUPERIOR rating. Content that is easily replaced with readily
available higher quality examples should receive an INFERIOR rating. Content with 4 or more Provided
Guidance failures should receive an INFERIOR rating (although otherwise the overall rating should
not be based on the Provided Guidance). You should never reference the Provided Guidance in your
Overall Assessment. The Overall Assessment rating should always be upper-cased.

## Instructions
The user will send you a markdown document and no other instructions. Your job is to evaluate the
content and provide an overall rating and a detailed rationale for your rating. If the markdown
document contains URLs, be sure to download the content of the URL and examine it when evaluating
the content.
""")

class PassFailRating(Enum):
    PASS = "PASS"
    FAIL = "FAIL"

class PassFailResult(BaseModel):
    result: str
    reason: str

class ComparisonRating(Enum):
    SUPERIOR = "SUPERIOR"
    ACCEPTABLE = "ACCEPTABLE"
    INFERIOR = "INFERIOR"

class ComparisonResult(BaseModel):
    result: str
    reason: str

class EvaluationResult(BaseModel):
    overall: ComparisonResult
    curriculum_alignment: PassFailResult
    cognitive_demand: PassFailResult
    accuracy_and_rigor: PassFailResult
    variety: PassFailResult
    image_quality: PassFailResult
    reveals_misconceptions: PassFailResult
    question_type_appropriateness: PassFailResult
    engagement_and_relevance: PassFailResult
    instructional_support: PassFailResult
    clarity_and_accessibility: PassFailResult

async def evaluate_content(content: str) -> str:
    """
    Evaluates educational content using OpenAI's o4-mini model.
    
    Parameters
    ----------
    content : str
        The markdown content to evaluate
        
    Returns
    -------
    str
        The evaluation response from the model as a JSON string
    """
    logger.info(f"Evaluating content: {content[:50]}...")
    
    def _sync_evaluate_with_retry():
        """Synchronous function to call OpenAI API with retry logic"""
        max_retries = 2
        
        for attempt in range(max_retries + 1):
            try:
                client = get_openai_client(timeout=300.0)  # 5 minutes timeout for evaluation calls
                
                # Use the responses.parse API for structured output with o4-mini
                response = client.responses.parse(
                    model="o3",
                    input=[
                        {"role": "developer", "content": system_prompt},
                        {"role": "user", "content": content}
                    ],
                    text_format=EvaluationResult
                )
                return response
                
            except Exception as e:
                attempt_num = attempt + 1
                logger.warning(
                    f"Error in evaluation (attempt {attempt_num}/{max_retries + 1}): "
                    f"{type(e).__name__}: {str(e)}"
                )
                
                if attempt < max_retries:
                    backoff_time = min(2 ** attempt, 10)  # Exponential backoff, max 10 seconds
                    logger.info(
                        f"Evaluation waiting {backoff_time}s before retry {attempt_num + 1}"
                    )
                    time.sleep(backoff_time)
                else:
                    logger.error(f"Evaluation failed after {max_retries + 1} attempts")
                    raise
    
    try:
        # Run the OpenAI call in a thread pool to avoid blocking the event loop
        response = await asyncio.get_event_loop().run_in_executor(None, _sync_evaluate_with_retry)
        
        # Process the structured response
        for output_item in response.output:
            if output_item.type == "message":
                # Look for parsed data in the message content
                for content_item in output_item.content:
                    if (content_item.type == "output_text" and 
                        hasattr(content_item, "parsed") and 
                        content_item.parsed is not None):
                        
                        if hasattr(content_item, "text") and content_item.text:
                            try:
                                return content_item.text
                            except Exception as text_error:
                                logger.warning(
                                    f"Error using text representation: {str(text_error)}"
                                )
                                # Continue to try other methods
                        
                        # Manual conversion of the parsed object to handle enums
                        try:
                            # Convert parsed object to dict and stringify enum values
                            parsed_dict = content_item.parsed.model_dump()
                            
                            # Handle the overall result enum
                            if "overall" in parsed_dict and "result" in parsed_dict["overall"]:
                                parsed_dict["overall"]["result"] = parsed_dict["overall"] \
                                                                    ["result"].value
                            
                            # Handle each category's result enum
                            for category in ["curriculum_alignment", "cognitive_demand",
                            "accuracy_and_rigor", "variety", "image_quality",
                            "reveals_misconceptions", "question_type_appropriateness",
                            "engagement_and_relevance", "instructional_support",
                            "clarity_and_accessibility"]:
                                if category in parsed_dict and "result" in parsed_dict[category]:
                                    parsed_dict[category]["result"] = parsed_dict[category]\
                                                                        ["result"].value
                            
                            return json.dumps(parsed_dict)
                        except Exception as enum_error:
                            logger.warning(f"Error handling enum serialization: {str(enum_error)}")
                            # Continue to try other methods
                
                # Fallback to the raw text if parsed object not available but text is
                for content_item in output_item.content:
                    if content_item.type == "output_text" and hasattr(content_item, "text"):
                        try:
                            # Just return the text which should be properly formatted JSON
                            return content_item.text
                        except Exception as text_error:
                            logger.warning(f"Error using text: {str(text_error)}")
                            return json.dumps({"error": "Could not parse structured output"})
        
        # If we can't find anything, return an error
        logger.error("Could not extract evaluation from response")
        return json.dumps({"error": "Could not extract evaluation results"})
        
    except Exception as e:
        logger.error(f"Error evaluating content: {str(e)}")
        return json.dumps({"error": f"Evaluation failed: {str(e)}"})
