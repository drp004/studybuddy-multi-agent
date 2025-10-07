from typing_extensions import TypedDict
from typing import List, Literal, Annotated
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


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
