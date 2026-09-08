import os
import sys
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)

from data_loader import load_pathways
from semantic_matcher import get_model

EMBEDDINGS_DIR = os.path.join(CURRENT_DIR, "..", "data", "embeddings")
VOCAB_EMB_PATH = os.path.join(EMBEDDINGS_DIR, "skill_vocab_embeddings.npy")
VOCAB_LIST_PATH = os.path.join(EMBEDDINGS_DIR, "skill_vocab.json")

SIMILARITY_THRESHOLD = 0.55


def build_skill_vocabulary(pathways=None):
    pathways = pathways or load_pathways()
    vocab = set()
    for p in pathways:
        for skill in p.get("skills", {}).get("required", []):
            vocab.add(skill.lower().strip())
        for skill in p.get("skills", {}).get("preferred", []):
            vocab.add(skill.lower().strip())
    return sorted(vocab)


def get_skill_vocab_embeddings():
    if os.path.exists(VOCAB_EMB_PATH) and os.path.exists(VOCAB_LIST_PATH):
        embeddings = np.load(VOCAB_EMB_PATH)
        with open(VOCAB_LIST_PATH, "r", encoding="utf-8") as f:
            vocab = json.load(f)
        return embeddings, vocab

    vocab = build_skill_vocabulary()
    model = get_model()
    embeddings = model.encode(vocab, convert_to_numpy=True, show_progress_bar=False)

    os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
    np.save(VOCAB_EMB_PATH, embeddings)
    with open(VOCAB_LIST_PATH, "w", encoding="utf-8") as f:
        json.dump(vocab, f)

    return embeddings, vocab


def normalize_skill(raw_skill, threshold=SIMILARITY_THRESHOLD):
    embeddings, vocab = get_skill_vocab_embeddings()
    model = get_model()
    query_embedding = model.encode([raw_skill.lower().strip()], convert_to_numpy=True, show_progress_bar=False)

    similarities = cosine_similarity(query_embedding, embeddings)[0]
    best_idx = int(np.argmax(similarities))
    best_score = float(similarities[best_idx])

    if best_score >= threshold:
        return {"normalized": vocab[best_idx], "original": raw_skill, "confidence": best_score}
    return {"normalized": raw_skill.lower().strip(), "original": raw_skill, "confidence": best_score}


def normalize_skill_list(raw_skills, threshold=SIMILARITY_THRESHOLD):
    return [normalize_skill(s, threshold) for s in raw_skills]


if __name__ == "__main__":
    test_skills = ["basic electronics", "fixing phones", "tractor repair", "stitching clothes"]
    for s in test_skills:
        result = normalize_skill(s)
        print(f"'{s}' -> '{result['normalized']}' (confidence: {result['confidence']:.2f})")