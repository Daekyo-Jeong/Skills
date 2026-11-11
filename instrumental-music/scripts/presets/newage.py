"""New age / ambient piano preset (seeded, mood-aware generator).

Fixed from "Tidewater": arpeggiated GM keys + singing melody, GM sustain layer
in later sections, DSP shimmer sine pad, low drone, FM bells, ambience bed,
long hall reverb, stem level ratios and -16 LUFS loudnorm (measures ~-15).
Mood and seed choose: key, tempo, progressions, arpeggio shape and density,
form, instrument palette, ambience texture, hall size, bells and the melody.
"""
import random
import engine as E
from engine import *  # noqa: F401,F403
from presets.common import Melody, chord_pcs, key_name
from moods import pick_palette

# In D major: (bass root, arpeggio tones low->high, pad/strings tones)
CH = {
    'Dmaj9': (38, [38, 45, 52, 54, 57], [62, 64, 66, 69]),
    'Bm11': (35, [35, 42, 49, 50, 54], [59, 62, 64, 66]),
    'Gmaj9#11': (31, [31, 38, 45, 47, 54], [59, 62, 66, 69]),
    'Asus2': (33, [33, 40, 45, 47, 52], [57, 61, 64, 69]),
    'Em9': (40, [40, 47, 54, 55, 59], [59, 62, 66, 67]),
    'F#m7': (42, [42, 49, 52, 57, 61], [61, 64, 66, 69]),
    'Gmaj7': (31, [31, 38, 43, 50, 54], [59, 62, 66, 67]),
    'Bm9': (35, [35, 42, 47, 49, 54], [57, 61, 62, 66]),
    'D/F#': (42, [42, 45, 50, 54, 57], [62, 64, 66, 69]),
}
PROGRESSIONS = {
    'tide': ['Dmaj9', 'Bm11', 'Gmaj9#11', 'Asus2'],
    'drift': ['Em9', 'F#m7', 'Gmaj7', 'Asus2'],
    'dusk': ['Bm11', 'Gmaj9#11', 'Dmaj9', 'Asus2'],
    'lift': ['Gmaj9#11', 'Asus2', 'F#m7', 'Bm11'],
    'open': ['Dmaj9', 'Asus2', 'Bm11', 'Gmaj7'],
    'nocturne': ['Bm9', 'Em9', 'Gmaj7', 'F#m7'],
    'lament': ['Em9', 'Bm11', 'Gmaj9#11', 'F#m7'],
    'morning': ['Dmaj9', 'D/F#', 'Gmaj9#11', 'Asus2'],
}
PAIRS = {'major': [('tide', 'drift'), ('tide', 'lift'), ('open', 'drift'), ('morning', 'lift'), ('morning', 'drift')],
         'minor': [('dusk', 'drift'), ('dusk', 'lift'), ('nocturne', 'lament'), ('lament', 'dusk'), ('nocturne', 'drift')]}
# arp = arpeggio instrument, mel = melody instrument, sus = sustain layer (GM programs)
PALETTES = {
    'piano-strings': dict(arp=0, mel=0, sus=49, bright=(0.0, 1.0), energy=(0.0, 1.0), tags=['warm']),
    'piano-choir': dict(arp=0, mel=0, sus=52, bright=(0.0, 0.6), energy=(0.0, 0.6), tags=['choir', 'dream', 'soft']),
    'harp-flute': dict(arp=46, mel=73, sus=49, bright=(0.4, 1.0), energy=(0.0, 0.8), tags=['harp', 'flute', 'dream']),
    'guitar-piano': dict(arp=24, mel=0, sus=89, bright=(0.3, 0.9), energy=(0.2, 1.0), tags=['guitar', 'warm']),
    'celesta-piano': dict(arp=8, mel=0, sus=89, bright=(0.5, 1.0), energy=(0.0, 0.6), tags=['musicbox', 'dream']),
    'piano-pad': dict(arp=0, mel=0, sus=89, bright=(0.0, 0.5), energy=(0.0, 0.5), tags=['soft', 'warm']),
}
FORMS = {
    'classic': ['intro'] * 4 + ['A'] * 8 + ['B'] * 8 + ['C'] * 8 + ['out'] * 4,
    'short': ['intro'] * 4 + ['A'] * 4 + ['B'] * 8 + ['C'] * 8 + ['out'] * 4,
    'return': ['intro'] * 4 + ['A'] * 8 + ['B'] * 8 + ['C'] * 8 + ['A'] * 4 + ['out'] * 4,
}
ARPS = [[0, 1, 2, 3, 4, 3, 2, 1], [0, 2, 1, 3, 2, 4, 3, 1], [0, 1, 2, 4, 3, 4, 2, 1]]
RHYTHMS = [[(0, 1.5), (1.5, .5), (2, 2)], [(0, 2), (2, 1), (3, 1)], [(0, 1.5), (1.5, 2.5)],
           [(0, 2), (2, 2)], [(1, 1), (2, 2)], [(0, 3), (3, 1)]]
ENDINGS = [[(0, 4)], [(0, 3), (3, 1)], [(0, 2.5), (2.5, 1.5)]]
PENT = [2, 4, 6, 9, 11]          # D major / B minor pentatonic
SCALE = [2, 4, 6, 7, 9, 11, 1]   # D major
BELLS = [74, 76, 78, 81, 83, 86, 88]
TEXTURE_DB = {'ocean': -36, 'rain': -34, 'fire': -38, 'birds': -36, 'night': -40, 'vinyl': -42}
LUFS = -16


def plan(seed, mood=None):
    r = random.Random(seed)
    m = mood or dict(energy=r.uniform(0.3, 0.6), brightness=r.uniform(0.3, 0.7), mode=None, space=0.5,
                     texture=None, palette=None, hints=[])
    e, br, sp = m['energy'], max(0.1, m['brightness']), m.get('space', 0.5)
    pairs = PAIRS.get(m.get('mode')) or PAIRS['major'] + PAIRS['minor']
    return dict(
        seed=seed,
        key=r.choice([-3, -2, -1] if br < 0.35 else ([1, 2, 3] if br > 0.65 else [-2, 0, 1])),
        bpm=int(round(56 + e * 18 + r.uniform(-2, 2))),
        pair=list(r.choice(pairs)),
        form=r.choice(['classic', 'classic', 'short', 'return']),
        arp=r.randrange(len(ARPS)),
        arp_density=4 if e < 0.25 else 8,
        bells=0 if e < 0.15 else (3 if e > 0.6 else 2),
        palette=pick_palette(r, PALETTES, dict(m, brightness=br)),
        texture=m.get('texture') or 'ocean',
        hall=round(4.0 + 3.0 * sp, 2), wet=round(0.35 + 0.2 * sp, 3),
        piano_cut=int(6500 + 4000 * br),
        mood={k: m.get(k) for k in ('energy', 'brightness', 'mode', 'space', 'texture', 'matched') if k in m},
    )


def render(p, out_path):
    E.seed(p['seed'])
    random.seed(p['seed'] * 7919 + 2)
    k = p['key']; BPM = p['bpm']; b = 60 / BPM
    pal = PALETTES[p['palette']]
    pa, pb = p['pair']

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
    mlo = 71 + k + (5 if pal['mel'] == 73 else 0)
    mg = Melody(random, scale=[(x + k) % 12 for x in PENT], lo=mlo, hi=mlo + 12, rhythms=RHYTHMS, endings=ENDINGS)
    theme = mg.section(aligned('B'))
    answer = mg.vary(mg.refit(theme, aligned('C')), aligned('C'), bars_to_vary=(3, 6, 7))

    piano = []; strings = []; mel = []; score = []
    arp_pat = ARPS[p['arp']]
    for i, sc in enumerate(sect):
        root, arp, tones = chs_at(i, sc)[i % 4]
        score.append(dict(bar=i, start=T(i, 0), end=T(i + 1, 0), pcs=sorted(chord_pcs([root] + arp + tones))))
        if sc == 'intro':
            if i >= 2: piano.append((root + 12, T(i, 0), 4 * b, 38))
            continue
        if sc in ('B', 'C'):
            dens = 8 if (sc == 'C' or p['arp_density'] == 8) else 4
        else:
            dens = 4 if (sc == 'A' and i - first['A'] < 2) or p['arp_density'] == 4 else 8
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
    if pal['arp'] == pal['mel']:
        PIA = render_midi(piano + mel, pal['arp'], L, BPM, gain=0.6)
    else:
        A = to_db(render_midi(piano, pal['arp'], L, BPM, gain=0.6), -20)
        Mm = to_db(render_midi(mel, pal['mel'], L, BPM, gain=0.6), -21.5)
        PIA = A + Mm
    STR = render_midi(strings, pal['sus'], L, BPM, gain=0.5)
    PIA = lp(PIA, p['piano_cut'])
    shimmer = np.zeros((L, 2)); bells = np.zeros((L, 2)); drone = np.zeros((L, 2))
    for i, sc in enumerate(sect):
        root, arp, tones = chs_at(i, sc)[i % 4]
        for x in tones[:3]:
            place(shimmer, sine_pad(x + 12, 4 * b, a=2.5, r=4), T(i, 0), 0.25, 0.25 + 0.5 * random.random())
        if i % 2 == 0: place(drone, sine_pad(26 + k, 8 * b, a=4, r=5), T(i, 0), 0.5, 0.5)
        if sc in ('intro', 'A', 'C', 'out') and p['bells']:
            for _ in range(p['bells'] if sc == 'C' else max(1, p['bells'] - 1)):
                x = random.choice(BELLS) + k
                place(bells, fm_bell(x, 5, idx=2.5, ratio=3.5), T(i, random.choice([0.5, 1.5, 2.5, 3, 3.5])), 0.12, random.random())
    t = np.arange(L) / SR
    tex = p['texture']
    if tex == 'ocean':
        amb = st(wind(L, 150, 700)) * (0.55 + 0.45 * np.sin(2 * np.pi * t / (8 * b) - np.pi / 2))[:, None]
    else:
        amb = texture(tex, L)
    PIA = to_db(PIA, -19); STR = to_db(STR, -29); shimmer = to_db(shimmer, -30)
    drone = to_db(drone, -32)
    amb = to_db(amb, TEXTURE_DB[tex]) if tex != 'none' else 0
    bells = to_db(bells, -30) if p['bells'] else bells
    dry = PIA + STR + shimmer + bells + drone + amb
    wet = reverb(PIA * 0.8 + STR + shimmer + bells * 1.2, decay=p['hall'], tone=6000, predelay=0.04)
    mix = dry + wet * p['wet']
    fadein = np.clip(t / 6, 0, 1)[:, None]; fadeout = np.clip((L / SR - t) / 8, 0, 1)[:, None]
    master(mix * fadein * fadeout, out_path, lufs=LUFS)
    return dict(lufs_target=LUFS, beat=b, key_pcs=sorted((x + k) % 12 for x in SCALE),
                chords=score, melody=[dict(pitch=x[0], start=x[1], dur=x[2]) for x in mel],
                key_name=(key_name(k, 'B') + 'm') if pa in ('dusk', 'nocturne', 'lament') else key_name(k, 'D'), bars=bars)
