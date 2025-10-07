import json
from dotenv import load_dotenv
from typing import Annotated, Literal
from typing_extensions import TypedDict, List
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_cerebras import ChatCerebras
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.types import Command
from pydantic import BaseModel, Field

# ==== import envs ==== #
load_dotenv()

# import models
from AI.lg_models import *

# import system prompts
from AI.lg_prompt import *

# import agents
from AI.lg_agents import *


# ==== Define Graph ==== #
graph_builder = StateGraph(State)

# Adding Graph nodes; Nodes: ["orchastrator", "notes_agent", "yt_notes_agent", "summariser_agent", "career_guide_agent"]
graph_builder.add_node("orchastrator", orchastrator)
graph_builder.add_node("notes_agent", notes_agent)
graph_builder.add_node("yt_notes_agent", yt_notes_agent)
graph_builder.add_node("summariser_agent", summariser_agent)
graph_builder.add_node("career_guide_agent", career_guide_agent)

# Adding Graph edges
graph_builder.add_edge(START, "orchastrator")

# conditional edge between orchastrator and each agent
graph_builder.add_conditional_edges(
    "orchastrator",
    lambda state: state.get("next"),   # or use the `goto` returned in Command
    {
        "notes_agent": "notes_agent",
        "yt_notes_agent": "yt_notes_agent",
        "summariser_agent": "summariser_agent",
        "career_guide_agent": "career_guide_agent",
        "END": END
    }
)

# compile graph
lg_agent = graph_builder.compile()



# runner code
if __name__ == "__main__":
    while True:    
        user = input("User: ")

        if user in {"quit", "q", "exit"}:
            print("\nAget: GoodBye!")
            break

        else:
            response = lg_agent.invoke({"messages": [HumanMessage(content=user)]})
            print(f"Agent: {response['messages'][-1].content}")