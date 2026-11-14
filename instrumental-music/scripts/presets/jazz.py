"""Jazz trio / quartet preset (seeded, mood-aware generator). Draft, 2026-11.

Fixed: swung eighths, rootless piano comping, walking acoustic bass, brush kit
(ride + pedal hat, or snare swirls when quiet), a head - bridge - head - piano
solo - head form, small room reverb and the stem level ratios.
Mood and seed choose, from curated banks only: key, tempo, swing, progressions
(head and bridge), form, comping patterns, lead instrument, drum feel, ambience
texture, room size and the melody (rule-built, always fits the chords).
"""
import random
import engine as E
from engine import *  # noqa: F401,F403
from presets.common import Melody, chord_pcs, key_name
from moods import pick_palette

# In C: name -> (bass root, rootless voicing)
CH = {
    'Cmaj9': (36, [52, 55, 59, 62]), 'C6/9': (36, [52, 57, 62, 67]), 'Dm9': (38, [53, 57, 60, 64]),
    'G13': (43, [53, 57, 59, 64]), 'G7b9': (43, [53, 56, 59, 62]), 'Em7': (40, [55, 59, 62, 64]),
    'A13b9': (45, [55, 58, 61, 66]), 'Fmaj9': (41, [57, 60, 64, 67]), 'Bb9': (46, [56, 60, 62, 65]),
    'Fm6': (41, [56, 60, 62, 65]), 'Am9': (45, [55, 59, 60, 64]), 'D9': (38, [54, 57, 60, 64]),
    'E7b9': (40, [56, 59, 62, 65]), 'Bm7b5': (47, [57, 62, 65, 69]),
}
# 8 bars each; a tuple is two chords in one bar (two beats each)
PROGRESSIONS = {
    'two-five': ['Dm9', 'G13', 'Cmaj9', 'A13b9', 'Dm9', 'G13', 'C6/9', ('Dm9', 'G13')],
    'rhythm': [('Cmaj9', 'A13b9'), ('Dm9', 'G13'), ('Em7', 'A13b9'), ('Dm9', 'G13'),
               ('Cmaj9', 'D9'), ('Dm9', 'G7b9'), 'C6/9', ('Dm9', 'G13')],
    'backdoor': ['Fmaj9', 'Fm6', 'Cmaj9', 'A13b9', 'Dm9', 'Bb9', 'Cmaj9', ('Dm9', 'G13')],
    'turnaround': ['Cmaj9', 'Em7', 'Fmaj9', 'E7b9', 'Am9', 'D9', 'Dm9', 'G13'],
    'falling-leaves': ['Dm9', 'G13', 'Cmaj9', 'Fmaj9', 'Bm7b5', 'E7b9', 'Am9', 'Am9'],
    'minor-blue': ['Am9', 'Am9', 'Dm9', 'Dm9', 'Bm7b5', 'E7b9', 'Am9', ('Bm7b5', 'E7b9')],
    'bridge-four': ['Fmaj9', 'Fmaj9', 'Em7', 'A13b9', 'D9', 'D9', 'Dm9', 'G7b9'],
}
HEADS = {'major': ['two-five', 'rhythm', 'backdoor', 'turnaround'], 'minor': ['falling-leaves', 'minor-blue']}
BRIDGES = {'two-five': 'bridge-four', 'rhythm': 'bridge-four', 'backdoor': 'turnaround', 'turnaround': 'bridge-four',
           'falling-leaves': 'minor-blue', 'minor-blue': 'falling-leaves'}
MINOR = ('falling-leaves', 'minor-blue')
# lead = melody instrument (GM), lo = bottom of its melody range in C
PALETTES = {
    'piano-trio': dict(lead=0, lo=72, bright=(0.0, 1.0), energy=(0.0, 1.0), tags=['piano', 'warm']),
    'vibes-trio': dict(lead=11, lo=72, bright=(0.4, 1.0), energy=(0.2, 1.0), tags=['vibes']),
    'tenor-quartet': dict(lead=66, lo=60, bright=(0.0, 0.6), energy=(0.0, 0.8), tags=['sax', 'warm', 'night']),
    'trumpet-quartet': dict(lead=59, lo=67, bright=(0.3, 0.9), energy=(0.3, 1.0), tags=['trumpet', 'jazz']),
    'guitar-trio': dict(lead=26, lo=67, bright=(0.2, 0.8), energy=(0.0, 0.8), tags=['guitar', 'soft']),
}
FORMS = {
    'standard': ['intro'] * 4 + ['A'] * 8 + ['A2'] * 8 + ['B'] * 8 + ['A3'] * 8 + ['solo'] * 8 + ['A4'] * 8 + ['out'] * 4,
    'long': ['intro'] * 4 + ['A'] * 8 + ['A2'] * 8 + ['B'] * 8 + ['A3'] * 8 + ['solo'] * 16 + ['A4'] * 8 + ['out'] * 4,
}
COMPS = [[(0, 1.2, 58), (1.5, 0.4, 50)], [(1.5, 0.4, 52), (3, 0.8, 50)], [(0.5, 0.4, 50), (2, 1.4, 56)],
         [(0, 0.4, 54), (2.5, 1.2, 52)], [(1.5, 0.4, 48), (2.5, 0.4, 50), (3.5, 0.4, 46)]]
RHYTHMS = [[(0, 1.5), (1.5, .5), (2, .5), (2.5, 1.5)], [(.5, .5), (1, .5), (1.5, 1), (2.5, 1.5)],
           [(0, .5), (.5, .5), (1, .5), (1.5, .5), (2, 1), (3, 1)], [(1.5, .5), (2, .5), (2.5, .5), (3, 1)],
           [(0, 1), (1, .5), (1.5, .5), (2, 2)], [(0, .5), (.5, 1), (1.5, .5), (2, .5), (2.5, 1.5)]]
SOLO_RHYTHMS = [[(0, .5), (.5, .5), (1, .5), (1.5, .5), (2, .5), (2.5, .5), (3, 1)],
                [(.5, .5), (1, .5), (1.5, .5), (2, .5), (2.5, 1.5)],
                [(0, .5), (.5, .5), (1, 1), (2, .5), (2.5, .5), (3, .5), (3.5, .5)],
                [(0, 1), (1, .5), (1.5, .5), (2, .5), (2.5, .5), (3, 1)]]
ENDINGS = [[(0, 3)], [(0, 2), (2.5, 1.5)], [(.5, .5), (1, 3)]]
SCALE = [0, 2, 4, 5, 7, 9, 11]
TEXTURE_DB = {'vinyl': -42, 'rain': -34, 'fire': -37, 'birds': -37, 'night': -39, 'ocean': -37}
LUFS = -15
# brush kit notes
KICK, SNARE, SWIRL, HAT, RIDE = 36, 38, 40, 44, 51


def plan(seed, mood=None):
    r = random.Random(seed)
    m = mood or dict(energy=r.uniform(0.3, 0.65), brightness=r.uniform(0.3, 0.7), mode=None, space=0.5,
                     texture=None, palette=None, prog=None, hints=[])
    e, br = m['energy'], max(0.1, m['brightness'])
    heads = HEADS.get(m.get('mode')) or HEADS['major'] + HEADS['minor']
    head = m.get('prog') if m.get('prog') in PROGRESSIONS and m.get('prog') in BRIDGES else r.choice(heads)
    return dict(
        seed=seed,
        key=r.choice([-5, -4, -3, -2] if br < 0.35 else ([0, 1, 2, 3] if br > 0.65 else [-3, -2, -1, 0, 2])),
        bpm=int(round(90 + e * 50 + r.uniform(-4, 4))),
        swing=round(r.uniform(0.12, 0.16), 3),
        prog=head, bridge=BRIDGES[head],
        form='long' if e < 0.35 else r.choice(['standard', 'standard', 'long']),
        brushes='swirl' if e < 0.4 else 'ride',
        palette=pick_palette(r, PALETTES, dict(m, brightness=br)),
        texture=m.get('texture') or 'none',
        lead_cut=int(5000 + 4000 * br),
        room=round(1.2 + 1.2 * m.get('space', 0.5), 2), wet=round(0.14 + 0.1 * m.get('space', 0.5), 3),
        mood={k: m.get(k) for k in ('energy', 'brightness', 'mode', 'space', 'texture', 'matched') if k in m},
    )


def _bars(name, k):
    """-> per bar: list of (beat, beats, root, voicing) segments"""
    out = []
    for b in PROGRESSIONS[name]:
        names = b if isinstance(b, tuple) else (b,)
        seg = 4 / len(names)
        out.append([(j * seg, seg, CH[n][0] + k, [x + k for x in CH[n][1]]) for j, n in enumerate(names)])
    return out


def render(p, out_path):
    E.seed(p['seed'])
    random.seed(p['seed'] * 7919 + 3)
    k = p['key']; BPM = p['bpm']; b = 60 / BPM; SW = p['swing']
    pal = PALETTES[p['palette']]
    A = _bars(p['prog'], k); Bb = _bars(p['bridge'], k)
    sect = FORMS[p['form']]
    bars = len(sect); L = int((bars * 4 * b + 7) * SR)
    first = {s: sect.index(s) for s in set(sect)}

    def T(bar, beat):
        sw = SW if abs(beat * 2 - round(beat * 2)) < 1e-6 and round(beat * 2) % 2 == 1 else 0
        return (bar * 4 + beat + sw) * b

    def bar_of(i):
        sc = sect[i]
        if sc == 'intro':
            return A[4 + i]
        j = (i - first[sc]) % 8
        return Bb[j] if sc == 'B' else A[j]

    def pcs(segs):
        out = set()
        for _, _, root, v in segs:
            out |= chord_pcs([root] + v)
        return out

    # ---- melody: head theme over A, a bridge line over B, piano solo over A ----
    lo = pal['lo'] + k
    scale = [(x + k) % 12 for x in SCALE]
    mg = Melody(random, scale=scale, lo=lo, hi=lo + 14, rhythms=RHYTHMS, endings=ENDINGS)
    a_ch = [pcs(A[j]) for j in range(8)]
    theme = mg.section(a_ch)
    lines = {'A': theme, 'A2': mg.vary(theme, a_ch, bars_to_vary=(3, 6, 7)),
             'B': mg.section([pcs(Bb[j]) for j in range(8)]), 'A3': theme,
             'A4': mg.vary(theme, a_ch, bars_to_vary=(1, 7))}
    sg = Melody(random, scale=scale, lo=72 + k, hi=88 + k, rhythms=SOLO_RHYTHMS, endings=ENDINGS)
    solo = []
    for _ in range(sect.count('solo') // 8):
        solo += sg.section(a_ch)

    comp = []; lead = []; piano_solo = []; bass = []; drums = []; score = []
    prev_bass = 36 + k
    for i, sc in enumerate(sect):
        segs = bar_of(i)
        for beat, beats, root, v in segs:
            score.append(dict(bar=i, start=T(i, beat), end=T(i, beat + beats), pcs=sorted(chord_pcs([root] + v))))
        # piano comping (sparser under the solo and in the intro)
        hits = random.choice(COMPS) if sc not in ('out',) else [(0, 4, 50)]
        if sc in ('solo', 'intro'):
            hits = hits[:1]
        for pos, l, vel in hits:
            root, v = next((r_, v_) for bt, bl, r_, v_ in segs if bt <= pos < bt + bl)
            for j, x in enumerate(v):
                comp.append((x, T(i, pos) + j * 0.008 + random.uniform(0, 0.01), l * b, vel + random.randint(-6, 6)))
        # melody
        if sc in lines:
            for o, x, l in lines[sc][(i - first[sc]) % 8]:
                lead.append((x, T(i, o) + random.uniform(0, 0.015), l * b * 0.92, 74 + random.randint(-8, 8)))
        if sc == 'solo':
            for o, x, l in solo[i - first['solo']]:
                piano_solo.append((x, T(i, o) + random.uniform(0, 0.01), l * b * 0.85, 64 + random.randint(-10, 8)))
        # walking bass: root on the chord's first beat, chord tones between, approach note on the last beat
        nxt = bar_of(i + 1)[0][2] if i + 1 < bars else segs[0][2]
        two_feel = sc in ('intro', 'out')
        for beat in range(4):
            if two_feel and beat % 2:
                continue
            seg = next(s for s in segs if s[0] <= beat < s[0] + s[1])
            root, v = seg[2], seg[3]
            tones = sorted({(x - root) % 12 for x in [root] + v})
            if beat == seg[0]:
                target = root
            elif beat == 3 and not two_feel:
                target = nxt + random.choice([-1, 1, 7 - 12, 2])
            else:
                target = root + random.choice([t for t in tones if t] or [7])
            cands = [x for x in range(28, 50) if x % 12 == target % 12]
            note = min(cands, key=lambda x: abs(x - prev_bass) + (3 if x == prev_bass else 0))
            prev_bass = note
            bass.append((note, T(i, beat), b * (1.9 if two_feel else 0.92), 88 + (8 if beat == 0 else 0) + random.randint(-6, 4)))
        # brushes
        if sc == 'out':
            if i == bars - 1:
                drums.append((51, T(i, 0), 3 * b, 50))
            continue
        for beat in range(4):
            if beat in (1, 3):
                drums.append((HAT, T(i, beat), 0.1, 52 + random.randint(-6, 6)))
            if sc == 'intro':
                continue
            drums.append((KICK, T(i, beat), 0.1, 22 + random.randint(-4, 4)))
            if p['brushes'] == 'swirl':
                drums.append((SWIRL, T(i, beat), b, 40 + random.randint(-6, 6)))
            else:
                drums.append((RIDE, T(i, beat), 0.3, 58 + (6 if beat in (1, 3) else 0) + random.randint(-6, 6)))
                if beat in (1, 3):
                    drums.append((RIDE, T(i, beat + 0.5), 0.2, 46 + random.randint(-6, 6)))
        if p['brushes'] == 'ride' and sc != 'intro' and random.random() < 0.3:
            drums.append((SNARE, T(i, random.choice([1.5, 2.5, 3.5])), 0.1, 40 + random.randint(-8, 10)))
    end = bars * 4 * b
    root0, v0 = A[0][0][2], A[0][0][3]
    comp += [(x, end - 4 * b, 4 * b + 3, 46) for x in v0]
    bass.append((min((x for x in range(28, 50) if x % 12 == root0 % 12), key=lambda x: abs(x - prev_bass)), end - 4 * b, 4 * b + 3, 80))

    P = render_midi(comp + piano_solo, 0, L, BPM, gain=0.55) if pal['lead'] != 0 else render_midi(comp + piano_solo + lead, 0, L, BPM, gain=0.55)
    LEAD = render_midi(lead, pal['lead'], L, BPM, gain=0.5) if pal['lead'] != 0 else np.zeros((L, 2))
    BASS = render_midi(bass, 32, L, BPM, gain=0.6)
    DR = render_midi(drums, 40, L, BPM, is_drum=True, gain=0.5)
    P = lp(hp(P, 90), 7000); LEAD = lp(LEAD, p['lead_cut']); BASS = lp(BASS, 2500)
    P = to_db(P, -20); BASS = to_db(BASS, -19.5); DR = to_db(DR, -25)
    LEAD = to_db(LEAD, -20.5) if pal['lead'] != 0 else LEAD
    # stage: piano a little left, lead centre-right, bass centre, kit spread as recorded
    P = np.stack([P[:, 0] * 1.0, P[:, 1] * 0.8], 1); LEAD = np.stack([LEAD[:, 0] * 0.85, LEAD[:, 1]], 1)
    dry = P + LEAD + BASS + DR
    wet = reverb(P * 0.6 + LEAD * 0.8 + DR * 0.5 + BASS * 0.1, decay=p['room'], tone=5000)
    tex = p['texture']
    amb = to_db(texture(tex, L), TEXTURE_DB[tex]) if tex not in (None, 'none') else 0
    mix = dry + wet * p['wet'] + amb
    t = np.arange(L) / SR
    mix *= np.clip(t / 0.5, 0, 1)[:, None] * np.clip((L / SR - t) / 4, 0, 1)[:, None]
    master(mix, out_path, lufs=LUFS)
    return dict(lufs_target=LUFS, beat=b, key_pcs=sorted(scale), chords=score,
                melody=[dict(pitch=x[0], start=x[1], dur=x[2]) for x in lead],
                key_name=(key_name(k, 'A') + 'm') if p['prog'] in MINOR else key_name(k, 'C'), bars=bars)
