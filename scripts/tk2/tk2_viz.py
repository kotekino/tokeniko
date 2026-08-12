#!/usr/bin/env python
"""tk2 — A PICTURE OF THE TWO-MATRIX BASE.

A side instrument: it measures nothing, it *shows*. The reason it can exist at all is the rule that
made stage 2b: R and D are two matrices, never blended into one float. So the map keeps them as two
VISUAL channels and never mixes them either —

    position   comes from D (gloss overlap): where a word sits says what it is ABOUT.
    lines      come from R (named WordNet edges): a line means someone STATED a relation,
               and the sign is drawn, not averaged away — opposition gets its own hue.

Reading the picture is therefore the same discipline the CLI prints: a neighbour on screen is a D
answer, a line is an R answer, and the side panel lists the two separately with the matrix named.
Nothing on the map is a blend of the two, because there is no such thing to draw.

The layout is numpy-only. PCA (SVD) on the D rows is computed first, and it is honest but flat: two
components keep ~32% of D's variance, and only 3% of each word's ten nearest D neighbours are still
its nearest ten on screen — a smear, not a map. So the PCA coordinates are used as the SEED of a
small exact t-SNE on the D cosine distances, which lifts that neighbourhood fidelity to ~20%.
Seeding from PCA rather than from noise keeps the run deterministic and keeps the global orientation
PCA found. `--layout pca` keeps the raw projection, for comparison.

    python scripts/tk2/tk2_viz.py                      # -> scripts/tk2/out/base_map.html
    python scripts/tk2/tk2_viz.py --layout pca         # the flat, unrefined projection
    python scripts/tk2/tk2_viz.py --edge-min 0.9       # only the strongest stated relations

Read-only on every database. The HTML is fully self-contained: no CDN, no font, no library — it
must open from a file:// URL on a laptop with the wifi off.
"""

import argparse
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import tk2_config as CFG
import tk2_common as C


# ------------------------------------------------------------------------------------------------
# loading — both matrices, in the ONE dimension order the manifest fixed
# ------------------------------------------------------------------------------------------------


def load_base(base: str):
    """(the R docs, the D matrix). The index field is the shared dimension order, so sorting on it
    makes row i of D and node i of the drawing the same word by construction."""
    db = C.tk2_db()
    R = list(db.base_relational.find({"base": base}).sort("index", 1))
    D = list(db.base_distributional.find({"base": base}).sort("index", 1))
    if not R or not D:
        raise SystemExit(f"base '{base}' has no two-matrix build — run tk2_build2.py --apply first.")
    if [d["key"] for d in R] != [d["key"] for d in D]:
        raise SystemExit("R and D disagree on the key order — the two matrices are not comparable.")
    M = np.asarray([d["vector"] for d in D], dtype=np.float64)
    return R, M


# ------------------------------------------------------------------------------------------------
# layout — positions are a function of D alone. R never moves a node.
# ------------------------------------------------------------------------------------------------


def pca_2d(X: np.ndarray) -> tuple[np.ndarray, float]:
    """Plain SVD on the centred rows. Returns the coordinates and the variance the 2D picture keeps
    — reported out loud, because a projection that keeps a third of the variance has thrown away
    most of what it was given and should say so."""
    Xc = X - X.mean(axis=0)
    U, S, _ = np.linalg.svd(Xc, full_matrices=False)
    kept = float((S[:2] ** 2).sum() / (S ** 2).sum())
    return U[:, :2] * S[:2], kept


def _joint_p(dist: np.ndarray, perplexity: float) -> np.ndarray:
    """The t-SNE affinity matrix: per row, the bandwidth that makes the neighbourhood have exactly
    `perplexity` effective neighbours, found by bisection on beta. Symmetrised and normalised."""
    n = dist.shape[0]
    P = np.zeros((n, n))
    target = np.log(perplexity)
    for i in range(n):
        d = np.delete(dist[i], i)
        lo, hi, beta = 1e-12, 1e12, 1.0
        p = np.exp(-d)
        for _ in range(60):
            p = np.exp(-d * beta)
            s = p.sum()
            if s <= 0:
                break
            entropy = np.log(s) + beta * (d * p).sum() / s
            if abs(entropy - target) < 1e-5:
                break
            if entropy > target:                      # too many neighbours — tighten
                lo = beta
                beta = beta * 2 if hi == 1e12 else (beta + hi) / 2
            else:                                     # too few — widen
                hi = beta
                beta = beta / 2 if lo == 1e-12 else (beta + lo) / 2
        row = np.zeros(n)
        row[np.arange(n) != i] = p / max(p.sum(), 1e-300)
        P[i] = row
    P = (P + P.T) / (2 * n)
    return np.maximum(P, 1e-12)


def tsne_2d(X: np.ndarray, seed_xy: np.ndarray, perplexity: float, iters: int,
            lr: float) -> np.ndarray:
    """t-SNE on cosine distance, vectorised over the full 983x983 — no approximation is needed at
    this size, and an exact gradient keeps the result reproducible from the PCA seed."""
    n = X.shape[0]
    norm = np.linalg.norm(X, axis=1, keepdims=True)
    norm[norm == 0] = 1.0
    Xn = X / norm
    dist = 1.0 - Xn @ Xn.T
    np.fill_diagonal(dist, 0.0)
    P = _joint_p(dist, perplexity)

    Y = seed_xy / (seed_xy[:, 0].std() or 1.0) * 1e-2     # small, so early exaggeration can work
    dY = np.zeros_like(Y)
    gains = np.ones_like(Y)
    for it in range(iters):
        exaggerate = 12.0 if it < iters // 4 else 1.0     # pull the clusters apart first, then relax
        momentum = 0.5 if it < iters // 4 else 0.8
        sq = (Y ** 2).sum(1)
        num = 1.0 / (1.0 + (sq[:, None] + sq[None, :] - 2 * Y @ Y.T))
        np.fill_diagonal(num, 0.0)
        Q = np.maximum(num / num.sum(), 1e-12)
        PQ = (P * exaggerate - Q) * num
        grad = 4 * ((np.diag(PQ.sum(1)) - PQ) @ Y)
        gains = np.where(np.sign(grad) != np.sign(dY), gains + 0.2, gains * 0.8)
        gains = np.maximum(gains, 0.01)
        dY = momentum * dY - lr * gains * grad
        Y = Y + dY
        Y -= Y.mean(0)
    return Y


def neighbour_fidelity(X: np.ndarray, Y: np.ndarray, k: int = 10) -> float:
    """How much of D's own neighbourhood survived the trip to 2D — the only number that says
    whether the picture may be trusted as a picture of D. Reported, never optimised silently."""
    norm = np.linalg.norm(X, axis=1, keepdims=True)
    norm[norm == 0] = 1.0
    sim = (X / norm) @ (X / norm).T
    np.fill_diagonal(sim, -np.inf)
    high = np.argpartition(-sim, k, axis=1)[:, :k]
    d2 = ((Y[:, None, :] - Y[None, :, :]) ** 2).sum(-1)
    np.fill_diagonal(d2, np.inf)
    near = np.argpartition(d2, k, axis=1)[:, :k]
    return float(np.mean([len(set(a) & set(b)) / k for a, b in zip(high, near)]))


# ------------------------------------------------------------------------------------------------
# the two channels, packed for the browser
# ------------------------------------------------------------------------------------------------


def pack(R, M, xy, edge_min: float, dk: int) -> dict:
    """Parallel arrays rather than objects: 983 nodes and ~10k cells are small, but the file is
    meant to be opened by double-clicking it, and a compact payload keeps it that way.

    R cells are kept DIRECTED (the relation name is read from the row's point of view: `hypernym_1`
    on eat.v's row means the other word is eat.v's hypernym). The drawing dedupes the symmetric
    pairs itself; the panel needs the direction, so the direction is what gets stored."""
    keys = [d["key"] for d in R]
    idx = {k: i for i, k in enumerate(keys)}

    rels: list[str] = []
    rel_id: dict[str, int] = {}
    cells = []
    degree = [0] * len(keys)
    for i, doc in enumerate(R):
        for other, e in doc["edges"].items():
            j = idx.get(other)
            if j is None or j == i:
                continue
            w = float(e["w"])
            if abs(w) < edge_min:
                continue
            rel = e.get("rel") or "?"
            if rel not in rel_id:
                rel_id[rel] = len(rels)
                rels.append(rel)
            cells.append([i, j, round(w, 3), rel_id[rel]])
            degree[i] += 1
            degree[j] += 1

    # D's own answer, kept separate: the top-k gloss-overlap neighbours of every dimension.
    norm = np.linalg.norm(M, axis=1, keepdims=True)
    norm[norm == 0] = 1.0
    sim = (M / norm) @ (M / norm).T
    np.fill_diagonal(sim, -np.inf)
    top = np.argsort(-sim, axis=1)[:, :dk]
    dnear = [[[int(j), round(float(sim[i, j]), 3)] for j in row] for i, row in enumerate(top)]

    x, y = xy[:, 0], xy[:, 1]
    span = max(x.max() - x.min(), y.max() - y.min()) or 1.0
    x = (x - x.mean()) / span
    y = (y - y.mean()) / span

    return {
        "base": R[0]["base"],
        "keys": keys,
        "words": [d["word"] for d in R],
        "pos": [d["pos"] for d in R],
        "x": [round(float(v), 5) for v in x],
        "y": [round(float(v), 5) for v in y],
        "deg": degree,
        "rels": rels,
        "cells": cells,
        "dnear": dnear,
    }


# ------------------------------------------------------------------------------------------------
# the page — one file, everything inline, no network
# ------------------------------------------------------------------------------------------------

HTML = r"""<!doctype html>
<meta charset="utf-8">
<title>tk2 — base map</title>
<style>
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;background:#0b0e13;color:#dfe6f2;
    font:13px/1.45 ui-sans-serif,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    overflow:hidden}
  canvas{display:block;cursor:grab}
  canvas.drag{cursor:grabbing}
  .card{position:fixed;background:rgba(14,18,26,.93);border:1px solid #222a3a;border-radius:10px;
    padding:10px 12px;backdrop-filter:blur(6px)}
  #top{top:14px;left:14px;max-width:330px}
  h1{margin:0 0 2px;font-size:14px;font-weight:650;letter-spacing:.02em}
  .sub{color:#8894ab;font-size:11.5px;margin-bottom:9px}
  input[type=text]{width:100%;background:#0d1119;border:1px solid #2b3448;color:#dfe6f2;
    border-radius:7px;padding:6px 8px;font:12px inherit;outline:none}
  input[type=text]:focus{border-color:#4a7bd0}
  .row{display:flex;gap:12px;align-items:center;margin-top:8px;flex-wrap:wrap;font-size:11.5px;
    color:#9aa6bd}
  label{display:flex;gap:5px;align-items:center;cursor:pointer;user-select:none}
  #legend{bottom:14px;left:14px;font-size:11.5px;color:#9aa6bd;max-width:330px}
  #legend b{color:#dfe6f2;font-weight:600}
  .sw{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:5px;
    vertical-align:middle}
  .ln{display:inline-block;width:16px;height:2px;margin-right:5px;vertical-align:middle}
  #panel{top:14px;right:14px;width:300px;max-height:calc(100% - 28px);overflow:auto;display:none}
  #panel h2{margin:0;font-size:15px;font-weight:650}
  #panel .pos{color:#8894ab;font-weight:400;font-size:12px}
  .sec{margin-top:10px;border-top:1px solid #222a3a;padding-top:8px}
  .sec .hd{font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;color:#7e8aa1;
    margin-bottom:5px}
  .it{display:flex;justify-content:space-between;gap:8px;padding:1px 0;font-size:12px}
  .it .n{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .it .v{color:#8894ab;font-variant-numeric:tabular-nums;white-space:nowrap}
  .rel{color:#7e8aa1;font-size:11px}
  .neg{color:#ff6b6b}
  .none{color:#7e8aa1;font-style:italic;font-size:11.5px}
  #hint{bottom:14px;right:14px;color:#6c7789;font-size:11px}
</style>

<canvas id="c"></canvas>

<div class="card" id="top">
  <h1>tk2 base map <span style="color:#7e8aa1;font-weight:400" id="ttl"></span></h1>
  <div class="sub" id="counts"></div>
  <input type="text" id="q" placeholder="search a word — enter to centre on it" autocomplete="off">
  <div class="row">
    <label><input type="checkbox" id="showEdges" checked> lines</label>
    <label><input type="checkbox" id="onlyNeg"> opposition only</label>
    <label><input type="checkbox" id="showLabels" checked> labels</label>
    <a href="#" id="reset" style="color:#6d8ec9;text-decoration:none">reset view</a>
  </div>
</div>

<div class="card" id="legend">
  <b>position = D</b> (topical world-overlap) · <b>lines = R</b> (stated relations; red = opposition)
  <div class="row" style="margin-top:7px">
    <span><i class="sw" style="background:#6fb1ff"></i>noun</span>
    <span><i class="sw" style="background:#67d9a8"></i>verb</span>
    <span><i class="sw" style="background:#ffc46b"></i>adj</span>
    <span><i class="sw" style="background:#c79bff"></i>adv</span>
  </div>
  <div class="row" style="margin-top:4px">
    <span><i class="ln" style="background:#4a86d8"></i>positive cell</span>
    <span><i class="ln" style="background:#ff5555"></i>antonym (w &lt; 0)</span>
  </div>
  <div class="row" style="margin-top:4px">dot size = R degree · the two channels are never blended</div>
</div>

<div class="card" id="panel"></div>
<div id="hint" class="card">wheel = zoom · drag = pan · hover a dot</div>

<script>
const DATA = /*__DATA__*/;
const META = /*__META__*/;

// ---------------------------------------------------------------------------------------------
// the drawing. Nodes are placed by D and never moved by R; a line is only ever an R cell.
// ---------------------------------------------------------------------------------------------
const POSCOL = {n:'#6fb1ff', v:'#67d9a8', a:'#ffc46b', r:'#c79bff'};
const N = DATA.keys.length;
const cv = document.getElementById('c'), ctx = cv.getContext('2d');
let W=0, H=0, DPR=Math.min(window.devicePixelRatio||1, 2);

// undirected draw list — a symmetric pair is one line, and the negative sign always wins the hue,
// because an opposition that a stronger positive cell could hide is exactly what must not happen.
const seen = new Map(), E = [];
for (const [i,j,w,r] of DATA.cells){
  const k = i<j ? i+'_'+j : j+'_'+i;
  const at = seen.get(k);
  if (at === undefined){ seen.set(k, E.length); E.push([i,j,w,r]); }
  else if (w < 0 || (E[at][2] >= 0 && Math.abs(w) > Math.abs(E[at][2]))) E[at] = [i,j,w,r];
}
const negCount = E.filter(e => e[2] < 0).length;

// R adjacency (directed, for the panel) and the search index
const adj = Array.from({length:N}, () => []);
for (const [i,j,w,r] of DATA.cells) adj[i].push([j,w,r]);
for (const a of adj) a.sort((p,q) => Math.abs(q[1]) - Math.abs(p[1]));
const byWord = new Map();
DATA.words.forEach((w,i) => { if(!byWord.has(w)) byWord.set(w, []); byWord.get(w).push(i); });

const maxDeg = Math.max(1, ...DATA.deg);
const rad = i => 1.5 + 3.6 * Math.sqrt(DATA.deg[i] / maxDeg);
const order = DATA.keys.map((_,i)=>i).sort((a,b) => DATA.deg[b] - DATA.deg[a]);

let view = {s:1, tx:0, ty:0}, hover = -1, pinned = -1, dragging = false;
const opt = id => document.getElementById(id).checked;

function fit(){
  W = window.innerWidth; H = window.innerHeight;
  cv.style.width = W+'px'; cv.style.height = H+'px';   // the CSS box, not just the backing store
  cv.width = W*DPR; cv.height = H*DPR;
  ctx.setTransform(DPR,0,0,DPR,0,0);
}
// framing is robust rather than exact: a handful of dimensions with almost no gloss overlap get
// flung far out by the layout, and letting them set the scale would shrink the map to a dot.
const med = a => { const s = [...a].sort((p,q)=>p-q); return s[s.length>>1]; };
const CX = med(DATA.x), CY = med(DATA.y);
const RFRAME = (() => {
  const r = DATA.x.map((_,i) => Math.hypot(DATA.x[i]-CX, DATA.y[i]-CY)).sort((a,b)=>a-b);
  return r[Math.floor(r.length*0.90)] || 0.5;    // frame the body, not the strays
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

  if (opt('showEdges')){
    const negOnly = opt('onlyNeg');
    ctx.lineWidth = 1;
    for (const [i,j,w,r] of E){
      const neg = w < 0;
      if (negOnly && !neg) continue;
      const lit = focus >= 0 && (i === focus || j === focus);
      if (focus >= 0 && !lit && !neg) continue;          // hovering isolates that node's own R edges
      const a = neg ? (lit?0.95:0.6) : (lit?0.9:0.03 + 0.10*Math.abs(w));
      ctx.strokeStyle = neg ? 'rgba(255,85,85,'+a+')' : 'rgba(74,134,216,'+a+')';
      ctx.lineWidth = lit ? 1.6 : (neg ? 1.1 : 0.7);
      ctx.beginPath(); ctx.moveTo(sx(i), sy(i)); ctx.lineTo(sx(j), sy(j)); ctx.stroke();
    }
  }
  // D's answer for the focused node, drawn as a dotted ring of its top gloss-overlap neighbours —
  // a different mark from the R lines on purpose: it is a different matrix speaking.
  if (focus >= 0){
    ctx.save(); ctx.setLineDash([2,3]); ctx.strokeStyle = 'rgba(140,160,190,.45)'; ctx.lineWidth = 1;
    for (const [j] of DATA.dnear[focus]){
      ctx.beginPath(); ctx.moveTo(sx(focus), sy(focus)); ctx.lineTo(sx(j), sy(j)); ctx.stroke();
    }
    ctx.restore();
  }

  for (let i=0;i<N;i++){
    const x = sx(i), y = sy(i);
    if (x < -20 || y < -20 || x > W+20 || y > H+20) continue;
    ctx.beginPath(); ctx.arc(x, y, rad(i) * (i===focus?1.9:1), 0, 6.2832);
    ctx.fillStyle = POSCOL[DATA.pos[i]] || '#9aa6bd';
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
      if (drawn > 240) break;
      const x = sx(i), y = sy(i);
      if (x < 8 || y < 14 || x > W-8 || y > H) continue;
      const cell = (x/58|0) + ':' + (y/15|0);
      if (taken.has(cell)) continue;
      taken.add(cell);
      ctx.fillStyle = 'rgba(200,212,232,.75)';
      ctx.fillText(DATA.words[i], x, y - rad(i) - 2.5);
      drawn++;
    }
  }
  if (focus >= 0){                      // the focused label is never decluttered away
    ctx.font = '600 12px ui-sans-serif,-apple-system,Helvetica,Arial,sans-serif';
    ctx.textAlign = 'center'; ctx.textBaseline = 'bottom';
    ctx.fillStyle = '#ffffff';
    ctx.fillText(DATA.keys[focus], sx(focus), sy(focus) - rad(focus)*1.9 - 3);
  }
}

function pick(mx, my){
  let best = -1, bd = 14*14;
  for (let i=0;i<N;i++){
    const dx = sx(i)-mx, dy = sy(i)-my, d = dx*dx+dy*dy;
    if (d < bd){ bd = d; best = i; }
  }
  return best;
}

const panel = document.getElementById('panel');
function showPanel(i){
  if (i < 0){ panel.style.display='none'; return; }
  const POSN = {n:'noun', v:'verb', a:'adjective', r:'adverb'};
  let h = '<h2>' + DATA.words[i] + ' <span class="pos">' + (POSN[DATA.pos[i]]||DATA.pos[i]) + '</span></h2>';
  h += '<div class="sub" style="margin:2px 0 0">R degree ' + DATA.deg[i] + ' · dimension #' + i + '</div>';

  h += '<div class="sec"><div class="hd">R — stated relations (signed)</div>';
  if (!adj[i].length) h += '<div class="none">WordNet names no edge on this axis.</div>';
  for (const [j,w,r] of adj[i].slice(0, 14)){
    h += '<div class="it"><span class="n' + (w<0?' neg':'') + '">' + DATA.keys[j] +
         ' <span class="rel">' + DATA.rels[r] + '</span></span>' +
         '<span class="v' + (w<0?' neg':'') + '">' + (w<0?'':'+') + w.toFixed(3) + '</span></div>';
  }
  if (adj[i].length > 14) h += '<div class="none">+ ' + (adj[i].length-14) + ' more</div>';
  h += '</div>';

  h += '<div class="sec"><div class="hd">D — nearest by gloss overlap</div>';
  for (const [j,s] of DATA.dnear[i]){
    h += '<div class="it"><span class="n">' + DATA.keys[j] + '</span><span class="v">' +
         s.toFixed(3) + '</span></div>';
  }
  h += '<div class="none" style="margin-top:6px">D is topicality, not a relation — a word here ' +
       'need not have any stated edge to ' + DATA.words[i] + '.</div></div>';
  panel.innerHTML = h; panel.style.display = 'block';
}

// ---------------------------------------------------------------------------------------------
// interaction — wheel zooms at the cursor, drag pans, enter centres the searched word
// ---------------------------------------------------------------------------------------------
cv.addEventListener('mousemove', e => {
  if (dragging){ view.tx += e.movementX; view.ty += e.movementY; draw(); return; }
  const h = pick(e.clientX, e.clientY);
  if (h !== hover){ hover = h; if (pinned < 0) showPanel(h); draw(); }
});
cv.addEventListener('mousedown', () => { dragging = true; cv.classList.add('drag'); });
window.addEventListener('mouseup', () => { dragging = false; cv.classList.remove('drag'); });
cv.addEventListener('click', e => {
  const h = pick(e.clientX, e.clientY);
  pinned = (h >= 0 && h === pinned) ? -1 : h;      // click pins a node so the panel stays put
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
for (const id of ['showEdges','onlyNeg','showLabels'])
  document.getElementById(id).addEventListener('change', draw);
document.getElementById('reset').addEventListener('click', e => {
  e.preventDefault(); pinned = -1; showPanel(-1); home(); draw();
});
window.addEventListener('resize', () => { fit(); draw(); });

document.getElementById('ttl').textContent = 'base ' + DATA.base + ' · ' + META.layout;
document.getElementById('counts').textContent =
  N + ' dimensions · ' + E.length + ' R relations drawn, ' + negCount + ' of them opposition · ' +
  'D neighbourhood kept ' + Math.round(META.fidelity*100) + '%';
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


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description="draw the two-matrix base: position = D, lines = R")
    ap.add_argument("--base", default=CFG.BASE2_NAME)
    ap.add_argument("--out", default=os.path.join(here, "out", "base_map.html"))
    ap.add_argument("--layout", choices=("tsne", "pca"), default="tsne",
                    help="tsne = PCA seed refined on D's cosine distances (default); pca = raw SVD")
    ap.add_argument("--perplexity", type=float, default=30.0)
    ap.add_argument("--iters", type=int, default=1000)
    ap.add_argument("--lr", type=float, default=200.0)
    ap.add_argument("--edge-min", type=float, default=0.0,
                    help="drop R cells whose |w| is below this (the base's smallest is 0.5)")
    ap.add_argument("--dk", type=int, default=8, help="how many D neighbours to carry per node")
    args = ap.parse_args()

    t0 = time.time()
    R, M = load_base(args.base)
    print(f"base {args.base}: {len(R)} dimensions loaded from {CFG.TK2_DB} ({time.time()-t0:.1f}s)")

    t1 = time.time()
    xy, kept = pca_2d(M)
    print(f"PCA: 2 components keep {kept*100:.1f}% of D's variance")
    if args.layout == "tsne":
        xy = tsne_2d(M, xy, args.perplexity, args.iters, args.lr)
    fidelity = neighbour_fidelity(M, xy)
    print(f"layout {args.layout}: {time.time()-t1:.1f}s · "
          f"{fidelity*100:.1f}% of each node's 10 nearest D neighbours are still near it in 2D")

    payload = pack(R, M, xy, args.edge_min, args.dk)
    meta = {"layout": args.layout, "fidelity": fidelity, "pca_variance": kept,
            "edge_min": args.edge_min}
    html = render(payload, meta)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(html)

    neg = sum(1 for c in payload["cells"] if c[2] < 0)
    print(f"cells: {len(payload['cells'])} directed R cells, {neg} negative, "
          f"{len(payload['rels'])} relation names")
    print(f"wrote {args.out}  ({os.path.getsize(args.out)/1024:.0f} KB, "
          f"self-contained) in {time.time()-t0:.1f}s total")


if __name__ == "__main__":
    main()
