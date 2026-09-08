import sys
import os

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import bcrypt
from database import get_connection
from speech_to_text import transcribe_marathi_audio  # rename to transcribe_hindi_audio if you already renamed it in speech_to_text.py

# --- make the recommendation/ pipeline importable BEFORE anything imports from it ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "recommendation"))

from profile_extractor import extract_profile
from hybrid_recommender import recommend
from roadmap_generator import generate_roadmap
from data_loader import load_pathways
from text_translator import translate_to_english
from llm_profile_extractor import extract_profile_llm

app = FastAPI(title="SIH PS#97 Livelihood Navigator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ REQUEST MODELS (must be defined before any route uses them) ============

class SignupData(BaseModel):
    full_name: str
    mobile_number: str
    password: str
    preferred_language: str


class LoginData(BaseModel):
    mobile_number: str
    password: str


class ConversationInput(BaseModel):
    transcript: str


class ProfileInput(BaseModel):
    education_level: Optional[int] = None
    age: Optional[int] = None
    occupation: Optional[str] = None
    skills: List[str] = []
    interests: List[str] = []
    employment_preference: Optional[str] = None
    mobility: Optional[str] = None


# ============ AUTH ROUTES (Prathmesh) ============

@app.get("/")
def home():
    return {"message": "API is running"}


@app.get("/test-db")
def test_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"users": result}


@app.post("/signup")
def signup(data: SignupData):
    conn = get_connection()
    cursor = conn.cursor()
    hashed_pw = bcrypt.hashpw(data.password.encode("utf-8"), bcrypt.gensalt())
    query = (
        "INSERT INTO users (full_name, mobile_number, password_hash, preferred_language) "
        "VALUES (%s, %s, %s, %s)"
    )
    values = (data.full_name, data.mobile_number, hashed_pw.decode("utf-8"), data.preferred_language)
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "User created successfully"}


@app.post("/login")
def login(data: LoginData):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT full_name, password_hash, preferred_language FROM users WHERE mobile_number = %s"
    cursor.execute(query, (data.mobile_number,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user is None:
        return {"error": "User not found"}

    full_name, password_hash, preferred_language = user

    if not bcrypt.checkpw(data.password.encode("utf-8"), password_hash.encode("utf-8")):
        return {"error": "Incorrect password"}

    return {
        "message": "Login successful",
        "full_name": full_name,
        "preferred_language": preferred_language or "English",
    }

# ============ ML RECOMMENDATION ROUTES (Amit) ============

def format_results(profile, results):
    recommendations = [
        {
            "pathway_id": r["pathway"]["id"],
            "pathway_name": r["pathway"]["name"],
            "category": r["pathway"]["category"],
            "score": round(r["final_score"] * 100, 1),
            "semantic_score": round(r["semantic_score"] * 100, 1),
            "explanation": r["explanation"],
            "matched_skills": r["skill_gap"]["matched_skills"],
            "missing_skills": r["skill_gap"]["missing_skills"],
            "source": r["pathway"].get("source", "unknown"),
            "verified": r["pathway"].get("verified", False),
        }
        for r in results
    ]
    top_roadmap = generate_roadmap(results[0], profile) if results else None

    return {
        "profile": profile,
        "recommendations": recommendations,
        "roadmap_for_top_pick": top_roadmap,
    }


@app.get("/health")
def health():
    return {"status": "ok", "pathways_loaded": len(load_pathways())}


@app.post("/extract-profile")
def extract(input: ConversationInput):
    english_text = translate_to_english(input.transcript)
    return extract_profile_llm(english_text)


@app.post("/recommend-from-transcript")
def recommend_from_transcript(input: ConversationInput):
    english_text = translate_to_english(input.transcript)
    profile = extract_profile_llm(english_text)
    results = recommend(profile, top_n=5)
    response = format_results(profile, results)
    response["translated_text"] = english_text
    return response


@app.post("/recommend-from-profile")
def recommend_from_profile(input: ProfileInput):
    profile = input.dict()
    results = recommend(profile, top_n=5)
    return format_results(profile, results)


@app.post("/recommend-from-voice")
async def recommend_from_voice(audio: UploadFile = File(...)):
    audio_bytes = await audio.read()
    stt_result = transcribe_marathi_audio(audio_bytes, audio.filename)
    profile = extract_profile_llm(stt_result["english_text"])
    profile = extract_profile(stt_result["english_text"])
    results = recommend(profile, top_n=5)
    response = format_results(profile, results)
    response["translated_text"] = stt_result["english_text"]
    return response