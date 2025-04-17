from typing import List, Dict, Optional, Union, Literal
from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.chat_models.base import BaseChatModel
from .codebase_structure import FileDescription, CodebaseStructure

# Output Structures
class CodeBlockPlan(BaseModel):
    """Base structure defining the blueprint for a method in a class.
    This serves as a template for the code generator to understand the structure and requirements
    of the code block before implementation."""
    name: str = Field(..., description="The identifier of the code block, following Python naming conventions")
    description: str = Field(..., description="A concise explanation of what the code block does and its purpose in the system")
    args: Dict[str, str] = Field(..., description="Mapping of parameter names to their expected types (e.g., {'name': 'str', 'age': 'int'})")
    returns: Dict[str, str] = Field(..., description="Mapping of return value names to their types (e.g., {'result': 'bool', 'message': 'str'})")

class FunctionPlan(CodeBlockPlan):
    """Structure defining the blueprint for a standalone function in the codebase.
    This provides the code generator with all necessary information to implement
    the function according to the specified requirements."""
    type: Literal["function"] = "function"

class ClassPlan(BaseModel):
    """Generate a complete class structure with all its methods and attributes.
    The LLM should provide all class details including its methods (as CodeBlockPlans),
    attributes, and implementation location in a single response."""
    type: Literal["class"] = "class"
    name: str = Field(..., description="Class name in PascalCase (e.g., 'ImageProcessor', 'DataLoader')")
    description: str = Field(..., description="Clear explanation of the class's core functionality and purpose")
    attributes: Dict[str, str] = Field(..., description="Class attributes with their types (e.g., {'batch_size': 'int', 'model': 'nn.Module'})")
    methods: List[CodeBlockPlan] = Field(..., description="List of all methods the class should implement")

class FilePlan(BaseModel):
    """Complete plan for a single file containing all its classes and functions.
    This structure represents everything that needs to be implemented in a single file."""
    filename: str = Field(..., description="The relative path of the file (e.g., 'src/models/processor.py')")
    description: str = Field(..., description="Overall purpose and responsibility of this file")
    imports: List[str] = Field(..., description="List of required imports for this file")
    classes: List[ClassPlan] = Field(..., description="List of all classes to be implemented in this file")
    functions: List[FunctionPlan] = Field(..., description="List of all standalone functions to be implemented in this file")

# Prompt
CODE_PLANNER_PROMPT = """
You are an expert at analyzing code requirements and creating detailed implementation plans for individual files.
Your task is to create a complete plan for a single file, including all its classes, methods, and functions.

For the given file requirements, create a comprehensive plan that includes:

1. File Overview:
   - Clear purpose and responsibilities
   - Required imports and dependencies
   - Overall structure and organization

2. Classes:
   - Class names and purposes
   - All attributes with their types
   - All methods with their signatures
   - Method parameters and return types

3. Standalone Functions:
   - Function names and purposes
   - Input parameters and types
   - Return values and types

The plan should be complete enough for direct implementation and follow Python best practices.

Inputs:
1. File Path: {file_path}
2. File Description: {file_description}
3. Dependencies: {dependencies}

Generate the complete file plan following the FilePlan format.
"""

# Create chat prompt template
chat_prompt = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template(CODE_PLANNER_PROMPT)
])

def generate_file_plans(
    codebase_structure: CodebaseStructure,
    llm: BaseChatModel,
) -> Dict[str, FilePlan]:
    """
    Generates file plans for all files in the codebase structure using batch processing.
    
    Args:
        codebase_structure (CodebaseStructure): The complete codebase structure
        llm (BaseChatModel): The LangChain chat model to use for generation
        
    Returns:
        Dict[str, FilePlan]: Mapping of file paths to their generated plans
    """
    # Create output parser
    parser = PydanticOutputParser(pydantic_object=FilePlan)
    
    # Prepare all prompts
    prompts = []
    for file_desc in codebase_structure.files:
        prompt = chat_prompt.format_messages(
            file_path=file_desc.path,
            file_description=file_desc.description,
            dependencies=", ".join(file_desc.dependencies)
        )
        prompt[-1].content += f"\n{parser.get_format_instructions()}"
        prompts.append(prompt)
    
    # Generate responses for all files
    responses = llm.batch(prompts)
    
    # Process responses
    results: Dict[str, FilePlan] = {}
    for file_desc, response in zip(codebase_structure.files, responses):
        try:
            plan = parser.parse(response.content)
            results[file_desc.path] = plan
        except Exception as e:
            print(f"Failed to generate plan for {file_desc.path}: {str(e)}")
    
    return results

if __name__ == "__main__":
    pass