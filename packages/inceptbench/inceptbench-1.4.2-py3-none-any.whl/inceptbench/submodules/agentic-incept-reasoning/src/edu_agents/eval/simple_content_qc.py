from __future__ import annotations

import asyncio
import base64
import json
import logging
import os
import time
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple

import aiohttp
import markdown
from anthropic import AsyncAnthropic
from google import genai
from google.genai import types
from pydantic import BaseModel

from edu_agents.core.api_key_manager import get_async_openai_client

logger = logging.getLogger(__name__)

# Global constant to gate the simple QC process
ENABLE_SIMPLE_QC = True

# Screenshot service configuration
SCREENSHOT_SERVICE_URL = "http://127.0.0.1:8001"
SCREENSHOT_TIMEOUT = 30  # seconds
GPT_MODEL_PROVIDER = "gpt"
CLAUDE_MODEL_PROVIDER = "claude"
GEMINI_MODEL_PROVIDER = "gemini"
QC_MODEL_PROVIDER = CLAUDE_MODEL_PROVIDER
GPT_REASONING_EFFORT = "medium"

# Base system prompt shared across all model providers
QC_BASE_SYSTEM_PROMPT = """You are an expert educational content quality assessor. Evaluate a
screenshot for student suitability.

IMPORTANT: You must complete ALL analysis steps thoroughly BEFORE making any pass/fail
determination.
Do NOT decide whether content passes or fails until you have completed your full analysis.

Follow this procedure systematically:
1) Extract key quantitative facts from the screenshot's TEXT (numbers, units, labels).
2) Count relevant objects in the screenshot's image, if present (discrete items only; do not infer
hidden or cut-off ones).
    - **SYSTEMATIC OBJECT ENUMERATION REQUIRED**: For each type of object that should have a
    specific count:
      * ENUMERATE each individual object (e.g., "Table 1: plate 1, plate 2, plate 3, plate 4,
      plate 5")
      * LIST the location/position of each object as you count it
      * PROVIDE the total count only after individual enumeration
      * If objects are grouped (e.g., plates on tables), enumerate within each group separately
    - Count objects VERY CAREFULLY - verify each count multiple times
    - If the image contains multiple groups of objects (e.g., shelves with items on them),
    count both the number of groups (e.g., shelves) and the number of items in each group
    individually (e.g., count the items on EACH shelf INDIVIDUALLY).
    - If the screenshot does not contain an image, do not penalize for the lack of image
    UNLESS the text explicitly references an image that should have been present.
3) **VISUAL CLARITY AND PEDAGOGICAL APPROPRIATENESS CHECK**:
    - Are there any floating, disconnected, or unnatural visual elements that would confuse
      students?
    - Are objects positioned in ways that make pedagogical sense or would they cause confusion?
    - Would a grade-level student be able to clearly understand what the image depicts without
    confusion?
    - Are there redundant or contradictory visual representations of the same concept?
    - Does the image have a single, cohesive visual narrative or is it a confusing amalgamation?
    **CRITICAL**: Any floating objects, unnatural positioning, redundant representations, or
    visually confusing elements are BLOCKING issues.
4) Compute any implied results from the text (e.g., groups X items per group) and,
separately, any implied results from the image counts. Perform the any required calculations,
using code (if available) to ensure accuracy. Any math errors are blocking.
5) Compare text vs image. If they conflict in a way that could mislead a student, note the
mismatch. Any such issues are blocking.
    - As long as the content properly contextualizes the image, it is not a blocking issue
    if the image does not illustrate the entire content. For example, if the content is a
    problem about a group of 4 items, the image shows 1 example item, and the content
    properly contextualizes the image as 1 example of the 4 items, it is not a blocking
    issue.
    - The image only needs to reflect the present state of the content as described in the
    text. Do not penalize for images that do not reflect a future state as described in the
    text. For example, if the content says: "The image shows 3 empty baskets. The teacher
    plans to put 3 balls in each basket. How many balls does the teacher neeed?", the image
    is a correct if the baskets are empty, but incorrect if the baskets have 3 balls in them.
    Empty baskets are correct because the question says the image should show empty baskets.
    The image is incorrect if the baskets have 3 balls in them because the teacher has not
    yet put the balls in the baskets.
6) Look for any unrendered LaTeX anywhere within the text in the image (e.g., "\\div",
"\\\\times", "\\(", "\\[", "\\frac", etc.). Any occurances of unrendered LaTeX are blocking
issues.
7) Do not penalize for incorrect answer choices being correct. Do not penalize for Personalized
Academic Insights including incorrect answer choices or possibilities for answers that are in
fact incorrect.
8) **QUESTION TYPE IDENTIFICATION**: Determine if this is a multiple choice question or an 
open response/fill-in-the-blank question:
   - Multiple choice questions have explicit answer options (A, B, C, D or 1, 2, 3, 4, etc.)
   - Open response/fill-in-the-blank questions ask students to calculate, write, or fill in 
     answers without providing multiple choice options
   - This affects how strictly to evaluate Personalized Academic Insights (see decision rules)

CRITICAL: Only after completing ALL the above analysis steps should you determine whether
the content passes or fails. Base your final determination solely on whether blocking issues
were found during your systematic analysis.

The following are examples of blocking issues:
- Any unrendered LaTeX anywhere within the text in the image (e.g., "\\div", "\\\\times", "\\(",
"\\[", "\\frac", etc.)
- Any math errors (EXCEPT for mathematical errors in Personalized Academic Insights for 
open response/fill-in-the-blank questions - see non-blocking issues below)
- Any conflicts between the text and image
- **VISUAL CLARITY AND PEDAGOGICAL ISSUES**:
  - Floating, disconnected, or unnatural visual elements (e.g., objects suspended in air that
  wouldn't be suspended in reality [e.g., a floating apple is bad, but a floating balloon is okay])
  - Redundant visual representations that create confusion (e.g., showing the same objects both
  floating above AND inside containers)
  - Objects positioned in unnatural or confusing ways
  - Images that would confuse grade-level students rather than help them learn
  - Visually incoherent or amalgamated images that lack a single clear narrative
  - Incorrect object counts (verify counts carefully - don't accept "approximately" when exact
  counts are specified)
- Appropriateness of content for students
- Rendering issues
- Poor readability
- Difficulty in understanding the content for grade-level students
- Excessive wordiness
- Question details which are unrelated to answering the core question
- Confusing content that is not an intentional aspect of instruction
    - Examine Solution Steps and Personalized Academic Insights to determine if possible
    confusion is actually intentional
    - For example, 3rd grade students learning about multiplication learn rules about how to
    intepret multiplication problems as grouping statements. Within this context, the
    equations "4 x 3 = 12" and "3 x 4 = 12" are NOT both correct (even though they are
    mathematically equivalent) because they are NOT equivalent within the context of the problem
    and the 3rd grade math curriculum (3rd grade students learn multiplication as "N groups of 
    M objects" so N x M and M x N are NOT the same thing).
- Lack of clear correspondance between items in an image and the relevant text
- Any other issues which would cause an educator to not want to give the content to students

The following are examples of non-blocking issues, which should be noted but not lead to a
FAIL on their own:
- Minor differences in similar objects in an image. For example, if an image is supposed to
contain 6 gift bags, and does contain 6 similar bags but one is missing a ribbon or is slightly
different in ways that do not affect the student's ability to answer the question, this is not
a blocking issue.
- Using characters with a similar visual appearance as mathematical symbols (e.g., using "x"
instead of "×").
- Concerns about how the Grading Rubric scores responses
- Minor issues in Personalized Academic Insights
- Incorrect answer choices in a multiple choice question being incorrect
- Personalized Academic Insights describing incorrect answer choices or possibilities for answers
that are in fact incorrect, no matter why they are incorrect as long as the explanation is plausible
- For fill-in-the-blank or other open response questions, poor choice of Personalized
Academic Insights, INCLUDING mathematical errors in the Personalized Academic Insights
section (since students will receive runtime feedback from the teaching system rather
than relying solely on the pre-written insights)
- Any other issues which are not blocking, but should be noted

Decision rule:
- PASS only if there are no blocking issues.
- FAIL if there is at least one blocking issue.
- IMPORTANT: For open response/fill-in-the-blank questions, mathematical errors in the 
  Personalized Academic Insights section are NOT blocking issues. Only fail these questions 
  for mathematical errors in the core problem statement, solution steps, or grading rubric.

Be concise. Prefer concrete evidence (exact counts/numbers) over generalities."""

# Model-specific prompt additions
QC_GEMINI_JSON_INSTRUCTIONS = """

You must respond with a JSON object containing the following fields:
- "passed": boolean indicating if content passes quality assessment
- "reason": detailed explanation of the assessment
- "mismatch": boolean indicating whether there's a text-image mismatch
- "confidence": float from 0.0-1.0 indicating assessment confidence
- "evidence": object with structured evidence collection:
  - "text_numbers": array of strings - all numbers/quantities extracted from the text
  - "image_counts": array of strings - all object counts observed in the image  
  - "computed_from_text": string or null - any calculations performed using numbers from text
  - "computed_from_image": string or null - any calculations performed using counts from image
- "issues": array of issue objects, each containing:
  - "type": string from ["image_text_mismatch", "factual_error", "rendering_error", "readability",
  "layout", "inappropriate_content", "missing_elements", "malformed_latex", "incorrect_math",
  "missing_solution_steps", "confusing_content", "lack_of_clear_correspondence", 
  "visual_clarity_pedagogical", "other_issues"]
  - "severity": string from ["blocking", "non-blocking"] - whether this issue blocks content
  approval
  - "message": string - detailed description of the issue
  - "remediation": string or null - suggested fix for the issue

CRITICAL: Always populate the evidence fields by explicitly:
1. Extracting all numbers from text into text_numbers array
2. Counting all objects in image into image_counts array  
3. Showing any calculations in computed_from_text and computed_from_image
This separation helps ensure accurate counting and prevents text-image confusion."""

IssueType = Literal[
    "image_text_mismatch",
    "factual_error",
    "rendering_error",
    "readability",
    "layout",
    "inappropriate_content",
    "missing_elements",
    "malformed_latex",
    "incorrect_math",
    "missing_solution_steps",
    "confusing_content",
    "lack_of_clear_correspondence",
    "visual_clarity_pedagogical",
    "other_issues"
]

Severity = Literal["blocking", "non-blocking"]

class Evidence(BaseModel):
    text_numbers: List[str] = []
    image_counts: List[str] = []
    computed_from_text: Optional[str] = None
    computed_from_image: Optional[str] = None

class Issue(BaseModel):
    type: IssueType
    severity: Severity
    message: str
    evidence: Optional[Evidence] = None
    remediation: Optional[str] = None

class SimpleQCResult(BaseModel):
    passed: bool
    reason: str
    mismatch: bool = False
    issues: List[Issue] = []
    confidence: float = 0.5

class SimpleContentQC:
    """Simple content quality checker that renders markdown and uses various AI models."""
    
    def __init__(self):
        # Phase 3: Use async clients
        self.openai_client = get_async_openai_client(timeout=120.0)
        self.anthropic_client = AsyncAnthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        # Gemini doesn't have async SDK yet, will use asyncio.to_thread()
        self.gemini_client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    
    def _render_markdown_to_html(self, markdown_content: str) -> str:
        """
        Convert markdown content to well-styled HTML with LaTeX and image support.
        
        Parameters
        ----------
        markdown_content : str
            Markdown content to render
            
        Returns
        -------
        str
            Complete HTML document ready for screenshot
        """
        # Convert markdown to HTML with extensions
        html_content = markdown.markdown(
            markdown_content,
            extensions=[
                'tables',           # Table support
                'fenced_code',      # Code block support
                'attr_list',        # Attribute lists
                'def_list',         # Definition lists
                'footnotes',        # Footnotes
                'toc'               # Table of contents
            ]
        )
        
        # Create complete HTML document with MathJax and good styling
        html_document = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Content Quality Check</title>
            <!-- MathJax for LaTeX rendering -->
            <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
            <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
            <script>
                window.MathJax = {{
                    tex: {{
                        inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
                        displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
                    }},
                    chtml: {{
                        scale: 1.2
                    }}
                }};
            </script>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
                    Ubuntu, Cantarell, sans-serif;
                    line-height: 1.8;
                    color: #333;
                    max-width: 1000px;
                    margin: 40px auto;
                    padding: 40px;
                    background-color: #ffffff;
                    box-sizing: border-box;
                }}
                
                h1, h2, h3, h4, h5, h6 {{
                    color: #2c3e50;
                    margin: 2rem 0 1rem 0;
                    font-weight: 600;
                    line-height: 1.3;
                }}
                
                h1 {{ font-size: 2.5rem; border-bottom: 3px solid #3498db; padding-bottom: 0.5rem;}}
                h2 {{ font-size: 2rem; border-bottom: 2px solid #95a5a6; padding-bottom: 0.3rem; }}
                h3 {{ font-size: 1.5rem; }}
                h4 {{ font-size: 1.25rem; }}
                
                p {{
                    margin: 1.2rem 0;
                    font-size: 1.1rem;
                }}
                
                ul, ol {{
                    margin: 1.2rem 0;
                    padding-left: 2rem;
                }}
                
                li {{
                    margin: 0.6rem 0;
                    font-size: 1.1rem;
                }}
                
                blockquote {{
                    border-left: 4px solid #3498db;
                    margin: 1.5rem 0;
                    padding: 1rem 1.5rem;
                    background-color: #f8f9fa;
                    font-style: italic;
                    border-radius: 0 6px 6px 0;
                }}
                
                code {{
                    background-color: #f1f3f4;
                    padding: 3px 8px;
                    border-radius: 4px;
                    font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas,
                    'Courier New', monospace;
                    font-size: 0.95em;
                }}
                
                pre {{
                    background-color: #f8f9fa;
                    padding: 1.5rem;
                    border-radius: 8px;
                    overflow-x: auto;
                    border-left: 4px solid #3498db;
                    margin: 1.5rem 0;
                }}
                
                pre code {{
                    background-color: transparent;
                    padding: 0;
                }}
                
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 2rem 0;
                    background-color: white;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                
                th, td {{
                    padding: 12px 16px;
                    text-align: left;
                    border: 1px solid #dee2e6;
                    font-size: 1.05rem;
                }}
                
                th {{
                    background-color: #f8f9fa;
                    font-weight: 600;
                    color: #495057;
                    border-bottom: 2px solid #dee2e6;
                }}
                
                tr:nth-child(even) {{
                    background-color: #f8f9fa;
                }}
                
                img {{
                    max-width: 100%;
                    height: auto;
                    margin: 1.5rem 0;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                    display: block;
                }}
                
                hr {{
                    border: none;
                    height: 2px;
                    background: linear-gradient(to right, #3498db, transparent);
                    margin: 3rem 0;
                }}
                
                /* MathJax styling */
                .MathJax {{
                    font-size: 1.1em !important;
                }}
                
                /* Ensure content is clearly visible for QC */
                * {{
                    box-sizing: border-box;
                }}
                
                /* Add spacing around math expressions */
                mjx-container {{
                    margin: 0.5rem 0;
                }}
                
                mjx-container[display="true"] {{
                    margin: 1rem 0;
                }}
            </style>
        </head>
        <body>
            {html_content}
            
            <script>
                // Ensure all images load before screenshot
                window.addEventListener('load', function() {{
                    const images = document.querySelectorAll('img');
                    let loadedImages = 0;
                    
                    if (images.length === 0) {{
                        document.body.setAttribute('data-ready', 'true');
                        return;
                    }}
                    
                    images.forEach(img => {{
                        if (img.complete) {{
                            loadedImages++;
                        }} else {{
                            img.addEventListener('load', () => {{
                                loadedImages++;
                                if (loadedImages === images.length) {{
                                    document.body.setAttribute('data-ready', 'true');
                                }}
                            }});
                            img.addEventListener('error', () => {{
                                loadedImages++;
                                if (loadedImages === images.length) {{
                                    document.body.setAttribute('data-ready', 'true');
                                }}
                            }});
                        }}
                    }});
                    
                    if (loadedImages === images.length) {{
                        document.body.setAttribute('data-ready', 'true');
                    }}
                }});
                
                // Wait for MathJax to finish rendering
                window.MathJax.startup.promise.then(() => {{
                    if (!document.body.hasAttribute('data-ready')) {{
                        // Check if we're still waiting for images
                        const images = document.querySelectorAll('img');
                        if (images.length === 0) {{
                            document.body.setAttribute('data-ready', 'true');
                        }}
                    }}
                }});
            </script>
        </body>
        </html>
        """
        
        return html_document
    
    async def _take_screenshot_with_fallback(self, html_content: str) -> Tuple[bytes, bool]:
        """
        Take a screenshot using the Node.js screenshot service with fallback.
        
        Parameters
        ----------
        html_content : str
            Complete HTML document to screenshot
            
        Returns
        -------
        Tuple[bytes, bool]
            (screenshot_data, success) - PNG data and whether screenshot succeeded
        """
        start_time = time.time()
        
        try:
            # Make HTTP request to screenshot service
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=SCREENSHOT_TIMEOUT)
            ) as session:
                payload = {
                    "html": html_content,
                    "width": 1400,
                    "height": 2000,
                    "timeout": 15000  # 15 second timeout for page rendering
                }
                
                logger.debug(f"Requesting screenshot from {SCREENSHOT_SERVICE_URL}/screenshot")
                
                async with session.post(
                    f"{SCREENSHOT_SERVICE_URL}/screenshot",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        screenshot_data = await response.read()
                        elapsed = time.time() - start_time
                        logger.info(f"Screenshot completed successfully in {elapsed:.2f}s "
                                  f"(size: {len(screenshot_data)} bytes)")
                        return screenshot_data, True
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"Screenshot service returned {response.status}: {error_text}")
                        return b"", False
                        
        except aiohttp.ClientTimeout:
            elapsed = time.time() - start_time
            logger.error(f"Screenshot service timeout after {elapsed:.2f}s")
            return b"", False
            
        except aiohttp.ClientConnectorError as e:
            logger.error(f"Cannot connect to screenshot service at {SCREENSHOT_SERVICE_URL}: {e}")
            return b"", False
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Screenshot service error after {elapsed:.2f}s: {e}")
            return b"", False
    
    async def _text_only_quality_check(self, markdown_content: str) -> SimpleQCResult:
        """
        Perform text-only quality check when screenshot is not available.
        
        Parameters
        ----------
        markdown_content : str
            Markdown content to assess
            
        Returns
        -------
        SimpleQCResult
            Quality assessment result based on text analysis only
        """
        try:
            # Defensive check: ensure markdown_content is actually a string, not a coroutine
            if hasattr(markdown_content, '__await__'):
                logger.error("markdown_content is a coroutine, awaiting it")
                markdown_content = await markdown_content
            
            # Basic heuristic checks for text-only QC
            lines = markdown_content.strip().split('\n')
            line_count = len([line for line in lines if line.strip()])
            
            # Check for obvious issues
            issues = []
            
            if line_count < 3:
                issues.append("Content appears too short")
            
            # Check for common markdown syntax issues
            if "$$" in markdown_content and markdown_content.count("$$") % 2 != 0:
                issues.append("Unmatched LaTeX delimiters")
            
            # Check for placeholder text
            placeholder_patterns = ["lorem ipsum", "TODO", "FIXME", "placeholder", "example text"]
            for pattern in placeholder_patterns:
                if pattern.lower() in markdown_content.lower():
                    issues.append(f"Contains placeholder text: '{pattern}'")
            
            # If we have serious issues, use GPT for a more thorough text analysis
            if len(issues) > 0:
                gpt_assessment = await self._assess_text_with_gpt(markdown_content)
                if gpt_assessment:
                    return gpt_assessment
            
            # Basic heuristic result
            passed = len(issues) == 0
            reason = "Text-only QC: " + (
                "Content appears acceptable" if passed 
                else f"Issues found: {', '.join(issues)}"
            )
            
            return SimpleQCResult(
                passed=passed,
                reason=reason,
                mismatch=False,
                confidence=0.6  # Lower confidence for text-only
            )
            
        except Exception as e:
            logger.error(f"Error in text-only quality check: {e}")
            return SimpleQCResult(
                passed=False,
                reason=f"Text-only QC failed: {str(e)}",
                mismatch=False,
                confidence=0.0
            )
    
    async def _assess_text_with_gpt(self, markdown_content: str) -> Optional[SimpleQCResult]:
        """
        Use GPT to assess text-only content when screenshot fails.
        
        Parameters
        ----------
        markdown_content : str
            Markdown content to assess
            
        Returns
        -------
        Optional[SimpleQCResult]
            GPT assessment result or None if GPT call fails
        """
        try:
            prompt = f"""
            Please assess the quality of this educational content (text only, no image available):

            {markdown_content}

            Focus on:
            1. Content completeness and clarity
            2. Proper formatting and structure  
            3. Educational value
            4. Absence of placeholder text
            5. Proper LaTeX/markdown syntax

            Respond with a JSON object containing:
            - "passed": boolean indicating if content meets quality standards
            - "reason": detailed explanation of assessment
            - "confidence": float from 0.0-1.0 indicating assessment confidence
            """

            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                timeout=30
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return SimpleQCResult(
                passed=result.get("passed", False),
                reason=f"Text-only GPT QC: {result.get('reason', 'Assessment completed')}",
                mismatch=False,
                confidence=max(0.0, min(1.0, result.get("confidence", 0.5)))
            )
            
        except Exception as e:
            logger.error(f"GPT text assessment failed: {e}")
            return None
    
    async def _assess_content_quality_single(self, screenshot_data: bytes) -> SimpleQCResult:
        """
        Run a single GPT-5 quality assessment on the content screenshot.
        
        Parameters
        ----------
        screenshot_data : bytes
            PNG screenshot data
            
        Returns
        -------
        SimpleQCResult
            Result of the quality assessment
        """
        # Convert screenshot to base64 for API
        screenshot_b64 = base64.b64encode(screenshot_data).decode('utf-8')
        image_url = f'data:image/png;base64,{screenshot_b64}'

        system_prompt = QC_BASE_SYSTEM_PROMPT

        user_prompt = """Perform a thorough analysis of this educational content screenshot.
        
        First, systematically extract all quantitative information from the text and count all
        relevant objects in the image. Then perform any necessary calculations and check for
        consistency between text and image.
        
        Complete your full analysis before determining whether the content passes or fails.
        Only mark as failed if you find actual blocking issues after completing your analysis."""

        try:
            # Phase 3: Direct async call to OpenAI
            response = await self.openai_client.responses.parse(
                model="gpt-5",
                input=[
                    {"role": "developer", "content": system_prompt},
                    {"role": "user", "content": [
                        {"type": "input_text", "text": user_prompt},
                        {"type": "input_image", "image_url": image_url}
                    ]}
                ],
                text_format=SimpleQCResult,
                reasoning={"effort": GPT_REASONING_EFFORT}
            )
            
            # Extract the structured response
            for output_item in response.output:
                if output_item.type == "message":
                    for content_item in output_item.content:
                        if (content_item.type == "output_text" and 
                            hasattr(content_item, "parsed") and 
                            content_item.parsed is not None):
                            logger.info(f"Simple QC run result: {content_item.parsed}")
                            return content_item.parsed
                        elif (content_item.type == "output_text" and 
                              hasattr(content_item, "text")):
                            # Fallback parsing if structured output fails
                            text_response = content_item.text.strip()
                            if text_response.startswith("PASS"):
                                return SimpleQCResult(
                                    passed=True, 
                                    reason="Content passed quality check",
                                    mismatch=False,
                                    confidence=0.8
                                )
                            elif text_response.startswith("FAIL"):
                                reason = text_response[4:].strip()
                                if reason.startswith(":"):
                                    reason = reason[1:].strip()
                                return SimpleQCResult(
                                    passed=False, 
                                    reason=reason or "Content failed quality check",
                                    mismatch=True,
                                    confidence=0.8
                                )
                            else:
                                return SimpleQCResult(
                                    passed=False, 
                                    reason=f"Unexpected response format: {text_response}",
                                    mismatch=False,
                                    confidence=0.5
                                )
            
            raise RuntimeError("No structured response found in API response")
            
        except Exception as e:
            logger.error(f"Error in GPT-5 quality assessment: {str(e)}")
            # Default to failure on error to be safe
            return SimpleQCResult(
                passed=False, 
                reason=f"Quality assessment failed due to error: {str(e)}",
                mismatch=False,
                confidence=0.0
            )
    
    async def _assess_content_quality_single_claude(self, screenshot_data: bytes) -> SimpleQCResult:
        """
        Run a single Claude quality assessment on the content screenshot.
        
        Parameters
        ----------
        screenshot_data : bytes
            PNG screenshot data
            
        Returns
        -------
        SimpleQCResult
            Result of the quality assessment
        """
        # Convert screenshot to base64 for API
        screenshot_b64 = base64.b64encode(screenshot_data).decode('utf-8')

        system_prompt = QC_BASE_SYSTEM_PROMPT

        user_prompt = """Perform a thorough analysis of this educational content screenshot.
        
        First, systematically extract all quantitative information from the text and count all
        relevant objects in the image. Then perform any necessary calculations and check for
        consistency between text and image.
        
        Complete your full analysis before determining whether the content passes or fails.
        Only mark as failed if you find actual blocking issues after completing your analysis."""

        try:
            # Define the structured output tool with Evidence and Issue tracking
            tools = [
                {
                    "name": "quality_assessment",
                    "description": "Provide a structured assessment of content quality with "
                                   "detailed evidence.",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "analysis": {
                                "type": "string",
                                "description": "Complete step-by-step analysis performed before "
                                "making final determination. Include text extraction, image "
                                "counting, calculations, and consistency checks."
                            },
                            "passed": {
                                "type": "boolean",
                                "description": "Whether the content passes quality assessment "
                                "(determined AFTER completing analysis)"
                            },
                            "reason": {
                                "type": "string",
                                "description": "Concise summary of the final assessment decision "
                                "based on the completed analysis"
                            },
                            "mismatch": {
                                "type": "boolean",
                                "description": "Whether there's a text-image mismatch"
                            },
                            "confidence": {
                                "type": "number",
                                "minimum": 0.0,
                                "maximum": 1.0,
                                "description": "Confidence in the assessment (0.0-1.0)"
                            },
                            "evidence": {
                                "type": "object",
                                "description": "Structured evidence from text and image analysis",
                                "properties": {
                                    "text_numbers": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "List of all numbers/quantities extracted "
                                                       "from the text"
                                    },
                                    "image_counts": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "List of all object counts observed in the "
                                                       "image"
                                    },
                                    "computed_from_text": {
                                        "type": ["string", "null"],
                                        "description": "Any calculations performed using numbers "
                                                       "from text"
                                    },
                                    "computed_from_image": {
                                        "type": ["string", "null"],
                                        "description": "Any calculations performed using counts "
                                                       "from image"
                                    }
                                },
                                "required": ["text_numbers", "image_counts"]
                            },
                            "issues": {
                                "type": "array",
                                "description": "List of specific issues found during assessment",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {
                                            "type": "string",
                                            "enum": ["image_text_mismatch", "factual_error",
                                                    "rendering_error", "readability", "layout",
                                                    "inappropriate_content", "missing_elements",
                                                   "malformed_latex", "incorrect_math",
                                                   "missing_solution_steps", "confusing_content",
                                                   "lack_of_clear_correspondence", 
                                                   "visual_clarity_pedagogical", "other_issues"],
                                            "description": "Type of issue identified"
                                        },
                                        "severity": {
                                            "type": "string",
                                            "enum": ["blocking", "non-blocking"],
                                            "description": "Whether this issue blocks content "
                                                           "approval"
                                        },
                                        "message": {
                                            "type": "string",
                                            "description": "Detailed description of the issue"
                                        },
                                        "remediation": {
                                            "type": ["string", "null"],
                                            "description": "Suggested fix for the issue"
                                        }
                                    },
                                    "required": ["type", "severity", "message"]
                                }
                            }
                        },
                        "required": ["analysis", "passed", "reason", "mismatch", "confidence",
                                    "evidence", "issues"]
                    }
                }
            ]

            message_content = [
                {"type": "text", "text": user_prompt},
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": screenshot_b64
                    }
                }
            ]

            # Phase 3: Direct async call to Anthropic
            response = await self.anthropic_client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=16384,
                system=system_prompt,
                tools=tools,
                tool_choice={"type": "tool", "name": "quality_assessment"},
                messages=[
                    {"role": "user", "content": message_content}
                ]
            )

            # Extract the structured response from tool use
            for content in response.content:
                if content.type == "tool_use" and content.name == "quality_assessment":
                    tool_input = content.input
                    logger.debug(f"Claude tool_input received: {tool_input}")
                    
                    # Parse evidence (handle both object and JSON string cases)
                    evidence_data = tool_input.get("evidence", {})
                    if isinstance(evidence_data, str):
                        try:
                            evidence_data = json.loads(evidence_data)
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse evidence JSON string: {e}")
                            logger.error(f"Raw evidence data: {evidence_data}")
                            evidence_data = {}
                    
                    evidence = Evidence(
                        text_numbers=evidence_data.get("text_numbers", []),
                        image_counts=evidence_data.get("image_counts", []),
                        computed_from_text=evidence_data.get("computed_from_text"),
                        computed_from_image=evidence_data.get("computed_from_image")
                    )
                    
                    # Parse issues (handle both array and JSON string cases)
                    issues_data = tool_input.get("issues", [])
                    issues = []
                    
                    # Handle case where Claude returns issues as a JSON string
                    if isinstance(issues_data, str):
                        try:
                            issues_data = json.loads(issues_data)
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse issues JSON string: {e}")
                            logger.error(f"Raw issues data: {issues_data}")
                            issues_data = []
                    
                    for issue_data in issues_data:
                        issue = Issue(
                            type=issue_data["type"],
                            severity=issue_data["severity"],
                            message=issue_data["message"],
                            evidence=evidence,  # Associate evidence with each issue
                            remediation=issue_data.get("remediation")
                        )
                        issues.append(issue)
                    
                    return SimpleQCResult(
                        passed=tool_input["passed"],
                        reason=tool_input["reason"],
                        mismatch=tool_input["mismatch"],
                        confidence=max(0.0, min(1.0, tool_input["confidence"])),
                        issues=issues
                    )
            
            raise RuntimeError("No structured response found in Claude API response")
            
        except Exception as e:
            logger.error(f"Error in Claude quality assessment: {str(e)}")
            # Default to failure on error to be safe
            return SimpleQCResult(
                passed=False, 
                reason=f"Claude quality assessment failed due to error: {str(e)}",
                mismatch=False,
                confidence=0.0
            )
    
    async def _assess_content_quality_single_gemini(self, screenshot_data: bytes) -> SimpleQCResult:
        """
        Run a single Gemini quality assessment on the content screenshot.
        
        Parameters
        ----------
        screenshot_data : bytes
            PNG screenshot data
            
        Returns
        -------
        SimpleQCResult
            Result of the quality assessment
        """
        system_prompt = QC_BASE_SYSTEM_PROMPT + QC_GEMINI_JSON_INSTRUCTIONS

        user_prompt = """Perform a thorough analysis of this educational content screenshot.
        
        First, systematically extract all quantitative information from the text and count all
        relevant objects in the image. Then perform any necessary calculations and check for
        consistency between text and image.
        
        Complete your full analysis before determining whether the content passes or fails.
        Only mark as failed if you find actual blocking issues after completing your analysis."""

        try:
            # Create image part using proper types.Part.from_bytes
            image_part = types.Part.from_bytes(
                data=screenshot_data,
                mime_type="image/png"
            )

            # Run the synchronous Gemini API call in a thread pool to make it async
            # Phase 3: Use asyncio.to_thread() for Gemini (no native async SDK)
            response = await asyncio.to_thread(
                self.gemini_client.models.generate_content,
                model="gemini-2.5-pro",
                contents=[
                    system_prompt + "\n\n" + user_prompt,
                    image_part
                ],
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=4096,
                    response_mime_type="application/json"
                )
            )
            
            # Parse the JSON response - ensure we properly extract text
            # Check if response.text is a coroutine (defensive check)
            response_text_raw = response.text
            if hasattr(response_text_raw, '__await__'):
                response_text_raw = await response_text_raw
            if isinstance(response_text_raw, str):
                response_text = response_text_raw.strip()
            else:
                response_text = str(response_text_raw).strip()
            logger.info(f"Gemini QC response: {response_text}")
            
            try:
                response_data = json.loads(response_text)
                
                # Parse evidence (handle both object and JSON string cases)
                evidence_data = response_data.get("evidence", {})
                if isinstance(evidence_data, str):
                    try:
                        evidence_data = json.loads(evidence_data)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse Gemini evidence JSON string: {e}")
                        logger.error(f"Raw evidence data: {evidence_data}")
                        evidence_data = {}
                
                evidence = Evidence(
                    text_numbers=evidence_data.get("text_numbers", []),
                    image_counts=evidence_data.get("image_counts", []),
                    computed_from_text=evidence_data.get("computed_from_text"),
                    computed_from_image=evidence_data.get("computed_from_image")
                )
                
                # Parse issues (handle both array and JSON string cases)
                issues_data = response_data.get("issues", [])
                issues = []
                
                # Handle case where Gemini returns issues as a JSON string
                if isinstance(issues_data, str):
                    try:
                        issues_data = json.loads(issues_data)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse Gemini issues JSON string: {e}")
                        logger.error(f"Raw issues data: {issues_data}")
                        issues_data = []
                
                for issue_data in issues_data:
                    issue = Issue(
                        type=issue_data["type"],
                        severity=issue_data["severity"],
                        message=issue_data["message"],
                        evidence=evidence,  # Associate evidence with each issue
                        remediation=issue_data.get("remediation")
                    )
                    issues.append(issue)
                
                return SimpleQCResult(
                    passed=response_data["passed"],
                    reason=response_data["reason"],
                    mismatch=response_data.get("mismatch", False),
                    confidence=max(0.0, min(1.0, response_data.get("confidence", 0.5))),
                    issues=issues
                )
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini JSON response: {e}")
                logger.error(f"Raw response: {response_text}")
                # Fallback to a FAIL result
                return SimpleQCResult(
                    passed=False,
                    reason=f"Unable to parse Gemini response. Raw: {response_text}",
                    mismatch=False,
                    confidence=0.0
                )
            
        except Exception as e:
            logger.error(f"Error in Gemini quality assessment: {str(e)}")
            # Default to failure on error to be safe
            return SimpleQCResult(
                passed=False, 
                reason=f"Gemini quality assessment failed due to error: {str(e)}",
                mismatch=False,
                confidence=0.0
            )
    
    async def _run_single_assessment(self, screenshot_data: bytes,
    assessment_num: int) -> SimpleQCResult:
        """Run a single quality assessment using the configured model provider."""
        try:
            # Route to the appropriate assessment method based on global flag
            if QC_MODEL_PROVIDER == CLAUDE_MODEL_PROVIDER:
                result = await self._assess_content_quality_single_claude(screenshot_data)
            elif QC_MODEL_PROVIDER == GEMINI_MODEL_PROVIDER:
                result = await self._assess_content_quality_single_gemini(screenshot_data)
            else:  # Default to GPT
                result = await self._assess_content_quality_single(screenshot_data)
            
            provider_name = QC_MODEL_PROVIDER.upper()
            status = 'PASSED' if result.passed else 'FAILED'
            logger.info(f"QC{assessment_num+1} ({provider_name}): {status} - {result.reason}")
            return result
        except Exception as e:
            # If an assessment fails, treat it as a failure
            error_result = SimpleQCResult(
                passed=False, 
                reason=f"Assessment error: {str(e)}",
                mismatch=False,
                confidence=0.0
            )
            provider_name = QC_MODEL_PROVIDER.upper()
            logger.error(f"QC{assessment_num+1} ({provider_name}): ERROR - {str(e)}")
            return error_result
        
    async def _assess_content_quality(self, screenshot_data: bytes) -> SimpleQCResult:
        """
        Run 3 independent quality assessments using the configured model provider.
        
        Parameters
        ----------
        screenshot_data : bytes
            PNG screenshot data
            
        Returns
        -------
        SimpleQCResult
            Combined result of the 3 quality assessments
        """
        provider_name = QC_MODEL_PROVIDER.upper()
        logger.info(f"Running 3 independent QC assessments concurrently using {provider_name}")
        
        # Run all 3 assessments concurrently using the factored-out method
        results = await asyncio.gather(
            self._run_single_assessment(screenshot_data, 0),
            self._run_single_assessment(screenshot_data, 1),
            self._run_single_assessment(screenshot_data, 2),
            return_exceptions=False
        )
        
        # Format the combined reason
        reason_parts = []
        for i, result in enumerate(results):
            status = "PASSED" if result.passed else "FAILED"
            reason_parts.append(f"QC{i+1}: {status}: {result.reason}")
        
        combined_reason = "\n".join(reason_parts)
        
        # Only pass if ALL 3 assessments passed (meaning all 3 think content is fine)
        all_passed = all(result.passed for result in results)
        
        # Calculate combined confidence and mismatch detection
        avg_confidence = sum(result.confidence for result in results) / len(results)
        any_mismatch = any(result.mismatch for result in results)
        
        # Cross-validation check: Flag if there are discrepancies in object counting
        # Extract any numerical mentions from reasons to spot count disagreements
        count_discrepancies = []
        for i, result1 in enumerate(results):
            for j, result2 in enumerate(results[i+1:], i+1):
                # Look for counting disagreements in the analysis text
                if hasattr(result1, 'issues') and hasattr(result2, 'issues'):
                    # Check if both mention counts but with different numbers
                    reason1_lower = result1.reason.lower()
                    reason2_lower = result2.reason.lower()
                    if ('count' in reason1_lower or 'plate' in reason1_lower \
                        or 'table' in reason1_lower) and \
                       ('count' in reason2_lower or 'plate' in reason2_lower \
                        or 'table' in reason2_lower):
                        # Basic check for numerical disagreement (simplified)
                        import re
                        numbers1 = set(re.findall(r'\b\d+\b', reason1_lower))
                        numbers2 = set(re.findall(r'\b\d+\b', reason2_lower))
                        if numbers1 and numbers2 and numbers1 != numbers2:
                            count_discrepancies.append(
                                f"QC{i+1} vs QC{j+1}: potential count disagreement"
                            )
        
        if count_discrepancies:
            logger.warning(f"Potential counting discrepancies detected: {count_discrepancies}")
            # Lower confidence when there are counting discrepancies
            avg_confidence = max(0.3, avg_confidence - 0.2)
        
        if all_passed:
            logger.info("All 3 QC assessments passed (content is acceptable)")
            return SimpleQCResult(
                passed=True,
                reason=combined_reason,
                mismatch=any_mismatch,
                confidence=avg_confidence
            )
        else:
            failing_count = sum(1 for result in results if not result.passed)
            logger.info(f"{failing_count}/3 QC assessments failed (content has issues)")
            return SimpleQCResult(
                passed=False,
                reason=combined_reason,
                mismatch=any_mismatch,
                confidence=avg_confidence
            )
    
    async def check_content_quality(self, markdown_content: str) -> Tuple[bool, str, bytes]:
        """
        Check the quality of markdown content by rendering and screenshotting it.
        
        Parameters
        ----------
        markdown_content : str
            Markdown content to check
            
        Returns
        -------
        Tuple[bool, str, bytes]
            (passed, reason, screenshot_data) - whether QC passed, the reason/details, and
            screenshot bytes
        """
        try:
            start_time = time.time()
            logger.info("Starting simple content quality check")
            
            # Render markdown to HTML
            html_content = self._render_markdown_to_html(markdown_content)
            
            # Try to take screenshot with fallback
            result = await self._take_screenshot_with_fallback(html_content)
            screenshot_data, screenshot_success = result
            
            if screenshot_success and screenshot_data:
                # Assess quality with GPT-5 using screenshot
                qc_result = await self._assess_content_quality(screenshot_data)
                status = 'PASSED' if qc_result.passed else 'FAILED'
                elapsed = time.time() - start_time
                logger.info(f"Screenshot-based QC completed: {status} in {elapsed:.2f} seconds")
                return qc_result.passed, qc_result.reason, screenshot_data
            else:
                # Fallback to text-only quality check
                logger.warning("Screenshot failed, using text-only QC fallback")
                qc_result = await self._text_only_quality_check(markdown_content)
                status = 'PASSED' if qc_result.passed else 'FAILED'
                elapsed = time.time() - start_time
                logger.info(f"Text-only QC completed: {status} in {elapsed:.2f} seconds")
                return qc_result.passed, qc_result.reason, b""
            
        except Exception as e:
            logger.error(f"Error in simple content quality check: {str(e)}")
            # Try text-only fallback as last resort
            try:
                logger.info("Attempting text-only QC as last resort")
                qc_result = await self._text_only_quality_check(markdown_content)
                return qc_result.passed, f"Fallback QC: {qc_result.reason}", b""
            except Exception as fallback_error:
                logger.error(f"Fallback QC also failed: {fallback_error}")
                return False, f"All QC methods failed: {str(e)}", b""


async def run_simple_content_qc(markdown_content: str) -> Tuple[bool, str]:
    """
    Run simple content quality check on markdown content.
    
    Parameters
    ----------
    markdown_content : str
        Markdown content to check
        
    Returns
    -------
    Tuple[bool, str]
        (passed, reason) - whether QC passed and detailed reason
    """
    if not ENABLE_SIMPLE_QC:
        logger.info("Simple QC is disabled, skipping check")
        return True, "Simple QC disabled"
    
    qc_checker = SimpleContentQC()
    qc_passed, qc_reason, screenshot_data = await qc_checker.check_content_quality(markdown_content)
    
    return qc_passed, qc_reason

def get_qc_stats() -> dict:
    """
    Get QC system statistics including screenshot service stats.
    
    Returns
    -------
    dict
        Statistics about QC operations and screenshot service
    """
    try:
        import requests
        response = requests.get(f"{SCREENSHOT_SERVICE_URL}/stats", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Screenshot service returned {response.status_code}"}
    except Exception as e:
        logger.error(f"Error getting QC stats: {e}")
        return {"error": str(e), "screenshot_service_url": SCREENSHOT_SERVICE_URL}

async def cleanup_qc_resources() -> None:
    """
    Clean up QC system resources.
    Note: Screenshot service manages its own browser instances.
    Call this on application shutdown if needed.
    """
    try:
        # The screenshot service handles its own cleanup via SIGTERM
        # No explicit cleanup needed from Python side
        logger.info("QC resources cleanup initiated (screenshot service manages browsers)")
    except Exception as e:
        logger.error(f"Error cleaning up QC resources: {e}")

def cleanup_qc_resources_sync() -> None:
    """
    Synchronous cleanup function for compatibility.
    Screenshot service manages its own browser instances.
    """
    try:
        # No explicit cleanup needed - screenshot service handles this
        logger.info("QC resources cleanup called (screenshot service manages browsers)")
    except Exception as e:
        logger.error(f"Error cleaning up QC resources: {e}")


def generate_simple_content_qc_tool() -> Tuple[Dict[str, Any], Callable]:
    """
    Generate tool specification for simple content QC that generator agent can use.
    
    This tool allows the generator agent to check content quality before finalizing
    responses, enabling iterative improvement based on QC feedback. The tool handles
    rendering content as students will see it and checking for various quality issues.
    
    Returns
    -------
    Tuple[Dict[str, Any], Callable]
        A tuple of (tool_spec, tool_function) for use by the agent
    """
    
    async def check_content_quality_tool(content: str) -> str:
        """
        Check content quality and return structured feedback for the generator agent.
        
        This function renders the content, takes a screenshot, and uses AI models to
        assess quality. It returns clear PASSED/FAILED feedback with details about
        any issues found.
        
        Parameters
        ----------
        content : str
            The complete markdown content to check for quality issues
            
        Returns
        -------
        str
            Structured feedback string with PASSED or FAILED status and details
        """
        from edu_agents.core.tool_context import get_current_request_id
        
        request_id = get_current_request_id()
        
        # Log QC attempt
        if request_id:
            logger.info(f"Generator agent running QC check for request {request_id}")
        else:
            logger.info("Generator agent running QC check (no request_id in context)")
        
        if not ENABLE_SIMPLE_QC:
            logger.info("Simple QC is disabled, returning PASSED")
            return "PASSED: Content quality check is disabled."
        
        try:
            qc_checker = SimpleContentQC()
            qc_passed, qc_reason, screenshot_data = await qc_checker.check_content_quality(content)
            
            # Log QC result
            status = "passed" if qc_passed else "failed"
            if request_id:
                logger.info(f"QC check {status} for request {request_id}")
            else:
                logger.info(f"QC check {status}")
            
            # Log to database if request_id available
            if request_id:
                try:
                    from utils.supabase_utils import update_request_log_simple_qc
                    await update_request_log_simple_qc(request_id, qc_passed, qc_reason, None)
                except Exception as e:
                    logger.error(f"Failed to log QC results to database for {request_id}: {e}")
            
            # Return structured feedback for the agent
            if qc_passed:
                return "PASSED: Content meets all quality standards."
            else:
                return (
                    f"FAILED: The content has quality issues that must be addressed.\n\n"
                    f"Details:\n{qc_reason}\n\n"
                    f"Please carefully review the issues above, revise your content to address "
                    f"ALL of them, and then run this quality check again."
                )
                
        except Exception as e:
            error_msg = f"Quality check encountered an error: {str(e)}"
            logger.error(f"QC tool error: {error_msg}")
            
            # Log error to database if request_id available
            if request_id:
                try:
                    from utils.supabase_utils import update_request_log_simple_qc
                    await update_request_log_simple_qc(
                        request_id, 
                        False, 
                        f"QC check error: {str(e)}", 
                        None
                    )
                except Exception as db_error:
                    logger.error(f"Failed to log QC error to database: {db_error}")
            
            return (
                f"FAILED: {error_msg}\n\n"
                f"The quality check could not be completed due to a technical error. "
                f"You may need to revise your content and try again."
            )
    
    spec = {
        "type": "function",
        "name": "check_content_quality",
        "description": (
            "Check the quality of educational content by rendering it as students will see it "
            "and analyzing for issues including: text-image mismatches, unrendered LaTeX, "
            "mathematical errors, readability problems, inappropriate content, and pedagogical "
            "issues. This tool MUST be called before returning any final content to ensure "
            "quality standards are met. Returns PASSED if content is acceptable, or FAILED "
            "with detailed feedback about what needs to be fixed."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": (
                        "The complete markdown content to check for quality issues. Include "
                        "all text, LaTeX expressions, images, and other components exactly as "
                        "they will appear to students."
                    )
                }
            },
            "required": ["content"]
        }
    }
    
    return spec, check_content_quality_tool 