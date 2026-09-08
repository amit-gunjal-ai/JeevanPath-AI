def meets_eligibility(user_profile, pathway):
    reasons = []
    eligible = True

    eligibility = pathway.get("eligibility", {})
    min_education = eligibility.get("minimum_education")
    age_requirement = eligibility.get("age_requirement")

    user_education = user_profile.get("education_level")
    user_age = user_profile.get("age")

    if min_education is not None:
        if user_education is None:
            reasons.append("Education level unknown; cannot confirm eligibility.")
        elif user_education < min_education:
            eligible = False
            reasons.append(
                f"Requires minimum education level {min_education}, user has {user_education}."
            )
        else:
            reasons.append("Education requirement met.")

    if age_requirement:
        min_age = age_requirement.get("min")
        max_age = age_requirement.get("max")

        if user_age is None:
            reasons.append("Age unknown; cannot confirm age eligibility.")
        else:
            if min_age is not None and user_age < min_age:
                eligible = False
                reasons.append(f"Minimum age required is {min_age}.")
            if max_age is not None and user_age > max_age:
                eligible = False
                reasons.append(f"Maximum age allowed is {max_age}.")
            if eligible and (min_age is not None or max_age is not None):
                reasons.append("Age requirement met.")

    return {"eligible": eligible, "reasons": reasons}


def filter_eligible_pathways(user_profile, pathways):
    return [
        {
            "pathway": pathway,
            "eligible": (check := meets_eligibility(user_profile, pathway))["eligible"],
            "eligibility_reasons": check["reasons"],
        }
        for pathway in pathways
    ]


if __name__ == "__main__":
    from data_loader import load_pathways

    pathways = load_pathways()
    test_profile = {"education_level": 8, "age": 24}
    results = filter_eligible_pathways(test_profile, pathways)

    for r in results:
        status = "ELIGIBLE" if r["eligible"] else "NOT ELIGIBLE"
        print(f"{r['pathway']['name']}: {status}")
        for reason in r["eligibility_reasons"]:
            print(f"  - {reason}")
        print()