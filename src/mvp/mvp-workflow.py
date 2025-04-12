import dotenv
from pathlib import Path
from typing_extensions import TypedDict
from typing import Dict, Optional

from langgraph.graph import StateGraph, START, END

from llms import get_llm
from workflow_nodes import *
from output_structures import PlannerResponse, MasterReviewResponse

dotenv.load_dotenv()


class State(TypedDict):
    """
    State dictionary for the workflow.
    
    Attributes:
        input: User input for the workflow
        pdf_path: Path to the PDF file
        output_dir: Directory for output files
        extracted_text: Extracted text from PDF
        plan_response: Generated code plan
        code_response: Generated code files
        master_response: Review results
        fix_attempts: Number of fix attempts made
        max_fix_attempts: Maximum number of fix attempts allowed
    """
    input: str
    pdf_path: str
    output_dir: str
    extracted_text: Optional[str]
    plan_response: Optional[PlannerResponse]
    code_response: Optional[Dict[str, str]]
    master_response: Optional[MasterReviewResponse]
    fix_attempts: int
    max_fix_attempts: int


def extract_text_node(state: State) -> State:
    """
    Extract text from PDF file.
    
    Args:
        state: Current workflow state
        
    Returns:
        State: Updated state with extracted text
    """
    state["extracted_text"] = extract_text(state["pdf_path"], state["output_dir"])
    return state


def code_planner_node(state: State) -> State:
    """
    Generate code plan from extracted text.
    
    Args:
        state: Current workflow state
        
    Returns:
        State: Updated state with code plan
    """
    llm = get_llm()
    state["plan_response"] = code_planner(state["extracted_text"], llm, state["input"])
    return state


def coder_node(state: State) -> State:
    """
    Generate code based on the plan.
    
    Args:
        state: Current workflow state
        
    Returns:
        State: Updated state with generated code
    """
    llm = get_llm()
    state["code_response"] = coder(state["plan_response"], llm)
    return state


def master_review_node(state: State) -> State:
    """
    Review generated code against the plan.
    
    Args:
        state: Current workflow state
        
    Returns:
        State: Updated state with review results
    """
    llm = get_llm()
    state["master_response"] = master_review_node(
        state["plan_response"],
        state["code_response"],
        llm
    )
    return state


def code_fixer_node(state: State) -> State:
    """
    Fix code issues identified in review.
    
    Args:
        state: Current workflow state
        
    Returns:
        State: Updated state with fixed code
    """
    llm = get_llm()
    
    # Increment fix attempts
    state["fix_attempts"] = state.get("fix_attempts", 0) + 1
    
    # Fix code
    state["code_response"] = code_fixer(
        state["master_response"],
        state["code_response"],
        llm,
        max_tries=state.get("max_fix_attempts", 3)
    )
    return state


def should_continue(state: State) -> bool:
    """
    Determine if workflow should continue fixing code.
    
    Args:
        state: Current workflow state
        
    Returns:
        bool: True if should continue, False otherwise
    """
    max_attempts = state.get("max_fix_attempts", 3)
    current_attempts = state.get("fix_attempts", 0)
    
    return (
        not state["master_response"].overall_satisfied 
        and current_attempts < max_attempts
    )


def create_workflow() -> StateGraph:
    """
    Create the workflow graph.
    
    Args:
        max_fix_attempts: Maximum number of fix attempts allowed
        
    Returns:
        StateGraph: Compiled workflow graph
    """
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_node("extract_text", extract_text_node)
    workflow.add_node("code_planner", code_planner_node)
    workflow.add_node("coder", coder_node)
    workflow.add_node("master_review", master_review_node)
    workflow.add_node("code_fixer", code_fixer_node)
    
    # Add edges
    workflow.add_edge(START, "extract_text")
    workflow.add_edge("extract_text", "code_planner")
    workflow.add_edge("code_planner", "coder")
    workflow.add_edge("coder", "master_review")
    workflow.add_conditional_edges(
        "master_review",
        should_continue,
        {
            True: "code_fixer",
            False: END
        }
    )
    workflow.add_edge("code_fixer", "master_review")
    
    return workflow.compile()


if __name__ == "__main__":
    workflow = create_workflow()
    # Example usage:
    state = {
        "input": "Give me a plan of codebase structure to reproduce all results from this paper content",
        "pdf_path": "path/to/paper.pdf",
        "output_dir": "path/to/output",
        "max_fix_attempts": 3
    }
    result = workflow.invoke(state)

