# micro-nn — REQUIREMENTS

*What the instinct framework must be. One line each. Evidence in the dated `_notes.md` beside this.*

1. **One abstraction, many instances** — a single middleware serves every use case; instances differ by declaration (input schema · output kind · reward source), never by stack.
2. **One shape** — features in → a ranking or a scalar in [0,1] out; nothing else.
3. **Tiny and laptop-honest** — small nets, numpy-scale; no heavyweight framework.
4. **Weights are db rows, epoch-stamped** — an instance is config + weights in the db; training moves rows, never code.
5. **Learned online from the reward families** — intellectual + heart (brain req. 18); positive feedback loops.
6. **The six sites**: evaluator search order · brain thresholds · the heart jump (attention bias) · the figurative layer · the channel register · the mouth's coloring.
7. **The shared fence** — ranks among already-legal options ONLY: never a verdict, never content, no provenance ⇒ never a belief; a kb rule outranks it, always.
8. **Deterministic per weights-version** — same features, same epoch, same output; variability enters by learning, not by noise.
