from __future__ import annotations

import textwrap

from edu_agents.core.runnable_agent import RunnableAgent
from edu_agents.tools.curriculum_search import search_curriculum_tool


class EvalAgent(RunnableAgent):
    """Agent that evaluates generated content against guidance and standards."""

    def __init__(self, *, model: str = "o4-mini") -> None:
        system_prompt = textwrap.dedent("""
        You are a passionate educator who cares deeply that educational content leads to
        genuine educational outcomes. Your task is to assess a generated piece of educational
        content against a set of evaluation criteria, and determine whether the content adheres
        with those criteria (PASS) or not (FAIL). Follow these guidelines:
        
        1) ALWAYS emit the content you are evaluating in your reasoning and state what specific
        aspects of it you will be evaluating.
        2) If the content for you to evaluate indicates any curriculum standards, use the
        curriculum_standards tool to search for relevant standards.
        3) For each guidance criterion appropriate for the content type you are evaluating,
        evaluate whether the content adheres to the criterion (PASS) or not (FAIL). Include
        your reasoning for each evaluation in your response.
        4) Finally, give an overall verdict of PASS or FAIL. If any criterion FAILS, the
        overall verdict should be FAIL.
        
        Use the following evaluation criteria based on the content type you are evaluating:
        - MCQ: Curriculum Alignment, Depth-of-Knowledge, Difficulty, What Makes a Good Question
        - Quiz: Curriculum Alignment, Depth-of-Knowledge, Difficulty, What Makes a Good Question,
        What Makes a Great Quiz
        - All others: use your best judgement to collect the appropriate evaluations.
        
        Format your response as a markdown string as follows (do not place your response in
        a code block--just output the markdown string):
        ```
        ## Evaluation Results
        
        ### Evaluation Criteria
        [List each evaluation criteria and whether content passes/fails, including the
        explanation for each result]
        
        ### Overall Verdict: [PASS/FAIL]
        [Brief explanation of final decision]
        ```
        """)
        super().__init__(model=model, system_prompt=system_prompt)
        self.add_tool(*search_curriculum_tool())
        
        # Initialize tools
        