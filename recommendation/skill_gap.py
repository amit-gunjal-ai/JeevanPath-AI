def calculate_skill_gap(user_skills, required_skills):

    # Convert everything to lowercase for better comparison
    user_skills = [skill.lower() for skill in user_skills]
    required_skills = [skill.lower() for skill in required_skills]

    matched_skills = []
    missing_skills = []

    for skill in required_skills:

        if skill in user_skills:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }