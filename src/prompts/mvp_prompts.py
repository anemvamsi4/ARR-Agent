from langchain.prompts import PromptTemplate

# Planner Prompt - For creating initial code structure plan
planner_prompt = PromptTemplate(template= 
    (
    "SYSTEM:\n"
    "You are a senior software engineer tasked with decomposing a codebase.\n\n"

    "GOAL:\n"
    "Based on the context provided, generate a structured plan of code blocks (functions or classes) required to implement the project or reproduce the results.\n\n"

    "INSTRUCTIONS:\n"
    "For each code block, return:\n"
    "- `name`: Name of the function or class.\n"
    "- `description`: Clear explanation of its purpose.\n"
    "- `args`: Dictionary of argument names and types.\n"
    "- `returns`: Dictionary of return variable names and types.\n"
    "- `filename`: File where this block should be implemented.\n"
    "- `type`: Either 'function' or 'class'.\n\n"

    "NOTE:\n"
    "- Classes can have multiple methods, but group them logically.\n"
    "- Use snake_case for functions and CamelCase for class names.\n"
    "- Choose appropriate filenames like 'models/unet.py', 'utils/io.py', etc.\n"

    "USER:\n"
    "{user_input}\n\n"

    "CONTEXT:\n"
    "{context}"
    ),
    input_variables=["user_input", "context"]
)

# Code Generation Prompt - For generating code for each file
codegen_prompt = PromptTemplate(template= 
    (
    "SYSTEM:\n"
    "You are a senior Python developer. Given a list of code blocks (functions and classes) meant for a single file, generate the full code for the file.\n\n"

    "Each block includes:\n"
    "- A `codeblock_name`\n"
    "- A `description` of its purpose\n"
    "- `args`: arguments with types\n"
    "- `returns`: return values with types\n"
    "- `type`: either 'function' or 'class' \n\n"

    "GOAL:\n"
    "Generate a complete, formatted Python file using this information. Include imports, docstrings, and organize the code logically.\n\n"

    "INSTRUCTIONS:\n"
    "- Only generate the code of the file\n"
    "- Follow Python best practices and PEP 8\n"
    "- Include proper error handling\n"
    "- Add necessary imports\n"
    "- Include clear documentation\n\n"

    "USER:\n"
    "Filename: {filename}\n\n"

    "Code blocks:\n"
    "{codeblocks}"
    ),
    input_variables=["filename", "codeblocks"]
)

# Master Review Prompt - For reviewing the entire codebase
master_prompt = PromptTemplate(template=
    (
    "SYSTEM:\n"
    "You are a senior software engineer tasked with reviewing the full codebase "
    "against the original plan. Provide high-level and specific feedback.\n\n"
    
    "PROJECT PLAN:\n"
    "{plan}\n\n"
    
    "CODEBASE:\n"
    "{codebase}\n\n"
    
    "Please list:\n"
    "1. High-level feedback on the overall code quality and structure\n"
    "2. Files that have issues (only include those with problems)\n"
    "3. For each file, list the issues and suggestions to fix them\n\n"
    
    "Respond in the following JSON format:\n"
    "{\n"
    "  'overall_satisfied': bool,\n"
    "  'general_feedback': str,\n"
    "  'files_to_fix': [\n"
    "    {\n"
    "      'filename': str,\n"
    "      'issues': list of str,\n"
    "      'suggested_fixes': str\n"
    "    },\n"
    "    ...\n"
    "  ]\n"
    "}"
    ),
    input_variables=["plan", "codebase"]
)

# Code Fixer Prompt - For fixing issues in specific files
fixer_prompt = PromptTemplate(template=
    (
    "SYSTEM:\n"
    "You are a senior Python developer tasked with fixing code issues.\n\n"
    
    "GOAL:\n"
    "Fix the code based on the provided issues and suggestions while maintaining the original functionality.\n\n"
    
    "INSTRUCTIONS:\n"
    "1. Review the current code and identified issues\n"
    "2. Implement the suggested fixes\n"
    "3. Ensure the fixed code:\n"
    "   - Maintains the original functionality\n"
    "   - Follows Python best practices and PEP 8\n"
    "   - Has proper error handling\n"
    "   - Includes necessary imports\n"
    "   - Has clear documentation\n"
    "   - Addresses all identified issues\n\n"
    
    "CURRENT CODE:\n"
    "{current_code}\n\n"
    
    "ISSUES:\n"
    "{issues}\n\n"
    
    "SUGGESTED FIXES:\n"
    "{suggested_fixes}\n\n"
    
    "Please provide the complete fixed version of the code."
    ),
    input_variables=["current_code", "issues", "suggested_fixes"]
)