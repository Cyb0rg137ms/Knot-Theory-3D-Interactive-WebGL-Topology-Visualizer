// Exact Alexander polynomial of the torus knot T(p, q):
//   Δ(t) = (t^{pq} − 1)(t − 1) / ((t^p − 1)(t^q − 1))
// computed by exact integer polynomial division (mirrors knotlab.geometry.torus_alexander).

export type Poly = number[]; // coefficient of t^i at index i

export const gcd = (a: number, b: number): number => (b === 0 ? Math.abs(a) : gcd(b, a % b));

const mul = (a: Poly, b: Poly): Poly => {
  const out = new Array(a.length + b.length - 1).fill(0);
  a.forEach((x, i) => b.forEach((y, j) => (out[i + j] += x * y)));
  return out;
};

const binom = (k: number): Poly => {
  const p = new Array(k + 1).fill(0);
  p[0] = -1;
  p[k] = 1;
  return p; // t^k − 1
};

export const divExact = (num: Poly, den: Poly): Poly => {
  const r = num.slice();
  const dl = den.length - 1;
  const q = new Array(Math.max(r.length - dl, 1)).fill(0);
  for (let i = r.length - 1; i >= dl; i--) {
    const c = r[i] / den[dl];
    if (!Number.isInteger(c)) throw new Error('non-exact division');
    q[i - dl] = c;
    for (let j = 0; j <= dl; j++) r[i - dl + j] -= c * den[j];
  }
  if (r.some((x) => x !== 0)) throw new Error('non-exact division');
  return q;
};

/** Coefficients of Δ_{T(p,q)}, lowest degree first; null if T(p,q) is a link (gcd > 1). */
export const torusAlexander = (p: number, q: number): Poly | null => {
  p = Math.abs(p);
  q = Math.abs(q);
  if (p === 0 || q === 0 || gcd(p, q) !== 1) return null;
  if (p === 1 || q === 1) return [1];
  return divExact(mul(binom(p * q), binom(1)), mul(binom(p), binom(q)));
};

/** Symmetrised display string, e.g. T(2,3) -> "t - 1 + t^-1". */
export const formatSymmetric = (coeffs: Poly): string => {
  const shift = (coeffs.length - 1) / 2;
  const parts: string[] = [];
  for (let i = coeffs.length - 1; i >= 0; i--) {
    const c = coeffs[i];
    if (c === 0) continue;
    const e = i - shift;
    const mag = Math.abs(c);
    const mono = e === 0 ? `${mag}` : `${mag === 1 ? '' : mag}t${e === 1 ? '' : `^${e}`}`;
    parts.push(parts.length === 0 ? (c < 0 ? `-${mono}` : mono) : `${c < 0 ? '-' : '+'} ${mono}`);
  }
  return parts.join(' ');
};

export const torusAlexanderString = (p: number, q: number): string => {
  const c = torusAlexander(p, q);
  return c === null ? `T(${p},${q}) is a ${gcd(p, q)}-component link` : formatSymmetric(c);
};
