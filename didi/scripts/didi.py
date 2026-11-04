"""디디 도트 그림 도구. 의존성 없이 돈다(PNG·GIF만 Pillow 필요).

그림은 문자열 줄 목록이다. 한 글자가 한 칸이고 '.'은 빈칸, 나머지는 팔레트 키다.

  python3 didi.py check                         원본 데이터 규칙 검사
  python3 didi.py list                          쓸 수 있는 그림 이름
  python3 didi.py svg front out.svg --scale 10  한 장을 SVG로
  python3 didi.py png three out.png --scale 10  한 장을 PNG로 (Pillow)
  python3 didi.py gif motions.walk out.gif      모션을 GIF로 (Pillow)
  python3 didi.py json front                    줄 목록 JSON (웹 코드에 붙일 때)

이름: body.<front|three|back|…>, hands.<기본|…>, faces.<rest|…>, hobbies.<fishing|…>, motions.<walk|…>
'body.'는 생략해도 된다(front == body.front).
"""
import json
import os
import sys

DATA = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'didi.json'), encoding='utf-8'))
PAL = DATA['pal']
BODY = DATA['body']
FRONT, THREE, BACK = BODY['front'], BODY['three'], BODY['back']


def get(name):
    """'front', 'faces.rest', 'motions.walk' 같은 이름으로 그림(또는 모션)을 꺼낸다"""
    group, _, key = name.rpartition('.')
    item = DATA[group or 'body'][key]
    return item['rows'] if isinstance(item, dict) and 'rows' in item else item


# 몸 변형. 몸 그림 자체는 고치지 않고 이 함수들로만 바꾼다

def flip(rows):
    """좌우 반전. 반측면을 왼쪽으로 돌릴 때 쓴다"""
    return [r[::-1] for r in rows]


def squash(rows):
    """7행을 빼서 한 칸 눌린다. 착지·숨 고르기"""
    return rows[:7] + rows[8:]


def stretch(rows):
    """7행을 한 번 더 넣어 한 칸 늘어난다. 도약"""
    return rows[:7] + [rows[7]] + rows[7:]


def shut(rows):
    """눈 감기. 안경 렌즈 가운데가 어두운 초록으로 꺼진다"""
    return [r.replace('kggk', 'keek') for r in rows]


def lift_leg(rows, side):
    """정면 몸의 한쪽 발을 든다. 걷기"""
    rows = list(rows)
    last = rows[-1]
    rows[-1] = '.....' + last[5:] if side == 'left' else last[:15] + '.....'
    return rows


def hands(left=9, right=9, body=None):
    """양손을 몸 옆선의 원하는 줄에 붙인다. 숫자는 손 윗줄, 5(어깨)부터 10(허리)까지. 정면 몸 전용"""
    rows = [list(r) for r in (body or FRONT)]
    for y in (9, 10):
        rows[y][1] = rows[y][18] = '.'
    for top, mirrored in ((left, False), (right, True)):
        for y in (top, top + 1):
            line_ = rows[y][::-1] if mirrored else rows[y]
            edge = next(i for i, c in enumerate(line_) if c != '.')
            line_[edge - 1] = 'g'
            if mirrored:
                rows[y] = line_[::-1]
    return [''.join(r) for r in rows]


# 장면 조립

def blank(w, h):
    return ['.' * w] * h


def stamp(rows, glyph, gx, gy):
    """glyph를 (gx, gy)에 덮어 찍는다. 넘치는 칸은 잘린다"""
    out = [list(r) for r in rows]
    for y, row in enumerate(glyph):
        for x, c in enumerate(row):
            if c != '.' and 0 <= gy + y < len(out) and 0 <= gx + x < len(out[0]):
                out[gy + y][gx + x] = c
    return [''.join(r) for r in out]


def pad(rows, top=0, bottom=0, left=0, right=0):
    w = len(rows[0]) + left + right
    return ['.' * w] * top + ['.' * left + r + '.' * right for r in rows] + ['.' * w] * bottom


def line(rows, x0, y0, x1, y1, c):
    out = [list(r) for r in rows]
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        x, y = round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)
        if 0 <= y < len(out) and 0 <= x < len(out[0]):
            out[y][x] = c
    return [''.join(r) for r in out]


# 출력

def to_svg(rows, scale=10, pal=None):
    """가로로 같은 색이 이어지는 칸을 한 rect로 묶은 SVG. crispEdges로 흐리지 않게 그린다"""
    pal = pal or PAL
    w, h = max(len(r) for r in rows), len(rows)
    rects = []
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            c = row[x]
            n = 1
            while x + n < len(row) and row[x + n] == c:
                n += 1
            if c != '.':
                rects.append(f'<rect x="{x}" y="{y}" width="{n}" height="1" fill="{pal[c]}"/>')
            x += n
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w * scale}" height="{h * scale}" '
            f'shape-rendering="crispEdges">{"".join(rects)}</svg>')


def to_image(rows, scale=10, pal=None):
    from PIL import Image
    pal = pal or PAL
    w = max(len(r) for r in rows)
    im = Image.new('RGBA', (w, len(rows)), (0, 0, 0, 0))
    for y, row in enumerate(rows):
        for x, c in enumerate(row):
            if c != '.':
                hx = pal[c].lstrip('#')
                im.putpixel((x, y), tuple(int(hx[i:i + 2], 16) for i in (0, 2, 4)) + (255,))
    return im.resize((w * scale, len(rows) * scale), Image.NEAREST)


def save_gif(frames, ms, path, scale=6, bg=(0, 0, 0, 255)):
    from PIL import Image
    images = []
    for f in frames:
        im = to_image(f, scale)
        base = Image.new('RGBA', im.size, bg)
        base.alpha_composite(im)
        images.append(base.convert('P'))
    images[0].save(path, save_all=True, append_images=images[1:], duration=ms, loop=0, disposal=2)


def check():
    """원본 데이터가 디디 규칙을 지키는지 본다. 하나라도 어기면 AssertionError"""
    for k in ('front', 'back'):
        assert len(BODY[k]) == 14 and all(len(r) == 20 for r in BODY[k]), k
    assert len(THREE) == 14 and all(len(r) == 22 for r in THREE), 'three는 20칸 정면 + 옆면 띠 2칸'
    # 반측면은 정면을 한 칸도 바꾸지 않고 띠만 붙인 판이다
    assert [r.replace('s', '.')[2:] for r in THREE] == [r for r in FRONT], 'three에서 s를 지우면 정면과 같아야 한다'
    # 안경 렌즈는 정면 기준 4칸
    assert FRONT[2].count('kkkk') == 2, '렌즈 폭 4칸'
    used = {c for v in BODY.values() for r in v for c in r} - {'.'}
    assert used <= set(PAL), used - set(PAL)
    assert 's' not in ''.join(''.join(v) for k, v in BODY.items() if not k.startswith('three')), 's(옆면)는 반측면에만'
    for k, m in DATA['motions'].items():
        assert len(m['frames']) == len(m['ms']), k
        assert len({(len(f), len(f[0])) for f in m['frames']}) == 1, (k, '모션 프레임 크기는 모두 같아야 한다')
    for k, rows in DATA['hands'].items():
        assert rows == hands(*{'기본': (9, 9), '한 손 어깨': (9, 5), '두 손 가슴': (7, 7), '엇갈림': (6, 10)}[k]), k
    print('ok', {k: len(v) for k, v in DATA.items()})


if __name__ == '__main__':
    cmd, *args = sys.argv[1:] or ['check']
    scale = int(args[args.index('--scale') + 1]) if '--scale' in args else 10
    if cmd == 'check':
        check()
    elif cmd == 'list':
        for group in ('body', 'hands', 'faces', 'hobbies', 'motions'):
            print(group, ' '.join(DATA[group]))
    elif cmd == 'json':
        print(json.dumps(get(args[0]), ensure_ascii=False, indent=1))
    elif cmd == 'svg':
        open(args[1], 'w').write(to_svg(get(args[0]), scale))
    elif cmd == 'png':
        to_image(get(args[0]), scale).save(args[1])
    elif cmd == 'gif':
        m = get(args[0])
        save_gif(m['frames'], m['ms'], args[1], scale if '--scale' in args else 6)
    else:
        sys.exit(__doc__)
