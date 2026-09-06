import re
import json

EDUCATION_KEYWORDS = {
    r"\b8th\b|eighth standard|eighth class": 8,
    r"\b10th\b|tenth standard|tenth class|matric": 10,
    r"\b12th\b|twelfth standard|higher secondary|intermediate": 12,
    r"iti|diploma": 12,
    r"graduate|degree|b\.?a\b|b\.?sc\b|b\.?com\b|b\.?tech\b": 15,
}

INTEREST_KEYWORDS = {
    "machines": ["machine", "machinery", "mechanical", "engine", "tractor"],
    "electronics": ["electronic", "phone", "mobile", "wiring", "circuit"],
    "agriculture": ["farm", "farming", "crop", "field", "agriculture"],
    "repair": ["repair", "fix", "maintenance", "servicing"],
    "tailoring": ["stitch", "tailor", "sewing", "cloth", "garment"],
    "food processing": ["cooking", "food", "kitchen", "processing", "preserve"],
    "beauty and wellness": ["beauty", "salon", "makeup", "wellness", "spa"],
    "construction": ["construction", "mason", "building", "civil work"],
    "handicrafts": ["craft", "handmade", "weaving", "pottery", "embroidery"],
    "technology": ["computer", "technology", "digital", "internet"],
}

SKILL_KEYWORDS = [
    "basic mechanics", "machine maintenance", "equipment repair", "basic electronics",
    "mobile repair", "troubleshooting", "tailoring", "stitching", "cooking",
    "food processing", "farming", "tractor repair", "solar panel installation",
    "data entry", "computer operation", "beauty treatment", "carpentry", "masonry",
]

EMPLOYMENT_SELF_PATTERNS = [
    "start my own", "own shop", "own business", "self employed", "start a business",
    "open a shop", "work for myself", "my own enterprise",
]

EMPLOYMENT_WAGE_PATTERNS = [
    "want a job", "looking for a job", "work for a company", "salaried job",
    "want employment", "work under someone", "join a company",
]

MOBILITY_LOCAL_PATTERNS = [
    "can't travel", "cannot travel", "stay in my village", "near my home",
    "can't move", "cannot move", "close to home", "don't want to travel",
]

MOBILITY_WIDE_PATTERNS = [
    "willing to travel", "can move anywhere", "relocate", "go to another city",
    "willing to relocate", "move to a different place",
]


def extract_education(text):
    text_lower = text.lower()
    for pattern, level in EDUCATION_KEYWORDS.items():
        if re.search(pattern, text_lower):
            return level
    return None


def extract_interests(text):
    text_lower = text.lower()
    return [interest for interest, kws in INTEREST_KEYWORDS.items() if any(k in text_lower for k in kws)]


def extract_skills(text):
    text_lower = text.lower()
    found = []
    for skill in SKILL_KEYWORDS:
        tokens = skill.split()
        if all(tok in text_lower for tok in tokens):
            found.append(skill)
    return found


def extract_employment_preference(text):
    text_lower = text.lower()
    if any(p in text_lower for p in EMPLOYMENT_SELF_PATTERNS):
        return "self_employment"
    if any(p in text_lower for p in EMPLOYMENT_WAGE_PATTERNS):
        return "wage_employment"
    return None


def extract_mobility(text):
    text_lower = text.lower()
    if any(p in text_lower for p in MOBILITY_LOCAL_PATTERNS):
        return "local_only"
    if any(p in text_lower for p in MOBILITY_WIDE_PATTERNS):
        return "regional_or_national"
    return "local_or_regional"


def extract_age(text):
    match = re.search(r"\b(1[4-9]|[2-6][0-9])\s*(years old|year old|yrs|years)\b", text.lower())
    return int(match.group(1)) if match else None


def extract_profile(conversation_text):
    return {
        "education_level": extract_education(conversation_text),
        "age": extract_age(conversation_text),
        "occupation": conversation_text.strip()[:200],
        "skills": extract_skills(conversation_text),
        "interests": extract_interests(conversation_text),
        "employment_preference": extract_employment_preference(conversation_text),
        "mobility": extract_mobility(conversation_text),
        "raw_transcript": conversation_text.strip(),
    }


if __name__ == "__main__":
    sample = """
    I studied up to 10th class. I help my family with farming and I also know
    how to repair tractors and other farm machines. I am interested in
    mechanical work and technology. I want to start my own business and I
    cannot travel far from my village.
    """
    print(json.dumps(extract_profile(sample), indent=2))