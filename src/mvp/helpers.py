from typing import List, Union, Dict, Literal
from collections import defaultdict

from output_structures import FunctionPlan, ClassPlan
from prompts import codegen_prompt

def group_codeblocks_by_file(codeblocks: List[Union[FunctionPlan, ClassPlan]]):
    files = defaultdict(list)
    for block in codeblocks:
        files[block.filename].append(block)
    return files

def get_file_prompts(filename: str, blocks: List[Union[FunctionPlan, ClassPlan]]):
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
