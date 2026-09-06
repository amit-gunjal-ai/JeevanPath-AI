def generate_roadmap(recommendation, user_profile):
    pathway = recommendation["pathway"]
    gap = recommendation["skill_gap"]
    missing = gap["missing_skills"]
    matched = gap["matched_skills"]

    steps = []
    step_num = 1

    # Step 1: acknowledge existing strengths
    if matched:
        steps.append({
            "step": step_num,
            "title": "Build on what you already know",
            "detail": (
                f"You already have relevant experience in: {', '.join(matched)}. "
                f"This gives you a head start toward {pathway['name']}."
            ),
        })
        step_num += 1

    # Step 2: training for missing skills
    training_topics = pathway.get("training", {}).get("recommended_topics", missing)
    if missing:
        steps.append({
            "step": step_num,
            "title": "Complete skill-gap training",
            "detail": (
                f"Enroll in training covering: {', '.join(missing)}. "
                f"Suggested training topics: {', '.join(training_topics[:5])}."
            ),
        })
        step_num += 1

    # Step 3: certification, if this is a real NSQF-mapped role
    qp_code = pathway.get("training", {}).get("qp_code")
    nsqf_level = pathway.get("training", {}).get("nsqf_level")
    if qp_code:
        steps.append({
            "step": step_num,
            "title": "Get NSQF-certified",
            "detail": (
                f"This pathway maps to Qualification Pack {qp_code} (NSQF Level {nsqf_level}). "
                f"Look for a training provider offering this QP under PM-AJAY / Skill India "
                f"to receive a recognized certificate."
            ),
        })
        step_num += 1
    else:
        steps.append({
            "step": step_num,
            "title": "Find a local training provider",
            "detail": (
                "This is a prototype pathway without a confirmed official NSQF mapping yet. "
                "Check with your local Skill India / PM-AJAY center for the closest certified "
                "equivalent training."
            ),
        })
        step_num += 1

    # Step 4: employment path
    employment_types = pathway.get("employment", {}).get("types", [])
    if user_profile.get("employment_preference") == "self_employment" and "self_employment" in employment_types:
        steps.append({
            "step": step_num,
            "title": "Plan your self-employment setup",
            "detail": (
                f"Since you prefer self-employment, plan for the tools, workspace, or micro-loan "
                f"support (e.g. through PM-AJAY GIA component) needed to start as a "
                f"{pathway['name'].lower()}."
            ),
        })
    else:
        steps.append({
            "step": step_num,
            "title": "Look for local job openings",
            "detail": (
                f"Check with local {pathway['category']} sector employers, cooperatives, or "
                f"the district skill center for openings matching {pathway['name']}."
            ),
        })
    step_num += 1

    # Step 5: mobility-aware note
    mobility = user_profile.get("mobility")
    if mobility == "local_only":
        steps.append({
            "step": step_num,
            "title": "Look for opportunities close to home",
            "detail": (
                "Based on your preference to stay local, prioritize training centers and "
                "employers within your immediate area before considering regional options."
            ),
        })

    return {
        "pathway_name": pathway["name"],
        "pathway_id": pathway["id"],
        "roadmap": steps,
    }


if __name__ == "__main__":
    import sys, os
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, CURRENT_DIR)
    from hybrid_recommender import recommend

    test_profile = {
        "education_level": 10,
        "skills": ["farming", "tractor repair"],
        "interests": ["machines", "agriculture", "repair"],
        "employment_preference": "self_employment",
        "mobility": "local_only",
    }

    results = recommend(test_profile, top_n=1)
    roadmap = generate_roadmap(results[0], test_profile)

    import json
    print(json.dumps(roadmap, indent=2))