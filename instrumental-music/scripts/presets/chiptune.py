"""Chiptune preset (seeded, mood-aware generator). Draft, 2026-11.

All voices are DSP, modelled on a four-channel game console: two pulse waves
(lead with delayed vibrato and an echo copy, and a chord arpeggio), a stepped
triangle bass and a noise channel for drums. Fixed: the voices, the echo, a
gentle low-pass so the square waves never get harsh, a small room, and the
stem level ratios. Mood and seed choose: key, tempo, progressions, form, pulse
duty cycles, arpeggio speed, bass and drum patterns, brightness and the melody.
"""
import random
import engine as E
from engine import *  # noqa: F401,F403
from presets.common import Melody, chord_pcs, key_name

# In C: triads (bass root, chord tones)
CH = {'C': (36, [60, 64, 67]), 'G': (43, [59, 62, 67]), 'Am': (45, [60, 64, 69]), 'F': (41, [60, 65, 69]),
      'Dm': (38, [62, 65, 69]), 'Em': (40, [59, 64, 67]), 'E': (40, [59, 64, 68]), 'Bb': (46, [58, 62, 65])}
PROGRESSIONS = {
    'hero': ['C', 'G', 'Am', 'F', 'C', 'G', 'F', 'G'],
    'town': ['F', 'G', 'Em', 'Am', 'Dm', 'G', 'C', 'C'],
    'sky': ['C', 'Am', 'F', 'G', 'C', 'Am', 'Dm', 'G'],
    'mixo': ['C', 'Bb', 'F', 'C', 'C', 'Bb', 'F', 'G'],
    'cave': ['Am', 'F', 'C', 'G', 'Am', 'F', 'G', 'G'],
    'quest': ['Am', 'Dm', 'G', 'C', 'F', 'Dm', 'E', 'E'],
}
PAIRS = {'major': [('hero', 'town'), ('sky', 'town'), ('hero', 'mixo'), ('sky', 'hero')],
         'minor': [('cave', 'quest'), ('quest', 'town'), ('cave', 'town')]}
MINOR = ('cave', 'quest')
FORMS = {
    'classic': ['intro'] * 4 + ['A'] * 8 + ['A2'] * 8 + ['B'] * 8 + ['A3'] * 8 + ['brk'] * 4 + ['A4'] * 8 + ['out'] * 4,
    'long': ['intro'] * 4 + ['A'] * 8 + ['A2'] * 8 + ['B'] * 8 + ['B2'] * 8 + ['A3'] * 8 + ['brk'] * 4 + ['A4'] * 8 + ['out'] * 4,
}
RHYTHMS = [[(0, 1), (1, .5), (1.5, .5), (2, 1), (3, 1)], [(0, .5), (.5, .5), (1, 1), (2, 2)],
           [(0, 1.5), (1.5, .5), (2, 1.5), (3.5, .5)], [(0, .5), (.5, .5), (1, .5), (1.5, .5), (2, 2)],
           [(.5, .5), (1, 1), (2, .5), (2.5, 1.5)], [(0, 1), (1, 1), (2, 1), (3, 1)]]
ENDINGS = [[(0, 3)], [(0, 2), (2, 2)], [(0, 1), (1, 3)]]
KICKS = [[0, 2.5], [0, 1.5, 2.5], [0, 2]]
BASSES = ['octave', 'root-fifth', 'pulse']
SCALE = [0, 2, 4, 5, 7, 9, 11]
LUFS = -14


def plan(seed, mood=None):
    r = random.Random(seed)
    m = mood or dict(energy=r.uniform(0.35, 0.7), brightness=r.uniform(0.4, 0.8), mode=None, space=0.5,
                     texture=None, palette=None, prog=None, hints=[])
    e, br = m['energy'], max(0.1, m['brightness'])
    pairs = PAIRS.get(m.get('mode')) or PAIRS['major'] + PAIRS['minor']
    pa, pb = r.choice(pairs)
    if m.get('prog') in PROGRESSIONS:
        pa = m['prog']
    return dict(
        seed=seed,
        key=r.choice([-4, -3, -2, 0] if br < 0.35 else ([0, 2, 3, 5] if br > 0.65 else [-3, -2, 0, 2, 3])),
        bpm=int(round(100 + e * 36 + r.uniform(-4, 4))),
        pair=[pa, pb],
        form='long' if e < 0.4 else r.choice(['classic', 'long']),
        lead_duty=r.choice([0.25, 0.5] if br < 0.5 else [0.125, 0.25]),
        arp_duty=r.choice([0.25, 0.5]),
        arp_rate=4 if e < 0.5 else r.choice([4, 6]),   # notes per beat
        kick=r.randrange(len(KICKS)), bassline=r.choice(BASSES),
        half_time=e < 0.3,
        cut=int(4500 + 4500 * br),
        room=round(0.8 + 0.8 * m.get('space', 0.5), 2), wet=round(0.08 + 0.1 * m.get('space', 0.5), 3),
        texture=m.get('texture') or 'none',
        mood={k: m.get(k) for k in ('energy', 'brightness', 'mode', 'space', 'texture', 'matched') if k in m},
    )


# ---------- console voices ----------
def pulse(p, dur, duty=0.5, vib=0.0, a=0.005, d=0.08, s=0.7, r=0.04):
    n = int((dur + r) * SR); t = np.arange(n) / SR
    f = mtof(p) * (1 + vib * np.clip((t - 0.18) / 0.2, 0, 1) * np.sin(2 * np.pi * 5.5 * t))
    ph = np.cumsum(f) / SR
    x = np.where((ph % 1) < duty, 1.0, -1.0) - (2 * duty - 1)
    return x * adsr(n, a, d, s, r) * 0.5


def triangle(p, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    ph = (t * mtof(p)) % 1
    x = np.round((1 - 4 * np.abs(ph - 0.5)) * 7.5) / 7.5   # 4-bit steps
    return x * adsr(n, 0.002, 0.02, 1.0, 0.01) * 0.7


def noise_hit(kind):
    if kind == 'kick':
        n = int(0.16 * SR); t = np.arange(n) / SR
        f = 55 + 120 * np.exp(-t * 30)
        x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-t * 18) * 0.8
        return x + lp(rng.standard_normal(n), 2000) * np.exp(-t * 80) * 0.3
    if kind == 'snare':
        n = int(0.18 * SR); t = np.arange(n) / SR
        return lp(rng.standard_normal(n), 7000) * np.exp(-t * 22) * 0.6 + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 40) * 0.3
    n = int(0.035 * SR); t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 6000) * np.exp(-t * 90) * 0.35


def render(p, out_path):
    E.seed(p['seed'])
    random.seed(p['seed'] * 7919 + 4)
    k = p['key']; BPM = p['bpm']; b = 60 / BPM
    pa, pb = p['pair']
    P1 = [(CH[c][0] + k, [x + k for x in CH[c][1]]) for c in PROGRESSIONS[pa]]
    P2 = [(CH[c][0] + k, [x + k for x in CH[c][1]]) for c in PROGRESSIONS[pb]]
    sect = FORMS[p['form']]
    bars = len(sect); L = int((bars * 4 * b + 4) * SR)
    first = {s: sect.index(s) for s in set(sect)}
    T = lambda bar, beat: (bar * 4 + beat) * b

    def chord_at(i):
        sc = sect[i]
        if sc == 'intro':
            return P1[4 + i]
        j = (i - first[sc]) % 8
        return P2[j] if sc in ('B', 'B2') else P1[j]

    scale = [(x + k) % 12 for x in SCALE]
    mg = Melody(random, scale=scale, lo=72 + k, hi=86 + k, rhythms=RHYTHMS, endings=ENDINGS)
    a_ch = [chord_pcs([r_] + v) for r_, v in P1]; b_ch = [chord_pcs([r_] + v) for r_, v in P2]
    theme = mg.section(a_ch)
    lines = {'A': theme, 'A2': mg.vary(theme, a_ch, bars_to_vary=(3, 6, 7)), 'B': mg.section(b_ch), 'A3': theme,
             'A4': mg.vary(theme, a_ch, bars_to_vary=(1, 5, 7))}
    if 'B2' in first:
        lines['B2'] = mg.vary(lines['B'], b_ch, bars_to_vary=(2, 5, 7))

    lead = np.zeros((L, 2)); echo = np.zeros((L, 2)); arp = np.zeros((L, 2)); bass = np.zeros((L, 2)); drums = np.zeros((L, 2))
    mel = []; score = []
    for i, sc in enumerate(sect):
        root, tones = chord_at(i)
        score.append(dict(bar=i, start=T(i, 0), end=T(i + 1, 0), pcs=sorted(chord_pcs([root] + tones))))
        if sc in lines:
            for o, x, l in lines[sc][(i - first[sc]) % 8]:
                up = 12 if sc == 'A4' and x + 12 <= 93 + k else 0
                v = pulse(x + up, l * b * 0.9, p['lead_duty'], vib=0.006)
                place(lead, v, T(i, o), 0.9, 0.45)
                place(echo, v, T(i, o) + 0.75 * b, 0.35, 0.8)
                mel.append((x + up, T(i, o), l * b * 0.9))
        # arpeggio: chord tones cycling, quieter under the melody, alone in the break
        if sc != 'out':
            rate = p['arp_rate']; seq = tones + [tones[1]] if rate == 4 else tones + tones[::-1][1:-1] + [tones[0]]
            gain = 0.32 if sc in lines else 0.5
            for s in range(4 * rate):
                x = seq[s % len(seq)] + (12 if sc == 'brk' else 0)
                place(arp, pulse(x, b / rate * 0.8, p['arp_duty'], d=0.03, s=0.5, r=0.01), T(i, s / rate), gain, 0.62)
        # triangle bass
        if sc != 'brk':
            bl = p['bassline']
            if sc in ('intro', 'out') or p['half_time']:
                steps = [(0, root, 2), (2, root + 7 if bl != 'pulse' else root, 2)]
            elif bl == 'octave':
                steps = [(e / 2, root + (12 if e % 2 else 0), 0.5) for e in range(8)]
            elif bl == 'root-fifth':
                steps = [(0, root, 1), (1, root + 7, 1), (2, root + 12, 1), (3, root + 7, 1)]
            else:
                steps = [(0, root, 0.75), (0.75, root, 0.75), (1.5, root + 12, 0.5), (2, root, 1), (3, root + 7, 0.5), (3.5, root + 12, 0.5)]
            for o, x, l in steps:
                place(bass, triangle(x, l * b * 0.92), T(i, o), 0.9, 0.5)
        # noise drums
        if sc in ('A', 'A2', 'B', 'B2', 'A3', 'A4'):
            kicks = [0] if p['half_time'] else KICKS[p['kick']]
            snares = [2] if p['half_time'] else [1, 3]
            for pos in kicks: place(drums, noise_hit('kick'), T(i, pos), 0.9, 0.5)
            for pos in snares: place(drums, noise_hit('snare'), T(i, pos), 0.6, 0.5)
            for e in range(8):
                place(drums, noise_hit('hat'), T(i, e / 2), 0.5 if e % 2 == 0 else 0.3, 0.55)
        elif sc == 'brk' and i % 2 == 1:
            place(drums, noise_hit('hat'), T(i, 3.5), 0.4, 0.55)
    end = bars * 4 * b
    root0, tones0 = P1[0]
    for x in tones0: place(arp, pulse(x, 2.5, p['arp_duty'], d=0.4, s=0.4, r=1.0), end, 0.3, 0.62)
    place(bass, triangle(root0, 2.5), end, 0.8, 0.5)

    lead = lp(lead + echo, p['cut']); arp = lp(arp, p['cut'] * 0.8); drums = lp(drums, 9000); bass = lp(bass, 3000)
    lead = to_db(lead, -20); arp = to_db(arp, -25); bass = to_db(bass, -20); drums = to_db(drums, -24)
    dry = lead + arp + bass + drums
    wet = reverb(lead * 0.6 + arp * 0.6 + drums * 0.2, decay=p['room'], tone=6000)
    tex = p['texture']
    amb = to_db(texture(tex, L), -40) if tex not in (None, 'none') else 0
    mix = dry + wet * p['wet'] + amb
    t = np.arange(L) / SR
    mix *= np.clip(t / 0.05, 0, 1)[:, None] * np.clip((L / SR - t) / 3, 0, 1)[:, None]
    master(mix, out_path, lufs=LUFS)
    return dict(lufs_target=LUFS, beat=b, key_pcs=sorted(scale), chords=score,
                melody=[dict(pitch=x[0], start=x[1], dur=x[2]) for x in mel],
                key_name=(key_name(k, 'A') + 'm') if pa in MINOR else key_name(k, 'C'), bars=bars)
