from pathlib import Path

from langchain_core.messages import HumanMessage

from extraction import PDFTextExtractor
from llms import get_llm
from prompts import planner_prompt, master_prompt
from output_structures import PlannerResponse, MasterReviewResponse
from helpers import group_codeblocks_by_file, get_file_prompts, join_codebase

def extract_text(pdf_path: str, output_dir: str):
    markdown_file = str(Path.joinpath(output_dir, Path(pdf_path).stem, Path(pdf_path).stem)) + '.md'
    if Path.exists(markdown_file):
        with open(markdown_file, "r", encoding="utf-8") as file:
            markdown_text = file.read()
            
    markdown_text = PDFTextExtractor(pdf_path, Path.joinpath(output_dir, Path(pdf_path).stem)).extract()

    return markdown_text


def code_planner(context: str, llm, user_input: str = None) -> PlannerResponse:
    if user_input is None:
        user_input = "Give me a plan of codebase structure to reproduce all results from this paper content"
    
    
    final_prompt = planner_prompt.format(context = context, user_input = user_input)
    planner_llm = llm.with_structured_output(PlannerResponse)
    plan_response = planner_llm.invoke(final_prompt)
    return plan_response

def coder(planner_response, llm):
    files = group_codeblocks_by_file(planner_response.codeblocks)
    file_prompts = [get_file_prompts(filename, blocks) for filename, blocks in files.items()]
    filenames = list(files.keys())

    results = llm.batch(file_prompts)
    return dict(zip(filenames, results))

def master_review_node(plan_response, code_response_dict, llm):
    # Combine all code for review
    full_codebase = join_codebase(code_response_dict)

    final_prompt = master_prompt.format(
        plan=plan_response.json(indent=2),
        codebase=full_codebase
    )

    structured_llm = llm.with_structured_output(MasterReviewResponse)
    return structured_llm.invoke(final_prompt)