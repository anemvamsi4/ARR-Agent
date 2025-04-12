from typing import List, Union, Dict, Literal
from collections import defaultdict

from output_structures import FunctionPlan, ClassPlan, FileIssue
from prompts.mvp_prompts import codegen_prompt, fixer_prompt

def group_codeblocks_by_file(codeblocks: List[Union[FunctionPlan, ClassPlan]]):
    """
    Group code blocks by their target filename.
    
    Args:
        codeblocks: List of function and class plans
        
    Returns:
        Dict[str, List[Union[FunctionPlan, ClassPlan]]]: Code blocks grouped by filename
    """
    files = defaultdict(list)
    for block in codeblocks:
        files[block.filename].append(block)
    return files

def get_file_prompts(filename: str, blocks: List[Union[FunctionPlan, ClassPlan]]):
    """
    Generate code generation prompt for a file.
    
    Args:
        filename: Target filename
        blocks: List of code blocks for the file
        
    Returns:
        str: Formatted prompt for code generation
    """
    block_descriptions = ""

    for block in blocks:
        if block.type == "function":
            block_descriptions += (
                f"\n---\nType: Function\n"
                f"Name: {block.name}\n"
                f"Description: {block.description}\n"
                f"Args: {block.args}\n"
                f"Returns: {block.returns}\n"
            )
        elif block.type == "class":
            block_descriptions += (
                f"\n---\nType: Class\n"
                f"Name: {block.name}\n"
                f"Description: {block.description}\n"
                f"Attributes: {block.attributes}\n"
            )
            for method in block.methods:
                block_descriptions += (
                    f"  Method: {method.name}\n"
                    f"  Description: {method.description}\n"
                    f"  Args: {method.args}\n"
                    f"  Returns: {method.returns}\n"
                )
    
    return codegen_prompt.format(filename=filename, codeblocks=block_descriptions)

def get_fix_prompts(file_issues: List[FileIssue], code_dict: Dict[str, str]) -> Dict[str, str]:
    """
    Generate fix prompts for files with issues.
    
    Args:
        file_issues: List of files with issues to fix
        code_dict: Current state of code files
        
    Returns:
        Dict[str, str]: Mapping of filenames to their fix prompts
    """
    fix_prompts = {}
    
    for file_issue in file_issues:
        filename = file_issue.filename
        current_code = code_dict.get(filename, "")
        issues = "\n".join(file_issue.issues)
        suggested_fixes = file_issue.suggested_fixes
        
        fix_prompts[filename] = fixer_prompt.format(
            current_code=current_code,
            issues=issues,
            suggested_fixes=suggested_fixes
        )
    
    return fix_prompts

def join_codebase(code_dict: Dict[str, str]):
    """
    Join all code files into a single string for review.
    
    Args:
        code_dict: Mapping of filenames to their code
        
    Returns:
        str: Combined codebase with file markers
    """
    full_codebase = ""
    for filename, code in code_dict.items():
        full_codebase += f"\n=== {filename} ===\n{code.strip()}\n"
    return full_codebase