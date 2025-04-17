from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.chat_models.base import BaseChatModel

# Output Structure
class FileDescription(BaseModel):
    """
    Represents a file in the codebase with its path, purpose, and dependencies.
    Used by the LLM to understand and generate file's codeblocks structure.
    """
    path: str = Field(..., description="Relative path of the file from project root")
    description: str = Field(..., description="Clear description of the file's purpose and contents")
    dependencies: List[str] = Field(default_factory=list, description="List of other files this file depends on")

class CodebaseStructure(BaseModel):
    """Complete structure of the codebase with all files required."""
    files: List[FileDescription] = Field(..., description="List of all files in the codebase")
    project_structure: Dict[str, List[str]] = Field(..., description="Hierarchical structure of the project")
    main_components: List[str] = Field(..., description="List of main components/modules in the project")


# Prompt 
CODEBASE_STRUCTURE_PROMPT = """
You are an expert at analyzing research papers and creating a base plan for well-organized codebases.
Your task is to analyze the paper and user requirements to create a complete codebase structure.

Follow these steps:
1. Identify key implementation details from the paper:
   - Core algorithms and methods
   - Model architecture and components
   - Data processing requirements
   - Training and evaluation procedures

2. Make necessary assumptions for unspecified details:
   - Default hyperparameters
   - Common implementation patterns
   - Standard practices for the domain
   - Reasonable defaults for missing components

3. Create the codebase structure:
   - Determine all required files and their purposes
   - Identify dependencies between components
   - Organize files into logical directories
   - List main components of the project

For each file, provide:
- A clear path relative to project root
- A concise description of its purpose and contents
- Any files it depends on

The structure should be:
- Complete enough for implementation
- Focused on core components
- Include necessary utility files
- Account for both specified and assumed requirements

Inputs:
1. User Input: {user_input}
2. Paper Content (Markdown): {paper_markdown}

Generate the codebase structure following the CodebaseStructure format.
"""

# Create chat prompt template
chat_prompt = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template(CODEBASE_STRUCTURE_PROMPT)
])

def generate_codebase_structure(
    markdown_text: str,
    user_input: str,
    llm: BaseChatModel,
) -> CodebaseStructure:
    """
    Generates a codebase structure plan using a LangChain chat model.
    
    Args:
        markdown_text (str): The paper content in markdown format
        user_input (str): User's requirements and specifications
        llm (BaseChatModel): The LangChain chat model to use for generation
        
    Returns:
        CodebaseStructure: The generated codebase structure with files and organization
        
    Example:
        >>> from langchain.chat_models import ChatOpenAI
        >>> llm = ChatOpenAI(temperature=0.7)
        >>> structure = generate_codebase_structure(
        ...     markdown_text="Paper content...",
        ...     user_input="Implement with PyTorch",
        ...     llm=llm
        ... )
    """
    # Create output parser
    parser = PydanticOutputParser(pydantic_object=CodebaseStructure)
    
    # Format the prompt with inputs
    prompt = chat_prompt.format_messages(
        user_input=user_input,
        paper_markdown=markdown_text
    )
    
    # Add format instructions to the last message
    prompt[-1].content += f"\n{parser.get_format_instructions()}"
    
    # Generate response from LLM
    response = llm.invoke(prompt)
    
    # Parse the response into CodebaseStructure
    try:
        structure = parser.parse(response.content)
        return structure
    except Exception as e:
        raise ValueError(f"Failed to parse LLM response into CodebaseStructure: {str(e)}")

# Example usage
if __name__ == "__main__":
    pass