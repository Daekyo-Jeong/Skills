---
name: didi
description: 디디(dkdk의 도트 바다코끼리 마스코트, 네온 초록 #00FF99 몸 + 안경 + 흰 엄니)를 그리거나 움직이거나 장면·웹·아이콘에 넣을 때 쓴다. "디디", "Didi", "디디 그려줘", "디디 장면", "디디 스프라이트", "디디 모션", "마스코트 도트" 같은 요청이면 프로젝트와 상관없이 이 스킬부터 연다. 몸 그림은 assets/didi.json의 원본만 쓰고 새로 그리지 않는다.
---

# 디디

디디는 대교(dkdk)의 도트 마스코트다. 네온 초록 몸에 검은 안경, 흰 엄니 두 개가 있는 바다코끼리 덩어리다. 어느 프로젝트에서 쓰든 같은 디디가 나와야 하므로 **몸은 그리지 않고 꺼내 쓴다.**

- 원본: [assets/didi.json](assets/didi.json) — 팔레트, 몸, 손, 표정, 취미, 모션 전부
- 도구: [scripts/didi.py](scripts/didi.py) — 꺼내기·변형·조립·SVG/PNG/GIF 출력·규칙 검사 (표준 라이브러리만, PNG·GIF는 Pillow)
- 설정 보드: [assets/didi-board.png](assets/didi-board.png), [assets/didi-board.html](assets/didi-board.html)

작업 전에 보드 PNG를 Read로 한 번 본다. 무엇을 만들든 끝나면 결과를 렌더해서 눈으로 확인한다.

## 형태 규칙 (2026-11-04 확정)

1. **디디는 정면 그림을 밀어낸 판이다.** 앞으로 튀어나오는 부분이 없다. 정면에서 보이는 게 전부다.
2. **측면 그림은 없다.** 옆으로 움직여도 반측면(`three`)까지만 쓴다. 왼쪽을 보게 하려면 `flip(three)`.
3. **반측면 = 정면 + 옆면 띠 2칸.** 정면 20칸은 한 칸도 바꾸지 않고, 왼쪽에 옆면 띠 `s`(#00B86E) 2칸을 붙여 22칸이다. 정면 자리에 반측면을 놓을 땐 두 칸 왼쪽에 찍어야 머리가 맞는다.
4. **안경 렌즈는 하나에 4칸 폭.** 안경다리는 없다. 그래서 뒷모습(`back`)엔 안경이 안 보인다.
5. **엄니가 가장 앞 요소다.** 볼에 점은 없다.
6. **손은 몸 옆선 5~10행 어디든.** `hands(왼손 윗줄, 오른손 윗줄)`로 붙인다. 정면 몸 전용이다.
7. 크기: 정면·후면 20×14, 반측면 22×14. 눈줄 2-4행, 엄니줄 7-10행, 발줄 12-13행.

## 팔레트

| 키 | 색 | 쓰는 곳 |
|---|---|---|
| `g` | `#00FF99` | 몸. 초록은 디디 몸에만 쓴다 |
| `k` | `#0E110F` | 안경, 입 |
| `w` | `#FFFFFF` | 엄니 |
| `e` | `#0B7A52` | 감은 눈, 뒷모습 주름 |
| `s` | `#00B86E` | 반측면의 옆면 띠 |
| `p` | `#FFFFFF` | 물건 (밝은) |
| `q` | `#A6A6A6` | 물건 (중간) |
| `r` | `#5C5C5C` | 물건 (어두운) |

배경은 검정. 물건은 `p`·`q`·`r`만 쓴다. 새 색은 만들지 않는다.

## 꺼내 쓸 수 있는 것

`python3 scripts/didi.py list`로 전체를 본다.

- `body`: `front`, `three`, `back`, `front_blink`, `three_blink`, `half`(입 반쯤), `open`(입 벌림), `up`·`up_open`·`high`(손 듦), `left_up`·`right_up`(한 손), `lift_left`·`lift_right`(발 듦), `small`(파비콘 14×12)
- `hands`: 기본, 한 손 어깨, 두 손 가슴, 엇갈림
- `faces`: rest, talk, blink, laugh, surprise, think, sleep, wave
- `hobbies`: freediving, fishing, cooking, knitting, computer, drawing, singing, exercise
- `motions`: idle, talk, walk, wave, jump, surprise, laugh, type, think, sleep, glitch, dive (`frames` + 프레임별 `ms`)

## 변형은 함수로만

몸 줄을 손으로 고치지 않는다. 필요한 변화는 `didi.py`의 함수로 만든다.

| 함수 | 효과 |
|---|---|
| `flip(rows)` | 좌우 반전 |
| `squash(rows)` / `stretch(rows)` | 한 칸 눌림 / 늘어남 |
| `shut(rows)` | 눈 감기 (렌즈 가운데가 `e`로) |
| `lift_leg(rows, 'left'\|'right')` | 정면 몸 한 발 들기 |
| `hands(l, r)` | 손 위치 |
| `blank`, `stamp`, `pad`, `line` | 칸 만들기, 덮어 찍기, 여백, 선 |

여기 없는 자세가 꼭 필요하면 몸을 새로 그리지 말고 대교에게 먼저 보여 주고 정한다. 정해지면 원본(아래 "원본 고치기")에 넣는다.

## 쓰는 법

**Python 장면/스프라이트**

```python
import sys; sys.path.insert(0, '<스킬 경로>/scripts')
import didi as D
r = D.stamp(D.blank(40, 20), D.flip(D.THREE), 4, 6)   # 왼쪽 보는 반측면
r = D.stamp(r, ['pppp', 'qqqq'], 26, 14)              # 물건은 p/q/r
open('scene.svg', 'w').write(D.to_svg(r, 10))
```

**웹 (Canvas·React 등)**: `didi.json`을 프로젝트에 복사하거나 `python3 scripts/didi.py json three`로 줄 목록을 뽑아 붙인다. 그릴 땐 칸 하나를 정수 배율 사각형으로 찍고 `image-rendering: pixelated`(또는 SVG `shape-rendering="crispEdges"`)로 흐림을 막는다. 몸 배율은 정수만.

**이미지 파일**: `didi.py svg|png <이름> <출력> --scale N`, 모션은 `didi.py gif motions.<이름> out.gif`.

## 장면 만들 때

- 프레임은 3~7장, 모든 프레임과 깜빡임 프레임은 크기가 같다.
- 루프는 끊김이 없어야 한다. 마지막 프레임이 첫 프레임으로 자연스럽게 이어지게.
- 소품은 크게. 두께 2칸 이상, 몸 폭의 1/3 이상이어야 작은 칸에서도 읽힌다.
- 디디 몸이 소품에 묻히지 않게 몸 주변은 비운다.
- 직접적인 글자·기호(예: "생각"이라는 글씨)보다 동작과 소품으로 말한다.

## 검사

```bash
python3 scripts/didi.py check
```

반측면이 정면 + 띠인지, 렌즈 폭, `s`가 반측면에만 있는지, 팔레트 밖 색, 모션 프레임 크기, 손 표본을 확인한다. 원본을 바꾼 뒤엔 반드시 돌린다. 그리고 결과물은 PNG로 렌더해 Read로 직접 본다. 대교는 렌더된 화면으로 판단한다.

## 원본 고치기

디디 그림을 만드는 곳은 mov 레포(`github.com/Daekyo-Jeong/dkdk-mov`)의 `tools/didi/`, `tools/mascot/`이다. 형태를 바꿀 땐:

1. mov에서 그림을 고치고 mov 쪽 빌드·보드(`python3 tools/didi/board.py`)를 돌린다.
2. 이 스킬을 맞춘다: `python3 scripts/export_from_mov.py <mov 경로>`, 보드 PNG·HTML을 `assets/`로 복사.
3. `python3 scripts/didi.py check`, 렌더 확인, 형태 규칙이 바뀌었으면 위 "형태 규칙"도 고친다.

다른 프로젝트에 디디 복사본을 따로 그려 두지 않는다. 복사본은 원본이 바뀔 때 혼자 옛 모습으로 남는다(2026-11-04 어항 다이빙 디디가 옛 측면으로 남은 사례).
