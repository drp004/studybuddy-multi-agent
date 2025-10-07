import json
from langgraph.graph import END
from langchain_cerebras import ChatCerebras
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.types import Command

# import response models
from AI.lg_models import *

# import system prompts
from AI.lg_prompt import *



# ==== Agents llm ==== #
# Orchastrator agent llm
orchastrator_llm = ChatCerebras(model="gpt-oss-120b", temperature=0.3).with_structured_output(OrchastratorResponse, strict=True)

# Raw notes generator agent llm
notes_agent_llm = ChatCerebras(model="gpt-oss-120b", temperature=0.3).with_structured_output(NotesResponse, strict=True)

# Audio Summariser agent llm
summariser_agent_llm = ChatCerebras(model="gpt-oss-120b", temperature=0.3).with_structured_output(SummaryResponse, strict=True)

# Career Guide agent llm
career_guide_agent_llm = ChatCerebras(model="gpt-oss-120b", temperature=0.3).with_structured_output(RoadmapResponse, strict=True)


# ==== Agents ==== #
# Orchastrator agent
def orchastrator(state: State):
    """ Orchastrator Node that routes the workflow according to current status and requirements of flow """

    # get User message
    user_message = state["messages"][-1]

    # prepare state for orchastrator
    messages = [
        SystemMessage(content=orchastrator_prompt),
        user_message
    ]

    # Get next agent for workflow
    orc_response = orchastrator_llm.invoke(messages)

    goto = orc_response.goto
    reason = orc_response.reason

    print(f"\n --- workflow Transition: Orchastrator -> {goto.upper()}")

    return Command(
        update={
            "messages": [HumanMessage(content=reason, name="Orchastrator")],
            "next": goto
        },
        goto=goto
    )

# Raw text Notes generator agent
def notes_agent(state: State):
    """ 
        Raw Text notes generator agent node that generate clear structured notes from raw text.
        Takes user input of raw text and generate well structured and detailed notes from that.
    """ 

    # get User message
    user_message = state["messages"][-2]

    # prepare state for notes generator agent
    messages = [
        SystemMessage(content=notes_agent_prompt),
        HumanMessage(content=user_message.content)
    ]

    # Generate notes from raw text
    notes_response = notes_agent_llm.invoke(messages)

    # convert pydantic model to python dict
    notes_dict = notes_response.model_dump()

    # convert python dict to json string
    notes_json = json.dumps(notes_dict)

    return Command(
        update={
            "messages": HumanMessage(content=notes_json, name="NotesGenerator"),
            "next": "END"
        },
        goto=END
    )

# YT Transcript Notes generator Agent
def yt_notes_agent(state: State):
    """ YT Notes generator agent that generate notes from youtube video transcript.
        Takes YouTube video transcript as input and generate structured notes from it.  
    """

    # get User message
    user_message = state["messages"][-2]

    # prepare state for yt_notes generator agent
    messages = [
        SystemMessage(content=yt_agent_prompt),
        user_message
    ]

    # Generate notes from yt transcript
    notes_response = notes_agent_llm.invoke(messages)

    # convert pydantic model to python dict
    notes_dict = notes_response.model_dump()

    # convert python dict to json string
    notes_json = json.dumps(notes_dict)

    return Command(
        update={
            "messages": HumanMessage(content=notes_json, name="YTNotesGenerator"),
            "next": "END"
        },
        goto=END
    )

# Audio Summariser agent
def summariser_agent(state: State):
    """
        Audio summariser agent that summarize the audio transcript and give detailed summary or overview of conversation.
        Takes audio transcript as input and give summary of that transcript. 
    """

    # get User message
    user_message = state["messages"][-2]

    # prepare state for summariser agent
    messages = [
        SystemMessage(content=audio_agent_prompt),
        user_message
    ]

    # summarize audio transcript
    summary_respones = summariser_agent_llm.invoke(messages)

    # convert pydantic model to python dict
    summary_dict = summary_respones.model_dump()

    # convert python dict to json string
    summary_json = json.dumps(summary_dict)

    return Command(
        update={
            "messages": [HumanMessage(content=summary_json, name="AudioSummariser")],
            "next": "END"
        },
        goto=END
    )

# Career Path Guide Agent
def career_guide_agent(state: State):
    """
        Career path guide agent that gives structured and realistic roadmap for speciific career.
        Takes user skills, intrest, future goal, current expirence, etc as input and give detailed roadmap to achive goal.
    """

    # Get User message
    user_message = state["messages"][-2]

    # prepare state for career path guide agent
    messages = [
        SystemMessage(content=roadmap_agent_prompt),
        user_message
    ]

    # Generate Roadmap 
    roadmap_response = career_guide_agent_llm.invoke(messages)

    # convert pydantic model to python dict
    roadmap_dict = roadmap_response.model_dump()

    # convert python dict to json string
    roadmap_json = json.dumps(roadmap_dict)

    return Command(
        update={
            "messages": [HumanMessage(content=roadmap_json, name="RoadmapGuide")],
            "next": "END"
        },
        goto=END
    )