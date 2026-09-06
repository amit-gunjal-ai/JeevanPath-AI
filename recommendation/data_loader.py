import json
import os


def load_pathways():
    # Get the project root directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    data_path = os.path.join(
        current_dir,
        "..",
        "data",
        "livelihood_pathways.json"
    )

    with open(data_path, "r", encoding="utf-8") as file:
        pathways = json.load(file)

    return pathways


def create_pathway_text(pathway):
    """
    Convert a pathway JSON record into meaningful text
    for semantic similarity comparison.
    """

    name = pathway["name"]
    category = pathway["category"]
    description = pathway["description"]

    interests = ", ".join(pathway["interests"])

    required_skills = ", ".join(
        pathway["skills"]["required"]
    )

    preferred_skills = ", ".join(
        pathway["skills"]["preferred"]
    )

    keywords = ", ".join(pathway["keywords"])

    text = f"""
    Career: {name}.
    Category: {category}.
    Description: {description}.
    Required skills: {required_skills}.
    Preferred skills: {preferred_skills}.
    Suitable interests: {interests}.
    Related keywords: {keywords}.
    """

    return text.strip()


if __name__ == "__main__":

    pathways = load_pathways()

    for pathway in pathways:

        print("\n" + "=" * 60)

        print(create_pathway_text(pathway))