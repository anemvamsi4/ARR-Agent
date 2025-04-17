from typing import Dict
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chat_models.base import BaseChatModel
from .master import CodebaseFeedback
from .coder import GeneratedFile

# Prompt template for fixing code
CODE_FIXER_PROMPT = """
You are an expert Python developer.

You are given a file and a list of code issues within that file.
Your task is to fix the issues and return the full updated code.
Do not include explanations — only return the fixed code.

Filename: {filename}

Original Code:
--------------------
{code}

Issues:
--------------------
{issues}

Provide the corrected code only:
"""

chat_prompt = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template(CODE_FIXER_PROMPT)
])

def fix_code_issues(
    codebase_feedback: CodebaseFeedback,
    generated_files: Dict[str, GeneratedFile],
    llm: BaseChatModel,
) -> Dict[str, GeneratedFile]:
    """
    Fixes issues in files identified by the codebase feedback using batch LLM calls.

    Args:
        codebase_feedback (CodebaseFeedback): Feedback including which files need fixing.
        generated_files (Dict[str, GeneratedFile]): Original file contents.
        llm (BaseChatModel): LangChain chat model to apply fixes.

    Returns:
        Dict[str, GeneratedFile]: Mapping of fixed file paths to their updated content.
    """
    prompts = []
    file_paths = []

    for file_issue in codebase_feedback.file_issues:
        path = file_issue.filename
        original_code = generated_files[path].content
        issues_text = "\n".join(f"- {issue}" for issue in file_issue.issues)

        prompt = chat_prompt.format_messages(
            filename=path,
            code=original_code,
            issues=issues_text
        )
        prompts.append(prompt)
        file_paths.append(path)

    # Batch call to the LLM
    responses = llm.batch(prompts)

    # Create updated file objects
    fixed_files: Dict[str, GeneratedFile] = {}
    for path, response in zip(file_paths, responses):
        fixed_files[path] = GeneratedFile(
            path=path,
            content=response.content
        )

    return fixed_files