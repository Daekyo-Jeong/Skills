"""Lo-fi hip hop preset (seeded generator).

Everything that made "Rainy Window" work is fixed here: the sound chain
(EP keys -> band-limit + tape wow + saturation, DSP kick/snare/hat, sub bass,
saw pad, vinyl, sidechain, short room reverb, intro/outro low-pass sweep) and
the stem levels. The seed only picks from curated banks: key, tempo, swing,
progression, form, groove, comp pattern and the melody (built from rules, so
it always fits the chords).
"""
import random
import engine as E
from engine import *  # noqa: F401,F403
from presets.common import Melody, chord_pcs, key_name

# (bass root midi, keys voicing) in C. Pad uses the first three keys tones.
PROGRESSIONS = {
    'ii-V-I-vi': [(38, [53, 57, 60, 64]), (43, [57, 59, 64]), (36, [55, 59, 62]), (45, [60, 64, 67]),
                  (41, [57, 60, 64, 67]), (40, [56, 59, 62, 67]), (45, [60, 64, 67]), (43, [57, 58, 62, 65])],
    'descending': [(41, [57, 60, 64, 67]), (40, [55, 59, 62, 64]), (38, [53, 57, 60, 64]), (36, [52, 55, 59, 62]),
                   (41, [57, 60, 64, 67]), (40, [56, 59, 62, 67]), (45, [55, 59, 60, 64]), (43, [53, 57, 60, 64])],
    'minor-drift': [(45, [55, 59, 60, 64]), (38, [53, 57, 60, 64]), (43, [53, 57, 59, 64]), (36, [52, 55, 59, 62]),
                    (41, [52, 57, 59, 64]), (40, [56, 59, 62, 67]), (45, [55, 59, 60, 64]), (40, [56, 59, 62, 65])],
    'neo-soul': [(36, [52, 55, 59, 62]), (45, [55, 59, 60, 64]), (38, [53, 57, 60, 64]), (43, [53, 57, 59, 64]),
                 (41, [57, 60, 64, 67]), (40, [55, 59, 62, 64]), (38, [53, 57, 60, 64]), (43, [53, 57, 60, 64])],
}
FORMS = {
    'classic': ['intro'] * 4 + ['A'] * 8 + ['B'] * 8 + ['brk'] * 4 + ['A2'] * 8 + ['out'] * 4,
    'straight': ['intro'] * 4 + ['A'] * 8 + ['B'] * 8 + ['A2'] * 8 + ['out'] * 4,
    'long': ['intro'] * 4 + ['A'] * 8 + ['B'] * 8 + ['brk'] * 4 + ['A2'] * 8 + ['B2'] * 8 + ['out'] * 4,
}
KICKS = [([0, 1.75, 2.5], [0, 2.5, 3.25]), ([0, 2.5], [0, 1.5, 2.5]), ([0, 0.75, 2.5], [0, 2.25, 2.75])]
COMPS = [[(0, 1.6, 60), (2.5, 1.2, 50)], [(0, 1.0, 58), (1.5, 0.5, 46), (2.5, 1.4, 52)], [(0, 2.4, 58), (3.5, 0.5, 48)]]
BASSLINES = [lambda i: [(0, 0, 1.4), (2.5, 7 if i % 2 else 0, 0.6), (3.5, 12 if i % 2 else -2, 0.4)],
             lambda i: [(0, 0, 2.3), (3, 7, 0.8)],
             lambda i: [(0, 0, 1.4), (1.75, 0, 0.4), (2.5, 7, 1.2)]]
RHYTHMS = [[(0, 1), (1, .5), (1.5, 1), (3, 1)], [(0.5, .5), (1, .5), (1.5, 1.5), (3.5, .5)],
           [(0, 1.5), (1.5, .5), (2, 1), (3, 1)], [(0, .5), (.5, .5), (1, 1), (2, .5), (2.5, 1.5)],
           [(0, 2), (2, 1), (3, 1)], [(1, .5), (1.5, .5), (2, 2)], [(0, 1), (1.5, .5), (2, .5), (2.5, 1.5)]]
ENDINGS = [[(0, 3)], [(0, 2), (2, 1.5)], [(0.5, .5), (1, 2.5)]]
PENT = [0, 2, 4, 7, 9]   # C major pentatonic (relative to key)
SCALE = [0, 2, 4, 5, 7, 9, 11]
LUFS = -14


def plan(seed):
    r = random.Random(seed)
    return dict(
        seed=seed,
        key=r.choice([-4, -3, -2, 0, 0, 2, 3]),
        bpm=r.randint(70, 82),
        swing=round(r.uniform(0.05, 0.09), 3),
        prog=r.choice(list(PROGRESSIONS)),
        form=r.choice(['classic', 'classic', 'straight', 'long']),
        kick=r.randrange(len(KICKS)), comp=r.randrange(len(COMPS)), bassline=r.randrange(len(BASSLINES)),
        keys_prog=r.choice([4, 4, 4, 0]), mel_prog=r.choice([0, 0, 0, 11]),
        vinyl=r.randint(4, 7),
    )


def render(p, out_path):
    E.seed(p['seed'])
    random.seed(p['seed'] * 7919 + 1)
    k = p['key']; BPM = p['bpm']; b = 60 / BPM; SW = p['swing']
    prog = [(root + k, [x + k for x in ks]) for root, ks in PROGRESSIONS[p['prog']]]
    sect = FORMS[p['form']]
    bars = len(sect); L = int((bars * 4 * b + 6) * SR)

    def T(bar, beat):
        sw = SW if (round(beat * 2) % 2 == 1) else 0
        return (bar * 4 + beat + sw) * b

    # ---- melody (rule-based, chord aware) ----
    chords = [chord_pcs([root] + ks) for root, ks in prog]
    mel_gen = Melody(random, scale=[(x + k) % 12 for x in PENT], lo=69 + k, hi=81 + k,
                     rhythms=RHYTHMS, endings=ENDINGS)
    first = {s: sect.index(s) for s in set(sect)}
    aligned = lambda sc: [chords[(first[sc] + j) % 8] for j in range(8)]
    theme = mel_gen.section(aligned('B'))
    lines = {'B': theme}
    if 'B2' in first: lines['B2'] = mel_gen.refit(theme, aligned('B2'))
    lines['A2'] = mel_gen.vary(mel_gen.refit(theme, aligned('A2')), aligned('A2'), bars_to_vary=(1, 5, 7))

    keys = []; mel = []; score = []
    for i, sc in enumerate(sect):
        root, ch = prog[i % 8]
        hits = COMPS[p['comp']] if sc != 'brk' else [(0, 3.8, 52)]
        for pos, l, v in hits:
            for j, pp in enumerate(ch):
                keys.append((pp, T(i, pos) + j * 0.018 + random.uniform(0, 0.01), l * b, v + random.randint(-6, 6)))
        score.append(dict(bar=i, start=i * 4 * b, end=(i + 1) * 4 * b, pcs=sorted(chords[i % 8])))
        if sc in ('B', 'A2', 'B2'):
            for o, pp, l in lines[sc][(i - first[sc]) % 8]:
                mel.append((pp, T(i, o), l * b * 0.95, 70 + random.randint(-8, 8)))
    end = bars * 4 * b
    keys += [(x, end, 4, 48) for x in prog[0][1]]
    K = render_midi(keys, p['keys_prog'], L, BPM, gain=0.55)
    M = render_midi(mel, p['mel_prog'], L, BPM, gain=0.45)
    K = wow_flutter(saturate(lp(hp(K, 120), 4200), 1.8), 1.6, 0.45)
    M = wow_flutter(saturate(lp(M, 5000), 1.4), 1.2, 0.5)

    drums = np.zeros((L, 2)); bass = np.zeros((L, 2)); pad = np.zeros((L, 2)); kicks = []
    for i, sc in enumerate(sect):
        root, ch = prog[i % 8]
        if sc in ('A', 'B', 'A2', 'B2'):
            for pos in KICKS[p['kick']][i % 2]:
                place(drums, lofi_kick(), T(i, pos), 0.9); kicks.append(T(i, pos))
            for pos in (1, 3): place(drums, lofi_snare(), T(i, pos) + 0.012, 0.55, 0.52)
            for e in range(8):
                if random.random() < 0.92: place(drums, lofi_hat(), T(i, e / 2), 0.35 + 0.15 * (e % 2 == 0), 0.62)
            if i % 4 == 3: place(drums, lofi_hat(True), T(i, 3.5), 0.35, 0.62)
            for pos, iv, l in BASSLINES[p['bassline']](i):
                place(bass, sub_bass(root + iv, l * b), T(i, pos), 0.9)
        if sc != 'intro':
            for x in ch[:3]: place(pad, pad_voice(x + 12, 4 * b, bright=900, a=1.0, r=2.0), i * 4 * b, 0.07, 0.3 + 0.4 * random.random())
        else:
            for x in ch[:3]: place(pad, pad_voice(x + 12, 4 * b, bright=500, a=1.5, r=2.0), i * 4 * b, 0.05, 0.5)
    drums = lp(drums, 7500); drums = saturate(drums, 2.0)
    sc_gain = sidechain(L, kicks, 0.35, 0.3)
    K = to_db(K, -21); M = to_db(M, -23); drums = to_db(drums, -19.5); bass = to_db(bass, -21); pad = to_db(pad, -29)
    dry = K * sc_gain + M + drums + bass + pad * sc_gain
    wet = reverb(K * 0.5 + M * 0.7 + pad * 0.8 + drums * 0.12, decay=2.2, tone=4000)
    mix = dry + wet * 0.28 + to_db(st(vinyl(L, p['vinyl'])), -42)
    t = np.arange(L) / SR; intro_end = 4 * 4 * b; out_start = sect.index('out') * 4 * b
    filt = lp(mix, 900, 2); w = np.clip(t / intro_end, 0, 1) ** 2
    w = np.where(t > out_start, np.clip(1 - (t - out_start) / (4 * 4 * b), 0, 1), w)[:, None]
    mix = mix * w + filt * (1 - w)
    mix *= np.clip((L / SR - t) / 5, 0, 1)[:, None]
    master(mix, out_path, lufs=LUFS)
    melody_events = [dict(pitch=x[0], start=x[1], dur=x[2]) for x in mel]
    return dict(lufs_target=LUFS, beat=b, key_pcs=sorted((x + k) % 12 for x in SCALE),
                chords=score, melody=melody_events, key_name=key_name(k, 'C'), bars=bars)
