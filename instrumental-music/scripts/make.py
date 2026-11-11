#!/usr/bin/env python3
"""Generate instrumental tracks with a fixed-quality preset, QC them, keep the best.

  python make.py --genre lofi --variants 3              # 3 variants, random base seed
  python make.py --genre newage --seed 4242             # reproduce exactly
  python make.py --genre rainy-window                   # approved reference tracks
  python make.py --genre lofi --seed 7 --variants 1 --set bpm=76 key=2 prog=descending
  python make.py --mood "비 오는 새벽, 쓸쓸한데 따뜻하게" --variants 3   # genre inferred from mood
  python make.py --genre newage --mood-set energy=0.2 brightness=0.7 texture=birds palette=harp-flute
  python make.py --genre lofi --bitrate 128k           # smaller mp3 for streaming (same song)

Each variant: plan(seed) -> render -> qc. A failing variant is regenerated with
seed+1000 (deterministic) up to --tries times. Output per variant:
  <genre>_<seed>.mp3, <genre>_<seed>.json (plan, QC metrics, score)
plus report.json ranking the variants (best first).
"""
import argparse, importlib, json, os, random, sys, time
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

GENRES = {  # name -> (preset module, QC profile)
    'lofi': ('presets.lofi', 'lofi'),
    'newage': ('presets.newage', 'newage'),
    'rainy-window': ('presets.rainy_window', 'lofi'),
    'tidewater': ('presets.tidewater', 'newage'),
}


def parse_set(items):
    out = {}
    for it in items or []:
        k, v = it.split('=', 1)
        try:
            v = int(v)
        except ValueError:
            try:
                v = float(v)
            except ValueError:
                pass
        out[k] = v
    return out


def one(genre, seed, outdir, tries, overrides, keep_wav, mood=None):
    import qc
    mod_name, profile = GENRES[genre]
    mod = importlib.import_module(mod_name)
    attempts = []
    s = seed
    for t in range(tries):
        p = mod.plan(s, mood) if mood is not None and not mod_name.endswith(('rainy_window', 'tidewater')) else mod.plan(s)
        p.update(overrides)
        base = os.path.join(outdir, f"{genre}_{p['seed']}")
        t0 = time.time()
        score = mod.render(p, base)
        res = qc.check(base + '.mp3', profile, score)
        if not keep_wav and os.path.exists(base + '.wav'):
            os.remove(base + '.wav')
        info = dict(genre=genre, seed=p['seed'], plan=p, key=score.get('key_name'), bars=score.get('bars'),
                    render_s=round(time.time() - t0, 1), qc=res, mp3=base + '.mp3', score=score)
        json.dump(info, open(base + '.json', 'w'), indent=1)
        attempts.append(dict(seed=p['seed'], passed=res['passed'], score=res['score'],
                             failed=[k for k, v in res['checks'].items() if not v]))
        if res['passed'] or p.get('fixed'):
            break
        if t < tries - 1:
            os.remove(base + '.mp3'); os.remove(base + '.json')
        s += 1000
    info['attempts'] = attempts
    return info


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--genre', default='auto', choices=['auto'] + list(GENRES))
    ap.add_argument('--mood', help='free-text mood (Korean/English), mapped by moods.py')
    ap.add_argument('--mood-set', nargs='*', help='explicit mood axes: energy= brightness= mode= space= texture= palette= prog=')
    ap.add_argument('--seed', type=int, help='base seed (default: random). Same seed -> same track')
    ap.add_argument('--variants', type=int, default=1)
    ap.add_argument('--tries', type=int, default=4, help='regeneration attempts per variant on QC failure')
    ap.add_argument('--out', default='music_out')
    ap.add_argument('--set', nargs='*', help='override plan fields, e.g. bpm=76 key=2 prog=descending')
    ap.add_argument('--keep-wav', action='store_true')
    ap.add_argument('--bitrate', help='mp3 bitrate, e.g. 128k (default 224k or $MUSIC_BITRATE). Same song, smaller file')
    ap.add_argument('--jobs', type=int, default=min(3, os.cpu_count() or 1))
    a = ap.parse_args()
    if a.bitrate:
        os.environ['MUSIC_BITRATE'] = a.bitrate  # inherited by the worker processes
    os.makedirs(a.out, exist_ok=True)
    base = a.seed if a.seed is not None else random.randrange(1, 100000)
    seeds = [base + i for i in range(a.variants)]
    ov = parse_set(a.set)
    import moods
    mood = None
    if a.mood or a.mood_set:
        mood = moods.from_args(a.mood, parse_set(a.mood_set))
        print('mood:', json.dumps({k: v for k, v in mood.items() if v not in (None, [])}, ensure_ascii=False), flush=True)
    if a.genre == 'auto':
        a.genre = (mood or {}).get('genre') or 'lofi'
    print(f"genre={a.genre} seeds={seeds}", flush=True)
    with ProcessPoolExecutor(max_workers=max(1, min(a.jobs, len(seeds)))) as ex:
        results = list(ex.map(one, [a.genre] * len(seeds), seeds, [a.out] * len(seeds), [a.tries] * len(seeds),
                              [ov] * len(seeds), [a.keep_wav] * len(seeds), [mood] * len(seeds)))
    results.sort(key=lambda r: (r['qc']['passed'], r['qc']['score']), reverse=True)
    report = [dict(rank=i + 1, mp3=r['mp3'], seed=r['seed'], passed=r['qc']['passed'], score=r['qc']['score'],
                   key=r['key'], palette=r['plan'].get('palette'), texture=r['plan'].get('texture'),
                   bpm=r['plan'].get('bpm'), prog=r['plan'].get('prog') or r['plan'].get('pair'), plan=r['plan'], attempts=r['attempts'],
                   lufs=r['qc']['metrics']['lufs'], duration_s=round(r['qc']['metrics']['duration_s'], 1))
              for i, r in enumerate(results)]
    json.dump(report, open(os.path.join(a.out, 'report.json'), 'w'), indent=1)
    for r in report:
        flag = 'PASS' if r['passed'] else 'FAIL'
        print(f"#{r['rank']} {flag} score={r['score']:5.1f} seed={r['seed']} key={r['key']} "
              f"{r['bpm']}bpm {r['palette']} {r['texture']} {r['duration_s']}s  {r['mp3']}  tries={len(r['attempts'])}")
    sys.exit(0 if any(r['passed'] for r in report) else 1)


if __name__ == '__main__':
    main()
