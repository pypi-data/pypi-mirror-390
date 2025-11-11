"""CLI for Incept Eval"""
import click
import json
import sys
import os
from pathlib import Path
import requests

def get_api_key(api_key=None):
    """Get API key - now optional since we run locally"""
    if api_key:
        return api_key
    if os.getenv('INCEPT_API_KEY'):
        return os.getenv('INCEPT_API_KEY')
    config_file = Path.home() / '.incept' / 'config'
    if config_file.exists():
        try:
            with open(config_file) as f:
                return json.load(f).get('api_key')
        except:
            pass
    # API key is now optional - we run locally
    return None

@click.group()
@click.version_option(version='1.4.2')
def cli():
    """Incept Eval - Evaluate educational questions via Incept API

    \b
    CLI tool for evaluating educational questions with comprehensive
    assessment including DI compliance, answer verification, and
    specialized evaluators for math, reading, and image content.

    \b
    Commands:
      evaluate    Evaluate questions from a JSON file
      benchmark   Process many questions in parallel (high throughput)
      example     Generate sample input JSON file
      help        Show detailed help and usage examples

    \b
    Quick Start:
      1. Generate a sample file:
         $ inceptbench example

      2. Evaluate questions (automatic routing):
         $ inceptbench evaluate qs.json --subject math --grade 6

      3. Evaluate with image content:
         $ inceptbench evaluate qs.json --subject math --type mcq --verbose

    \b
    Examples:
      # Automatic evaluator selection based on content
      $ inceptbench evaluate questions.json --subject math --grade "6-8"

      # Full detailed evaluation results
      $ inceptbench evaluate questions.json --full --verbose

      # Save full results to file
      $ inceptbench evaluate questions.json --full -o results.json

      # Evaluate reading comprehension
      $ inceptbench evaluate questions.json --subject ela --type mcq

      # Benchmark mode for high throughput
      $ inceptbench benchmark questions.json --workers 100 -o results.json

    \b
    For detailed help, run: inceptbench help
    """
    pass

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Save results to file (overwrites)')
@click.option('--append', '-a', type=click.Path(), help='Append results to file (creates if not exists)')
@click.option('--api-key', '-k', envvar='INCEPT_API_KEY', help='API key for authentication')
@click.option('--api-url', default='https://uae-poc.inceptapi.com', help='API endpoint URL')
@click.option('--timeout', '-t', type=int, default=600, help='Request timeout in seconds (default: 600)')
@click.option('--pretty', is_flag=True, default=True, help='Show only scores (default: enabled)')
@click.option('--verbose', '-v', is_flag=True, help='Show progress messages')
@click.option('--full', '-f', is_flag=True, help='Return full detailed evaluation results (default: simplified scores only)')
@click.option('--subject', '-s', type=click.Choice(['math', 'ela', 'science', 'social-studies', 'history', 'general'], case_sensitive=False), help='Subject area for automatic evaluator selection')
@click.option('--grade', '-g', help='Grade level (e.g., "K", "3", "6-8", "9-12")')
@click.option('--type', type=click.Choice(['mcq', 'fill-in', 'short-answer', 'essay', 'text-content', 'passage', 'article'], case_sensitive=False), help='Content type for automatic evaluator selection')
def evaluate(input_file, output, append, api_key, api_url, timeout, pretty, verbose, full, subject, grade, type):
    """Evaluate educational content with comprehensive assessment

    The evaluator automatically selects appropriate evaluation methods based on
    your content and optional parameters (subject, grade, type).

    Examples:
        # Basic evaluation
        inceptbench evaluate questions.json

        # Math questions with specific grade
        inceptbench evaluate questions.json --subject math --grade "6-8"

        # ELA reading comprehension
        inceptbench evaluate questions.json --subject ela --type mcq
    """
    try:
        api_key = get_api_key(api_key)
        if verbose:
            click.echo(f"📂 Loading: {input_file}")

        with open(input_file) as f:
            data = json.load(f)

        # Add verbose flag and routing parameters to the data
        data['verbose'] = full
        if subject:
            data['subject'] = subject
        if grade:
            data['grade'] = grade
        if type:
            data['type'] = type

        # Import here to avoid loading evaluator for non-evaluation commands
        from .client import InceptClient
        client = InceptClient(api_key, api_url, timeout=timeout)
        result = client.evaluate_dict(data)

        # Always output full results - pretty only controls formatting
        json_output = json.dumps(result, indent=2 if pretty else None, ensure_ascii=False)

        # Handle output options
        if output:
            # Overwrite mode
            with open(output, 'w', encoding='utf-8') as f:
                f.write(json_output)
            if verbose:
                click.echo(f"✅ Saved to: {output}")
        elif append:
            # Append mode - load existing evaluations or create new list
            existing_data = []
            if Path(append).exists():
                try:
                    with open(append, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                        if not isinstance(existing_data, list):
                            # If file exists but isn't a list, wrap it
                            existing_data = [existing_data]
                except json.JSONDecodeError:
                    if verbose:
                        click.echo(f"⚠️  File exists but is invalid JSON, creating new file")
                    existing_data = []

            # Append new result
            existing_data.append(result)

            # Write back to file
            with open(append, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)

            if verbose:
                click.echo(f"✅ Appended to: {append} (total: {len(existing_data)} evaluations)")
        else:
            # Print to stdout
            click.echo(json_output)

    except requests.HTTPError as e:
        click.echo(f"❌ API Error: {e.response.status_code}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Save results to file')
@click.option('--workers', '-w', type=int, default=100, help='Number of parallel workers (default: 100)')
@click.option('--verbose', '-v', is_flag=True, help='Show progress messages')
@click.option('--subject', '-s', type=click.Choice(['math', 'ela', 'science', 'social-studies', 'history', 'general'], case_sensitive=False), help='Subject area for automatic evaluator selection')
@click.option('--grade', '-g', help='Grade level (e.g., "K", "3", "6-8", "9-12")')
@click.option('--type', type=click.Choice(['mcq', 'fill-in', 'short-answer', 'essay', 'text-content', 'passage', 'article'], case_sensitive=False), help='Content type for automatic evaluator selection')
def benchmark(input_file, output, workers, verbose, subject, grade, type):
    """Benchmark mode: Process many questions in parallel

    Evaluates all questions using parallel workers for maximum throughput.
    The evaluator automatically selects appropriate methods based on your content.

    Example:
        inceptbench benchmark questions.json --workers 100 --subject math -o results.json
    """
    try:
        if verbose:
            click.echo(f"📂 Loading: {input_file}")

        with open(input_file) as f:
            data = json.load(f)

        # Add routing parameters to the data
        if subject:
            data['subject'] = subject
        if grade:
            data['grade'] = grade
        if type:
            data['type'] = type

        # Import here to avoid loading evaluator for non-benchmark commands
        from .client import InceptClient
        client = InceptClient()

        # Use benchmark mode
        if verbose:
            click.echo(f"🚀 Benchmark mode: {len(data.get('generated_questions', []))} questions with {workers} workers")

        result = client.benchmark(data, max_workers=workers)

        # Format output
        json_output = json.dumps(result, indent=2, ensure_ascii=False)

        # Handle output
        if output:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(json_output)
            if verbose:
                click.echo(f"✅ Saved to: {output}")
                click.echo(f"📊 Results: {result['successful']}/{result['total_questions']} successful")
                click.echo(f"⏱️  Time: {result['evaluation_time_seconds']:.2f}s")
                click.echo(f"📈 Avg Score: {result['avg_score']:.3f}")
                if result['failed_ids']:
                    click.echo(f"❌ Failed IDs: {', '.join(result['failed_ids'])}")
        else:
            click.echo(json_output)

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('api_key')
def configure(api_key):
    """Save API key to config file"""
    try:
        config_dir = Path.home() / '.incept'
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / 'config'

        with open(config_file, 'w') as f:
            json.dump({'api_key': api_key}, f)

        config_file.chmod(0o600)
        click.echo(f"✅ API key saved to {config_file}")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)

@cli.command()
def help():
    """Show detailed help and usage examples"""
    help_text = """
╔═══════════════════════════════════════════════════════════════════╗
║                    INCEPT-EVAL CLI HELP                           ║
║                      Version 1.4.2                                ║
╚═══════════════════════════════════════════════════════════════════╝

OVERVIEW:
  InceptBench is a comprehensive evaluation framework for educational
  content. It features automatic evaluator routing based on content type,
  subject, and grade level with specialized evaluators for:
  - Reading Question QC (ALWAYS included - universal quality assessment)
  - Text & Instructional Content Quality
  - Math Content Evaluation
  - Answer Correctness Verification
  - Image Quality Assessment (DI principles)
  - Math Image Judge (visual problem evaluation)

INSTALLATION:
  pip install inceptbench

COMMANDS:

  1. example - Generate sample input file
     Usage: inceptbench example [OPTIONS]

     Options:
       -o, --output PATH    Save to file (default: qs.json)

     Examples:
       inceptbench example                    # Creates qs.json
       inceptbench example -o sample.json     # Creates sample.json

  2. evaluate - Evaluate questions from JSON file
     Usage: inceptbench evaluate INPUT_FILE [OPTIONS]

     Options:
       -o, --output PATH      Save results to file (overwrites)
       -a, --append PATH      Append results to file (creates if not exists)
       -s, --subject TEXT     Subject area: math, ela, science, social-studies, general
       -g, --grade TEXT       Grade level: K, 3, 6-8, 9-12, etc.
       --type TEXT            Content type: mcq, fill-in, short-answer, essay, text-content, passage
       -v, --verbose          Show progress messages
       -f, --full             Return full detailed evaluation (default: simplified scores)

     Examples:
       # Automatic routing for math content
       inceptbench evaluate questions.json --subject math --grade 6

       # Reading comprehension evaluation
       inceptbench evaluate questions.json --subject ela --type mcq

       # Full detailed evaluation with all scores
       inceptbench evaluate questions.json --full --verbose

       # Save results to file
       inceptbench evaluate questions.json -o results.json

       # Evaluate image-based questions
       inceptbench evaluate questions.json --subject math --grade "6-8" --full

  3. benchmark - High-throughput parallel evaluation
     Usage: inceptbench benchmark INPUT_FILE [OPTIONS]

     Options:
       -o, --output PATH      Save results to file
       -w, --workers INT      Number of parallel workers (default: 100)
       -s, --subject TEXT     Subject area for routing
       -g, --grade TEXT       Grade level for routing
       --type TEXT            Content type for routing
       -v, --verbose          Show progress messages

     Example:
       inceptbench benchmark questions.json --workers 100 --subject math -o results.json

AUTOMATIC EVALUATOR ROUTING:

  InceptBench v1.3.2 features automatic evaluator selection based on:
  - Subject area (math, ela, science, etc.)
  - Grade level (K-12 range)
  - Content type (mcq, essay, text-content, etc.)

  Available evaluators:
  • reading_question_qc     - ALWAYS included for all content
  • ti_question_qa          - Question quality assessment
  • answer_verification     - Answer correctness checking
  • math_content_evaluator  - Math-specific content evaluation
  • text_content_evaluator  - Text/instructional content quality
  • math_image_judge_evaluator - Math visual problem evaluation
  • image_quality_di_evaluator - DI-compliant image quality

  Reading QC is universal: runs on ALL content (questions AND text) to
  ensure comprehensive quality coverage across all submissions.

INPUT FILE FORMAT:

  Minimal format with automatic routing:
  {
    "subject": "math",           // Optional: for automatic routing
    "grade": "6",                // Optional: for automatic routing
    "generated_questions": [
      {
        "id": "q1",
        "type": "mcq",
        "question": "Question text here",
        "answer": "Correct answer",
        "answer_explanation": "Step-by-step explanation",
        "answer_options": {
          "A": "Option 1",
          "B": "Option 2",
          "C": "Option 3",
          "D": "Option 4"
        },
        "image_url": "https://...",  // Optional: for image evaluation
        "skill": {                    // Optional metadata
          "title": "Skill name",
          "grade": "6",
          "subject": "mathematics"
        }
      }
    ]
  }

  Use 'inceptbench example' to generate a complete sample file.

OUTPUT FORMAT:

  The response includes:
  - inceptbench_version: Version used for evaluation (1.4.2)
  - request_id: Unique evaluation identifier
  - evaluations: Per-question/content results with:
    - reading_question_qc: Universal quality scores (always present)
    - ti_question_qa: Question quality scores (0-1 scale)
    - answer_verification: Correctness with reasoning
    - math_content_evaluator: Math content quality
    - text_content_evaluator: Text content quality
    - math_image_judge_evaluator: Math visual evaluation
    - image_quality_di_evaluator: DI image quality scores
    - score: Combined final score (0-1 scale)
  - evaluation_time_seconds: Total evaluation time

QUICK START:

  # 1. Generate sample file
  inceptbench example

  # 2. Evaluate with automatic routing
  inceptbench evaluate qs.json --subject math --grade 6 --verbose

  # 3. Get full detailed results
  inceptbench evaluate qs.json --full -o results.json

  # 4. Benchmark mode for large datasets
  inceptbench benchmark qs.json --workers 100 -o results.json

For more information, visit: https://github.com/incept-ai/inceptbench
"""
    click.echo(help_text)

@cli.command()
@click.option('--output', '-o', type=click.Path(), default='qs.json', help='Save to file (default: qs.json)')
def example(output):
    """Generate sample input file

    Creates a complete example with Arabic math question demonstrating
    the simplified evaluation interface. The evaluator automatically
    selects appropriate methods based on your content.

    By default, saves to qs.json in the current directory.
    """
    example_data = {
  "subject": "math",
  "grade": "6",
  "generated_questions": [
    {
      "id": "q1",
      "type": "mcq",
      "question": "إذا كان ثمن 2 قلم هو 14 ريالًا، فما ثمن 5 أقلام بنفس المعدل؟",
      "answer": "35 ريالًا",
      "answer_explanation": "الخطوة 1: تحليل المسألة — لدينا ثمن 2 قلم وهو 14 ريالًا. نحتاج إلى معرفة ثمن 5 أقلام بنفس المعدل. يجب التفكير في العلاقة بين عدد الأقلام والسعر وكيفية تحويل عدد الأقلام بمعدل ثابت.\nالخطوة 2: تطوير الاستراتيجية — يمكننا أولًا إيجاد ثمن قلم واحد بقسمة 14 ÷ 2 = 7 ريال، ثم ضربه في 5 لإيجاد ثمن 5 أقلام: 7 × 5 = 35 ريالًا.\nالخطوة 3: التطبيق والتحقق — نتحقق من منطقية الإجابة بمقارنة السعر بعدد الأقلام. السعر يتناسب طرديًا مع العدد، وبالتالي 35 ريالًا هي الإجابة الصحيحة والمنطقية.",
      "answer_options": {
        "A": "28 ريالًا",
        "B": "70 ريالًا",
        "C": "30 ريالًا",
        "D": "35 ريالًا"
      },
      "skill": {
        "title": "Proportional Reasoning",
        "grade": "6",
        "subject": "mathematics",
        "difficulty": "medium",
        "description": "Apply proportional reasoning to solve real-world problems involving ratios and unit rates",
        "language": "ar",
        "standards": ["6.RP.A.2", "6.RP.A.3"]
      },
      "image_url": "null",
      "additional_details": "🔹 **Question generation logic:**\nThis question targets proportional reasoning for Grade 6 students, testing their ability to apply ratios and unit rates to real-world problems. It follows a classic proportionality structure — starting with a known ratio (2 items for 14 riyals) and scaling it up to 5 items. The stepwise reasoning develops algebraic thinking and promotes estimation checks to confirm logical correctness.\n\n🔹 **Personalized insight examples:**\n- Choosing 28 ريالًا shows a misunderstanding by doubling instead of proportionally scaling.\n- Choosing 70 ريالًا indicates multiplying the base price by 5 instead of finding unit rate first.\n- Choosing 30 ريالًا suggests estimation error or calculation mistake.\n\n🔹 **Instructional design & DI integration:**\nThe question aligns with *Percent, Ratio, and Probability* learning targets. In DI format 15.7, it models how equivalent fractions and proportional relationships can predict outcomes across different scales. This builds foundational understanding for probability and proportional reasoning. By using a simple, relatable context (price of pens), it connects mathematical ratios to practical real-world applications, supporting concept transfer and cognitive engagement."
    },
    {
      "id": "q2",
      "type": "mcq",
      "question": "What is the value of x in the equation 3x + 7 = 22?",
      "answer": "5",
      "answer_explanation": "Step 1: Start with the equation 3x + 7 = 22.\nStep 2: Subtract 7 from both sides: 3x = 15.\nStep 3: Divide both sides by 3: x = 5.\nStep 4: Verify by substituting back: 3(5) + 7 = 15 + 7 = 22 ✓",
      "answer_options": {
        "A": "3",
        "B": "4",
        "C": "5",
        "D": "6"
      },
      "skill": {
        "title": "Solving Linear Equations",
        "grade": "7",
        "subject": "mathematics",
        "difficulty": "medium",
        "language": "en",
        "standards": ["7.EE.B.4", "7.EE.B.4a"]
      },
      "image_url": "null",
      "additional_details": "This question assesses understanding of algebraic manipulation and inverse operations. Students must demonstrate the ability to isolate variables through systematic steps. Common errors: choosing 3 (subtracting only), 4 (calculation error), or 6 (adding instead of proper operations)."
    },
    {
      "id": "img2",
      "type": "mcq",
      "question": "Examine the image carefully. What mathematical operation does it illustrate?",
      "answer": "Addition",
      "answer_explanation": "The image displays two groups of objects with a plus sign between them, clearly illustrating the operation of addition where quantities are combined together.",
      "answer_options": {
        "A": "Addition",
        "B": "Subtraction",
        "C": "Multiplication",
        "D": "Division"
      },
      "skill": {
        "title": "Understanding Operations",
        "grade": "3",
        "subject": "mathematics",
        "difficulty": "easy",
        "language": "en",
        "standards": ["3.OA.A.1", "3.OA.D.8"]
      },
      "image_url": "https://drive.google.com/uc?export=view&id=17z-_rlrluycc0lPLUZ4IRBcqB33T2sof",
      "additional_details": "This question connects visual representations to mathematical operations, helping students understand operations conceptually through diagrams and illustrations."
    },
    {
      "id": "img7",
      "type": "mcq",
      "question": "The poster shows different types of bar models. What are the two main types of bar models shown for problem-solving?",
      "answer": "Part-Whole and Comparison Models",
      "answer_explanation": "The poster displays two fundamental types of bar models used in elementary mathematics: Part-Whole models (which show how parts combine to make a whole) and Comparison models (which show the relationship between two or more quantities).",
      "answer_options": {
        "A": "Addition and Subtraction Models",
        "B": "Part-Whole and Comparison Models",
        "C": "Equal Groups and Array Models",
        "D": "Number Line and Area Models"
      },
      "skill": {
        "title": "Understanding Bar Models",
        "grade": "4",
        "subject": "mathematics",
        "difficulty": "medium",
        "language": "en",
        "standards": ["4.OA.A.2", "4.NBT.B.5"]
      },
      "image_url": "https://ecdn.teacherspayteachers.com/thumbitem/Bar-Model-Poster-for-Elementary-Students-Part-Whole-and-Comparison-Models-14426442-1757863928/original-14426442-1.jpg",
      "additional_details": "This question tests students' ability to identify and understand different types of visual mathematical models. Bar models are essential problem-solving tools in elementary mathematics."
    },
    {
      "id": "img8",
      "type": "mcq",
      "question": "Based on the image, if 2 pens cost 14 riyals, how much would 5 pens cost at the same rate?",
      "answer": "35 riyals",
      "answer_explanation": "The image shows that 2 pens cost 14 riyals. To find the cost of 5 pens, first find the unit rate: 14 ÷ 2 = 7 riyals per pen. Then multiply 7 × 5 = 35 riyals. This maintains the same proportional relationship between the number of pens and their total cost.",
      "answer_options": {
        "A": "28 riyals",
        "B": "30 riyals",
        "C": "35 riyals",
        "D": "40 riyals"
      },
      "skill": {
        "title": "Proportional Reasoning",
        "grade": "5",
        "subject": "mathematics",
        "difficulty": "medium",
        "language": "en",
        "standards": ["5.RP.A.1", "5.RP.A.2"]
      },
      "image_url": "https://i.ibb.co/z9wgjWG/Chat-GPT-Image-Oct-27-2025-05-24-13-PM.png",
      "additional_details": "Question visualizes proportional reasoning through a bar model comparing the cost of pens. Students apply unit rate reasoning to extend a given ratio to a new quantity."
    }    
  ],
  "generated_content": [
    {
      "id": "text1",
      "type": "text",
      "title": "Understanding Proportional Reasoning",
      "content": "Proportional reasoning is a fundamental mathematical skill that involves understanding relationships between quantities. When two quantities maintain a constant ratio, they are said to be proportional. For example, if 2 pens cost 14 riyals, we can find the cost of any number of pens by maintaining this same ratio.\n\nThe key to solving proportional problems is identifying the unit rate - the cost or quantity per one item. In our pen example, dividing 14 by 2 gives us 7 riyals per pen. Once we know the unit rate, we can multiply it by any quantity to find the total cost.\n\nThis concept appears throughout mathematics and real life: in cooking recipes, map scales, speed calculations, and currency conversions. Understanding proportional reasoning helps students develop algebraic thinking and prepares them for more advanced mathematical concepts.",
      "skill": {
        "title": "Proportional Reasoning Concepts",
        "grade": "6",
        "subject": "mathematics",
        "difficulty": "medium",
        "language": "en",
        "standards": ["6.RP.A.1", "6.RP.A.3"]
      },
      "image_url": "null",
      "additional_details": "This explanatory text provides conceptual foundation for proportional reasoning problems, building understanding before procedural practice."
    },
    {
      "id": "passage1",
      "type": "passage",
      "title": "The History of Algebra",
      "content": "The word 'algebra' comes from the Arabic word 'al-jabr,' which means 'reunion of broken parts.' This mathematical discipline was formalized by the Persian mathematician Muhammad ibn Musa al-Khwarizmi in the 9th century. His book, 'The Compendious Book on Calculation by Completion and Balancing,' introduced systematic methods for solving linear and quadratic equations.\n\nAl-Khwarizmi's work built upon earlier contributions from Babylonian, Greek, and Indian mathematicians. However, his systematic approach and notation made algebra accessible to a wider audience. The methods he developed for solving equations - moving terms from one side to another and combining like terms - are still taught in classrooms today.\n\nAlgebra revolutionized mathematics by introducing the use of symbols to represent unknown quantities. This abstraction allowed mathematicians to solve general problems rather than specific numerical cases. Today, algebra serves as the foundation for advanced mathematics, science, engineering, and technology.",
      "skill": {
        "title": "History of Mathematics",
        "grade": "7",
        "subject": "mathematics",
        "difficulty": "medium",
        "language": "en",
        "standards": []
      },
      "image_url": "null",
      "additional_details": "Historical context passage that connects mathematical concepts to cultural and historical development, supporting interdisciplinary learning."
    },
    {
      "id": "text2",
      "type": "explanation",
      "title": "Why We Isolate Variables",
      "content": "When solving equations like 3x + 7 = 22, our goal is to isolate the variable (x) on one side of the equation. But why is this important?\n\nIsolating the variable reveals its value - the number that makes the equation true. Think of an equation as a balanced scale. Whatever we do to one side, we must do to the other to maintain balance. This principle, called the 'balance property of equality,' ensures our solution is valid.\n\nThe process follows a logical sequence: First, we undo addition or subtraction (in this case, subtract 7 from both sides). Then, we undo multiplication or division (divide both sides by 3). This order follows the reverse of the order of operations, systematically 'unwrapping' the variable.\n\nUnderstanding this process builds problem-solving skills that extend beyond mathematics. It teaches logical thinking, systematic approaches to complex problems, and the importance of maintaining equivalence - principles applicable to many real-world situations.",
      "skill": {
        "title": "Solving Equations Conceptually",
        "grade": "7",
        "subject": "mathematics",
        "difficulty": "medium",
        "language": "en",
        "standards": ["7.EE.B.4"]
      },
      "image_url": "null",
      "additional_details": "Conceptual explanation that builds deep understanding of why algebraic procedures work, not just how to perform them."
    },
    {
      "id": "content_with_image",
      "type": "text",
      "title": "Visual Models in Mathematics Education",
      "content": "Visual models play a crucial role in mathematics education by providing concrete representations of abstract concepts. Research shows that students who learn mathematical concepts through multiple representations - including visual models, symbolic notation, and verbal descriptions - develop deeper understanding and better retention.\n\nDifferent types of visual models serve different purposes:\n\n1. **Array Models**: Used for multiplication and division, showing equal groups in rows and columns.\n2. **Fraction Bars**: Represent parts of a whole, making fraction operations more intuitive.\n3. **Bar Models (Tape Diagrams)**: Help students visualize relationships in word problems.\n4. **Number Lines**: Show position, distance, and relationships between numbers.\n5. **Area Models**: Connect geometric concepts to algebraic thinking.\n\nWhen teachers use high-quality visual representations that align with Direct Instruction principles, students build stronger conceptual foundations. These models should show only the given information (no answer leakage), use canonical representations appropriate for the concept, and maintain pedagogical clarity without unnecessary decorative elements.\n\nThe transition from concrete manipulatives to visual models to abstract symbols follows a progression that supports mathematical understanding across grade levels. This approach, grounded in cognitive science research, helps students construct mental models they can apply to new problems.",
      "skill": {
        "title": "Visual Mathematics Pedagogy",
        "grade": "5",
        "subject": "mathematics",
        "difficulty": "medium",
        "language": "en",
        "standards": []
      },
      "image_url": "https://drive.google.com/uc?export=view&id=1QKIh_k0BKs6yIZujSsHjkhAax9WPlLxG",
      "additional_details": "This content explains the pedagogical value of visual models in mathematics, with an accompanying image demonstrating an array model. This showcases how the DI image evaluator handles educational content with supporting visuals."
    }
  ],
  "generated_articles": [
    {
      "id": "article_proportional_reasoning",
      "type": "article",
      "content": "# Understanding Proportional Reasoning\n\nProportional reasoning is a fundamental mathematical skill that involves understanding relationships between quantities. When two quantities maintain a constant ratio, they are said to be proportional. For example, if 2 pens cost 14 riyals, we can find the cost of any number of pens by maintaining this same ratio.\n\nThe key to solving proportional problems is identifying the **unit rate** - the cost or quantity per one item. In our pen example, dividing 14 by 2 gives us 7 riyals per pen. Once we know the unit rate, we can multiply it by any quantity to find the total cost.\n\nThis concept appears throughout mathematics and real life: in cooking recipes, map scales, speed calculations, and currency conversions. Understanding proportional reasoning helps students develop algebraic thinking and prepares them for more advanced mathematical concepts.\n\n## Visual Models in Mathematics\n\nVisual models help us understand mathematical relationships more clearly. Bar models are particularly useful for representing proportional relationships.\n\n![Bar Model Poster showing Part-Whole and Comparison Models](https://ecdn.teacherspayteachers.com/thumbitem/Bar-Model-Poster-for-Elementary-Students-Part-Whole-and-Comparison-Models-14426442-1757863928/original-14426442-1.jpg)\n\nThe image above shows different types of bar models used in elementary mathematics. These models help students visualize how parts combine to make a whole and how quantities compare to each other.\n\n### Practice Problem 1\n\n**Question:** The poster shows different types of bar models. What are the two main types of bar models shown for problem-solving?\n\n**A)** Addition and Subtraction Models  \n**B)** Part-Whole and Comparison Models ✓  \n**C)** Equal Groups and Array Models  \n**D)** Number Line and Area Models  \n\n**Answer:** B) Part-Whole and Comparison Models\n\n**Explanation:** The poster displays two fundamental types of bar models used in elementary mathematics: Part-Whole models (which show how parts combine to make a whole) and Comparison models (which show the relationship between two or more quantities). These are essential problem-solving tools that help students visualize mathematical relationships.\n\n---\n\n## Applying Proportional Reasoning\n\nNow let's apply proportional reasoning to a real-world problem. Consider the scenario where we know the cost of a small quantity and need to find the cost of a larger quantity.\n\n![Visual representation of the pen problem](https://i.ibb.co/z9wgjWG/Chat-GPT-Image-Oct-27-2025-05-24-13-PM.png)\n\n### Practice Problem 2\n\n**Question:** Based on the image above, if 2 pens cost 14 riyals, how much would 5 pens cost at the same rate?\n\n**A)** 28 riyals  \n**B)** 30 riyals  \n**C)** 35 riyals ✓  \n**D)** 40 riyals  \n\n**Answer:** C) 35 riyals\n\n**Explanation:** The image shows that 2 pens cost 14 riyals. To find the cost of 5 pens, we use proportional reasoning:\n\n**Step 1:** Find the unit rate (cost per pen)  \n14 riyals ÷ 2 pens = 7 riyals per pen\n\n**Step 2:** Multiply by the new quantity  \n7 riyals/pen × 5 pens = 35 riyals\n\nThis maintains the same proportional relationship between the number of pens and their total cost.\n\n---\n\n## Solving Step by Step\n\nLet's break down the solution process in detail:\n\n### Step 1: Identify what we know\n- 2 pens cost 14 riyals\n- We need to find the cost of 5 pens\n- The rate (price per pen) stays constant\n\n### Step 2: Find the unit rate\nThe unit rate is the cost of one item:\n\n```\nUnit rate = Total cost ÷ Number of items\nUnit rate = 14 ÷ 2 = 7 riyals per pen\n```\n\n### Step 3: Apply the unit rate\nNow multiply the unit rate by the desired quantity:\n\n```\nCost of 5 pens = Unit rate × Number of pens\nCost of 5 pens = 7 × 5 = 35 riyals\n```\n\n### Step 4: Verify the answer\nWe can verify by checking if the ratio stays constant:\n- Original ratio: 14:2 = 7:1\n- New ratio: 35:5 = 7:1 ✓\n\nThe ratios match, confirming our answer is correct!\n\n---\n\n## Connection to Algebra\n\nProportional reasoning forms the foundation for algebraic thinking. When we work with proportions, we're actually working with equations that can be solved algebraically.\n\n### Practice Problem 3\n\n**Question:** What is the value of x in the equation 3x + 7 = 22?\n\n**A)** 3  \n**B)** 4  \n**C)** 5 ✓  \n**D)** 6  \n\n**Answer:** C) 5\n\n**Explanation:** To solve this linear equation, we isolate the variable:\n\n**Step 1:** Start with the equation  \n3x + 7 = 22\n\n**Step 2:** Subtract 7 from both sides  \n3x = 22 - 7  \n3x = 15\n\n**Step 3:** Divide both sides by 3  \nx = 15 ÷ 3  \nx = 5\n\n**Step 4:** Verify by substituting back  \n3(5) + 7 = 15 + 7 = 22 ✓\n\nThis demonstrates how algebraic thinking extends the concepts we use in proportional reasoning.\n\n---\n\n## Historical Context\n\nThe concept of proportional reasoning has deep roots in the history of mathematics.\n\n### The Origins of Algebra\n\nThe word \"algebra\" comes from the Arabic word **\"al-jabr\"**, which means \"reunion of broken parts.\" This mathematical discipline was formalized by the Persian mathematician **Muhammad ibn Musa al-Khwarizmi** in the 9th century.\n\nAl-Khwarizmi wrote a groundbreaking book called *\"The Compendious Book on Calculation by Completion and Balancing,\"* which introduced systematic methods for solving linear and quadratic equations. His work built upon earlier contributions from Babylonian, Greek, and Indian mathematicians.\n\n### Legacy and Modern Applications\n\nThe methods al-Khwarizmi developed for solving equations - including working with proportional relationships - are still taught in classrooms around the world today. His systematic approach made algebra accessible to a wider audience and laid the foundation for modern mathematics.\n\nToday, proportional reasoning appears in countless real-world applications:\n\n- **Cooking:** Scaling recipes up or down\n- **Maps:** Converting map distances to real distances using scale\n- **Speed:** Calculating distance, rate, and time relationships\n- **Currency:** Converting between different monetary systems\n- **Medicine:** Calculating proper medication dosages based on body weight\n- **Construction:** Scaling architectural plans to actual dimensions\n\n---\n\n## Summary\n\nIn this article, we explored:\n\n1. ✓ **What proportional reasoning is** - understanding constant ratios between quantities\n2. ✓ **How to find unit rates** - dividing to find the value per one item\n3. ✓ **Visual models** - using bar models to represent relationships\n4. ✓ **Step-by-step problem solving** - systematic approach to proportional problems\n5. ✓ **Algebraic connections** - how proportions relate to equations\n6. ✓ **Historical context** - the origins of algebra and its applications\n\nProportional reasoning is a powerful mathematical tool that helps us solve real-world problems and prepares us for more advanced mathematics. By understanding the relationships between quantities and maintaining constant ratios, we can tackle complex problems with confidence.\n\n---\n\n### Try It Yourself!\n\nNow that you understand proportional reasoning, try solving these problems:\n\n1. If 3 books cost 45 dollars, how much would 7 books cost?\n2. A car travels 120 miles in 2 hours. How far will it travel in 5 hours at the same speed?\n3. A recipe calls for 2 cups of flour for 12 cookies. How much flour is needed for 30 cookies?\n\nRemember to:\n- Identify what you know\n- Find the unit rate\n- Apply it to the new quantity\n- Verify your answer\n\nHappy calculating! 🧮",
      "skill": {
        "title": "Proportional Reasoning",
        "grade": "6",
        "subject": "mathematics",
        "difficulty": "medium",
        "language": "en",
        "standards": ["6.RP.A.1", "6.RP.A.2", "6.RP.A.3"]
      },
      "title": "Understanding Proportional Reasoning",
      "language": "en",
      "additional_details": "Comprehensive article combining conceptual explanations, visual aids, embedded practice problems with solutions, step-by-step walkthroughs, historical context, and real-world applications. Designed for Grade 6 mathematics students learning proportional reasoning."
    }
  ],
  "verbose": "false"
}


    json_output = json.dumps(example_data, indent=2, ensure_ascii=False)

    with open(output, 'w', encoding='utf-8') as f:
        f.write(json_output)
    click.echo(f"✅ Sample file saved to: {output}")

if __name__ == '__main__':
    cli()
