Test Pack: Mini Hybrid KG-RAG QA with Evidence + Applicability Gate

Goal:
Build a mini QA pipeline that answers maintenance questions by combining:
- text retrieval (RAG)
- KG subgraph retrieval
and outputs an answer with evidence + applicability check.

You are given:
manual_chunks.jsonl  (12 manual chunks + metadata)
kg_triples.json      (small KG triples)
questions.json       (3 questions + aircraft configuration context)

Your task:
Write qa.py that:

1. Text retriever:
   For each question, retrieve top-k=3 most relevant chunks from manual_chunks.jsonl (TF-IDF is fine).

2. KG retriever:
   Detect entities from the question (simple keyword match is OK)
   and return a subgraph: triples where subject or object matches detected entities.

3. Applicability gate:
   Only use chunks/triples that are applicable to the given aircraft config:
   - variant must match
   - serial_number must fall inside sn_min–sn_max

   For KG triples:
   - If a triple explicitly encodes applicability (e.g., p="applicableTo" or p="applicableSerialRange"),
     enforce it.
   - If a triple has no applicability information, you may treat it as globally applicable.

   If no applicable evidence exists → output a refusal:
     "Cannot answer with available applicable evidence."

4. Answer and evidence:
   Produce results.json with, for any one question:
     - answer (1–3 sentences)
     - evidence_chunks (list of chunk_ids you used)
     - evidence_triples (list of triple_ids you used)
     - applicable (true/false)
     - reason (only if applicable=false)

Output format (required):
{
  "q1": {
    "answer": "...",
    "evidence_chunks": ["C1","C2"],
    "evidence_triples": ["T4","T6"],
    "applicable": true
  },
  "q2": {
    "answer": "Cannot answer with available applicable evidence.",
    "evidence_chunks": [],
    "evidence_triples": [],
    "applicable": false,
    "reason": "out-of-scope applicability"
  }
}

Allowed simplifications:
- Entity linking can be simple keyword matching.
- Answer generation can be lightweight: e.g., extract key sentence from best chunk.
- No UI required, just JSON output.

What we score:
- Correctness (relevant chunk selection + correct final answer)
- Evidence quality (clear chunk + triple IDs)
- Applicability correctness (refuse when not applicable)
- Code clarity (readable, structured)

Run expectation:
Your solution should be runnable as:
  python qa.py --data_dir  --out results.json
(or document your run command in a comment at top of qa.py)
