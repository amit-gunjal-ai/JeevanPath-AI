import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)

from semantic_matcher import get_semantic_matches
from eligibility import meets_eligibility
from skill_gap import calculate_skill_gap
from data_loader import load_pathways
from skill_normalizer import normalize_skill_list

DEFAULT_WEIGHTS = {
    "semantic": 0.35,
    "skills": 0.20,
    "interests": 0.15,
    "employment": 0.10,
    "mobility": 0.10,
    "skill_gap_penalty": 0.10,
}


def build_profile_text(user_profile):
    parts = []
    if user_profile.get("occupation"):
        parts.append(f"Current or past occupation: {user_profile['occupation']}.")
    if user_profile.get("skills"):
        parts.append("Skills: " + ", ".join(user_profile["skills"]) + ".")
    if user_profile.get("interests"):
        parts.append("Interests: " + ", ".join(user_profile["interests"]) + ".")
    if user_profile.get("experience"):
        parts.append(f"Experience: {user_profile['experience']}.")
    if user_profile.get("employment_preference"):
        parts.append(f"Prefers {user_profile['employment_preference']} employment.")
    return " ".join(parts)


def normalize_user_skills(user_profile):
    if not user_profile.get("skills"):
        return user_profile
    normalized = normalize_skill_list(user_profile["skills"])
    user_profile = dict(user_profile)
    user_profile["skills_original"] = [n["original"] for n in normalized]
    user_profile["skills"] = [n["normalized"] for n in normalized]
    return user_profile


def score_interests(user_profile, pathway):
    user_interests = {i.lower().strip() for i in user_profile.get("interests", [])}
    pathway_interests = {i.lower().strip() for i in pathway.get("interests", [])}
    if not pathway_interests:
        return 0.0, []
    overlap = user_interests.intersection(pathway_interests)
    return len(overlap) / len(pathway_interests), sorted(overlap)


def score_employment(user_profile, pathway):
    preference = user_profile.get("employment_preference")
    pathway_types = pathway.get("employment", {}).get("types", [])
    if not preference:
        return 0.0, False
    match = preference in pathway_types
    return (1.0 if match else 0.0), match


def score_mobility(user_profile, pathway):
    user_mobility = user_profile.get("mobility")
    pathway_mobility = pathway.get("constraints", {}).get("mobility")
    if not user_mobility or not pathway_mobility:
        return 0.5, None  # unknown -> neutral, doesn't penalize or reward

    rank = {"local_only": 1, "local_or_regional": 2, "regional_or_national": 3, "any": 4}
    match = rank.get(user_mobility, 2) >= rank.get(pathway_mobility, 2)
    return (1.0 if match else 0.0), match


def score_skill_gap(user_profile, pathway):
    required_skills = pathway.get("skills", {}).get("required", [])
    gap = calculate_skill_gap(user_profile.get("skills", []), required_skills)
    total = len(required_skills) if required_skills else 1
    return len(gap["matched_skills"]) / total, gap


def specificity_confidence(required_skills, min_specific=3):
    """Pathways with very few listed required skills (common for
    NSQF-derived entries whose 'skills' are just job-title keywords,
    not a real prerequisite list) shouldn't get full credit for a
    trivial 1-for-1 match. Scale confidence down for thin skill lists."""
    return min(len(required_skills) / min_specific, 1.0)


def generate_explanation(name, semantic_score, interest_overlap, employment_match,
                          mobility_match, gap_info, eligibility_reasons):
    lines = [f"Why {name} is recommended:"]
    if semantic_score >= 0.5:
        lines.append(f"- Your profile is semantically similar to this pathway ({semantic_score*100:.0f}% match).")
    if interest_overlap:
        lines.append("- Matches your interests: " + ", ".join(interest_overlap) + ".")
    if employment_match:
        lines.append("- Matches your preferred employment type.")
    if mobility_match:
        lines.append("- Fits your mobility constraints.")
    if gap_info["matched_skills"]:
        lines.append("- You already have: " + ", ".join(gap_info["matched_skills"]) + ".")
    if gap_info["missing_skills"]:
        lines.append("- Skills to develop: " + ", ".join(gap_info["missing_skills"]) + ".")
    for reason in eligibility_reasons:
        lines.append(f"- {reason}")
    return "\n".join(lines)


def recommend(user_profile, weights=None, top_n=5, include_ineligible=False):
    weights = weights or DEFAULT_WEIGHTS
    user_profile = normalize_user_skills(user_profile)
    pathways = load_pathways()

    profile_text = build_profile_text(user_profile)
    semantic_by_id = {
        r["pathway"]["id"]: r["semantic_score"]
        for r in get_semantic_matches(profile_text)
    }

    scored = []
    for pathway in pathways:
        eligibility = meets_eligibility(user_profile, pathway)
        if not eligibility["eligible"] and not include_ineligible:
            continue

        semantic_score = semantic_by_id.get(pathway["id"], 0.0)
        interest_score, interest_overlap = score_interests(user_profile, pathway)
        employment_score, employment_match = score_employment(user_profile, pathway)
        mobility_score, mobility_match = score_mobility(user_profile, pathway)
        skill_score, gap_info = score_skill_gap(user_profile, pathway)

        required_skills_list = pathway.get("skills", {}).get("required", [])
        required_count = max(len(required_skills_list), 1)
        gap_penalty_score = 1 - (len(gap_info["missing_skills"]) / required_count)

        confidence = specificity_confidence(required_skills_list)
        skill_score *= confidence
        gap_penalty_score = 0.5 + (gap_penalty_score - 0.5) * confidence
        final_score = (
            weights["semantic"] * semantic_score +
            weights["skills"] * skill_score +
            weights["interests"] * interest_score +
            weights["employment"] * employment_score +
            weights["mobility"] * mobility_score +
            weights["skill_gap_penalty"] * gap_penalty_score
        )

        scored.append({
            "pathway": pathway,
            "final_score": final_score,
            "semantic_score": semantic_score,
            "eligible": eligibility["eligible"],
            "skill_gap": gap_info,
            "explanation": generate_explanation(
                pathway["name"], semantic_score, interest_overlap,
                employment_match, mobility_match, gap_info, eligibility["reasons"]
            ),
        })

    scored.sort(key=lambda r: r["final_score"], reverse=True)
    return scored[:top_n]


if __name__ == "__main__":
    test_profile = {
        "education_level": 8,
        "age": 24,
        "occupation": "helps family with farming",
        "skills": ["basic mechanics", "tractor repair"],
        "interests": ["machines", "agriculture", "repair", "technology"],
        "employment_preference": "self_employment",
        "mobility": "local_or_regional",
    }

    for r in recommend(test_profile, top_n=3):
        print("=" * 60)
        print(f"{r['pathway']['name']}  |  Score: {r['final_score']*100:.1f}")
        print(r["explanation"])
        print()