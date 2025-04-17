from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.chat_models.base import BaseChatModel
from sqlalchemy import desc
from .coder import GeneratedFile

# Output Structure
# Output Structure
class FileIssue(BaseModel):
    """Represents a File that needs Code fixing with all the Issues listed"""
    filename: str = Field(..., description="Path of the file containing the issue")
    issues: List[str] = Field(..., description="List of all the Issues that shall be fixed in the given File.")


class CodebaseFeedback(BaseModel):
    """Represents review of the Master node with only files that needs fixing with it's feedback"""
    satisfied : bool = Field(..., description="'False' if only no files need code fixing, else 'True'")
    file_issues : List[FileIssue] = Field(..., description="List of all files that have code issues and their issues") 


# Prompt
MASTER_REVIEW_PROMPT = """
You are an expert Python code reviewer.

Review the following codebase and identify only the files that contain issues.

For each problematic file, provide:
- A clear list of issues in that file
- Only include files that need improvements
- Ignore files that are already well-written

Focus on:
- Code structure & clarity
- Naming, documentation, and type hints
- Error handling & edge cases
- Adherence to Python best practices
- Maintainability & design

Only respond in the specified structured format.

Codebase:
{codebase}
"""


# Create chat prompt template
chat_prompt = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template(MASTER_REVIEW_PROMPT)
])

def review_codebase(
    generated_files: Dict[str, GeneratedFile],
    llm: BaseChatModel,
) -> CodebaseFeedback:
    """
    Reviews the entire codebase and provides comprehensive feedback.
    
    Args:
        generated_files (Dict[str, GeneratedFile]): Mapping of file paths to their generated code
        llm (BaseChatModel): The LangChain chat model to use for review
        
    Returns:
        CodebaseFeedback: Comprehensive feedback on the entire codebase
    """
    # Create output parser
    parser = PydanticOutputParser(pydantic_object=CodebaseFeedback)
    
    # Format the codebase for review
    codebase_str = "\n\n".join([
        f"File: {path}\n{'='*50}\n{file.content}"
        for path, file in generated_files.items()
    ])
    
    # Format the prompt
    prompt = chat_prompt.format_messages(
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
        raise ValueError(f"Failed to parse LLM response into CodebaseFeedback: {str(e)}")

if __name__ == "__main__":
    pass

