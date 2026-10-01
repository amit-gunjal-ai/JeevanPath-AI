import os

# Keep CPU memory usage lower on small cloud instances
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys
import json
import hashlib
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)

from data_loader import load_pathways, create_pathway_text

MODEL_NAME = "all-MiniLM-L6-v2"

EMBEDDINGS_DIR = os.path.join(CURRENT_DIR, "..", "data", "embeddings")
EMBEDDINGS_PATH = os.path.join(EMBEDDINGS_DIR, "pathway_embeddings.npy")
IDS_PATH = os.path.join(EMBEDDINGS_DIR, "pathway_ids.json")
HASH_PATH = os.path.join(EMBEDDINGS_DIR, "pathways_hash.txt")

_model = None  # loaded once per process


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def _pathways_hash(pathways):
    raw = json.dumps(pathways, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _load_cache(current_hash):
    if not (os.path.exists(EMBEDDINGS_PATH)
            and os.path.exists(IDS_PATH)
            and os.path.exists(HASH_PATH)):
        return None, None

    with open(HASH_PATH, "r", encoding="utf-8") as f:
        cached_hash = f.read().strip()

    if cached_hash != current_hash:
        return None, None  # data.json changed since cache was built

    embeddings = np.load(EMBEDDINGS_PATH)
    with open(IDS_PATH, "r", encoding="utf-8") as f:
        ids = json.load(f)

    return embeddings, ids


def _save_cache(embeddings, ids, current_hash):
    os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
    np.save(EMBEDDINGS_PATH, embeddings)
    with open(IDS_PATH, "w", encoding="utf-8") as f:
        json.dump(ids, f)
    with open(HASH_PATH, "w", encoding="utf-8") as f:
        f.write(current_hash)


def get_pathway_embeddings(pathways=None):
    """Returns (embeddings, ids, pathways). Encodes only if the
    pathways JSON has changed since the last cached run."""
    if pathways is None:
        pathways = load_pathways()

    current_hash = _pathways_hash(pathways)
    embeddings, ids = _load_cache(current_hash)

    if embeddings is not None:
        return embeddings, ids, pathways

    model = get_model()
    texts = [create_pathway_text(p) for p in pathways]
    ids = [p["id"] for p in pathways]
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)

    _save_cache(embeddings, ids, current_hash)
    return embeddings, ids, pathways


def encode_user_profile(profile_text):
    model = get_model()
    return model.encode([profile_text], convert_to_numpy=True, show_progress_bar=False)[0]


def get_semantic_matches(user_profile_text, top_n=None):
    embeddings, ids, pathways = get_pathway_embeddings()
    user_embedding = encode_user_profile(user_profile_text)

    similarities = cosine_similarity([user_embedding], embeddings)[0]
    id_to_pathway = {p["id"]: p for p in pathways}

    results = [
        {"pathway": id_to_pathway[pid], "semantic_score": float(score)}
        for pid, score in zip(ids, similarities)
    ]
    results.sort(key=lambda r: r["semantic_score"], reverse=True)

    return results[:top_n] if top_n else results


if __name__ == "__main__":
    test_profile = """
    I help my family with farming. I know how to repair basic farm equipment
    like tractors and pumps. I am interested in machines and technology.
    I prefer to work locally and would like to start my own small business.
    """

    matches = get_semantic_matches(test_profile)

    print("SEMANTIC RECOMMENDATIONS\n")
    for m in matches:
        print(f"{m['pathway']['name']}")
        print(f"Semantic Match: {m['semantic_score'] * 100:.2f}%\n")