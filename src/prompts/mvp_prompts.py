from langchain.prompts import PromptTemplate

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

    "CONTEXT\n:"
    "{context}"
    ),
    input_variables=["user_input", "context"]
)

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

    "NOTE:\n"
    "- Only generate the code of the file\n\n"

    "USER:\n"
    "Filename: {filename}\n\n"

    "Code blocks:\n"
    "{codeblocks}"
    ),
    input_variables=["filename", "codeblocks"]
)

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