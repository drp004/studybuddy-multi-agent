from fastapi import APIRouter, Form, File, UploadFile, Depends, HTTPException, status
from datetime import datetime
from typing_extensions import Annotated

# Store Audio file temporary
import tempfile

# Tools to process data
from Tools import *

# dependacy for token validation
from utils import get_access

# LangGraph agent to Generate Response
from AI.lg_graph import lg_agent
from langchain_core.messages import HumanMessage


# agent router 
agent = APIRouter(
    prefix="/agent",
    tags=["Agent"]
)


# ===== Routes ===== #
# notes from docs
@agent.post("/doc-notes")
async def doc_notes(doc: Annotated[UploadFile, File()], access: bool = Depends(get_access)):
    """ This route will receive document (txt, pdf, jpg, etc.) & generate notes from it"""

    if not access:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or Expired Token!")

    try:
        if doc:
            print(f"\nTime: [{datetime.now()}]; File Received!")

            # getting file type
            file_type = doc.content_type
            print(f"\nFile type: {file_type}")

            # Extracting text from doc
            if file_type == "application/pdf":
                response = await extract_pdf_text(doc)
            elif file_type == "text/plain":
                response = await extract_txt_text(doc)
            elif file_type in ["image/jpeg", "image/jpg", "image/png"]:
                response = {"text": "Image received"}    
            else:
                return {"message": "File type not supported"}
    
            print(f"\nTime: [{datetime.now()}]; Text Extracted!")

            # return response
            if response.get("error", ""):
                return {"Error": response.get("error")}
            else:
                print(f"\nTime: [{datetime.now()}]; Generating notes with Agent invoke.")
                
                text = response.get("text", "")
                response = lg_agent.invoke({"messages": [HumanMessage(content=f"Generate notes from text: \n{text}")]})

                print(f"\nTime: [{datetime.now()}]; Doc-Notes Generated!")

                notes = response["messages"][-1].content

                return {"notes": notes}


        else:
            return {"message": "No file received!"}
        
    except Exception as e:
        print(f"\nTime: [{datetime.now()}]; Error occured during text extraction from doc; \nTraceback: {traceback.format_exc()}")
        return {"error": "Error occured during doc notes generaion!"}


# notes from yt_transcript
@agent.post("/yt-notes")
async def yt_notes(user_input: Annotated[str, Form()], access: bool = Depends(get_access)):
    """ This route will yt video link & generate notes from yt video transcript """

    if not access:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="INvalid or Expired Token!")

    try:
        # getting yt-transcript
        print(f"\nTime: [{datetime.now()}]; YT-link Received!")

        response = await extract_yt_transcript(user_input)
        
        print(f"\nTime: [{datetime.now()}]; Transcript extraction completed!")

        # Returning Transcript
        if response.get("error", ""):
            return {"message": response.get("error")}
        else:
            # return {"transcript": response.get("transcript")}
            print(f"\nTime: [{datetime.now()}]; Generating notes from transcript!")

            transcript = response.get("transcript", "")
            agent_response = lg_agent.invoke({"messages": [HumanMessage(content=f"Generate notes from below transcript: \n{transcript}")]})

            print(f"\nTime: [{datetime.now()}]; YT-Notes Generated!")

            notes = agent_response["messages"][-1].content

            return {"notes": notes}

    except Exception as e:
        print(f"\nTime: [{datetime.now()}]; Error occured during yt-notes generation; \nTraceback: {traceback.format_exc()}")
        return {"error": "error while processing yt-video"}


# audio summary
@agent.post("/audio-summary")
async def audio_summary(audio: Annotated[UploadFile, File()], access: bool = Depends(get_access)):
    """ This route will receive audio and & give summary """

    if not access:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or Expired Token!")

    try:
        print(f"\nTime: [{datetime.now()}]; Audio file received!")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(await audio.read())
            tmp_path = tmp.name

        # Audio transcribing
        audio_transcript = await transcribe_audio_file(tmp_path)

        print(f"\nTime: [{datetime.now()}]; Audio Transcription completed!")

        if audio_transcript.get("error", {}):
            return {"error": audio_transcript.get("error", "")}
        
        # accessing audio transcript
        transcript = audio_transcript.get("transcript", "")

        print(f"Time: [{datetime.now()}]; Agent invoked for transcript summarisation! ")

        # Agent invoke for audio summary
        agent_response = lg_agent.invoke({"messages": f"Summarise the below audio transcript: \n{transcript}"})

        print(f"Time: [{datetime.now()}]; Summarisation completed!")

        audio_summary = agent_response["messages"][-1].content
        
        return {"transcript": audio_summary}


    except Exception as e:
        print(f"\nTime: [{datetime.now()}]; Error occured in audio summary; \nTraceback: {traceback.format_exc()}")
        return {"error": "Error occured in audio summary"}
    

# career path guide
@agent.post("/career-guide")
async def career_guide(user_skills: Annotated[str, Form()], user_edu: Annotated[str, Form()], user_interest: Annotated[str, Form()], career_goal: Annotated[str, Form()], access: bool = Depends(get_access)):
    """ This route will generate career path """
    
    if not access:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or Expired Token!")

    try:
        print(f"\nTime: [{datetime.now()}]; User input Received!")

        # user details
        user_details = f"Skills: {user_skills}, Education/Experience: {user_edu}, Interest: {user_interest}, Career Goal: {career_goal}"

        # Generate Roadmap for user 
        agent_response = lg_agent.invoke({"messages": [HumanMessage(content=f"Create a Structured career path for following {user_details}")]})

        print(f"Time: [{datetime.now()}]; Career Path Generated!")

        career_path = agent_response["messages"][-1].content

        return {"career_path": career_path}
    
    except Exception as e:
        print(f"\nTime: [{datetime.now()}]; Error occured during generating career path; \nTraceback: {traceback.format_exc()}")
        return {"error": "Error occured during invoking Agent!"}