import sys
import os
from typing import Optional, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(CURRENT_DIR, "recommendation"))

from profile_extractor import extract_profile
from hybrid_recommender import recommend
from data_loader import load_pathways

app = FastAPI(title="Livelihood Navigator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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


def format_results(profile, results):
    return {
        "profile": profile,
        "recommendations": [
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
        ],
    }


@app.get("/health")
def health():
    return {"status": "ok", "pathways_loaded": len(load_pathways())}


@app.post("/extract-profile")
def extract(input: ConversationInput):
    return extract_profile(input.transcript)


@app.post("/recommend-from-transcript")
def recommend_from_transcript(input: ConversationInput):
    profile = extract_profile(input.transcript)
    results = recommend(profile, top_n=5)
    return format_results(profile, results)


@app.post("/recommend-from-profile")
def recommend_from_profile(input: ProfileInput):
    profile = input.dict()
    results = recommend(profile, top_n=5)
    return format_results(profile, results)