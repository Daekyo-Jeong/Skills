"""Mood -> generation axes.

A mood is a small dict of axes the presets understand:
  energy      0..1   tempo, groove density, drum presence
  brightness  0..1   register, filter cut-offs, palette choice
  mode        'major' | 'minor' | None (either)
  space       0..1   reverb size / wetness
  texture     'vinyl' | 'rain' | 'fire' | 'birds' | 'night' | 'ocean' | 'none' | None (genre default)
  palette     instrument palette name or None (picked from energy/brightness)
  genre       'lofi' | 'newage' | 'jazz' | 'chiptune' | None (inferred)

parse() turns free text (Korean or English) into these axes with a keyword
lexicon. Claude can also pass the axes explicitly (--set energy=0.3 ...), which
is more precise; see references/moods.md.
"""
import re

DEFAULT = dict(energy=0.5, brightness=0.5, mode=None, space=0.5, texture=None, palette=None, genre=None,
               prog=None)

# (keywords, adjustments). Numbers are deltas for energy/brightness/space; strings are set.
LEXICON = [
    (['잔잔', '차분', 'calm', 'chill', 'relax', '휴식', '쉬는'], dict(energy=-0.25, space=+0.1)),
    (['잠들', '잘 때', '수면', 'sleep', '자장가', 'lullaby'], dict(energy=-0.4, brightness=-0.15, space=+0.2, palette_hint='soft')),
    (['신나', '경쾌', 'upbeat', 'energetic', '활기', 'groovy', '그루브'], dict(energy=+0.3, brightness=+0.15)),
    (['집중', 'focus', 'study', '공부', '작업', 'work', 'coding', '코딩'], dict(energy=-0.05, genre='lofi')),
    (['슬픈', '슬프', 'sad', 'melanchol', '우울', '쓸쓸', '외로', 'lonely', '그리움', '그리운', '이별', '눈물'],
     dict(mode='minor', brightness=-0.25, energy=-0.1)),
    (['향수', 'nostalg', '추억', '회상', '옛날'], dict(brightness=-0.1, texture='vinyl')),
    (['따뜻', '포근', 'warm', 'cozy', '아늑'], dict(brightness=-0.1, palette_hint='warm')),
    (['밝', 'bright', 'happy', '행복', '희망', 'hope', '설레', '기분 좋'], dict(mode='major', brightness=+0.3)),
    (['아침', 'morning', '봄', 'spring', '햇살', 'sunny', 'sunrise', '일출'], dict(brightness=+0.25, texture='birds', mode='major')),
    (['숲', 'forest', '새소리', 'bird', '자연', 'nature', '산책'], dict(texture='birds')),
    (['밤', 'night', '새벽', 'midnight', '달빛', 'moon', '자정'], dict(brightness=-0.15, energy=-0.1, texture='night')),
    (['비 ', '비가', '비오', '비 오', 'rain', '장마', '빗소리'], dict(texture='rain', brightness=-0.1)),
    (['바다', 'ocean', 'sea', '파도', 'wave', '해변', 'beach'], dict(texture='ocean')),
    (['벽난로', 'fireplace', 'fire', '겨울', 'winter', '캠프', 'camp', '장작'], dict(texture='fire', palette_hint='warm')),
    (['꿈', 'dream', '몽환', 'ethereal', '신비', '우주', 'space', '별빛', 'stars'], dict(space=+0.3, palette_hint='dream')),
    (['웅장', 'cinematic', '광활', 'epic', '시네마'], dict(space=+0.3, energy=+0.1)),
    (['명상', 'meditat', '요가', 'yoga', '힐링', 'healing', '치유', 'spa', '스파'],
     dict(genre='newage', energy=-0.35, space=+0.3)),
    (['로파이', '로우파이', 'lofi', 'lo-fi', '힙합', 'hiphop', 'hip hop', 'beats'], dict(genre='lofi')),
    (['뉴에이지', 'new age', 'newage', 'ambient', '앰비언트', '피아노 솔로'], dict(genre='newage')),
    (['카페', 'cafe', 'café'], dict(genre='lofi', prog='neo-soul', palette='rhodes-piano')),
    (['재즈', 'jazz', '스윙', 'swing', '브러시', '트리오', 'trio', '색소폰', 'sax'], dict(genre='jazz')),
    (['칩튠', 'chiptune', '8bit', '8비트', '8-bit', '레트로 게임', '게임기', '픽셀', 'pixel', '오락실'], dict(genre='chiptune')),
    (['기타', 'guitar'], dict(palette_hint='guitar')),
    (['하프', 'harp'], dict(palette_hint='harp')),
    (['플루트', 'flute'], dict(palette_hint='flute')),
    (['오르골', 'music box', 'musicbox'], dict(palette_hint='musicbox')),
    (['비브라폰', 'vibes', 'vibraphone'], dict(palette_hint='vibes')),
    (['로즈', 'rhodes', '일렉피아노', 'electric piano'], dict(palette_hint='rhodes')),
    (['합창', 'choir', '보이스', 'voice'], dict(palette_hint='choir')),
    (['트럼펫', 'trumpet'], dict(palette_hint='trumpet')),
    (['클라리넷', 'clarinet'], dict(palette_hint='clarinet')),
    (['오보에', 'oboe', '목가', 'pastoral', '전원'], dict(palette_hint='oboe')),
    (['마림바', 'marimba'], dict(palette_hint='marimba')),
    (['칼림바', 'kalimba'], dict(palette_hint='kalimba')),
    (['단조', 'minor'], dict(mode='minor')),
    (['장조', 'major'], dict(mode='major')),
]


def parse(text):
    t = ' ' + text.lower() + ' '
    m = dict(DEFAULT); hints = []; hits = []
    # Apply matches in the order they appear in the text, so a later mention wins a conflict
    # ("바다 여행 중 비 오는 밤" -> rain, not ocean). Lexicon order only breaks ties.
    found = []
    for i, (words, adj) in enumerate(LEXICON):
        pos = [t.rfind(w) for w in words if w in t]
        if pos:
            found.append((max(pos), i, words, adj))
    for _, _, words, adj in sorted(found, key=lambda f: f[:2]):
        hits.append(words[0])
        for k, v in adj.items():
            if k == 'palette_hint':
                hints.append(v)
            elif isinstance(v, (int, float)) and k in ('energy', 'brightness', 'space'):
                m[k] += v
            else:
                m[k] = v
    for k in ('energy', 'brightness', 'space'):
        m[k] = round(min(1.0, max(0.0, m[k])), 2)
    m['hints'] = hints
    m['matched'] = hits
    if m['genre'] is None:
        m['genre'] = 'newage' if (m['texture'] == 'ocean' or 'dream' in hints or 'harp' in hints) else 'lofi'
    return m


def from_args(text=None, overrides=None):
    m = parse(text) if text else dict(DEFAULT, hints=[], matched=[])
    for k, v in (overrides or {}).items():
        if k in m or k in DEFAULT:
            m[k] = v
    return m


def pick_palette(r, palettes, mood):
    """palettes: {name: dict(bright=(lo,hi), energy=(lo,hi), tags=[...])}. Prefer hint tags, then axis fit."""
    if mood.get('palette') in palettes:
        return mood['palette']
    hints = set(mood.get('hints') or [])
    names = list(palettes)
    tagged = [n for n in names if hints & set(palettes[n].get('tags', []))]
    pool = tagged or names
    def fit(n):
        p = palettes[n]; b, e = mood['brightness'], mood['energy']
        return (p['bright'][0] <= b <= p['bright'][1]) + (p['energy'][0] <= e <= p['energy'][1])
    best = max(fit(n) for n in pool)
    return r.choice([n for n in pool if fit(n) == best])


if __name__ == '__main__':
    import sys, json
    print(json.dumps(parse(' '.join(sys.argv[1:])), ensure_ascii=False, indent=1))
