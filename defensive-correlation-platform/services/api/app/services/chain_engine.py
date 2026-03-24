from uuid import uuid4

def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    return len(a & b) / max(1, len(a | b))

def link_confidence(new_tags, old_tags, new_vec, old_vec) -> float:
    tag_overlap = jaccard(set(new_tags), set(old_tags))
    vec_overlap = jaccard(set(new_vec), set(old_vec))
    return (0.6 * tag_overlap) + (0.4 * vec_overlap)

def decide_action(best_score: float) -> str:
    if best_score >= 0.60:
        return "append"
    if best_score >= 0.35:
        return "orphan"
    return "seed"

def score_to_status(score: float) -> str:
    if score >= 0.70: return "CRITICAL"
    if score >= 0.50: return "VALIDATED"
    if score >= 0.30: return "CANDIDATE"
    return "POTENTIAL"

def new_chain_id():
    return uuid4()
