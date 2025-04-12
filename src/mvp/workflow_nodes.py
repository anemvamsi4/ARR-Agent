from pathlib import Path
from typing import Dict, List, Optional

from langchain_core.messages import HumanMessage

from extraction import PDFTextExtractor
from llms import get_llm
from prompts.mvp_prompts import planner_prompt, master_prompt, fixer_prompt
from output_structures import PlannerResponse, MasterReviewResponse
from helpers import group_codeblocks_by_file, get_file_prompts, join_codebase, get_fix_prompts

def extract_text(pdf_path: str, output_dir: str) -> str:
    """
    Extract text content from a PDF file and save as markdown.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save extracted markdown
        
    Returns:
        str: Extracted text content in markdown format
    """
    markdown_file = str(Path.joinpath(output_dir, Path(pdf_path).stem, Path(pdf_path).stem)) + '.md'
    
    # Check if markdown already exists
    if Path.exists(markdown_file):
        with open(markdown_file, "r", encoding="utf-8") as file:
            return file.read()
            
    # Extract and save markdown
    return PDFTextExtractor(pdf_path, Path.joinpath(output_dir, Path(pdf_path).stem)).extract()


def code_planner(context: str, llm, user_input: Optional[str] = None) -> PlannerResponse:
    """
    Generate a structured plan for the codebase based on context.
    
    Args:
        context: Text content to analyze
        llm: Language model to use for planning
        user_input: Optional specific instructions for planning
        
    Returns:
        PlannerResponse: Structured plan of code blocks
    """
    if user_input is None:
        user_input = "Give me a plan of codebase structure to reproduce all results from this paper content"
    
    # Create and execute planning prompt
    final_prompt = planner_prompt.format(context=context, user_input=user_input)
    planner_llm = llm.with_structured_output(PlannerResponse)
    return planner_llm.invoke(final_prompt)


def coder(planner_response: PlannerResponse, llm) -> Dict[str, str]:
    """
    Generate code for each file based on the plan.
    
    Args:
        planner_response: Structured plan of code blocks
        llm: Language model to use for code generation
        
    Returns:
        Dict[str, str]: Mapping of filenames to their generated code
    """
    # Group code blocks by file
    files = group_codeblocks_by_file(planner_response.codeblocks)
    filenames = list(files.keys())
    
    # Generate prompts for each file
    file_prompts = [get_file_prompts(filename, blocks) for filename, blocks in files.items()]
    
    # Generate code in parallel
    results = llm.batch(file_prompts)
    return dict(zip(filenames, results))


def master_review_node(plan_response: PlannerResponse, code_response_dict: Dict[str, str], llm) -> MasterReviewResponse:
    """
    Review the generated codebase against the original plan.
    
    Args:
        plan_response: Original plan of code blocks
        code_response_dict: Generated code for each file
        llm: Language model to use for review
        
    Returns:
        MasterReviewResponse: Review results with issues and suggestions
    """
    # Combine all code for review
    full_codebase = join_codebase(code_response_dict)

    # Create and execute review prompt
    final_prompt = master_prompt.format(
        plan=plan_response.json(indent=2),
        codebase=full_codebase
    )

    structured_llm = llm.with_structured_output(MasterReviewResponse)
    return structured_llm.invoke(final_prompt)


def code_fixer(master_response: MasterReviewResponse, code_response_dict: Dict[str, str], llm, max_tries: int = 3) -> Dict[str, str]:
    """
    Fix code issues identified in the master review using parallel processing.
    
    Args:
        master_response: Review results with issues and suggestions
        code_response_dict: Current state of code files
        llm: Language model to use for fixing
        max_tries: Maximum number of fix attempts per file
        
    Returns:
        Dict[str, str]: Updated code files with fixes applied
    """
    # Early return if no fixes needed
    if not master_response.files_to_fix:
        return code_response_dict
    
    # Get fix prompts for files with issues
    fix_prompts = get_fix_prompts(master_response.files_to_fix, code_response_dict)
    
    # Process fixes in parallel
    fixed_codes = llm.batch(list(fix_prompts.values()))
    
    # Update code response
    fixed_files = dict(zip(fix_prompts.keys(), fixed_codes))
    code_response_dict.update(fixed_files)
    
    return code_response_dict