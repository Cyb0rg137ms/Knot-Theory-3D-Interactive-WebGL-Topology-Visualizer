import { describe, expect, it } from 'vitest';
import { torusAlexander, torusAlexanderString } from './torus';

describe('torusAlexander', () => {
  it('matches knotlab / KnotInfo values', () => {
    expect(torusAlexanderString(2, 3)).toBe('t - 1 + t^-1');
    expect(torusAlexanderString(3, 4)).toBe('t^3 - t^2 + 1 - t^-2 + t^-3');
    expect(torusAlexanderString(2, 5)).toBe('t^2 - t + 1 - t^-1 + t^-2');
  });
  it('Δ(1) = 1 and degree (p-1)(q-1)', () => {
    for (const [p, q] of [[2, 7], [3, 5], [4, 7], [5, 6]]) {
      const c = torusAlexander(p, q)!;
      expect(c.reduce((a, b) => a + b, 0)).toBe(1);
      expect(c.length - 1).toBe((p - 1) * (q - 1));
    }
  });
  it('reports links', () => {
    expect(torusAlexander(2, 4)).toBeNull();
    expect(torusAlexanderString(3, 6)).toContain('3-component link');
  });
});
