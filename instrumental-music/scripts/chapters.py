"""Chapters: per-section mood changes inside one song.

A chapter is a small change on top of the song's mood, applied to one main section
(A, B, A2, B2 — never intro/out). A short break (brk) has no melody or drums of its own,
so it carries on the chapter before it instead of using one up. The song keeps one key, tempo, progression and
palette so it still sounds like one piece; chapters only move:

  energy      -0.3..0.3   drum/comp density (delta on the song's energy)
  brightness  -0.3..0.3   tone: low-pass when negative, air when positive
  space       -0.3..0.3   reverb send
  texture     vinyl|rain|fire|birds|night|ocean|none|None   extra ambience for this chapter
  lead        piano|rhodes|musicbox|vibes|marimba|guitar|harp|choir|trumpet|oboe|clarinet|flute|kalimba|None
  drums       full|light|off|None   (None: follows energy)
  label       free text, kept for the timeline (e.g. the pieces this chapter stands for)

Chapters are listed in song order. More chapters than body sections are merged
(neighbours share a section); fewer are stretched. make.py --chapters takes a JSON list.
"""
import numpy as np

DELTA = 0.3
LEADS = {'piano': 0, 'rhodes': 4, 'musicbox': 10, 'vibes': 11, 'marimba': 12, 'guitar': 24, 'harp': 46,
         'choir': 52, 'trumpet': 59, 'oboe': 68, 'clarinet': 71, 'flute': 73, 'kalimba': 108}
TEXTURES = ('vinyl', 'rain', 'fire', 'birds', 'night', 'ocean', 'none')
DRUMS = ('full', 'light', 'off')
MAX = 8
EDGE = ('intro', 'out')
CARRY = ('brk',)


def _num(v):
    try:
        return round(max(-DELTA, min(DELTA, float(v))), 3)
    except (TypeError, ValueError):
        return 0.0


def clean(chapters):
    """Validate a chapter list (anything outside the vocabulary is dropped). None/[] -> []."""
    out = []
    for c in (chapters or [])[:MAX]:
        if not isinstance(c, dict):
            continue
        out.append(dict(
            energy=_num(c.get('energy', 0)), brightness=_num(c.get('brightness', 0)), space=_num(c.get('space', 0)),
            texture=c.get('texture') if c.get('texture') in TEXTURES else None,
            lead=c.get('lead') if c.get('lead') in LEADS else None,
            drums=c.get('drums') if c.get('drums') in DRUMS else None,
            label=str(c.get('label') or '')[:80],
        ))
    return out


def runs(sect):
    """Per-bar section names -> [(name, first_bar, end_bar)] contiguous runs."""
    out = []
    for i, s in enumerate(sect):
        if out and out[-1][0] == s:
            out[-1] = (s, out[-1][1], i + 1)
        else:
            out.append((s, i, i + 1))
    return out


def _merge(group):
    if len(group) == 1:
        return dict(group[0])
    first = lambda k: next((c[k] for c in group if c[k]), None)
    drums = [c['drums'] for c in group if c['drums']]
    return dict(
        energy=round(sum(c['energy'] for c in group) / len(group), 3),
        brightness=round(sum(c['brightness'] for c in group) / len(group), 3),
        space=round(sum(c['space'] for c in group) / len(group), 3),
        texture=first('texture'), lead=first('lead'),
        drums=('off' if 'off' in drums and len(set(drums)) == 1 else 'light' if 'light' in drums or 'off' in drums else
               'full' if drums else None),
        label=' / '.join(c['label'] for c in group if c['label']),
    )


def assign(sect, chapters):
    """-> (per-bar chapter dict or None, timeline). Timeline: one entry per body section."""
    chapters = clean(chapters)
    per_bar = [None] * len(sect)
    if not chapters:
        return per_bar, []
    every = [r for r in runs(sect) if r[0] not in EDGE]
    main = [r for r in every if r[0] not in CARRY]
    n, m = len(chapters), len(main)
    timeline = []
    prev = None
    for name, a, b in every:
        if name in CARRY:
            if prev is None:
                continue
            idx, ch = prev
        else:
            s = main.index((name, a, b))
            lo, hi = s * n // m, max(s * n // m + 1, (s + 1) * n // m)
            idx = list(range(lo, min(hi, n)))
            ch = _merge([chapters[j] for j in idx])
            prev = (idx, ch)
        for i in range(a, b):
            per_bar[i] = ch
        timeline.append(dict(section=name, bars=[a, b], chapters=idx, label=ch['label']))
    return per_bar, timeline


def env(values, bar_s, length, sr):
    """Per-bar values -> per-sample envelope (L, 1). Holds inside a bar run, ramps over one bar at changes."""
    t = np.arange(length) / sr
    centers = (np.arange(len(values)) + 0.5) * bar_s
    return np.interp(t, centers, np.asarray(values, dtype=float))[:, None]
