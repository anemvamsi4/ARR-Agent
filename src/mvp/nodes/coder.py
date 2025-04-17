from typing import List, Dict, Optional, Union, Literal
from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chat_models.base import BaseChatModel
from .code_planner import FilePlan

# Output Structure
class GeneratedFile(BaseModel):
    """Represents a generated code file with its content and metadata."""
    path: str = Field(..., description="The relative path of the file")
    content: str = Field(..., description="The complete generated code content")

# Prompt
CODE_GENERATOR_PROMPT = """
You are an expert Python developer. Your task is to generate complete, working Python code based on the provided file plan.

The file plan includes:
1. File Overview:
   - Purpose and responsibilities
   - Required imports
   - Overall structure

2. Classes:
   - Class names and purposes
   - Attributes and their types
   - Methods with their signatures
   - Method parameters and return types

3. Standalone Functions:
   - Function names and purposes
   - Input parameters and types
   - Return values and types

Generate complete, working Python code that:
- Implements all specified classes and functions
- Includes proper imports
- Follows Python best practices
- Includes type hints
- Has clear documentation
- Handles edge cases appropriately

Input:
File Plan: {file_plan}

Generate the complete Python code for this file.
"""

# Create chat prompt template
chat_prompt = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template(CODE_GENERATOR_PROMPT)
])

def generate_code(
    file_plans: Dict[str, FilePlan],
    llm: BaseChatModel,
) -> Dict[str, GeneratedFile]:
    """
    Generates code for all files in the file plans using batch processing.
    
    Args:
        file_plans (Dict[str, FilePlan]): Mapping of file paths to their plans
        llm (BaseChatModel): The LangChain chat model to use for generation
        
    Returns:
        Dict[str, GeneratedFile]: Mapping of file paths to their generated code
    """
    # Prepare all prompts
    prompts = []
    for file_path, plan in file_plans.items():
        prompt = chat_prompt.format_messages(
            file_plan=plan.model_dump_json()
        )
        prompts.append(prompt)
    
    # Generate responses for all files
    responses = llm.batch(prompts)
    
    # Process responses
    results: Dict[str, GeneratedFile] = {}
    for (file_path, plan), response in zip(file_plans.items(), responses):
        try:
            results[file_path] = GeneratedFile(
                path=file_path,
                content=response.content
            )
        except Exception as e:
            print(f"Failed to generate code for {file_path}: {str(e)}")
            # Continue with other files even if one fails
    
    return results

if __name__ == "__main__":
    pass
