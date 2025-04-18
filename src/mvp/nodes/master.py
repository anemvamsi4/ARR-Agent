from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.chat_models.base import BaseChatModel

from .coder import GeneratedFile
from .code_planner import FilePlan

# Output Structure
class FileIssue(BaseModel):
    """Represents a File that needs Code fixing with all the Issues listed"""
    filename: str = Field(..., description="Path of the file containing the issue")
    issues: List[str] = Field(..., description="List of all the Issues that shall be fixed in the given File.")


class CodebaseFeedback(BaseModel):
    """Represents review of the Master node with only files that needs fixing with it's feedback"""

    satisfied : bool = Field(..., description="'True' if the codebase meets the requirements and has no major issues, 'False' otherwise.")
    file_issues : List[FileIssue] = Field(..., description="List of all files that have code issues and their issues. If 'satisfied' is True, this list should be empty.")


# Prompt
MASTER_REVIEW_PROMPT = """
You are an expert Python code reviewer.

Review the following codebase against the provided plan and identify only the files that contain issues or deviate significantly from the plan.

Code Plan:
{code_plan}

Codebase:
{codebase}

For each problematic file, provide:
- A clear list of issues in that file (e.g., deviations from the plan, bugs, style issues)
- Only include files that need improvements or corrections
- Ignore files that are already well-written and align with the plan

Focus on:
- Adherence to the provided code plan (structure, components, purpose)
- Code structure & clarity
- Naming, documentation, and type hints
- Error handling & edge cases
- Adherence to Python best practices
- Maintainability & design

Only respond in the specified structured format. If the codebase is satisfactory and aligns with the plan, respond with 'satisfied' as true and an empty list for 'file_issues'.
"""



chat_prompt = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template(MASTER_REVIEW_PROMPT)
])

def review_codebase(
    generated_files: Dict[str, GeneratedFile],
    plan_response: Dict[str, FilePlan],
    llm: BaseChatModel,
) -> CodebaseFeedback:
    """
    Reviews the entire codebase against the plan and provides comprehensive feedback.

    Args:
        generated_files (Dict[str, GeneratedFile]): Mapping of file paths to their generated code
        plan_response (Dict[str, FilePlan]): Mapping of file paths to their planned structure and content.
        llm (BaseChatModel): The LangChain chat model to use for review

    Returns:
        CodebaseFeedback: Comprehensive feedback on the entire codebase, focusing on issues and plan deviations.
    """
    # Create output parser
    parser = PydanticOutputParser(pydantic_object=CodebaseFeedback)

    # Format the codebase for review
    codebase_str = "\n\n".join([
        f"--- File: {path} ---\n{file.content}"
        for path, file in generated_files.items()
    ])

    plan_str = "\n\n".join([
        f"--- Plan for: {path} ---\n{plan.model_dump_json(indent=2)}"
        for path, plan in plan_response.items()
    ])

    # Format the prompt
    prompt = chat_prompt.format_messages(
        code_plan=plan_str,
        codebase=codebase_str
    )
    prompt[-1].content += f"\n{parser.get_format_instructions()}"

    # Generate response from LLM
    response = llm.invoke(prompt)

    # Parse the response into CodebaseFeedback
    try:
        feedback = parser.parse(response.content)

        return feedback
    except Exception as e:
        raise ValueError(f"Failed to parse LLM response into CodebaseFeedback: {str(e)}\nResponse content:\n{response.content}")
    
if __name__ == "__main__":
    pass