# import io
# import os
# import traceback

# from dotenv import load_dotenv

# from typing import Annotated

# from fastapi import FastAPI, Form, File, UploadFile
# from pydantic import BaseModel, Field

# # PDF processing
# import fitz

# # YT processing
# import yt_dlp
# import tempfile
# import assemblyai as aai

# # date & time
# from datetime import datetime

# # lg Agent
# from AI.lg_graph import lg_agent
# from langchain_core.messages import HumanMessage

# # import envs
# load_dotenv()
# ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")


# # ===== FastAPI app ===== #
# app = FastAPI()


# # ===== utils ===== #
# # PDF processing tool
# async def extract_pdf_text(pdf: UploadFile):
#     try:
#         pdf_bytes = pdf.file.read()                                # read pdf content in-memory
#         docs = fitz.open(stream=pdf_bytes, filetype="pdf")         # read text from in-memory (from pdf_bytes)
#         text = "\n".join([page.get_text() for page in docs])       # concate entire text in single variable
    
#     except Exception as e:
#         print(f"Time: [{datetime.now()}]; Error Occured during pdf read; \nTraceback: {traceback.format_exc()}")
#         return {"error": "Some error occured during pdf read."}

#     return {"text": text}


# # Text file processing tool
# async def extract_txt_text(txt: UploadFile):
#     try:
#         content = txt.file.read()
#         text = content.decode("utf-8")

#     except Exception as e:
#         print(f"Time: [{datetime.now()}]; Error Occured during txt read; \nTraceback: {traceback.format_exc()}")
#         return {"error": "Some error occured during text read"}

#     return {"text": text}


# # YT transcript extracting tool
# async def extract_yt_transcript(yt_link: str):
#     try:
#         ydl_opts = {
#             "format": "bestaudio[ext=m4a]",  # downloads as .m4a (no conversion)
#             "outtmpl": "%(title)s.%(ext)s",
#             # "cookiefile": cookie
#         }

#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info = ydl.extract_info(yt_link, download=True)
#             filename = ydl.prepare_filename(info)

#         # Step 2: Transcribe with AssemblyAI
#         transcriber = aai.Transcriber()
#         transcript = transcriber.transcribe(filename)

#         os.remove(filename)
#         # print(transcript.text)

#         return  {"transcript": transcript.text}

#     except Exception as e:
#         print(f"Time: [{datetime.now()}]; Error Occured during Audio transcribing; \nTraceback: {traceback.format_exc()}")
#         return {"error": "Error occured during Audio transcribing"}


# # Audio transcript tool
# aai.settings.api_key = ASSEMBLYAI_API_KEY
# async def transcribe_audio_file(audio_path: str) -> str:
#     try:
#         transcriber = aai.Transcriber()
#         transcript = transcriber.transcribe(audio_path)

#         return {"transcript": transcript.text}
#     except Exception as e:
#         print(f"\nTime: [{datetime.now()}]; Error occured during transcribing audio!; \nTraceback: {traceback.format_exc()}")
#         return {"error": "Error occured during Audio transcribing"}



# # ===== Routes ===== #
# @app.get("/")
# def welcome():
#     return {"Message": "Hello, Buddy!"}


# # notes from docs
# @app.post("/api/doc-notes")
# async def doc_notes(doc: Annotated[UploadFile, File()]):
#     """ This route will receive document (txt, pdf, jpg, etc.) & generate notes from it"""

#     try:
#         if doc:
#             print(f"\nTime: [{datetime.now()}]; File Received!")

#             # getting file type
#             file_type = doc.content_type
#             print(f"\nFile type: {file_type}")

#             # Extracting text from doc
#             if file_type == "application/pdf":
#                 response = await extract_pdf_text(doc)
#             elif file_type == "text/plain":
#                 response = await extract_txt_text(doc)
#             elif file_type in ["image/jpeg", "image/jpg", "image/png"]:
#                 response = {"text": "Image received"}    
#             else:
#                 return {"message": "File type not supported"}
    
#             print(f"\nTime: [{datetime.now()}]; Text Extracted!")

#             # return response
#             if response.get("error", ""):
#                 return {"Error": response.get("error")}
#             else:
#                 print(f"\nTime: [{datetime.now()}]; Generating notes with Agent invoke.")
                
#                 text = response.get("text", "")
#                 response = lg_agent.invoke({"messages": [HumanMessage(content=f"Generate notes from text: \n{text}")]})

#                 print(f"\nTime: [{datetime.now()}]; Doc-Notes Generated!")

#                 notes = response["messages"][-1].content

#                 return {"notes": notes}

#                 # text = response.get("text", "")
#                 # return {"text": text}

#         else:
#             return {"message": "No file received!"}
        
#     except Exception as e:
#         print(f"\nTime: [{datetime.now()}]; Error occured during text extraction from doc; \nTraceback: {traceback.format_exc()}")
#         return {"error": "Error occured during doc notes generaion!"}


# # notes from yt_transcript
# @app.post("/api/yt-notes")
# async def yt_notes(user_input: Annotated[str, Form()]):
#     """ This route will yt video link & generate notes from yt video transcript """

#     try:
#         # getting yt-transcript
#         print(f"\nTime: [{datetime.now()}]; YT-link Received!")

#         response = await extract_yt_transcript(user_input)
        
#         print(f"\nTime: [{datetime.now()}]; Transcript extraction completed!")

#         # Returning Transcript
#         if response.get("error", ""):
#             return {"message": response.get("error")}
#         else:
#             # return {"transcript": response.get("transcript")}
#             print(f"\nTime: [{datetime.now()}]; Generating notes from transcript!")

#             transcript = response.get("transcript", "")
#             agent_response = lg_agent.invoke({"messages": [HumanMessage(content=f"Generate notes from below transcript: \n{transcript}")]})

#             print(f"\nTime: [{datetime.now()}]; YT-Notes Generated!")

#             notes = agent_response["messages"][-1].content

#             return {"notes": notes}

#     except Exception as e:
#         print(f"\nTime: [{datetime.now()}]; Error occured during yt-notes generation; \nTraceback: {traceback.format_exc()}")
#         return {"error": "error while processing yt-video"}


# # audio summary
# @app.post("/api/audio-summary")
# async def audio_summary(audio: Annotated[UploadFile, File()]):
#     """ This route will receive audio and & give summary """

#     try:
#         print(f"\nTime: [{datetime.now()}]; Audio file received!")

#         with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
#             tmp.write(await audio.read())
#             tmp_path = tmp.name

#         # Audio transcribing
#         audio_transcript = await transcribe_audio_file(tmp_path)

#         print(f"\nTime: [{datetime.now()}]; Audio Transcription completed!")

#         if audio_transcript.get("error", {}):
#             return {"error": audio_transcript.get("error", "")}
        
#         # accessing audio transcript
#         transcript = audio_transcript.get("transcript", "")

#         print(f"Time: [{datetime.now()}]; Agent invoked for transcript summarisation! ")

#         # Agent invoke for audio summary
#         agent_response = lg_agent.invoke({"messages": f"Summarise the below audio transcript: \n{transcript}"})

#         print(f"Time: [{datetime.now()}]; Summarisation completed!")

#         audio_summary = agent_response["messages"][-1].content
        
#         return {"transcript": audio_summary}


#     except Exception as e:
#         print(f"\nTime: [{datetime.now()}]; Error occured in audio summary; \nTraceback: {traceback.format_exc()}")
#         return {"error": "Error occured in audio summary"}
    

# # career path guide
# @app.post("/api/career-guide")
# async def career_guide(user_input: Annotated[str, Form()]):
#     """ This route will generate career path """
    
#     try:
#         return {"response": "Your path will come here..."}
    
#     except Exception as e:
#         print(f"\nTime: [{datetime.now()}]; Error occured during generating career path; \nTraceback: {traceback.format_exc()}")
#         return {"error": "Error occured during invoking Agent!"}

from fastapi import FastAPI

from Routers.ai import agent
from Routers.auth import auth

app = FastAPI()

app.include_router(agent)
app.include_router(auth)

# ===== Router ===== #
# welcome router
@app.get("/")
async def welcome():
    return {"message": "Hello, Buddy!"}