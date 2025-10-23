# scripts/bp_extractor_min.py（抜粋）
import re, itertools, networkx as nx

CAUSE_WORDS = ("because","therefore","so","hence","thus","ので","だから","ゆえに")
TIME_WORDS  = ("today","now","later","before","after","昨日","今日","明日")

def split_sentences(txt):
    return [s.strip() for s in re.split(r'[。.!?]', txt) if s.strip()]

def extract_triplets(sent):
    # 超簡易：名詞-動詞-名詞 を貪欲に拾う（日本語/英語の混在でも動く程度）
    toks = re.findall(r'[A-Za-z0-9一-龥ぁ-んァ-ン]+', sent)
    trip = []
    for i in range(len(toks)-2):
        a,b,c = toks[i:i+3]
        if re.match(r'.*(する|した|なる|した|be|is|are|do|make|cause).*', b):
            trip.append([a,"rel",c])
    return trip or ([[toks[0],"rel",toks[-1]]] if len(toks)>=2 else [])

def build_claims(texts):
    claims=[]
    for t in texts:
        for s in split_sentences(open(t,encoding='utf-8').read()):
            for tri in extract_triplets(s):
                claims.append({"form":tri,"conf":1.0})
    # 型付け（簡易）：因果語があれば causes、括弧や「含む」語なら includes、時相なら precedes
    for c in claims:
        s = " ".join(c["form"])
        if any(w in s for w in CAUSE_WORDS): c["form"][1]="causes"
        elif "含" in s or "include" in s:    c["form"][1]="includes"
        else:                                 c["form"][1]="precedes"
    # ID付与
    for i,c in enumerate(claims): c["id"]=f"c_{i}"
    return claims

def axes_from_texts(texts):
    txt=" ".join(open(t,encoding='utf-8').read() for t in texts)
    toks=re.findall(r'[A-Za-z0-9一-龥ぁ-んァ-ン]+', txt)
    uniq=len(set(toks)); total=max(1,len(toks))
    abstractness = min(1.0, uniq/total*1.5)             # 語彙多様度で近似
    causal_density = 1.0 if any(w in txt for w in CAUSE_WORDS) else 0.3
    timescale = "mid" if any(w in txt for w in TIME_WORDS) else "long"
    return {"abstractness":abstractness,"causal_density":causal_density,"timescale":timescale}

def constraints_from_claims(claims):
    cons=[]
    for rel in ("causes","includes","precedes"):
        edges=[(c["form"][0],c["form"][2]) for c in claims if c["form"][1]==rel]
        G=nx.DiGraph(); G.add_edges_from(edges)
        ok = nx.is_directed_acyclic_graph(G)
        cons.append({"rule":f"{rel}_acyclic","value":1 if ok else 0})
    return cons

def bp_from_texts(texts):
    A=axes_from_texts(texts)
    C=build_claims(texts)
    φ=constraints_from_claims(C)
    return {"A":A,"C":C,"phi":φ}

def r_struct_from_texts(texts):
    # |R|_struct：命題数として、全文からの triplet 個数
    return sum(len(extract_triplets(s)) for t in texts for s in split_sentences(open(t,encoding='utf-8').read())) or 1

def sp_between(bp0,bp1):
    # Edge Jaccard + Path F1（簡易）：型付きエッジのみ
    E0=set((tuple(c["form"]) for c in bp0["C"]))
    E1=set((tuple(c["form"]) for c in bp1["C"]))
    j_edge = len(E0 & E1)/len(E0 | E1) if (E0|E1) else 1.0
    # 簡易path（長さ2の連鎖）
    P0=set((a,b,c) for (a,_,b) in E0 for (bb,_,c) in E0 if b==bb)
    P1=set((a,b,c) for (a,_,b) in E1 for (bb,_,c) in E1 if b==bb)
    f1 = (2*len(P0 & P1)/(len(P0)+len(P1))) if (P0 or P1) else 1.0
    return 0.5*j_edge + 0.5*f1
