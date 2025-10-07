import os
import traceback
from datetime import datetime

from dotenv import load_dotenv
from fastapi import UploadFile

# PDF Processing
import fitz

# YT Processing
import yt_dlp

# Audio Transcription
import assemblyai as aai


load_dotenv()

ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

# ===== Tools ===== #
# PDF processing tool
async def extract_pdf_text(pdf: UploadFile):
    try:
        pdf_bytes = pdf.file.read()                                # read pdf content in-memory
        docs = fitz.open(stream=pdf_bytes, filetype="pdf")         # read text from in-memory (from pdf_bytes)
        text = "\n".join([page.get_text() for page in docs])       # concate entire text in single variable
    
    except Exception as e:
        print(f"Time: [{datetime.now()}]; Error Occured during pdf read; \nTraceback: {traceback.format_exc()}")
        return {"error": "Some error occured during pdf read."}

    return {"text": text}


# Text file processing tool
async def extract_txt_text(txt: UploadFile):
    try:
        content = txt.file.read()
        text = content.decode("utf-8")

    except Exception as e:
        print(f"Time: [{datetime.now()}]; Error Occured during txt read; \nTraceback: {traceback.format_exc()}")
        return {"error": "Some error occured during text read"}

    return {"text": text}


# YT transcript extracting tool
async def extract_yt_transcript(yt_link: str):
    try:
        ydl_opts = {
            "format": "bestaudio[ext=m4a]",  # downloads as .m4a (no conversion)
            "outtmpl": "%(title)s.%(ext)s",
            # "cookiefile": cookie
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(yt_link, download=True)
            filename = ydl.prepare_filename(info)

        # Step 2: Transcribe with AssemblyAI
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(filename)

        os.remove(filename)
        # print(transcript.text)

        return  {"transcript": transcript.text}

    except Exception as e:
        print(f"Time: [{datetime.now()}]; Error Occured during Audio transcribing; \nTraceback: {traceback.format_exc()}")
        return {"error": "Error occured during Audio transcribing"}


# Audio transcript tool
aai.settings.api_key = ASSEMBLYAI_API_KEY
async def transcribe_audio_file(audio_path: str) -> str:
    try:
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_path)

        return {"transcript": transcript.text}
    except Exception as e:
        print(f"\nTime: [{datetime.now()}]; Error occured during transcribing audio!; \nTraceback: {traceback.format_exc()}")
        return {"error": "Error occured during Audio transcribing"}
