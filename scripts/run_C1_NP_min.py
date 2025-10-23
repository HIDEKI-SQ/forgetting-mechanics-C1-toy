# Minimal N-P (pruning) smoke script: generates metrics.json (no heavy ML)
import json, pathlib

def train_model():
    # Stub: return a dict-like model
    return {"trained": True}

def prune_by_l1_norm(model, p):
    # Stub pruning: clone model and annotate p
    return {"trained": True, "p": p}

def extract_BP(model, texts):
    # Stub: just return a fake BP size that depends on 'p'
    p = model.get("p", 0.0)
    # base size 100 -> reduced by p
    bp_size = int(100 * (1 - 0.9*p))
    return {"size": bp_size, "p": p}

def compute_CR(bp0, bp1):
    # CR_struct ~ 1 - |BP1|/|BP0|
    return max(0.0, min(1.0, 1.0 - (bp1["size"] / max(1.0, bp0["size"]))))

def compute_SP(bp0, bp1):
    # Use a deterministic convex curve around p*=0.42 as a proxy
    p = bp1.get("p", 0.0)
    sp = -2.34 * (p - 0.42)**2 + 0.63
    return max(0.0, min(1.0, sp))

def main():
    out = pathlib.Path("outputs/C1"); out.mkdir(parents=True, exist_ok=True)
    texts = ["texts/doc1.txt", "texts/doc2.txt"]
    model0 = train_model()
    bp0 = extract_BP(model0, texts)

    results = []
    for p in [0.0, 0.4, 0.8]:
        m = prune_by_l1_norm(model0, p)
        bp = extract_BP(m, texts)
        cr = round(compute_CR(bp0, bp), 2)
        sp = round(compute_SP(bp0, bp), 2)
        results.append({"p": p, "CR": cr, "SP": sp, "BP_size": bp["size"]})

    meta = {"experiment":"N-P-mini","grain":"L2","anchors":"sft_basic","seeds":[1]}
    with open(out/"metrics.json","w",encoding="utf-8") as f:
        json.dump({"meta":meta,"results":results}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
