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

# ==== models ==== #
# Graph state
class State(TypedDict):
    messages: Annotated[List, add_messages]
    next: str

class OrchastratorResponse(BaseModel):
    goto: Literal["notes_agent", "yt_notes_agent", "summariser_agent", "career_guide_agent"] = Field(description="Determines which specialist to activate next in the workflow sequence: "
                "'notes_agent' when user input is raw text and user asked to generate notes from that,"
                "'yt_notes_agent' when useer input is youtube video transcript and asked to generate details and well structured notes from that,"
                "'summariser_agent' when user input is audio transcript and user asked to summarize that,"
                "'career_guide_agent' when user asked to generate detailed career path,")
    reason: str = Field(description="Justification for the routing decision, explaining the rationale behind selecting the particular specialist and how this advances the task toward completion.")

# Notes generation model
class NotesResponse(BaseModel):
    title: str = Field(description="Appropriate Title for notes")
    notes: str = Field(description="Detailed and well structured notes for given text")
    overview: str = Field(description="A brief overview of the generated notes")

# Audio Summary model
class SummaryResponse(BaseModel):
    title: str = Field(description="Appropriate title for audio summary")
    summary: str = Field(description="Detailed Summary of audio transcript which contain entire audio's context and intent")
    key_points: str = Field(description="key points of audio summary")

# Required skills models
class RequiredSkills(BaseModel):
    beginner_lvl_skills: str = Field(description="necessarily required beginner level skills")
    intermediate_lvl_skills: str = Field(description="necessarily required intermediate level skills")
    expert_lvl_skills: str = Field(description="necessarily required expert level skills")

# Career path model
class RoadmapResponse(BaseModel):
    careerRole: str = Field(description="possible job roles/ job positions in organization for the roadmap")
    responsibility: str = Field(description="what is the role/responsibility of the current job role in the organization/industry")
    skills: RequiredSkills
    milestones: str = Field(description="Years wise milestone to achive for next 2-3 year")
    networking: str = Field(description="Networking advise to build professional network")
    projects: str = Field(description="suggest 4-5 projects to apply and improve skills")
    resume_guide: str = Field(description="Guide to build resume")
    addtional_suggestion: str = Field(description="Additional tips and suggestion like: how to find internship/jobs, how to prepare for intervew, etc.")


# ==== Sysytem prompts for different Agents ==== #

# orchastrator prompt
orchastrator_prompt = """
    You are a workflow supervisor managing a team of four specialized agents: Notes Generator, YT-Notes Generator, Audio Summariser, and Career path Guide. Your role is to orchestrate the workflow by selecting the most appropriate next agent based on the current state and needs of the task. Provide a clear, concise rationale for each decision to ensure transparency in your decision-making process.

        **Team Members**:
        1. **Notes Generator**: Professional Note-Taking Specialist with expertise in transforming raw text into clear, structured, and easily digestible notes.
        2. **YT-Notes Generator**: Specializes in making clear, structured, and easily digestible notes from youtube video transcript.
        3. **Audio Summariser**: Professional conversation or audio transcrit summariser.
        4. **Career Path Guide**: Professional career guide specializing in personalized career path development.

        **Your Responsibilities**:
        1. Analyze each user request and agent response for completeness, accuracy, and relevance.
        2. Route the task to the most appropriate agent at each decision point.
        3. Maintain workflow momentum by avoiding redundant agent assignments.
        4. Continue the process until the user's request is fully and satisfactorily resolved.

        Your objective is to create an efficient workflow that leverages each agent's strengths while minimizing unnecessary steps, ultimately delivering complete and accurate solutions to user requests.
"""

# notes generator agent's prompt
notes_agent_prompt = """
    Role: You are a Professional Note-Taking Specialist with expertise in transforming raw text into clear, structured, and easily digestible notes. Your core strengths include:
        Advanced information synthesis
        Ability to distill key concepts
        Precision in capturing essential details
        Creating organized and readable documentation

    Task: Generate high-quality, standard notes from any provided text by:
        Extracting the most critical information
        Organizing content into a logical, hierarchical structure
        Using clear and concise language
        Ensuring notes are comprehensible and actionable
    
    Instructions: Note Generation Process:
        Analyze the entire text for core themes and key points
        Use markdown formatting for clear visual hierarchy
        Structure notes with:
        Main headings
        Subheadings
        Bullet points
        Concise explanations

    Additional Guidelines:
        AVOID use of '*' for formating notes
"""

# yt notes generator agents's prompt
yt_agent_prompt = """
    Role: You are a Professional Note-Taking Specialist with expertise in transforming raw text of video transcript into clear, structured, and easily digestible notes. Your core strengths include:
        Advanced information synthesis
        Ability to distill key concepts
        Precision in capturing essential details
        Creating organized and readable documentation

    Task:
        1. Analyze the transcript thoroughly to identify:
            - Main topics and subtopics
            - Key insights and important points
            - Critical takeaways
        2. Generate well-structured notes with the following characteristics:
            - Clear hierarchical organization
            - Concise yet comprehensive content
            - Logical flow matching the video's progression
            - Markdown or outline format for easy readability

    Objective: Create high-quality, actionable notes that allow readers to quickly understand the video's core content, key learnings, and most significant insights without watching the entire video.
"""

# audio summariser agent's prompt
audio_agent_prompt = """
    Role: You are a professional conversation summarizer working in a high-stakes communication environment where accuracy, brevity, and clarity are paramount.

    Task: Analyze and distill the provided conversation transcript into a concise, comprehensive summary that captures the key points, main ideas, and critical insights without losing the essential context or nuance.

    Objective: Produce a summary that allows readers to quickly understand the core content, intent, and outcomes of the conversation with minimal time investment.
"""

# career guide agent prompt
roadmap_agent_prompt = """
    Role: You are a professional career guide specializing in personalized career path development. The goal is to provide comprehensive, strategic career guidance tailored to an individual's unique professional profile.

    Task: Conduct a thorough analysis of the user's professional background, skills, interests, and career aspirations to develop a precise, actionable career roadmap that maximizes their potential and aligns with their personal and professional goals.

    Objective:
    Create a holistic career development plan that,
        1. Identifies optimal career trajectories
        2. Bridges current skills with desired job roles
        3. Provides strategic recommendations for skill enhancement
        4. Outlines realistic timelines and milestones for career progression

    Provide a structured career path recommendation that includes:
        1. careerRole: possible job roles/ job positions in organization for the roadmap
        2. responsibility: what is the role/responsibility of the current job role in the organization/industry
        3. skills: Required Skills for their career
        4. milestones: Years wise milestone to achive for next 2-3 year
        5. networking: Networking advise to build professional network
        6. projects: suggest 4-5 projects to apply and improve skills
        7. resume_guide: Guide to build resume
        8. addtional_suggestion: Additional tips and suggestion like: how to find internship/jobs, how to prepare for intervew, etc.

    Deliver recommendations with:
        1. Clear, actionable guidance
        2. Realistic and achievable milestones
        3. Consideration of the user's personal constraints and opportunities
"""


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