from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional
import random
import json
import os
import glob

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount audio directory
app.mount("/audio", StaticFiles(directory="audio"), name="audio")

# Load all question files dynamically
QUESTIONS = []
json_files = glob.glob(os.path.join(os.path.dirname(__file__), '*_questions.json'))

for json_file in json_files:
    try:
        with open(json_file, encoding='utf-8') as f:
            questions = json.load(f)
            QUESTIONS.extend(questions)
            print(f"Loaded {len(questions)} questions from {os.path.basename(json_file)}")
    except Exception as e:
        print(f"Error loading {json_file}: {e}")

print(f"Total questions loaded: {len(QUESTIONS)}")

@app.get("/questions/")
def get_questions(
    language: str = Query(..., description="Language to filter questions"),
    level: Optional[int] = Query(None, description="Level to filter questions"),
    module: Optional[str] = Query(None, description="Module to filter questions"),
    submodule: Optional[str] = Query(None, description="Submodule to filter questions"),
    limit: int = Query(5, description="Number of random questions to return")
):
    filtered = [
        q for q in QUESTIONS
        if q["language"].lower() == language.lower()
        and (level is None or q.get("level") == level)
        and (module is None or q.get("module", "").lower() == module.lower())
        and (submodule is None or q.get("submodule", "").lower() == submodule.lower())
    ]
    random.shuffle(filtered)
    return filtered[:limit]

@app.get("/audio/{filename}")
def get_audio(filename: str):
    return FileResponse(f"audio/{filename}", media_type="audio/mpeg")
