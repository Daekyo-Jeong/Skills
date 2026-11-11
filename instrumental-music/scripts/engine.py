"""Hybrid renderer: MIDI parts -> FluidSynth stems, DSP parts -> numpy, then mix/master.

Sound-design code is kept identical to the engine that produced the reference
tracks "Rainy Window" (lo-fi) and "Tidewater" (new age). Only plumbing changed:
seedable RNG, SoundFont discovery, output directory, and master() returning data
for the quality checker.
"""
import os, shutil, subprocess, tempfile
import numpy as np, pretty_midi as pm
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR = 44100
_SF_CANDIDATES = [
    os.environ.get("MUSIC_SF2", ""),
    os.path.expanduser("~/.claude/soundfonts/default.sf2"),
    "/usr/share/sounds/sf2/FluidR3_GM.sf2",
    "/opt/homebrew/share/soundfonts/default.sf2",
    "/usr/local/share/soundfonts/default.sf2",
    "/opt/homebrew/share/fluid-synth/sf2/FluidR3_GM.sf2",
]


def find_soundfont():
    for p in _SF_CANDIDATES:
        if p and os.path.isfile(p):
            return p
    raise SystemExit(
        "SoundFont not found. Set MUSIC_SF2=/path/to/GM.sf2 "
        "(Linux: apt install fluid-soundfont-gm, macOS: see SKILL.md setup)."
    )


SF = None
rng = np.random.default_rng(11)


def seed(n):
    """Reset the DSP noise RNG (vinyl, hats, reverb IR...). Same seed -> same audio."""
    global rng
    rng = np.random.default_rng(n)


def mtof(m): return 440 * 2 ** ((m - 69) / 12)


# ---------- filters ----------
def _sos(kind, fc, o=2): return butter(o, np.clip(np.array(fc) / (SR / 2), 1e-4, 0.999), kind, output='sos')
def lp(x, fc, o=2): return sosfilt(_sos('low', fc, o), x, axis=0)
def hp(x, fc, o=2): return sosfilt(_sos('high', fc, o), x, axis=0)
def bp(x, lo, hi, o=2): return sosfilt(_sos('band', [lo, hi], o), x, axis=0)
def st(x): return np.stack([x, x], 1) if x.ndim == 1 else x
def pan(x, p):  # p 0..1
    return np.stack([x * np.cos(p * np.pi / 2), x * np.sin(p * np.pi / 2)], 1)


# ---------- MIDI stems via FluidSynth ----------
def render_midi(notes, program, length, bpm=90, is_drum=False, gain=0.5):
    """notes: list of (pitch,start_s,dur_s,vel)"""
    global SF
    SF = SF or find_soundfont()
    m = pm.PrettyMIDI(initial_tempo=bpm); ins = pm.Instrument(program=program, is_drum=is_drum)
    for p, s, d, v in notes:
        ins.notes.append(pm.Note(velocity=int(np.clip(v, 1, 127)), pitch=int(p), start=s, end=s + d))
    m.instruments.append(ins)
    d = tempfile.mkdtemp(); mid = os.path.join(d, 'a.mid'); wav = os.path.join(d, 'a.wav'); m.write(mid)
    r = subprocess.run(['fluidsynth', '-ni', '-R', '0', '-C', '0', '-g', str(gain), '-r', str(SR), '-F', wav, SF, mid],
                       capture_output=True)
    if not os.path.exists(wav):
        raise RuntimeError("fluidsynth failed: " + r.stderr.decode(errors='ignore')[-400:])
    sr, x = wavfile.read(wav); x = x.astype(np.float32) / 32768
    shutil.rmtree(d, ignore_errors=True)
    out = np.zeros((length, 2)); n = min(length, len(x)); out[:n] = x[:n]; return out


# ---------- DSP voices ----------
def adsr(n, a, d, s, r):
    A = int(a * SR); D = int(d * SR); R = int(r * SR); S = max(0, n - A - D - R)
    e = np.concatenate([np.linspace(0, 1, A, False), np.linspace(1, s, D, False), np.full(S, s), np.linspace(s, 0, R)])
    return np.pad(e, (0, max(0, n - len(e))))[:n]
def saw(f, n, ph=None):
    ph = rng.random() if ph is None else ph; t = np.arange(n) / SR; return 2 * ((t * f + ph) % 1) - 1
def pad_voice(p, dur, bright=1200, detune=0.007, a=1.5, r=2.5, voices=4):
    n = int((dur + r) * SR); x = np.zeros(n)
    for k in range(voices):
        d = (k - (voices - 1) / 2) * detune; x += saw(mtof(p) * (1 + d), n)
    x /= voices
    y = lp(x, bright, 2)
    return y * adsr(n, a, 0.5, 0.85, r)
def sine_pad(p, dur, a=2.5, r=4):
    n = int((dur + r) * SR); t = np.arange(n) / SR; f = mtof(p)
    x = sum(np.sin(2 * np.pi * f * h * (1 + 0.0015 * np.sin(2 * np.pi * 0.2 * t + h)) * t) / h ** 1.5 for h in (1, 2, 3, 4))
    return x * adsr(n, a, 1, 0.8, r) * 0.5
def fm_bell(p, dur=4, idx=3.5, ratio=3.5):
    n = int(dur * SR); t = np.arange(n) / SR; f = mtof(p)
    env = np.exp(-t * 1.2); ienv = np.exp(-t * 3)
    return np.sin(2 * np.pi * f * t + idx * ienv * np.sin(2 * np.pi * f * ratio * t)) * env * 0.6
def sub_bass(p, dur):
    n = int(dur * SR); t = np.arange(n) / SR; f = mtof(p)
    x = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)
    return np.tanh(1.6 * x) * adsr(n, 0.01, 0.2, 0.75, 0.08) * 0.6
def lofi_kick():
    n = int(0.5 * SR); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * (48 * t + 70 * (1 - np.exp(-t * 25)) / 25)) * np.exp(-t * 7)
    click = lp(rng.standard_normal(n), 3000) * np.exp(-t * 200) * 0.3
    return np.tanh(2 * (x + click)) * 0.8
def lofi_snare():
    n = int(0.35 * SR); t = np.arange(n) / SR
    nz = bp(rng.standard_normal(n), 900, 5000) * np.exp(-t * 16)
    body = np.sin(2 * np.pi * 180 * t) * np.exp(-t * 25) * 0.5
    return (nz * 0.7 + body) * 0.7
def lofi_hat(open_=False):
    n = int((0.25 if open_ else 0.06) * SR); t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 7000, 2) * np.exp(-t * (12 if open_ else 70)) * 0.35
def vinyl(n, density=6):
    x = hp(rng.standard_normal(n), 3000, 1) * 0.004          # surface hiss
    pops = np.zeros(n); idx = rng.integers(0, n, int(n / SR * density))
    pops[idx] = rng.uniform(0.05, 0.35, len(idx)) * rng.choice([-1, 1], len(idx))
    pops = lp(fftconvolve(pops, np.exp(-np.arange(60) / 8))[:n], 6000)
    hum = 0.0015 * np.sin(2 * np.pi * 60 * np.arange(n) / SR)
    return x + pops * 0.5 + hum
def wind(n, lo=200, hi=900):
    x = rng.standard_normal(n); t = np.arange(n) / SR
    sweep = 0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * t)
    a = bp(x, lo, hi, 2); b = bp(x, lo * 2, hi * 2, 2)
    return (a * (1 - sweep) + b * sweep) * 0.08


# ---------- FX ----------
def reverb(x, decay=2.5, tone=5000, predelay=0.02):
    n = int(decay * 1.5 * SR); t = np.arange(n) / SR
    ir = np.stack([lp(rng.standard_normal(n), tone) * np.exp(-t * 6.9 / decay) for _ in range(2)], 1)
    ir = np.concatenate([np.zeros((int(predelay * SR), 2)), ir]); ir /= np.sqrt((ir ** 2).sum(0))
    x = st(x); return np.stack([fftconvolve(x[:, c], ir[:, c])[:len(x)] for c in range(2)], 1)
def wow_flutter(x, depth_ms=1.2, rate=0.5, flutter_ms=0.15, frate=6.0):
    x = st(x); n = len(x); t = np.arange(n) / SR
    d = (depth_ms * np.sin(2 * np.pi * rate * t) + flutter_ms * np.sin(2 * np.pi * frate * t)) * SR / 1000 + depth_ms * SR / 1000 + 2
    idx = np.clip(np.arange(n) - d, 0, n - 1); i0 = idx.astype(int); fr = idx - i0; i1 = np.minimum(i0 + 1, n - 1)
    return x[i0] * (1 - fr)[:, None] + x[i1] * fr[:, None]
def saturate(x, drive=1.5): return np.tanh(x * drive) / np.tanh(drive)
def sidechain(length, hits, depth=0.5, release=0.25):
    g = np.ones(length); r = np.linspace(0, 1, int(release * SR)) ** 0.6
    for h in hits:
        s = int(h * SR); e = min(length, s + len(r)); g[s:e] = np.minimum(g[s:e], 1 - depth * (1 - r[:e - s]))
    return g[:, None]
def place(buf, x, t, gain=1.0, p=0.5):
    x = pan(x, p) if x.ndim == 1 else x
    s = int(t * SR); e = min(len(buf), s + len(x))
    if e > s: buf[s:e] += x[:e - s] * gain


def master(x, path, lufs=-14, lowcut=30, bitrate='224k'):
    """Write <path>.wav (pre-loudnorm, peak-normalised) and <path>.mp3 (compressed + loudnorm).
    Returns the peak-normalised float mix for QC."""
    x = hp(x, lowcut, 2); x = saturate(x, 1.2); x /= np.abs(x).max() * 1.02
    wavfile.write(path + '.wav', SR, (x * 32767).astype(np.int16))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', path + '.wav', '-af',
                    f'acompressor=threshold=-16dB:ratio=2.5:attack=20:release=200,loudnorm=I={lufs}:TP=-1.0',
                    '-ar', str(SR), '-b:a', bitrate, path + '.mp3'], check=True)
    return x


def rms_db(x):
    a = np.abs(st(x)).max(1); act = a > 1e-4
    return 20 * np.log10(np.sqrt((st(x)[act] ** 2).mean()) + 1e-12) if act.any() else -120
def to_db(x, target):
    """scale stem so its RMS over active samples equals target dBFS"""
    return x * 10 ** ((target - rms_db(x)) / 20)
