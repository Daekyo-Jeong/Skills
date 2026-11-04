"""mov 레포의 디디 그림을 이 스킬의 assets/didi.json으로 다시 뽑는다.
사용: python3 scripts/export_from_mov.py ~/Desktop/work/mov
그림을 고치는 곳은 mov(tools/didi, tools/mascot)이고, 고친 뒤 이걸 돌려 스킬을 맞춘다."""
import json
import os
import sys

mov = os.path.abspath(os.path.expanduser(sys.argv[1]))
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'didi.json')
os.chdir(os.path.join(mov, 'tools', 'didi'))
sys.path[:0] = ['.', '../mascot']
import phosphor as P
import motion as M
import favicon as F
import poses as S
import views as V
import kit as K  # noqa: F401  소품 색까지 팔레트에 들어간 실제 출력 상태로 만든다

data = {
    'pal': dict(P.PAL),
    'body': {
        'front': V.FRONT, 'three': K.Q, 'back': V.BACK,
        'front_blink': K.SHUT, 'three_blink': K.QB,
        'half': M.HALF, 'open': M.OPEN,
        'up': M.UP_CLOSED, 'up_open': M.UP_OPEN, 'high': M.HIGH_CLOSED,
        'left_up': K.LEFT, 'right_up': K.RIGHT,
        'lift_left': K.LIFT_L, 'lift_right': K.LIFT_R,
        'small': F.SMALL,
    },
    'hands': V.HANDS,
    'faces': {k: {'label': l, 'rows': r} for k, (l, r) in S.FACES.items()},
    'hobbies': {k: {'label': l, 'rows': r} for k, (l, r) in S.HOBBIES.items()},
    'motions': {k: {'label': l, 'frames': [f for f, _ in seq], 'ms': [d for _, d in seq]} for k, (l, seq) in M.MOTIONS.items()},
}
json.dump(data, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(os.path.normpath(out), {k: len(v) for k, v in data.items()})
