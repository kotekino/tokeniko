"""A PICTURE OF THE REAL BASE — 4,445 dimensions, R and D, and the dual read they are read as.

    PYTHONPATH=. ../.venv/bin/python tools/base_map.py                    # -> out/base_map.html
    PYTHONPATH=. ../.venv/bin/python tools/base_map.py --db … --build …   # the STORED base
    PYTHONPATH=. ../.venv/bin/python tools/base_map.py --layout pca       # the flat projection

A DIAGNOSTIC INSTRUMENT AND NOT A DELIVERABLE. The Captain walks the map as part of the E1 gate, and
what he is walking it for is one class of defect: the kind that hides in plain sight because every
number about it looks healthy. `left` was one — a key that should not have existed, mined from an
inflection, sitting quietly in the base for weeks. So this page is built to surface THREE shapes of
that, and everything else on it is in service of them:

  A KEY THAT SHOULD NOT EXIST.  Every dimension carries FLAGS, computed and shown rather than
                                counted: its word lemmatises to another word that is also a key
                                (`left`'s own shape, requirement 21) · its word is a closed-class
                                form, which by the standing law is COMPILED and never defined · its
                                definition is two words long · its whole gloss vocabulary is
                                function words. The map can be filtered down to the flagged ones,
                                which is the walk worth taking first.
  A CELL WHOSE PROVENANCE IS WRONG.  Every R cell in the panel names its relation, its SOURCE
                                (mined / curated / axis) and its `via` — every relation that held
                                between the two, not only the one that won. A derivation that
                                out-ranked a stated `attribute` is a thing you can see here.
  A NEIGHBOURHOOD THAT IS INCOHERENT.  D's neighbours are listed WITH THE WORDS THEY SHARE. This is
                                the change that matters most against the prototype's map: `below.r`
                                and `consist.v` read +0.865 and the reason is that both definitions
                                contain the word `in`, and no cosine on a screen will ever say so.

THE TWO CHANNELS STAY TWO, exactly as the prototype ruled: position comes from D (where a word sits
says what it is ABOUT), lines come from R (a line means somebody STATED a relation, and the sign is
drawn rather than averaged away). Nothing on the map is a blend — but the PANEL now carries a third
list, the dual read at the ruled mix, because since 2026-09-09 that is what the base is actually
read as, and a map that could not show it would be a picture of a base nobody uses.

The layout is numpy-only: PCA (SVD) on D's rows, then a small exact t-SNE on D's cosine distances
seeded from it. Both numbers the picture can be doubted with are printed — the variance PCA keeps,
and how much of each node's own D neighbourhood survived the trip to two dimensions.

Read-only on every database. The HTML is fully self-contained: no CDN, no font, no library — it must
open from a file:// URL on a laptop with the wifi off.
"""

import argparse
import json
import os
import time

import numpy as np

from tk2.datatier.policy_source import closed_forms, standing_bar, standing_policy
from tk2.dictionary import build, distribution, keys, policy, proposal
from tk2.dictionary.wordnet import WordNetProvider, wordnet_lexicon

#: How many D neighbours are carried per dimension. Ten is the prototype's and it is the right size
#: for a panel; the whole matrix is 1.67 million cells and no page wants them.
NEIGHBOURS = 10

#: A definition this short cannot say much, and two rows this short that share one function word are
#: the junk plateau in miniature — 5.3 words is the base's mean.
SHORT_GLOSS = 2

#: The words the base's definitions cannot avoid (`tools/build_dictionary.py`'s own set, and the
#: same reason it is stated rather than derived: the flag is a COMPARISON with a measured figure).
JUNK_WORDS = frozenset({"in", "be", "by", "as"})

#: The flags a dimension can carry, in the order they are shown. Each is a defect CLASS the E1
#: history actually produced, not a plausible one.
FLAGS = (
    ("inflection", "its word lemmatises to another word that is also a dimension — `left`'s shape"),
    ("closed", "its word is a closed-class form: compiled, never defined (the standing law)"),
    ("mute_r", "no named relation reaches this dimension — R is silent about it"),
    ("mute_d", "its definition shares no word with any other — D is silent about it"),
    ("junk", "its whole gloss vocabulary is function words: its D neighbourhood means nothing"),
    ("short", f"its definition is {SHORT_GLOSS} words or fewer"),
)


# ------------------------------------------------------------------------------------------------
# the base — built in place, or read back out of a body
# ------------------------------------------------------------------------------------------------


def load(db_name: str | None, build_label: str | None):
    """(the build, the gloss vectors, the config, a label for the page).

    Built in process by default and read from a database when one is named. The default is the
    build, not the read, for the same reason every other instrument's is: on the day a policy is
    ruled the rows exist in `db/` and nowhere else, and an instrument that could only look at a body
    could not look at what is about to be applied to it.
    """
    rows, policy_source = standing_policy(db_name)
    bar, bar_rows, bar_source = standing_bar(db_name)
    config = policy.config_from_rows(rows, bar_rows)
    provider = WordNetProvider(wordnet_lexicon(), lemma_scope=config.relations.lemma_scope)

    if db_name and build_label:
        from tk2.datatier import database
        from tk2.datatier.matrix_store import MongoMatrixStore

        store = MongoMatrixStore(database(db_name))
        relational = store.matrix(build_label, constants.DICTIONARY_RELATIONS)
        distributional = store.matrix(build_label, constants.DICTIONARY_DISTRIBUTION)
        built = build.BaseBuild(words=(), dimensions=relational.keys,
                                relational=relational, distributional=distributional)
        source = f"{db_name} build {build_label!r} (read back, sealed)"
    else:
        built = build.build_base(config, provider)
        source = f"built in process from {policy_source}"

    vectors = distribution.gloss_vectors(built.dimensions, provider, config.distribution)
    return built, vectors, config, provider, source, bar, bar_source


# ------------------------------------------------------------------------------------------------
# layout — positions are a function of D alone. R never moves a node.
# ------------------------------------------------------------------------------------------------


def dense_rows(matrix_object) -> np.ndarray:
    index = {key: i for i, key in enumerate(matrix_object.keys)}
    dense = np.zeros((len(index), len(index)), dtype=np.float32)
    for row in matrix_object.rows:
        for cell in row.cells:
            dense[row.index, index[cell.column]] = cell.weight
    return dense


def pca_2d(X: np.ndarray) -> tuple[np.ndarray, float]:
    """Plain SVD on the centred rows. Returns the coordinates and the variance the 2D picture keeps
    — reported out loud, because a projection that keeps a third of the variance has thrown away
    most of what it was given and should say so."""
    centred = X - X.mean(axis=0)
    U, S, _ = np.linalg.svd(centred, full_matrices=False)
    kept = float((S[:2] ** 2).sum() / (S ** 2).sum())
    return (U[:, :2] * S[:2]).astype(np.float32), kept


def joint_p(dist: np.ndarray, perplexity: float) -> np.ndarray:
    """The t-SNE affinity matrix: per row, the bandwidth that makes the neighbourhood have exactly
    `perplexity` effective neighbours, found by bisection on beta. Symmetrised and normalised."""
    n = dist.shape[0]
    P = np.zeros((n, n), dtype=np.float32)
    target = np.log(perplexity)
    for i in range(n):
        d = np.delete(dist[i], i).astype(np.float64)
        lo, hi, beta = 1e-12, 1e12, 1.0
        for _ in range(50):
            p = np.exp(-d * beta)
            s = p.sum()
            if s <= 0:
                break
            entropy = np.log(s) + beta * (d * p).sum() / s
            if abs(entropy - target) < 1e-5:
                break
            if entropy > target:
                lo = beta
                beta = beta * 2 if hi == 1e12 else (beta + hi) / 2
            else:
                hi = beta
                beta = beta / 2 if lo == 1e-12 else (beta + lo) / 2
        row = np.zeros(n)
        row[np.arange(n) != i] = p / max(p.sum(), 1e-300)
        P[i] = row
    P = (P + P.T) / (2 * n)
    return np.maximum(P, 1e-12)


def tsne_2d(dist: np.ndarray, seed_xy: np.ndarray, perplexity: float, iters: int,
            lr: float, say=print) -> np.ndarray:
    """t-SNE on the cosine distances, vectorised over the full 4,445 — exact, because at this size
    an approximation would buy a minute and cost reproducibility."""
    n = dist.shape[0]
    started = time.time()
    P = joint_p(dist, perplexity)
    say(f"  affinities in {time.time() - started:.0f}s")
    Y = (seed_xy / (seed_xy[:, 0].std() or 1.0) * 1e-2).astype(np.float32)
    dY = np.zeros_like(Y)
    gains = np.ones_like(Y)
    for step in range(iters):
        exaggerate = 12.0 if step < iters // 4 else 1.0
        momentum = 0.5 if step < iters // 4 else 0.8
        sq = (Y ** 2).sum(1)
        num = 1.0 / (1.0 + (sq[:, None] + sq[None, :] - 2 * Y @ Y.T))
        np.fill_diagonal(num, 0.0)
        Q = np.maximum(num / num.sum(), 1e-12)
        PQ = (P * exaggerate - Q) * num
        grad = 4 * ((np.diag(PQ.sum(1)) - PQ) @ Y)
        gains = np.maximum(np.where(np.sign(grad) != np.sign(dY), gains + 0.2, gains * 0.8), 0.01)
        dY = momentum * dY - lr * gains * grad
        Y = Y + dY
        Y -= Y.mean(0)
        if step and step % 200 == 0:
            say(f"  t-SNE {step}/{iters} ({time.time() - started:.0f}s)")
    return Y


def neighbour_fidelity(sim: np.ndarray, Y: np.ndarray, k: int = 10) -> float:
    """How much of D's own neighbourhood survived the trip to 2D — the only number that says whether
    the picture may be trusted as a picture of D. Reported, never optimised silently."""
    high = np.argpartition(-sim, k, axis=1)[:, :k]
    d2 = ((Y[:, None, :] - Y[None, :, :]) ** 2).sum(-1)
    np.fill_diagonal(d2, np.inf)
    near = np.argpartition(d2, k, axis=1)[:, :k]
    return float(np.mean([len(set(a) & set(b)) / k for a, b in zip(high, near)]))


# ------------------------------------------------------------------------------------------------
# the flags — the defect classes, computed per dimension
# ------------------------------------------------------------------------------------------------


def flags_of(built, vectors, provider, closed: frozenset[str]) -> tuple[list[int], dict[str, int]]:
    """One bitmask per dimension, and how many dimensions each flag caught.

    The inflection flag is `tk2.dictionary.proposal.inflection_of`'s question asked of the BASE
    rather than of the seed ranking it was written for: is this word an inflected form of another
    word that is ALSO a dimension here? That is `left` exactly — and the answer being yes is not by
    itself a defect (`used` is an honest adjective), which is why this is a flag on a map and not a
    refusal in the builder.
    """
    words = frozenset(keys.word_of(key) for key in built.dimensions)
    silent_r = {row.key for row in built.relational.rows if row.is_silent}
    silent_d = {row.key for row in built.distributional.rows if row.is_silent}

    masks = []
    counts = {name: 0 for name, _why in FLAGS}
    for key in built.dimensions:
        word = keys.word_of(key)
        gloss_words = vectors.get(key, frozenset())
        raised = {
            "inflection": bool(proposal.inflection_of(word, words, provider)),
            "closed": word in closed,
            "mute_r": key in silent_r,
            "mute_d": key in silent_d,
            "junk": bool(gloss_words) and set(gloss_words) <= JUNK_WORDS,
            "short": len(gloss_words) <= SHORT_GLOSS,
        }
        mask = 0
        for position, (name, _why) in enumerate(FLAGS):
            if raised[name]:
                mask |= 1 << position
                counts[name] += 1
        masks.append(mask)
    return masks, counts


# ------------------------------------------------------------------------------------------------
# the payload — parallel arrays, because the file is opened by double-clicking it
# ------------------------------------------------------------------------------------------------


def pack(built, vectors, provider, xy, sim_d, sim_dual, masks, bar, mix: float,
         floor: float, edge_min: float, neighbours: int) -> dict:
    keys_list = list(built.dimensions)
    index = {key: i for i, key in enumerate(keys_list)}

    relations: list[str] = []
    relation_id: dict[str, int] = {}
    sources = ["mined", "curated", "axis"]
    cells = []
    degree = [0] * len(keys_list)
    for row in built.relational.rows:
        for cell in row.cells:
            other = index.get(cell.column)
            if other is None or other == row.index:
                continue
            if abs(cell.weight) < edge_min:
                continue
            if cell.relation not in relation_id:
                relation_id[cell.relation] = len(relations)
                relations.append(cell.relation)
            via = [[relation_id.setdefault(p.relation, _add(relations, p.relation)), round(p.weight, 3)]
                   for p in cell.via]
            cells.append([row.index, other, round(cell.weight, 3), relation_id[cell.relation],
                          sources.index(cell.source) if cell.source in sources else 0, via])
            degree[row.index] += 1
            degree[other] += 1

    # The gloss VOCABULARY as word ids: the page intersects two rows' lists to show what a D cell is
    # actually made of. Sent once per dimension rather than once per neighbour pair — ten neighbours
    # each carrying their own word list would be ten copies of the same handful of words.
    vocabulary: list[str] = []
    word_id: dict[str, int] = {}
    gloss_words = []
    for key in keys_list:
        ids = []
        for word in sorted(vectors.get(key, ())):
            if word not in word_id:
                word_id[word] = len(vocabulary)
                vocabulary.append(word)
            ids.append(word_id[word])
        gloss_words.append(ids)

    def top(sim):
        order = np.argsort(-sim, axis=1)[:, :neighbours]
        return [[[int(j), round(float(sim[i, j]), 3)] for j in row] for i, row in enumerate(order)]

    above = (sim_dual >= floor).sum(axis=1).tolist()

    x, y = xy[:, 0].astype(np.float64), xy[:, 1].astype(np.float64)
    span = max(x.max() - x.min(), y.max() - y.min()) or 1.0
    x = (x - x.mean()) / span
    y = (y - y.mean()) / span

    return {
        "keys": keys_list,
        "words": [keys.word_of(key) for key in keys_list],
        "pos": [keys.split_key(key)[1] for key in keys_list],
        "gloss": [" ".join(provider.gloss_of_key(key).split()) for key in keys_list],
        "x": [round(float(v), 5) for v in x],
        "y": [round(float(v), 5) for v in y],
        "deg": degree,
        "rels": relations,
        "srcs": sources,
        "cells": cells,
        "vocab": vocabulary,
        "gwords": gloss_words,
        "dnear": top(sim_d),
        "bnear": top(sim_dual),
        "above": above,
        "flags": masks,
        "flagNames": [name for name, _why in FLAGS],
        "flagWhy": [why for _name, why in FLAGS],
        "bar": [[index.get(pair.a, -1), index.get(pair.b, -1), pair.verdict, pair.why]
                for pair in bar],
        "mix": mix,
        "floor": floor,
    }


def _add(relations: list[str], name: str) -> int:
    relations.append(name)
    return len(relations) - 1


# ------------------------------------------------------------------------------------------------
# the page — one file, everything inline, no network
# ------------------------------------------------------------------------------------------------

HTML = r"""<!doctype html>
<meta charset="utf-8">
<title>tk2 — the base, walked</title>
<style>
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;background:#0b0e13;color:#dfe6f2;
    font:13px/1.45 ui-sans-serif,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    overflow:hidden}
  canvas{display:block;cursor:grab}
  canvas.drag{cursor:grabbing}
  .card{position:fixed;background:rgba(14,18,26,.94);border:1px solid #222a3a;border-radius:10px;
    padding:10px 12px;backdrop-filter:blur(6px)}
  #top{top:14px;left:14px;max-width:352px;max-height:calc(100% - 28px);overflow:auto}
  h1{margin:0 0 2px;font-size:14px;font-weight:650;letter-spacing:.02em}
  .sub{color:#8894ab;font-size:11.5px;margin-bottom:9px}
  input[type=text]{width:100%;background:#0d1119;border:1px solid #2b3448;color:#dfe6f2;
    border-radius:7px;padding:6px 8px;font:12px inherit;outline:none}
  input[type=text]:focus{border-color:#4a7bd0}
  .row{display:flex;gap:12px;align-items:center;margin-top:8px;flex-wrap:wrap;font-size:11.5px;
    color:#9aa6bd}
  label{display:flex;gap:5px;align-items:center;cursor:pointer;user-select:none}
  .sw{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:5px;
    vertical-align:middle}
  .ln{display:inline-block;width:16px;height:2px;margin-right:5px;vertical-align:middle}
  #panel{top:14px;right:14px;width:340px;max-height:calc(100% - 28px);overflow:auto;display:none}
  #panel h2{margin:0;font-size:15px;font-weight:650}
  #panel .pos{color:#8894ab;font-weight:400;font-size:12px}
  .sec{margin-top:10px;border-top:1px solid #222a3a;padding-top:8px}
  .sec .hd{font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;color:#7e8aa1;
    margin-bottom:5px}
  .it{display:flex;justify-content:space-between;gap:8px;padding:1px 0;font-size:12px}
  .it .n{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .it .v{color:#8894ab;font-variant-numeric:tabular-nums;white-space:nowrap}
  .rel{color:#7e8aa1;font-size:11px}
  .via{color:#5d6779;font-size:10.5px;margin:0 0 3px 2px}
  .shared{color:#c2a15f;font-size:10.5px;margin:0 0 3px 2px}
  .junkshare{color:#c0554a}
  .gloss{color:#a9b4c8;font-size:11.5px;font-style:italic;margin-top:4px}
  .neg{color:#ff6b6b}
  .none{color:#7e8aa1;font-style:italic;font-size:11.5px}
  .flag{display:inline-block;background:#3a2233;border:1px solid #5d3450;color:#e7b6d3;
    border-radius:5px;padding:0 5px;margin:2px 3px 0 0;font-size:10.5px}
  .cnt{color:#8894ab;font-variant-numeric:tabular-nums}
  a{color:#6d8ec9;text-decoration:none;cursor:pointer}
  #hint{bottom:14px;right:14px;color:#6c7789;font-size:11px}
</style>

<canvas id="c"></canvas>

<div class="card" id="top">
  <h1>the base, walked <span style="color:#7e8aa1;font-weight:400" id="ttl"></span></h1>
  <div class="sub" id="counts"></div>
  <input type="text" id="q" placeholder="search a word — enter to centre on it" autocomplete="off">
  <div class="row">
    <label><input type="checkbox" id="showEdges"> all R lines</label>
    <label><input type="checkbox" id="onlyNeg"> opposition only</label>
    <label><input type="checkbox" id="showLabels" checked> labels</label>
    <label><input type="checkbox" id="showBar"> the bar</label>
  </div>
  <div class="row">
    <label><input type="checkbox" id="onlyFlagged"> only flagged dimensions</label>
    <a id="reset">reset view</a>
  </div>
  <div class="row" style="margin-top:6px">
    colour: <label><input type="radio" name="col" value="pos" checked> part of speech</label>
    <label><input type="radio" name="col" value="flag"> flags</label>
    <label><input type="radio" name="col" value="above"> neighbours over the floor</label>
  </div>
  <div class="sec" style="margin-top:9px">
    <div class="hd">the flags — what to walk first</div>
    <div id="flagcounts"></div>
  </div>
  <div class="sec">
    <div class="hd">legend</div>
    <div><b>position = D</b> (gloss overlap) · <b>lines = R</b> (stated; red = opposition)</div>
    <div class="row" style="margin-top:5px">
      <span><i class="sw" style="background:#6fb1ff"></i>noun</span>
      <span><i class="sw" style="background:#67d9a8"></i>verb</span>
      <span><i class="sw" style="background:#ffc46b"></i>adj</span>
      <span><i class="sw" style="background:#c79bff"></i>adv</span>
      <span><i class="sw" style="background:#e06fb4"></i>flagged</span>
    </div>
    <div class="row" style="margin-top:4px">dot size = R degree · the two channels are never blended
      on the map; the panel reads them together only where it says so</div>
  </div>
</div>

<div class="card" id="panel"></div>
<div id="hint" class="card">wheel = zoom · drag = pan · hover a dot · click to pin</div>

<script>
const DATA = /*__DATA__*/;
const META = /*__META__*/;

const POSCOL = {n:'#6fb1ff', v:'#67d9a8', a:'#ffc46b', r:'#c79bff'};
const FLAGCOL = '#e06fb4';
const N = DATA.keys.length;
const cv = document.getElementById('c'), ctx = cv.getContext('2d');
let W=0, H=0, DPR=Math.min(window.devicePixelRatio||1, 2);

// undirected draw list — a symmetric pair is one line, and the negative sign always wins the hue,
// because an opposition a stronger positive cell could hide is exactly what must not happen.
const seen = new Map(), E = [];
for (const [i,j,w,r] of DATA.cells){
  const k = i<j ? i+'_'+j : j+'_'+i;
  const at = seen.get(k);
  if (at === undefined){ seen.set(k, E.length); E.push([i,j,w,r]); }
  else if (w < 0 || (E[at][2] >= 0 && Math.abs(w) > Math.abs(E[at][2]))) E[at] = [i,j,w,r];
}
const negCount = E.filter(e => e[2] < 0).length;

const adj = Array.from({length:N}, () => []);
for (const [i,j,w,r,s,via] of DATA.cells) adj[i].push([j,w,r,s,via]);
for (const a of adj) a.sort((p,q) => Math.abs(q[1]) - Math.abs(p[1]));
const byWord = new Map();
DATA.words.forEach((w,i) => { if(!byWord.has(w)) byWord.set(w, []); byWord.get(w).push(i); });
const flagged = i => DATA.flags[i] !== 0;
const maxAbove = Math.max(1, ...DATA.above);

const maxDeg = Math.max(1, ...DATA.deg);
const rad = i => 1.4 + 3.4 * Math.sqrt(DATA.deg[i] / maxDeg);
const order = DATA.keys.map((_,i)=>i).sort((a,b) => DATA.deg[b] - DATA.deg[a]);

let view = {s:1, tx:0, ty:0}, hover = -1, pinned = -1, dragging = false;
const opt = id => document.getElementById(id).checked;
const colourMode = () => document.querySelector('input[name=col]:checked').value;
const visible = i => !opt('onlyFlagged') || flagged(i);

function colourOf(i){
  const mode = colourMode();
  if (mode === 'flag') return flagged(i) ? FLAGCOL : '#39424f';
  if (mode === 'above'){
    const t = DATA.above[i] / maxAbove;
    return 'rgb(' + Math.round(60 + 195*t) + ',' + Math.round(120 - 40*t) + ',' + Math.round(200 - 150*t) + ')';
  }
  return POSCOL[DATA.pos[i]] || '#9aa6bd';
}

function fit(){
  W = window.innerWidth; H = window.innerHeight;
  cv.style.width = W+'px'; cv.style.height = H+'px';
  cv.width = W*DPR; cv.height = H*DPR;
  ctx.setTransform(DPR,0,0,DPR,0,0);
}
// framing is robust rather than exact: a handful of dimensions with almost no gloss overlap get
// flung far out by the layout, and letting them set the scale would shrink the map to a dot.
const med = a => { const s = [...a].sort((p,q)=>p-q); return s[s.length>>1]; };
const CX = med(DATA.x), CY = med(DATA.y);
const RFRAME = (() => {
  const r = DATA.x.map((_,i) => Math.hypot(DATA.x[i]-CX, DATA.y[i]-CY)).sort((a,b)=>a-b);
  return r[Math.floor(r.length*0.90)] || 0.5;
})();
function home(){
  const s = Math.min(W,H)*0.46/RFRAME;
  view = {s, tx: W/2 - CX*s, ty: H/2 - CY*s};
}
const sx = i => DATA.x[i]*view.s + view.tx;
const sy = i => DATA.y[i]*view.s + view.ty;

function draw(){
  ctx.setTransform(DPR,0,0,DPR,0,0);
  ctx.fillStyle = '#0b0e13'; ctx.fillRect(0,0,W,H);
  const focus = pinned >= 0 ? pinned : hover;

  // THE LINE LAYER IS OFF BY DEFAULT AT THIS SCALE, and that is a decision made by looking: 31,250
  // drawn relations over 4,445 nodes is a blue fog with the 405 oppositions shouting through it, and
  // the D landscape underneath — which is what the positions MEAN — disappears. So the layer is
  // opt-in, and the edges of whatever is under the cursor are drawn whether it is on or not: the
  // question a walker actually asks is «what does THIS one state», never «show me all of them».
  const showAll = opt('showEdges'), negOnly = opt('onlyNeg');
  if (showAll || focus >= 0){
    for (const [i,j,w] of E){
      if (!visible(i) || !visible(j)) continue;
      const neg = w < 0;
      const lit = focus >= 0 && (i === focus || j === focus);
      if (!lit && !showAll) continue;
      if (negOnly && !neg && !lit) continue;
      if (showAll && focus >= 0 && !lit && !neg) continue;
      const a = neg ? (lit?0.95:0.6) : (lit?0.9:0.02 + 0.08*Math.abs(w));
      ctx.strokeStyle = neg ? 'rgba(255,85,85,'+a+')' : 'rgba(74,134,216,'+a+')';
      ctx.lineWidth = lit ? 1.6 : (neg ? 1.1 : 0.7);
      ctx.beginPath(); ctx.moveTo(sx(i), sy(i)); ctx.lineTo(sx(j), sy(j)); ctx.stroke();
    }
  }

  // the declared bar, drawn: a NEAR pair that sits on the far side of the map is the gate failing
  // in a way no table shows as vividly.
  if (opt('showBar')){
    for (const [i,j,verdict] of DATA.bar){
      if (i < 0 || j < 0) continue;
      ctx.save();
      ctx.setLineDash(verdict === 'NEAR' ? [] : [3,3]);
      ctx.strokeStyle = verdict === 'NEAR' ? 'rgba(120,230,180,.85)' : 'rgba(220,170,80,.75)';
      ctx.lineWidth = 1.8;
      ctx.beginPath(); ctx.moveTo(sx(i), sy(i)); ctx.lineTo(sx(j), sy(j)); ctx.stroke();
      ctx.restore();
    }
  }

  // D's own answer for the focused node, drawn as a dotted ring — a different mark from the R
  // lines on purpose: it is a different matrix speaking.
  if (focus >= 0){
    ctx.save(); ctx.setLineDash([2,3]); ctx.strokeStyle = 'rgba(140,160,190,.45)'; ctx.lineWidth = 1;
    for (const [j] of DATA.dnear[focus]){
      ctx.beginPath(); ctx.moveTo(sx(focus), sy(focus)); ctx.lineTo(sx(j), sy(j)); ctx.stroke();
    }
    ctx.restore();
  }

  for (let i=0;i<N;i++){
    if (!visible(i)) continue;
    const x = sx(i), y = sy(i);
    if (x < -20 || y < -20 || x > W+20 || y > H+20) continue;
    ctx.beginPath(); ctx.arc(x, y, rad(i) * (i===focus?1.9:1), 0, 6.2832);
    ctx.fillStyle = colourOf(i);
    ctx.globalAlpha = focus >= 0 && i !== focus ? 0.55 : 1;
    ctx.fill(); ctx.globalAlpha = 1;
    if (i === focus){ ctx.strokeStyle='#fff'; ctx.lineWidth=1.5; ctx.stroke(); }
  }

  if (opt('showLabels')){
    // greedy decluttering: walk the nodes richest-in-R first and drop any label whose cell is
    // already taken. Zooming in frees cells, so the ranking reveals itself gradually.
    ctx.font = '11px ui-sans-serif,-apple-system,Helvetica,Arial,sans-serif';
    ctx.textAlign = 'center'; ctx.textBaseline = 'bottom';
    const taken = new Set();
    let drawn = 0;
    for (const i of order){
      if (drawn > 260) break;
      if (!visible(i)) continue;
      const x = sx(i), y = sy(i);
      if (x < 8 || y < 14 || x > W-8 || y > H) continue;
      const cell = (x/58|0) + ':' + (y/15|0);
      if (taken.has(cell)) continue;
      taken.add(cell);
      ctx.fillStyle = flagged(i) ? 'rgba(224,111,180,.85)' : 'rgba(200,212,232,.75)';
      ctx.fillText(DATA.words[i], x, y - rad(i) - 2.5);
      drawn++;
    }
  }
  if (focus >= 0){
    ctx.font = '600 12px ui-sans-serif,-apple-system,Helvetica,Arial,sans-serif';
    ctx.textAlign = 'center'; ctx.textBaseline = 'bottom';
    ctx.fillStyle = '#ffffff';
    ctx.fillText(DATA.keys[focus], sx(focus), sy(focus) - rad(focus)*1.9 - 3);
  }
}

function pick(mx, my){
  let best = -1, bd = 14*14;
  for (let i=0;i<N;i++){
    if (!visible(i)) continue;
    const dx = sx(i)-mx, dy = sy(i)-my, d = dx*dx+dy*dy;
    if (d < bd){ bd = d; best = i; }
  }
  return best;
}

const JUNK = new Set(META.junk);
function sharedWords(i, j){
  const a = new Set(DATA.gwords[i]);
  return DATA.gwords[j].filter(w => a.has(w)).map(w => DATA.vocab[w]);
}
function sharedHtml(i, j){
  const words = sharedWords(i, j);
  if (!words.length) return '<div class="shared">shares no word — this is a SECOND-ORDER nearness</div>';
  const junkOnly = words.every(w => JUNK.has(w));
  return '<div class="shared' + (junkOnly ? ' junkshare' : '') + '">shares: ' + words.join(' ') +
         (junkOnly ? '  ← nothing but function words' : '') + '</div>';
}

const panel = document.getElementById('panel');
function showPanel(i){
  if (i < 0){ panel.style.display='none'; return; }
  const POSN = {n:'noun', v:'verb', a:'adjective', r:'adverb'};
  let h = '<h2>' + DATA.words[i] + ' <span class="pos">' + (POSN[DATA.pos[i]]||DATA.pos[i]) + '</span></h2>';
  h += '<div class="sub" style="margin:2px 0 0">R degree ' + DATA.deg[i] + ' · dimension #' + i +
       ' · ' + DATA.above[i] + ' of ' + (N-1) + ' dimensions over the candidate floor ' +
       DATA.floor.toFixed(3) + '</div>';
  h += '<div class="gloss">' + DATA.gloss[i] + '</div>';

  const flags = DATA.flagNames.filter((_,b) => DATA.flags[i] & (1<<b));
  if (flags.length){
    h += '<div style="margin-top:6px">' + flags.map(f => '<span class="flag" title="' +
         DATA.flagWhy[DATA.flagNames.indexOf(f)] + '">' + f + '</span>').join('') + '</div>';
  }

  h += '<div class="sec"><div class="hd">R — stated relations, with provenance</div>';
  if (!adj[i].length) h += '<div class="none">WordNet names no edge on this axis.</div>';
  for (const [j,w,r,s,via] of adj[i].slice(0, 12)){
    h += '<div class="it"><span class="n' + (w<0?' neg':'') + '">' + DATA.keys[j] +
         ' <span class="rel">' + DATA.rels[r] + ' · ' + DATA.srcs[s] + '</span></span>' +
         '<span class="v' + (w<0?' neg':'') + '">' + (w<0?'':'+') + w.toFixed(3) + '</span></div>';
    if (via && via.length > 1)
      h += '<div class="via">via ' + via.map(v => DATA.rels[v[0]] + ' ' + v[1]).join(' · ') + '</div>';
  }
  if (adj[i].length > 12) h += '<div class="none">+ ' + (adj[i].length-12) + ' more</div>';
  h += '</div>';

  h += '<div class="sec"><div class="hd">D — nearest by gloss overlap, and WHY</div>';
  for (const [j,s] of DATA.dnear[i]){
    h += '<div class="it"><span class="n">' + DATA.keys[j] + '</span><span class="v">' +
         s.toFixed(3) + '</span></div>' + sharedHtml(i, j);
  }
  h += '</div>';

  h += '<div class="sec"><div class="hd">the dual read — R and D at mix ' + DATA.mix + '</div>';
  for (const [j,s] of DATA.bnear[i]){
    h += '<div class="it"><span class="n">' + DATA.keys[j] + '</span><span class="v">' +
         (s<0?'':'+') + s.toFixed(3) + '</span></div>';
  }
  h += '<div class="none" style="margin-top:5px">this is the list the base is actually read as ' +
       'since the ruling of 2026-09-09. It is a CONCATENATION, never an average.</div></div>';
  panel.innerHTML = h; panel.style.display = 'block';
}

document.getElementById('flagcounts').innerHTML = DATA.flagNames.map((name, b) => {
  const n = DATA.flags.filter(m => m & (1<<b)).length;
  return '<div class="it" title="' + DATA.flagWhy[b] + '"><span class="n">' + name +
         '</span><span class="cnt">' + n + '</span></div>';
}).join('');

cv.addEventListener('mousemove', e => {
  if (dragging){ view.tx += e.movementX; view.ty += e.movementY; draw(); return; }
  const h = pick(e.clientX, e.clientY);
  if (h !== hover){ hover = h; if (pinned < 0) showPanel(h); draw(); }
});
cv.addEventListener('mousedown', () => { dragging = true; cv.classList.add('drag'); });
window.addEventListener('mouseup', () => { dragging = false; cv.classList.remove('drag'); });
cv.addEventListener('click', e => {
  const h = pick(e.clientX, e.clientY);
  pinned = (h >= 0 && h === pinned) ? -1 : h;
  showPanel(pinned >= 0 ? pinned : hover); draw();
});
cv.addEventListener('wheel', e => {
  e.preventDefault();
  const k = Math.exp(-e.deltaY * 0.0016);
  view.tx = e.clientX - (e.clientX - view.tx)*k;
  view.ty = e.clientY - (e.clientY - view.ty)*k;
  view.s *= k; draw();
}, {passive:false});

function centreOn(i){
  view.s = Math.max(view.s, Math.min(W,H)*2.2);
  view.tx = W/2 - DATA.x[i]*view.s;
  view.ty = H/2 - DATA.y[i]*view.s;
  pinned = i; showPanel(i); draw();
}
const q = document.getElementById('q');
q.addEventListener('keydown', e => {
  if (e.key !== 'Enter') return;
  const t = q.value.trim().toLowerCase();
  if (!t) return;
  let i = DATA.keys.indexOf(t);
  if (i < 0 && byWord.has(t)) i = byWord.get(t)[0];
  if (i < 0) i = DATA.words.findIndex(w => w.startsWith(t));
  if (i < 0){ q.style.borderColor = '#c04a4a'; setTimeout(() => q.style.borderColor = '', 600); return; }
  centreOn(i);
});
for (const id of ['showEdges','onlyNeg','showLabels','showBar','onlyFlagged'])
  document.getElementById(id).addEventListener('change', draw);
for (const radio of document.querySelectorAll('input[name=col]'))
  radio.addEventListener('change', draw);
document.getElementById('reset').addEventListener('click', e => {
  e.preventDefault(); pinned = -1; showPanel(-1); home(); draw();
});
window.addEventListener('resize', () => { fit(); draw(); });

document.getElementById('ttl').textContent = META.layout + ' · ' + META.source;
document.getElementById('counts').textContent =
  N + ' dimensions · ' + E.length + ' R relations drawn, ' + negCount + ' opposition · ' +
  DATA.flags.filter(m => m).length + ' flagged · D neighbourhood kept ' +
  Math.round(META.fidelity*100) + '%';
fit(); home(); draw();
</script>
"""


def render(payload: dict, meta: dict) -> str:
    return (HTML
            .replace("/*__DATA__*/", json.dumps(payload, separators=(",", ":")))
            .replace("/*__META__*/", json.dumps(meta, separators=(",", ":"))))


# ------------------------------------------------------------------------------------------------
# main
# ------------------------------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parser = argparse.ArgumentParser(description="draw the base: position = D, lines = R, flags on top")
    parser.add_argument("--db", default=None, help="read the policy (and, with --build, the stored "
                                                   "base) from this database")
    parser.add_argument("--build", default=None, help="the stored build label to read back")
    parser.add_argument("--out", default=os.path.join(here, "out", "base_map.html"))
    parser.add_argument("--layout", choices=("tsne", "pca"), default="tsne",
                        help="tsne = PCA seed refined on D's cosine distances (default); pca = raw SVD")
    parser.add_argument("--perplexity", type=float, default=30.0)
    parser.add_argument("--iters", type=int, default=800)
    parser.add_argument("--lr", type=float, default=200.0)
    parser.add_argument("--edge-min", type=float, default=0.0,
                        help="drop R cells whose |w| is below this")
    parser.add_argument("--neighbours", type=int, default=NEIGHBOURS,
                        help="how many D and dual-read neighbours to carry per dimension")
    parser.add_argument("--floor", type=float, default=0.1431,
                        help="the CANDIDATE acceptance floor the per-dimension count is taken "
                             "against. Not a declaration — no floor is ruled (T5 measures them, the "
                             "Captain rules them); it is here so the junk plateau is visible as a "
                             "number on every node")
    parser.add_argument("--mix", type=float, default=None,
                        help="the dual read's mix (default: whatever the policy rows declare)")
    args = parser.parse_args(argv)

    started = time.time()
    built, vectors, config, provider, source, bar, bar_source = load(args.db, args.build)
    mix = args.mix if args.mix is not None else (config.reading.mix if config.reading else 0.0)
    print(f"base          {len(built.dimensions):,} dimensions · {source}")
    print(f"bar           {bar_source}, {len(bar)} pairs · dual read at mix {mix}")

    D = dense_rows(built.distributional)
    norm = np.linalg.norm(D, axis=1, keepdims=True)
    norm[norm == 0] = 1.0
    Dn = D / norm
    sim_d = Dn @ Dn.T
    np.fill_diagonal(sim_d, -np.inf)

    R = dense_rows(built.relational)
    blended = np.concatenate([R, mix * D], axis=1)
    norm = np.linalg.norm(blended, axis=1, keepdims=True)
    norm[norm == 0] = 1.0
    blended /= norm
    sim_dual = blended @ blended.T
    np.fill_diagonal(sim_dual, -np.inf)
    print(f"geometry      R and D densified, the dual read taken ({time.time() - started:.0f}s)")

    xy, kept = pca_2d(D)
    print(f"PCA           2 components keep {kept * 100:.1f}% of D's variance")
    if args.layout == "tsne":
        distances = np.maximum(1.0 - np.where(np.isfinite(sim_d), sim_d, 1.0), 0.0)
        np.fill_diagonal(distances, 0.0)
        xy = tsne_2d(distances, xy, args.perplexity, args.iters, args.lr)
    fidelity = neighbour_fidelity(sim_d, xy)
    print(f"layout        {args.layout}: {fidelity * 100:.1f}% of each node's 10 nearest D "
          f"neighbours are still near it in 2D ({time.time() - started:.0f}s)")

    closed, closed_source = closed_forms(args.db)
    masks, counts = flags_of(built, vectors, provider, frozenset(closed))
    print(f"flags         {closed_source}")
    for name, why in FLAGS:
        print(f"  {name:<12} {counts[name]:>5}   {why}")
    print(f"  {'any':<12} {sum(1 for m in masks if m):>5}   dimensions carrying at least one flag")

    payload = pack(built, vectors, provider, xy, sim_d, sim_dual, masks, bar, mix, args.floor,
                   args.edge_min, args.neighbours)
    meta = {"layout": args.layout, "fidelity": fidelity, "pca_variance": kept,
            "source": source, "junk": sorted(JUNK_WORDS)}
    html = render(payload, meta)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as handle:
        handle.write(html)
    print(f"wrote {args.out}  ({os.path.getsize(args.out) / 1024 / 1024:.1f} MB, self-contained) "
          f"in {time.time() - started:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
