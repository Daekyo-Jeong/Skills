"""New age / ambient piano preset (seeded generator).

Fixed from "Tidewater": GM piano arpeggios + singing melody, GM strings in
later sections, DSP shimmer sine pad, low drone, FM bells, wave-swelling ocean
wind, long 5.5 s hall reverb, stem levels and -16 LUFS master. The seed picks
key, tempo, progressions, arpeggio shape, form, bell placement and melody.
"""
import random
import engine as E
from engine import *  # noqa: F401,F403
from presets.common import Melody, chord_pcs, key_name

# In D major: (bass root, arpeggio tones low->high, pad/strings tones)
CH = {
    'Dmaj9': (38, [38, 45, 52, 54, 57], [62, 64, 66, 69]),
    'Bm11': (35, [35, 42, 49, 50, 54], [59, 62, 64, 66]),
    'Gmaj9#11': (31, [31, 38, 45, 47, 54], [59, 62, 66, 69]),
    'Asus2': (33, [33, 40, 45, 47, 52], [57, 61, 64, 69]),
    'Em9': (40, [40, 47, 54, 55, 59], [59, 62, 66, 67]),
    'F#m7': (42, [42, 49, 52, 57, 61], [61, 64, 66, 69]),
    'Gmaj7': (31, [31, 38, 43, 50, 54], [59, 62, 66, 67]),
}
PROGRESSIONS = {
    'tide': ['Dmaj9', 'Bm11', 'Gmaj9#11', 'Asus2'],
    'drift': ['Em9', 'F#m7', 'Gmaj7', 'Asus2'],
    'dusk': ['Bm11', 'Gmaj9#11', 'Dmaj9', 'Asus2'],
    'lift': ['Gmaj9#11', 'Asus2', 'F#m7', 'Bm11'],
    'open': ['Dmaj9', 'Asus2', 'Bm11', 'Gmaj7'],
}
PAIRS = [('tide', 'drift'), ('dusk', 'drift'), ('tide', 'lift'), ('open', 'drift'), ('dusk', 'lift')]
FORMS = {
    'classic': ['intro'] * 4 + ['A'] * 8 + ['B'] * 8 + ['C'] * 8 + ['out'] * 4,
    'short': ['intro'] * 4 + ['A'] * 4 + ['B'] * 8 + ['C'] * 8 + ['out'] * 4,
    'return': ['intro'] * 4 + ['A'] * 8 + ['B'] * 8 + ['C'] * 8 + ['A'] * 4 + ['out'] * 4,
}
ARPS = [[0, 1, 2, 3, 4, 3, 2, 1], [0, 2, 1, 3, 2, 4, 3, 1], [0, 1, 2, 4, 3, 4, 2, 1]]
RHYTHMS = [[(0, 1.5), (1.5, .5), (2, 2)], [(0, 2), (2, 1), (3, 1)], [(0, 1.5), (1.5, 2.5)],
           [(0, 2), (2, 2)], [(1, 1), (2, 2)], [(0, 3), (3, 1)]]
ENDINGS = [[(0, 4)], [(0, 3), (3, 1)], [(0, 2.5), (2.5, 1.5)]]
PENT = [2, 4, 6, 9, 11]          # D major pentatonic
SCALE = [2, 4, 6, 7, 9, 11, 1]   # D major
BELLS = [74, 76, 78, 81, 83, 86, 88]
LUFS = -16


def plan(seed):
    r = random.Random(seed)
    return dict(
        seed=seed,
        key=r.choice([-3, -2, 0, 0, 1, 2, 3]),
        bpm=r.randint(60, 72),
        pair=r.randrange(len(PAIRS)),
        form=r.choice(['classic', 'classic', 'short', 'return']),
        arp=r.randrange(len(ARPS)),
    )


def render(p, out_path):
    E.seed(p['seed'])
    random.seed(p['seed'] * 7919 + 2)
    k = p['key']; BPM = p['bpm']; b = 60 / BPM
    pa, pb = PAIRS[p['pair']]

    def chord(name):
        root, arp, tones = CH[name]
        return root + k, [x + k for x in arp], [x + k for x in tones]
    P1 = [chord(n) for n in PROGRESSIONS[pa]]; P2 = [chord(n) for n in PROGRESSIONS[pb]]
    sect = FORMS[p['form']]
    bars = len(sect); L = int((bars * 4 * b + 9) * SR)
    T = lambda bar, beat: (bar * 4 + beat) * b

    def chs_at(i, sc):
        return P1 if (i // 4) % 2 == 0 or sc in ('intro', 'A') else P2

    first = {s: sect.index(s) for s in set(sect)}
    def aligned(sc):
        out = []
        for j in range(8):
            root, arp, tones = chs_at(first[sc] + j, sc)[(first[sc] + j) % 4]
            out.append(chord_pcs([root] + arp + tones))
        return out
    bchords = aligned('B')
    mg = Melody(random, scale=[(x + k) % 12 for x in PENT], lo=71 + k, hi=83 + k, rhythms=RHYTHMS, endings=ENDINGS)
    theme = mg.section(bchords)
    answer = mg.vary(mg.refit(theme, aligned('C')), aligned('C'), bars_to_vary=(3, 6, 7))

    piano = []; strings = []; mel = []; score = []
    arp_pat = ARPS[p['arp']]
    for i, sc in enumerate(sect):
        root, arp, tones = chs_at(i, sc)[i % 4]
        score.append(dict(bar=i, start=T(i, 0), end=T(i + 1, 0), pcs=sorted(chord_pcs([root] + arp + tones))))
        if sc == 'intro':
            if i >= 2: piano.append((root + 12, T(i, 0), 4 * b, 38))
            continue
        dens = 8 if sc in ('B', 'C') else (4 if sc == 'A' and i - first['A'] < 2 else 8)
        for e in range(dens):
            x = arp[arp_pat[e * (8 // dens)]]
            v = 46 + 10 * (e == 0) + (8 if sc == 'C' else 0) + random.randint(-5, 5)
            piano.append((x, T(i, e * (4 / dens)) + random.uniform(0, 0.015), (4 / dens) * b * 1.8, v))
        if sc in ('B', 'C', 'out'):
            for x in tones: strings.append((x - 12 if sc == 'out' else x, T(i, 0), 4 * b + 0.3, 50 if sc == 'C' else 40))
        if sc == 'out': piano.append((root, T(i, 0), 4 * b, 40))
        if sc in ('B', 'C'):
            j = (i - first[sc]) % 8
            src = theme if sc == 'B' else answer
            for o, x, l in src[j]:
                x2 = x + 12 if sc == 'C' and j >= 4 and x + 12 <= 93 + k else x
                mel.append((x2, T(i, o) + random.uniform(0, 0.02), l * b * 1.05, 62 + random.randint(-6, 6) + (6 if sc == 'C' else 0)))
    end = bars * 4 * b
    for x, dt, v in ((50, 0, 34), (57, 0, 30), (66, 0.05, 30), (76, 0.1, 28)):
        piano.append((x + k, end + dt, 6, v))
    PIA = render_midi(piano + mel, 0, L, BPM, gain=0.6)
    STR = render_midi(strings, 49, L, BPM, gain=0.5)
    PIA = lp(PIA, 9000)
    shimmer = np.zeros((L, 2)); bells = np.zeros((L, 2)); drone = np.zeros((L, 2))
    for i, sc in enumerate(sect):
        root, arp, tones = chs_at(i, sc)[i % 4]
        for x in tones[:3]:
            place(shimmer, sine_pad(x + 12, 4 * b, a=2.5, r=4), T(i, 0), 0.25, 0.25 + 0.5 * random.random())
        if i % 2 == 0: place(drone, sine_pad(26 + k, 8 * b, a=4, r=5), T(i, 0), 0.5, 0.5)
        if sc in ('intro', 'A', 'C', 'out'):
            for _ in range(2 if sc != 'C' else 3):
                x = random.choice(BELLS) + k
                place(bells, fm_bell(x, 5, idx=2.5, ratio=3.5), T(i, random.choice([0.5, 1.5, 2.5, 3, 3.5])), 0.12, random.random())
    ocean = st(wind(L, 150, 700))
    t = np.arange(L) / SR
    ocean = ocean * (0.55 + 0.45 * np.sin(2 * np.pi * t / (8 * b) - np.pi / 2))[:, None]
    PIA = to_db(PIA, -19); STR = to_db(STR, -29); shimmer = to_db(shimmer, -30); bells = to_db(bells, -30)
    drone = to_db(drone, -32); ocean = to_db(ocean, -36)
    dry = PIA + STR + shimmer + bells + drone + ocean
    wet = reverb(PIA * 0.8 + STR + shimmer + bells * 1.2, decay=5.5, tone=6000, predelay=0.04)
    mix = dry + wet * 0.45
    fadein = np.clip(t / 6, 0, 1)[:, None]; fadeout = np.clip((L / SR - t) / 8, 0, 1)[:, None]
    master(mix * fadein * fadeout, out_path, lufs=LUFS)
    return dict(lufs_target=LUFS, beat=b, key_pcs=sorted((x + k) % 12 for x in SCALE),
                chords=score, melody=[dict(pitch=x[0], start=x[1], dur=x[2]) for x in mel],
                key_name=key_name(k, 'D'), bars=bars)
