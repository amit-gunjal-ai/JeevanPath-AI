import json
import os
import re

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, "..", "data")

CURATED_PATH = os.path.join(DATA_DIR, "livelihood_pathways.json")
NSQF_PATH = os.path.join(DATA_DIR, "nsqf_dataset.json")
OUTPUT_PATH = os.path.join(DATA_DIR, "livelihood_pathways.json")
BACKUP_PATH = os.path.join(DATA_DIR, "livelihood_pathways_prototype_backup.json")

EDUCATION_PATTERNS = [
    (r"8\s*th", 8),
    (r"10\s*th|class\s*x\b|matric", 10),
    (r"12\s*th|class\s*xii\b|higher secondary", 12),
    (r"graduate|degree|b\.?tech|b\.?sc|b\.?a\.?", 15),
    (r"diploma|iti", 10),
]


def parse_min_education(text):
    if not text:
        return None
    text_lower = text.lower()
    for pattern, level in EDUCATION_PATTERNS:
        if re.search(pattern, text_lower):
            return level
    return None


def qp_to_pathway(qp):
    min_education = parse_min_education(qp.get("entry_qualification", ""))
    keywords = qp.get("informal_skill_keywords", [])
    employment_types = (
        ["self_employment", "wage_employment"] if qp.get("self_employment") else ["wage_employment"]
    )
    pathway_id = "NSQF-" + qp["qp_code"].replace("/", "-")

    return {
        "id": pathway_id,
        "name": qp["job_role"],
        "category": qp["sector"],
        "description": (
            f"{qp['job_role']} is an NSQF-aligned job role in the {qp['sector']} sector "
            f"(Qualification Pack {qp['qp_code']}, NSQF Level {qp['nsqf_level']})."
        ),
        "eligibility": {
            "minimum_education": min_education,
            "age_requirement": None,
        },
        "employment": {
            "types": employment_types,
            "work_environment": [qp["sector"].lower()],
        },
        "skills": {
            "required": keywords if keywords else [qp["job_role"].lower()],
            "preferred": [],
        },
        "interests": keywords if keywords else [qp["sector"].lower()],
        "constraints": {
            "mobility": "local_or_regional",
        },
        "training": {
            "recommended_topics": keywords if keywords else [qp["job_role"].lower()],
            "qp_code": qp["qp_code"],
            "nsqf_level": qp["nsqf_level"],
            "duration_hours": qp.get("duration_hours"),
        },
        "keywords": keywords,
        "source": "NSQF master QP-NOS list (2018 notification, unverified against live NCVET records)",
        "verified": False,
    }


def main():
    with open(CURATED_PATH, "r", encoding="utf-8") as f:
        curated = json.load(f)

    for p in curated:
        p.setdefault("source", "curated_prototype")
        p.setdefault("verified", False)

    if not os.path.exists(BACKUP_PATH):
        with open(BACKUP_PATH, "w", encoding="utf-8") as f:
            json.dump(curated, f, indent=2, ensure_ascii=False)
        print(f"Backed up original 6 curated pathways to {BACKUP_PATH}")

    with open(NSQF_PATH, "r", encoding="utf-8") as f:
        nsqf_data = json.load(f)

    qps = nsqf_data["qualification_packs"]
    nsqf_pathways = [qp_to_pathway(qp) for qp in qps]

    curated_ids = {p["id"] for p in curated}
    merged = curated + [p for p in nsqf_pathways if p["id"] not in curated_ids]

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(merged)} pathways ({len(curated)} curated + {len(nsqf_pathways)} NSQF-derived) to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()