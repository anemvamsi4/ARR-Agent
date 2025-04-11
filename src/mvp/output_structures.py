from pydantic import BaseModel, Field
from typing import List, Dict, Literal, Union

# Code Planning
class CodeBlockPlan(BaseModel):
    name: str = Field(..., description="Name of the codeblock(function or method)")
    description: str = Field(..., description= "Short and clear explaination of codeblock's role")
    args : Dict[str, str] = Field(..., "Dictionary mapping of argument names to types")
    returns: Dict[str, str] = Field(..., description="Dictionary mapping of return variable names to types")

class FunctionPlan(CodeBlockPlan):
    type: Literal["function"] = "function"
    filename: str = Field(..., description="Target file for this function, example: root/utils/helpers.py")

class ClassPlan(BaseModel):
    type: Literal["class"] = "class"
    name: str = Field(..., description="Name of the class")
    description: str = Field(..., description="Description of the class and what it does")
    attributes: Dict[str, str] = Field(..., description="Class attributes and their types")
    methods: List[CodeBlockPlan] = Field(..., description="Methods inside this class")
    filename: str = Field(..., description="Target file for this class, example: root/models/unet.py")

class PlannerResponse(BaseModel):
    codeblocks : List[Union[FunctionPlan, ClassPlan]] = Field(...,
                    description="All code units: either function or class; for the codebase")

# Code Generation
class FileCode(BaseModel):
    filename: str = Field(..., description="Name of the file with path, example: root/models/unet.py")
    code: str = Field(..., description="Python code of all codeblocks of it organized logically")