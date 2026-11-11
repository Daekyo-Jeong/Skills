"""Shared composition helpers: chord-aware melody generator."""

NOTE_NAMES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']


def key_name(offset, base):
    return NOTE_NAMES[(NOTE_NAMES.index(base) + offset) % 12]


def chord_pcs(notes):
    return {n % 12 for n in notes}


def clashes(pc, chord):
    """A non-chord tone a semitone away from a chord tone (minor 2nd / minor 9th rub)."""
    return pc not in chord and ((pc + 1) % 12 in chord or (pc - 1) % 12 in chord)


class Melody:
    """Pentatonic, chord-aware melody built from a curated rhythm bank.

    Rules: strong-beat / long notes land on chord tones; passing notes move by
    step and never rub a semitone against the chord; bars 5-6 repeat the rhythm
    and contour of bars 1-2 (motif), bars 4 and 8 are long cadence notes.
    """

    def __init__(self, rnd, scale, lo, hi, rhythms, endings):
        self.r = rnd
        self.pool = [m for m in range(lo, hi + 1) if m % 12 in scale]
        self.rhythms, self.endings = rhythms, endings
        self.cur = len(self.pool) // 2

    def _ok(self, i, chord):
        return 0 <= i < len(self.pool) and not clashes(self.pool[i] % 12, chord)

    def _snap(self, chord, near):
        cands = [i for i, m in enumerate(self.pool) if m % 12 in chord]
        if not cands:
            cands = [i for i in range(len(self.pool)) if self._ok(i, chord)]
        best = min(abs(i - near) for i in cands)
        return self.r.choice([i for i in cands if abs(i - near) == best])

    def _step(self, chord, forced=None):
        steps = [forced] if forced is not None else []
        steps += self.r.choices([-2, -1, -1, 1, 1, 2, 0], k=7)
        for s in steps:
            j = self.cur + s
            if j < 0 or j >= len(self.pool):
                j = self.cur - s
            if self._ok(j, chord):
                return j, s
        return self._snap(chord, self.cur), 0

    def bar(self, rhythm, chord, steps=None, cadence=False):
        out, used = [], []
        for n, (o, d) in enumerate(rhythm):
            strong = n == 0 or o in (0, 2) or d >= 1.5
            forced = steps[n] if steps and n < len(steps) else None
            j, s = self._step(chord, forced)
            if strong or (cadence and n == len(rhythm) - 1):
                j = self._snap(chord, j)
            self.cur = j; used.append(s)
            out.append((o, self.pool[j], d))
        return out, used

    def section(self, chords):
        r = self.r
        rh = [r.choice(self.rhythms) for _ in range(3)] + [r.choice(self.endings)]
        rh += [rh[0], rh[1], r.choice(self.rhythms), max(self.endings, key=lambda e: e[-1][0] + e[-1][1])]
        bars, motif = [], {}
        for i in range(8):
            steps = motif.get(i - 4) if i in (4, 5) else None
            notes, used = self.bar(rh[i], chords[i], steps, cadence=i in (3, 7))
            motif[i] = used
            bars.append(notes)
        return bars

    def vary(self, theme, chords, bars_to_vary=(1, 5, 7)):
        out = [list(b) for b in theme]
        for i in bars_to_vary:
            prev = out[i - 1][-1][1] if i > 0 and out[i - 1] else self.pool[len(self.pool) // 2]
            self.cur = min(range(len(self.pool)), key=lambda j: abs(self.pool[j] - prev))
            rhythm = [(o, d) for o, _, d in theme[i]]
            if i not in (3, 7) and self.r.random() < 0.5:
                rhythm = self.r.choice(self.rhythms)
            out[i], _ = self.bar(rhythm, chords[i], cadence=i in (3, 7))
        return out

    def refit(self, bars, chords):
        """Keep rhythm and contour, but move any note that does not fit the chords
        it now sits on (used when a theme returns over a shifted progression)."""
        out = []
        for notes, chord in zip(bars, chords):
            nb = []
            for n, (o, m, d) in enumerate(notes):
                strong = n == 0 or o in (0, 2) or d >= 1.5
                pc = m % 12
                if clashes(pc, chord) or (strong and pc not in chord and any(x % 12 in chord for x in self.pool)):
                    near = min(range(len(self.pool)), key=lambda j: abs(self.pool[j] - m))
                    m = self.pool[self._snap(chord, near)]
                nb.append((o, m, d))
            out.append(nb)
        return out
