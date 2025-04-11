import dotenv
from pathlib import Path
import operator
from typing import Annotated, List, Tuple
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent

from llms import get_llm
dotenv.load_dotenv()

class State(TypedDict):
    input: str





