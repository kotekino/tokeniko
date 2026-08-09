import React from 'react';

interface Props {
  /** Pixel size of the square emblem. */
  size?: number;
  className?: string;
}

/* ══════════════════════════════════════════════════════════════════════════
   THE EMBLEM (BI 1.1) — a `tk` monogram plotted as a dot matrix on the
   outline of the Mac mini tokeniko runs on. Twenty-five dots on an 11 × 7
   lattice; the dot diameter equals the lattice pitch, so neighbours meet
   exactly and the strokes read as beads rather than as a line.

   This is the REDUCED emblem: field and dots only, no radar field. The radar
   is drawn at hairline weight in the master artwork and turns to mud below
   ~256 px — and this mark is used at 38 px (header) and 26 px (footer). The
   full artwork lives in bi/1.1/assets/tokeniko-emblem.svg.

   THE COLOURS ARE NOT SET HERE. They come from --lm-* in global.css, which
   the tone blocks re-point when the mind sleeps — so the header mark and the
   footer mark can never disagree about whether he is awake (BI 1.1 §02).
   ══════════════════════════════════════════════════════════════════════════ */

const PITCH = 137.15;
const ORIGIN_X = 472;
const ORIGIN_Y = 750;
const DOT_R = 69.5;
const SIDE = 2048;
const CORNER_R = 404; // 0.197 × side — the machine's own radius

type Cell = [col: number, row: number];

/** The four terminals where a stroke ends pointing up or outward. */
const SIGNAL: Cell[] = [[6, 0], [1, 1], [4, 2], [10, 2]];

const PAPER: Cell[] = [
  [6, 1],
  [0, 2], [1, 2], [2, 2], [3, 2], [6, 2],
  [1, 3], [6, 3], [9, 3],
  [1, 4], [6, 4], [7, 4], [8, 4],
  [1, 5], [6, 5], [9, 5],
  [2, 6], [3, 6], [4, 6], [6, 6], [10, 6],
];

const at = (i: number, origin: number) => Number((origin + i * PITCH).toFixed(1));

const dots = (cells: Cell[], fill: string) =>
  cells.map(([c, r]) => (
    <circle key={`${c}-${r}`} cx={at(c, ORIGIN_X)} cy={at(r, ORIGIN_Y)} r={DOT_R} fill={fill} />
  ));

const LogoMark: React.FC<Props> = ({ size = 38, className }) => (
  <svg
    className={className ? `logomark ${className}` : 'logomark'}
    width={size}
    height={size}
    viewBox={`0 0 ${SIDE} ${SIDE}`}
    role="img"
    aria-label="tokeniko"
  >
    <rect width={SIDE} height={SIDE} rx={CORNER_R} ry={CORNER_R} fill="var(--lm-field)" />
    {dots(PAPER, 'var(--lm-dot)')}
    {dots(SIGNAL, 'var(--lm-signal)')}
  </svg>
);

export default LogoMark;
