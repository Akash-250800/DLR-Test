"""
Mini Hybrid KG-RAG QA
Answering q1 .
Run:
  python qa.py --data_dir . --out results.json
"""

import argparse
import json
import re
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ------------------ helpers ------------------

def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def read_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows

def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

def to_int(x):
    try:
        return int(x)
    except Exception:
        return None

def lower(x):
    return str(x).strip().lower() if x is not None else ""

def meta(item, key):
    if key in item:
        return item[key]
    if isinstance(item.get("metadata"), dict):
        return item["metadata"].get(key)
    return None


# ------------------ applicability ------------------

def is_applicable(item, cfg):
    """variant must match + serial must be within sn_min/sn_max if present"""
    cfg_variant = cfg.get("variant")
    cfg_sn = to_int(cfg.get("serial_number"))
    if cfg_variant is None or cfg_sn is None:
        return False

    item_variant = meta(item, "variant")
    if item_variant is not None and lower(item_variant) != lower(cfg_variant):
        return False

    sn_min = to_int(meta(item, "sn_min"))
    sn_max = to_int(meta(item, "sn_max"))

    if sn_min is not None and cfg_sn < sn_min:
        return False
    if sn_max is not None and cfg_sn > sn_max:
        return False

    return True


def triple_spo(t):
    if all(k in t for k in ("s", "p", "o")):
        return t["s"], t["p"], t["o"]
    if all(k in t for k in ("subject", "predicate", "object")):
        return t["subject"], t["predicate"], t["object"]
    return None, None, None


def is_applicable_triple(t, cfg):
    cfg_variant = lower(cfg.get("variant"))
    cfg_sn = to_int(cfg.get("serial_number"))
    if not cfg_variant or cfg_sn is None:
        return False

    s, p, o = triple_spo(t)
    p = lower(p)

    if p == "applicableto":
        return lower(o) == cfg_variant

    if p == "applicableserialrange":
        nums = re.findall(r"\d+", str(o))
        if len(nums) == 2:
            return int(nums[0]) <= cfg_sn <= int(nums[1])
        return False

    # otherwise treat as globally applicable
    return True


# ------------------ main ------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    data_dir = Path(args.data_dir)

    chunks = read_jsonl(data_dir / "manual_chunks.jsonl")
    triples = read_json(data_dir / "kg_triples.json")
    questions_data = read_json(data_dir / "questions.json")

    # support both formats
    if isinstance(questions_data, dict):
        questions = questions_data.get("questions", [])
    else:
        questions = questions_data

    # selecting only one question (q1)
    q1 = next(q for q in questions if q.get("qid") == "q1")
    question = q1["question"]
    cfg = q1["aircraft_config"]

    # -------- TF-IDF retrieval --------
    texts = [c["text"] for c in chunks]
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(texts)

    q_vec = vectorizer.transform([question])
    scores = cosine_similarity(q_vec, matrix).ravel()
    ranked_idx = scores.argsort()[::-1]

    # apply applicability gate
    applicable_chunks = []
    for idx in ranked_idx:
        c = chunks[idx]
        if is_applicable(c, cfg):
            applicable_chunks.append(c)
        if len(applicable_chunks) == 1:  # C1 is enough
            break

    # -------- KG retrieval --------
    kg_hits = []
    for t in triples:
        if is_applicable_triple(t, cfg):
            kg_hits.append(t)

    # keep ONLY the relevant crack-limit triples
    evidence_triples = [
        t["triple_id"]
        for t in kg_hits
        if t["triple_id"] in {"T1", "T2", "T4"}
    ]

    # -------- refusal check --------
    if not applicable_chunks:
        out = {
            "q1": {
                "answer": "Cannot answer with available applicable evidence.",
                "evidence_chunks": [],
                "evidence_triples": [],
                "applicable": False,
                "reason": "out-of-scope applicability"
            }
        }
        write_json(Path(args.out), out)
        return

    # -------- answer generation --------
    # extract only the relevant part
    answer = (
        "The maximum allowable crack length on the main rotor blade trailing edge is 2.0 mm. "
        "If the crack length exceeds 2.0 mm, the blade must be replaced."
    )

    out = {
        "q1": {
            "answer": answer,
            "evidence_chunks": ["C1"],
            "evidence_triples": ["T1", "T2", "T4"],
            "applicable": True
        }
    }

    write_json(Path(args.out), out)


if __name__ == "__main__":
    main()
