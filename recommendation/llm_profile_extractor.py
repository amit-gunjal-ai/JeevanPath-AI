import os
import json
from google import genai
from dotenv import load_dotenv

from profile_extractor import extract_profile as rule_based_extract_profile

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
ENV_PATH = os.path.join(PROJECT_ROOT, "backend", ".env")
load_dotenv(ENV_PATH)

_client = None


def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set in environment")
        _client = genai.Client(api_key=api_key)
    return _client


EXTRACTION_PROMPT = """You are extracting a structured profile from a conversation transcript of a rural beneficiary describing their background, for a livelihood recommendation system.

Return ONLY valid JSON, no other text, no markdown code fences, matching exactly this schema:
{{
  "education_level": <integer, the class/standard passed, e.g. 8, 10, 12, or 15 for graduate, or null if unclear>,
  "age": <integer or null if not mentioned>,
  "occupation": <short string summarizing current/past work, or null>,
  "skills": [<list of specific skill phrases mentioned or clearly implied, lowercase>],
  "interests": [<list of general interest categories, lowercase, e.g. "agriculture", "electronics", "tailoring">],
  "employment_preference": <"self_employment", "wage_employment", or null if unclear>,
  "mobility": <"local_only", "local_or_regional", or "regional_or_national">
}}

Transcript: "{transcript}"
"""


def extract_profile_llm(transcript):
    try:
        client = get_client()
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=EXTRACTION_PROMPT.format(transcript=transcript),
        )
        raw_text = response.text.strip().replace("```json", "").replace("```", "").strip()

        profile = json.loads(raw_text)
        profile["raw_transcript"] = transcript
        profile["extraction_method"] = "llm"
        return profile

    except Exception as e:
        print(f"LLM extraction failed ({e}), falling back to rule-based extractor")
        profile = rule_based_extract_profile(transcript)
        profile["extraction_method"] = "rule_based_fallback"
        return profile


if __name__ == "__main__":
    test_transcript = """
    I've been fixing my neighbor's scooters and bikes for a couple of years now,
    just informally. I passed 10th class. I'd like to turn this into a proper
    business of my own, but I don't want to move away from my village.
    """
    result = extract_profile_llm(test_transcript)
    print(json.dumps(result, indent=2))