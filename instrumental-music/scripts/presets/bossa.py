"""Bossa nova preset (seeded, mood-aware generator). Draft, 2026-11.

Fixed: straight eighths, nylon-guitar comping on a syncopated bossa pattern, acoustic
bass on root-fifth dotted figures, light percussion (rim click on a bossa clave, shaker,
soft kick), a head - head - bridge - head - solo - head form, small warm room.
Mood and seed choose, from curated banks only: key, tempo, progressions (head and
bridge), form, clave direction, comping pattern, lead instrument, optional string pad,
ambience texture, room size and the melody (rule-built, always fits the chords).
"""
import random
import engine as E
from engine import *  # noqa: F401,F403
from presets.common import Melody, chord_pcs, key_name
from presets.jazz import CH as JAZZ_CH
from moods import pick_palette

# In C: name -> (bass root, guitar voicing). Jazz rootless voicings plus a few open bossa shapes.
CH = dict(JAZZ_CH, **{
    'Cmaj7': (36, [52, 55, 59, 64]), 'Am7': (45, [55, 60, 64, 67]), 'Dm7': (38, [53, 57, 60, 65]),
    'G7': (43, [53, 57, 59, 65]), 'Ebdim7': (39, [54, 57, 60, 63]), 'Fm7': (41, [56, 60, 63, 67]),
    'Bb7': (46, [56, 58, 62, 65]), 'Gm7': (43, [53, 58, 62, 65]), 'C7': (36, [52, 55, 58, 62]),
})
PROGRESSIONS = {
    'sunny-two-five': ['Cmaj9', 'Cmaj9', 'Dm9', 'G13', 'Em7', 'A13b9', 'Dm9', 'G13'],
    'terrace': ['Fmaj9', 'Fmaj9', 'Em7', 'A13b9', 'Dm9', 'G13', 'Cmaj7', ('Dm7', 'G7')],
    'promenade': ['Cmaj7', 'Ebdim7', 'Dm7', 'G7', 'Em7', 'Am7', 'Dm9', 'G13'],
    'side-step': ['Cmaj9', 'Gm7', 'C7', 'Fmaj9', 'Fm7', 'Bb7', 'Cmaj7', ('Dm7', 'G7')],
    'saudade': ['Am9', 'Am9', 'D9', 'D9', 'Dm9', 'E7b9', 'Am9', 'E7b9'],
    'low-tide': ['Am9', 'Dm9', 'G13', 'Cmaj9', 'Fmaj9', 'Bm7b5', 'E7b9', 'Am9'],
}
HEADS = {'major': ['sunny-two-five', 'terrace', 'promenade', 'side-step'], 'minor': ['saudade', 'low-tide']}
BRIDGES = {'sunny-two-five': 'terrace', 'terrace': 'promenade', 'promenade': 'side-step', 'side-step': 'sunny-two-five',
           'saudade': 'low-tide', 'low-tide': 'saudade'}
MINOR = ('saudade', 'low-tide')
# lead = melody instrument (GM), lo = bottom of its melody range in C, strings = soft pad under the head
PALETTES = {
    'guitar-flute': dict(lead=73, lo=72, strings=False, bright=(0.4, 1.0), energy=(0.0, 0.9), tags=['flute', 'guitar']),
    'guitar-vibes': dict(lead=11, lo=72, strings=False, bright=(0.3, 1.0), energy=(0.2, 1.0), tags=['vibes']),
    'guitar-piano': dict(lead=0, lo=72, strings=True, bright=(0.0, 0.8), energy=(0.0, 0.8), tags=['warm', 'piano']),
    'guitar-trumpet': dict(lead=59, lo=67, strings=False, bright=(0.2, 0.8), energy=(0.3, 1.0), tags=['trumpet', 'jazz']),
    'guitar-clarinet': dict(lead=71, lo=67, strings=True, bright=(0.0, 0.6), energy=(0.0, 0.7), tags=['clarinet', 'soft', 'warm']),
    'guitar-sax': dict(lead=66, lo=60, strings=False, bright=(0.0, 0.6), energy=(0.0, 0.8), tags=['sax', 'night', 'warm']),
    'guitar-solo': dict(lead=24, lo=67, strings=True, bright=(0.2, 0.9), energy=(0.0, 0.6), tags=['guitar', 'soft']),
}
FORMS = {
    'standard': ['intro'] * 4 + ['A'] * 8 + ['A2'] * 8 + ['B'] * 8 + ['A3'] * 8 + ['solo'] * 8 + ['A4'] * 8 + ['out'] * 4,
    'long': ['intro'] * 4 + ['A'] * 8 + ['A2'] * 8 + ['B'] * 8 + ['A3'] * 8 + ['solo'] * 16 + ['A4'] * 8 + ['out'] * 4,
}
# guitar comping: two-bar patterns of (beat, beats) chord hits (thumb is the bass player's job)
COMPS = [
    ([(0, .5), (1, .5), (2.5, .5), (3.5, .5)], [(.5, .5), (1.5, .5), (2.5, 1), (3.5, .5)]),
    ([(0, .75), (1.5, .5), (3, .5)], [(.5, .5), (2, .5), (3, 1)]),
    ([(0, .5), (.5, .5), (1.5, .5), (2.5, .5), (3.5, .5)], [(0, .5), (1, .5), (2, .5), (2.5, .5), (3.5, .5)]),
    ([(0, 1.5), (2.5, .5), (3.5, .5)], [(.5, 1), (2, 1), (3.5, .5)]),
]
# bossa clave (3-2 / 2-3 by swapping the bars), in beats
CLAVE = ([0, 1.5, 3], [1, 2.5])
RHYTHMS = [[(0, 1.5), (1.5, .5), (2, 2)], [(.5, .5), (1, 1), (2, 1.5), (3.5, .5)], [(0, .5), (.5, 1.5), (2.5, 1.5)],
           [(1, .5), (1.5, .5), (2, 1), (3, 1)], [(0, 2), (2.5, .5), (3, 1)], [(0, 1), (1.5, 1), (3, 1)],
           [(.5, 1), (1.5, .5), (2, .5), (2.5, 1.5)]]
SOLO_RHYTHMS = [[(0, .5), (.5, .5), (1, .5), (1.5, 1), (2.5, .5), (3, 1)], [(.5, .5), (1, .5), (1.5, .5), (2, 2)],
                [(0, 1), (1, .5), (1.5, .5), (2, .5), (2.5, .5), (3, 1)], [(0, .5), (.5, .5), (1, 1), (2.5, 1.5)]]
ENDINGS = [[(0, 3)], [(0, 2), (2.5, 1.5)], [(.5, .5), (1, 3)]]
SCALE = [0, 2, 4, 5, 7, 9, 11]
TEXTURE_DB = {'vinyl': -42, 'rain': -34, 'fire': -37, 'birds': -36, 'night': -38, 'ocean': -35}
LUFS = -15
KICK, RIM, SHAKER, CABASA = 36, 37, 82, 69


def plan(seed, mood=None):
    r = random.Random(seed)
    m = mood or dict(energy=r.uniform(0.3, 0.7), brightness=r.uniform(0.35, 0.75), mode=None, space=0.5,
                     texture=None, palette=None, prog=None, hints=[])
    e, br = m['energy'], max(0.1, m['brightness'])
    heads = HEADS.get(m.get('mode')) or HEADS['major'] + HEADS['minor']
    head = m.get('prog') if m.get('prog') in BRIDGES else r.choice(heads)
    return dict(
        seed=seed,
        key=r.choice([-5, -4, -3, -2] if br < 0.35 else ([0, 1, 2, 3, 5] if br > 0.65 else [-3, -2, 0, 2, 3])),
        bpm=int(round(102 + e * 26 + r.uniform(-3, 3))),
        prog=head, bridge=BRIDGES[head],
        form='long' if e < 0.35 else r.choice(['standard', 'standard', 'long']),
        clave=r.choice(['3-2', '2-3']),
        comp=r.randrange(len(COMPS)),
        shaker=e >= 0.3,
        palette=pick_palette(r, PALETTES, dict(m, brightness=br)),
        texture=m.get('texture') or r.choice(['none', 'none', 'ocean', 'birds']),
        lead_cut=int(5000 + 4000 * br),
        room=round(1.0 + 1.2 * m.get('space', 0.5), 2), wet=round(0.12 + 0.1 * m.get('space', 0.5), 3),
        mood={k: m.get(k) for k in ('energy', 'brightness', 'mode', 'space', 'texture', 'matched') if k in m},
    )


def _bars(name, k):
    out = []
    for b in PROGRESSIONS[name]:
        names = b if isinstance(b, tuple) else (b,)
        seg = 4 / len(names)
        out.append([(j * seg, seg, CH[n][0] + k, [x + k for x in CH[n][1]]) for j, n in enumerate(names)])
    return out


def render(p, out_path):
    E.seed(p['seed'])
    random.seed(p['seed'] * 7919 + 5)
    k = p['key']; BPM = p['bpm']; b = 60 / BPM
    pal = PALETTES[p['palette']]
    A = _bars(p['prog'], k); Bb = _bars(p['bridge'], k)
    sect = FORMS[p['form']]
    bars = len(sect); L = int((bars * 4 * b + 7) * SR)
    first = {s: sect.index(s) for s in set(sect)}
    clave = CLAVE if p['clave'] == '3-2' else (CLAVE[1], CLAVE[0])

    def T(bar, beat):
        return (bar * 4 + beat) * b

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

    def seg_at(segs, beat):
        return next(s for s in segs if s[0] <= beat < s[0] + s[1])

    lo = pal['lo'] + k
    scale = [(x + k) % 12 for x in SCALE]
    mg = Melody(random, scale=scale, lo=lo, hi=lo + 14, rhythms=RHYTHMS, endings=ENDINGS)
    a_ch = [pcs(A[j]) for j in range(8)]
    theme = mg.section(a_ch)
    lines = {'A': theme, 'A2': mg.vary(theme, a_ch, bars_to_vary=(3, 6, 7)),
             'B': mg.section([pcs(Bb[j]) for j in range(8)]), 'A3': theme,
             'A4': mg.vary(theme, a_ch, bars_to_vary=(1, 7))}
    sg = Melody(random, scale=scale, lo=lo + 3, hi=lo + 17, rhythms=SOLO_RHYTHMS, endings=ENDINGS)
    solo = []
    for _ in range(sect.count('solo') // 8):
        solo += sg.section(a_ch)

    gtr = []; lead = []; bass = []; drums = []; strings = []; score = []
    pat = COMPS[p['comp']]
    for i, sc in enumerate(sect):
        segs = bar_of(i)
        for beat, beats, root, v in segs:
            score.append(dict(bar=i, start=T(i, beat), end=T(i, beat + beats), pcs=sorted(chord_pcs([root] + v))))
        hits = pat[i % 2] if sc != 'out' else [(0, 4)]
        for pos, l in hits:
            _, _, root, v = seg_at(segs, pos)
            vel = (60 if pos in (0, 2) else 52) + random.randint(-6, 6)
            for j, x in enumerate(v):
                gtr.append((x, T(i, pos) + j * 0.012 + random.uniform(0, 0.008), l * b * 0.9, vel))
        if sc in lines:
            for o, x, l in lines[sc][(i - first[sc]) % 8]:
                lead.append((x, T(i, o) + random.uniform(0, 0.012), l * b * 0.9, 72 + random.randint(-8, 8)))
        if sc == 'solo':
            for o, x, l in solo[i - first['solo']]:
                lead.append((x, T(i, o) + random.uniform(0, 0.01), l * b * 0.85, 66 + random.randint(-10, 8)))
        if pal['strings'] and sc in ('A', 'A3', 'B'):
            _, _, root, v = segs[0]
            for x in v[:3]:
                strings.append((x + 12, T(i, 0), 4 * b + 0.1, 34))
        # bass: root dotted-quarter + eighth, fifth dotted-quarter + eighth (two-feel in intro/outro)
        for beat, dur, iv in ((0, 1.5, 0), (1.5, .5, 0), (2, 1.5, 7), (3.5, .5, 7)):
            if sc in ('intro', 'out') and beat in (1.5, 3.5):
                continue
            _, _, root, _ = seg_at(segs, beat)
            note = 28 + ((root + iv - 28) % 12)
            bass.append((note, T(i, beat), dur * b * 0.92, 86 + (8 if beat == 0 else 0) + random.randint(-6, 4)))
        if sc == 'out':
            continue
        for pos in clave[i % 2]:
            drums.append((RIM, T(i, pos), 0.1, 58 + random.randint(-8, 6)))
        if sc != 'intro':
            for pos in (0, 2):
                drums.append((KICK, T(i, pos), 0.1, 40 + random.randint(-6, 6)))
            drums.append((KICK, T(i, 1.5), 0.1, 30 + random.randint(-6, 6)))
            if p['shaker']:
                for e8 in range(8):
                    drums.append((SHAKER, T(i, e8 / 2), 0.1, (48 if e8 % 2 else 36) + random.randint(-6, 6)))
            elif i % 2 == 0:
                drums.append((CABASA, T(i, 3.5), 0.1, 40))
    end = bars * 4 * b
    root0, v0 = A[0][0][2], A[0][0][3]
    gtr += [(x, end - 4 * b + j * 0.05, 4 * b + 3, 50) for j, x in enumerate(v0)]
    bass.append((28 + ((root0 - 28) % 12), end - 4 * b, 4 * b + 2, 78))

    G = render_midi(gtr, 24, L, BPM, gain=0.6)
    LEAD = render_midi(lead, pal['lead'], L, BPM, gain=0.5)
    BASS = render_midi(bass, 32, L, BPM, gain=0.6)
    DR = render_midi(drums, 0, L, BPM, is_drum=True, gain=0.5)
    STR = render_midi(strings, 49, L, BPM, gain=0.4) if strings else np.zeros((L, 2))
    G = lp(hp(G, 110), 7500); LEAD = lp(LEAD, p['lead_cut']); BASS = lp(BASS, 2200); DR = lp(DR, 9000)
    G = to_db(G, -20); LEAD = to_db(LEAD, -20.5); BASS = to_db(BASS, -20); DR = to_db(DR, -26)
    STR = lp(hp(to_db(STR, -31), 250), 4000) if strings else STR
    # stage: guitar left of centre, lead centre-right, strings wide
    G = np.stack([G[:, 0], G[:, 1] * 0.75], 1); LEAD = np.stack([LEAD[:, 0] * 0.85, LEAD[:, 1]], 1)
    dry = G + LEAD + BASS + DR + STR
    wet = reverb(G * 0.5 + LEAD * 0.8 + DR * 0.3 + STR * 0.9 + BASS * 0.05, decay=p['room'], tone=5500)
    tex = p['texture']
    amb = to_db(texture(tex, L), TEXTURE_DB[tex]) if tex not in (None, 'none') else 0
    mix = dry + wet * p['wet'] + amb
    t = np.arange(L) / SR
    mix *= np.clip(t / 0.5, 0, 1)[:, None] * np.clip((L / SR - t) / 4, 0, 1)[:, None]
    master(mix, out_path, lufs=LUFS)
    return dict(lufs_target=LUFS, beat=b, key_pcs=sorted(scale), chords=score,
                melody=[dict(pitch=x[0], start=x[1], dur=x[2]) for x in lead],
                key_name=(key_name(k, 'A') + 'm') if p['prog'] in MINOR else key_name(k, 'C'), bars=bars)
