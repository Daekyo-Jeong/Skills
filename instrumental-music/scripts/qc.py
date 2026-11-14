"""Automatic quality check for a rendered track.

Usage: python qc.py track.mp3 [--genre lofi|newage] [--score track.json]

Hard checks (any failure -> track rejected and regenerated):
  loudness     integrated LUFS within +-1 LU of the genre target
  true_peak    <= -0.1 dBTP (4x oversampled)
  clipping     < 0.001 % of samples at full scale
  silence      no dead air (>2 s below -50 dBFS) inside the song body
  stereo       L/R correlation > 0.2 (mono-safe)
  dynamics     crest factor and loudness range inside the genre window
  spectrum     low / mid / high energy shares inside the genre window
  harmony      melody notes that rub a semitone against the chord <= 8 %,
               melody notes outside the key <= 5 %
Windows were calibrated on the two approved reference tracks
("Rainy Window", "Tidewater") with a tolerance margin.
"""
import argparse, json, subprocess, sys
import numpy as np
import pyloudnorm as pyln
from scipy.signal import resample_poly, welch

SR = 44100

# Calibrated on the approved references (see references/quality-bar.md)
PROFILES = {
    'lofi':   dict(lufs=-14, crest=(9, 20), lra=(1.5, 12), low=(0.30, 0.80), mid=(0.18, 0.65), high=(0.001, 0.08),
                   dur=(90, 330)),
    'newage': dict(lufs=-15, crest=(10, 22), lra=(1.0, 14), low=(0.15, 0.75), mid=(0.20, 0.80), high=(0.002, 0.08),
                   dur=(90, 360)),
    # drafts: wide windows until a reference track is approved
    'jazz':   dict(lufs=-15, crest=(8, 24), lra=(1.0, 14), low=(0.10, 0.85), mid=(0.10, 0.85), high=(0.001, 0.15),
                   dur=(90, 360)),
    'bossa':  dict(lufs=-15, crest=(8, 24), lra=(1.0, 14), low=(0.10, 0.85), mid=(0.10, 0.85), high=(0.001, 0.15),
                   dur=(90, 360)),
    'chiptune': dict(lufs=-14, crest=(6, 22), lra=(1.0, 14), low=(0.05, 0.85), mid=(0.10, 0.85), high=(0.001, 0.25),
                     dur=(90, 330)),
}


def decode(path):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).astype(np.float64)


def loudness_range(x, meter):
    win, hop = 3 * SR, SR
    st = []
    for s in range(0, len(x) - win, hop):
        v = meter.integrated_loudness(x[s:s + win])
        if np.isfinite(v) and v > -70:
            st.append(v)
    st = np.array(st)
    if len(st) < 3:
        return 0.0
    gated = st[st > (10 * np.log10(np.mean(10 ** (st / 10))) - 20)]
    return float(np.percentile(gated, 95) - np.percentile(gated, 10))


def band_shares(x):
    mono = x.mean(1)
    f, pxx = welch(mono, SR, nperseg=8192)
    tot = pxx[(f >= 20) & (f <= 16000)].sum() + 1e-20
    return (float(pxx[(f >= 20) & (f < 250)].sum() / tot), float(pxx[(f >= 250) & (f < 4000)].sum() / tot),
            float(pxx[(f >= 4000) & (f <= 16000)].sum() / tot))


def harmony(score):
    mel, chords = score.get('melody'), score.get('chords')
    if not mel or not chords:
        return None
    key = set(score['key_pcs'])
    rub = out = 0
    for n in mel:
        ch = next((c for c in chords if c['start'] - 1e-3 <= n['start'] < c['end']), None)
        if ch is None:
            continue
        pcs = set(ch['pcs']); pc = n['pitch'] % 12
        if pc not in pcs and ((pc + 1) % 12 in pcs or (pc - 1) % 12 in pcs) and n['dur'] >= 0.25:
            rub += 1
        if pc not in key:
            out += 1
    return rub / len(mel), out / len(mel)


def check(path, genre, score=None):
    P = PROFILES[genre]
    x = decode(path)
    meter = pyln.Meter(SR)
    m = {}
    m['duration_s'] = len(x) / SR
    m['lufs'] = float(meter.integrated_loudness(x))
    up = resample_poly(x, 4, 1, axis=0)
    m['true_peak_dbtp'] = float(20 * np.log10(np.abs(up).max() + 1e-12))
    m['clip_pct'] = float((np.abs(x) >= 0.999).mean() * 100)
    peak = np.abs(x).max(); rms = np.sqrt((x ** 2).mean())
    m['crest_db'] = float(20 * np.log10(peak / (rms + 1e-12)))
    m['lra_lu'] = loudness_range(x, meter)
    body = x[10 * SR: -10 * SR] if len(x) > 30 * SR else x
    sec = body[: len(body) // SR * SR].reshape(-1, SR, 2)
    sec_db = 20 * np.log10(np.sqrt((sec ** 2).mean((1, 2))) + 1e-12)
    quiet = sec_db < -50; run = best = 0
    for q in quiet:
        run = run + 1 if q else 0; best = max(best, run)
    m['max_silence_s'] = best
    m['stereo_corr'] = float(np.corrcoef(x[:, 0], x[:, 1])[0, 1])
    m['low'], m['mid'], m['high'] = band_shares(x)
    h = harmony(score) if score else None
    if h:
        m['melody_rub_pct'], m['melody_out_of_key_pct'] = h[0] * 100, h[1] * 100

    checks = {
        'loudness': abs(m['lufs'] - P['lufs']) <= 1.0,
        'true_peak': m['true_peak_dbtp'] <= -0.1,
        'clipping': m['clip_pct'] < 0.001,
        'silence': m['max_silence_s'] <= 2,
        'stereo': m['stereo_corr'] > 0.2,
        'duration': P['dur'][0] <= m['duration_s'] <= P['dur'][1],
        'crest': P['crest'][0] <= m['crest_db'] <= P['crest'][1],
        'loudness_range': P['lra'][0] <= m['lra_lu'] <= P['lra'][1],
        'spectrum_low': P['low'][0] <= m['low'] <= P['low'][1],
        'spectrum_mid': P['mid'][0] <= m['mid'] <= P['mid'][1],
        'spectrum_high': P['high'][0] <= m['high'] <= P['high'][1],
    }
    if h:
        checks['harmony_rub'] = m['melody_rub_pct'] <= 8
        checks['harmony_key'] = m['melody_out_of_key_pct'] <= 5
    # 0-100 score: start at 100, subtract distance from window centres (used to rank passing variants)
    def dist(v, lo, hi):
        c, w = (lo + hi) / 2, (hi - lo) / 2
        return min(abs(v - c) / w, 2)
    pen = 10 * abs(m['lufs'] - P['lufs']) + 6 * dist(m['crest_db'], *P['crest']) + 6 * dist(m['lra_lu'], *P['lra'])
    pen += 4 * sum(dist(m[b], *P[b]) for b in ('low', 'mid', 'high'))
    if h:
        pen += 1.5 * m['melody_rub_pct'] + 2 * m['melody_out_of_key_pct']
    pen += 25 * sum(not v for v in checks.values())
    return dict(passed=all(checks.values()), score=round(max(0, 100 - pen), 1), checks=checks,
                metrics={k: round(v, 4) if isinstance(v, float) else v for k, v in m.items()})


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('path'); ap.add_argument('--genre', default='lofi', choices=list(PROFILES))
    ap.add_argument('--score')
    a = ap.parse_args()
    sc = json.load(open(a.score)).get('score') if a.score else None
    r = check(a.path, a.genre, sc)
    print(json.dumps(r, indent=2))
    sys.exit(0 if r['passed'] else 1)
