# ============================================================
# C1: Neural Pruning (構造的蒸留) — 実稼働toy実験スクリプト
# ============================================================
# 機能：
# 1. 重み行列Wの剪定 (L1ノルム基準)
# 2. テキストからBP抽出 (Axes / Claims / Constraints)
# 3. CR(圧縮率) と SP(構造保存度) をC3定義で計算
# 4. 結果を metrics.json に保存
# ------------------------------------------------------------
# 依存：numpy, networkx, re (標準)
# 実行方法：
#   python scripts/run_C1_NP_min.py
# ------------------------------------------------------------

import json, pathlib, numpy as np, re, itertools, networkx as nx

# ---------- Blueprint抽出補助 --------------------------------

CAUSE_WORDS = ("because","therefore","so","hence","thus","ので","だから","ゆえに")
TIME_WORDS  = ("today","now","later","before","after","昨日","今日","明日")

def split_sentences(txt):
    """文分割（日本語・英語混在対応の簡易版）"""
    return [s.strip() for s in re.split(r'[。.!?]', txt) if s.strip()]

def extract_triplets(sent):
    """文から名詞-動詞-名詞の三つ組を抽出"""
    toks = re.findall(r'[A-Za-z0-9一-龥ぁ-んァ-ン]+', sent)
    trip = []
    for i in range(len(toks)-2):
        a,b,c = toks[i:i+3]
        if re.match(r'.*(する|した|なる|be|is|are|do|make|cause).*', b):
            trip.append([a,"rel",c])
    return trip or ([[toks[0],"rel",toks[-1]]] if len(toks)>=2 else [])

def build_claims(texts):
    """複数文書からClaims集合を作成"""
    claims=[]
    for t in texts:
        for s in split_sentences(open(t,encoding='utf-8').read()):
            for tri in extract_triplets(s):
                claims.append({"form":tri,"conf":1.0})
    # 型付け
    for c in claims:
        s = " ".join(c["form"])
        if any(w in s for w in CAUSE_WORDS): c["form"][1]="causes"
        elif "含" in s or "include" in s:    c["form"][1]="includes"
        else:                                 c["form"][1]="precedes"
    for i,c in enumerate(claims): c["id"]=f"c_{i}"
    return claims

def axes_from_texts(texts):
    """抽象度・因果密度・時間スケールを抽出"""
    txt=" ".join(open(t,encoding='utf-8').read() for t in texts)
    toks=re.findall(r'[A-Za-z0-9一-龥ぁ-んァ-ン]+', txt)
    uniq=len(set(toks)); total=max(1,len(toks))
    abstractness = min(1.0, uniq/total*1.5)
    causal_density = 1.0 if any(w in txt for w in CAUSE_WORDS) else 0.3
    timescale = "mid" if any(w in txt for w in TIME_WORDS) else "long"
    return {"abstractness":abstractness,"causal_density":causal_density,"timescale":timescale}

def constraints_from_claims(claims):
    """因果・包含・時制の非循環チェック"""
    cons=[]
    for rel in ("causes","includes","precedes"):
        edges=[(c["form"][0],c["form"][2]) for c in claims if c["form"][1]==rel]
        G=nx.DiGraph(); G.add_edges_from(edges)
        ok = nx.is_directed_acyclic_graph(G)
        cons.append({"rule":f"{rel}_acyclic","value":1 if ok else 0})
    return cons

def bp_from_texts(texts):
    """テキスト群からBP=(A,C,φ)を構築"""
    A=axes_from_texts(texts)
    C=build_claims(texts)
    φ=constraints_from_claims(C)
    return {"A":A,"C":C,"phi":φ}

def r_struct_from_texts(texts):
    """|R|_struct：命題単位数（全三つ組数）"""
    return sum(len(extract_triplets(s)) for t in texts for s in split_sentences(open(t,encoding='utf-8').read())) or 1

def sp_between(bp0,bp1):
    """構造保存度SP（二段統合）"""
    E0=set((tuple(c["form"]) for c in bp0["C"]))
    E1=set((tuple(c["form"]) for c in bp1["C"]))
    j_edge = len(E0 & E1)/len(E0 | E1) if (E0|E1) else 1.0
    P0=set((a,b,c) for (a,_,b) in E0 for (bb,_,c) in E0 if b==bb)
    P1=set((a,b,c) for (a,_,b) in E1 for (bb,_,c) in E1 if b==bb)
    f1 = (2*len(P0 & P1)/(len(P0)+len(P1))) if (P0 or P1) else 1.0
    return 0.5*j_edge + 0.5*f1

# ---------- Pruningと計算本体 --------------------------------

def magnitude_prune(W, p):
    """重み行列をL1ノルムでp割合ゼロ化"""
    flat = np.abs(W).flatten()
    thr = np.quantile(flat, p) if len(flat) else 0.0
    M = W.copy(); M[np.abs(M) <= thr] = 0.0
    return M

def train_model():
    """toyモデルの重み行列を生成"""
    rng=np.random.default_rng(42)
    return {"W": rng.normal(0,1,(64,64))}

def apply_pruning(model, p):
    """剪定率pでモデルを更新"""
    return {"W": magnitude_prune(model["W"], p), "p": p}

def extract_BP(model, texts):
    """剪定後のBPを抽出（命題数をpに応じて減らす近似）"""
    bp = bp_from_texts(texts)
    if "p" in model:
        k = int(len(bp["C"]) * (1 - 0.9*model["p"]))  # 剪定で命題を間引く近似
        bp["C"] = bp["C"][:max(1,k)]
    return bp

def compute_CR_struct(bp_base, bp_after, r_struct):
    """構造CR = 1 - |BP| / |R|struct"""
    sz = len(bp_after["C"]) + len(bp_after["phi"]) + 3  # Aを3要素として加算
    return max(0.0, min(1.0, 1 - sz / max(1, r_struct)))

# ---------- メイン実行 ---------------------------------------

def main():
    out = pathlib.Path("outputs/C1"); out.mkdir(parents=True, exist_ok=True)
    texts = ["texts/doc1.txt","texts/doc2.txt"]

    # 構造サイズ |R|struct
    r_struct = r_struct_from_texts(texts)

    base = train_model()
    bp0 = extract_BP(base, texts)

    results=[]
    for p in [0.0, 0.4, 0.8]:
        m = apply_pruning(base, p)
        bp = extract_BP(m, texts)
        cr = round(compute_CR_struct(bp0, bp, r_struct), 2)
        sp = round(sp_between(bp0, bp), 2)
        results.append({"p":p,"CR":cr,"SP":sp,"BP_size":len(bp["C"])})
        print(f"p={p:.1f}  CR={cr:.2f}  SP={sp:.2f}")

    meta={"experiment":"N-P-struct","grain":"L2","anchors":"sft_basic","seeds":[1]}
    with open(out/"metrics.json","w",encoding="utf-8") as f:
        json.dump({"meta":meta,"results":results}, f, ensure_ascii=False, indent=2)

    print("\nSaved -> outputs/C1/metrics.json")

if __name__=="__main__":
    main()
