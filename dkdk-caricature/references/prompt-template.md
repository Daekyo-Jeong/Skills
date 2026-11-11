# 생성 프롬프트 템플릿

한 장 = 한 번의 생성. `./brief/<slug>.md`에 아래를 채워 넣고 `assets/reference-original.jpg`를 `-i`로 첨부한다.

```text
Generate one standalone 3:4 portrait graphite-pencil caricature on plain white paper.

Scene:
{소품과 상황. 예: He holds a steaming fried chicken drumstick up near his cheek between two fingers, eyes closed, savoring the smell with deep ceremony, other hand resting on his chest.}

Expression:
{음미 / 심사 / 몰입 / 체념 / 확신 + 한 줄 묘사}

Caption: {없음 → "None. Do not draw any text, letters or caption anywhere." / 있으면 → hand-lettered Korean, spelled EXACTLY, centered below the figure: "{1줄}" / "{2줄}"}

Character identity reference (dkdk caricature):
The attached image is the official reference drawing. Draw the SAME man as a graphite-pencil caricature on plain white paper.
- Face: round, broad face with soft double-chin jawline. Short neck, rounded shoulders.
- Hair: thick wavy shoulder-length hair swept back off the forehead with big volume and a slight center split; strands drawn as 3-5 bold S-curves; tips curl outward at the nape. Ears half visible; the hair behind the ears is filled solid with dense pencil hatching.
- Glasses: thin metal frames, wide horizontal rectangles with slightly rounded corners, sitting high right under short thick eyebrows. Never round, never thick plastic.
- Brow: 2-3 short frown lines between the eyebrows.
- Facial hair: drooping mustache thin in the middle, ends falling past the mouth corners; a small patch under the lower lip; a pointed downward-triangle chin beard filled dark with rough edges. No cheek beard, no sideburn beard.
- Nose: wide nostrils, two dots, almost no bridge line. Mouth: small and closed, no teeth.
- Clothing: plain crew-neck short-sleeve t-shirt, no logo or pattern.

Line style:
Single-weight soft 4B pencil outlines drawn in one stroke, occasionally broken. Solid hatched pencil fill ONLY in three places: hair behind the ears, the chin beard, and one side of the body outline (under a sleeve / along the torso). No gray tonal shading, no blending, no color, no digital clean lines.

Framing and constraints:
Deadpan exaggeration — emotion through eyebrows, brow lines and head tilt; mouth stays closed. 3:4 portrait, bust-up, three-quarter front view, head slightly raised. One prop held near the face. At least 35% empty white paper. No background, no speech bubbles, no other people, no title in a corner. If a caption is given: one or two lines of neat, upright, widely spaced hand-lettered Korean in the same pencil, centered below the figure; otherwise no text at all. Do not copy the reference's pose or prop unless the scene asks for it.
```

`Character identity reference`부터 끝까지는 고정 문구. 바꾸지 않는다. 캡션은 기본 "None".

## 수정 프롬프트

아이덴티티 보정 (`-i REF -i 직전결과`):

```text
Keep the same pose, prop, composition and caption. Correct the face to match the first attached reference exactly: {틀린 부분 — 예: glasses must be thin rectangular metal frames, not round; chin beard must be a dark pointed triangle}.
```

캡션 수정:

```text
Keep everything exactly the same. Fix only the Korean caption so it reads exactly "{1줄}" / "{2줄}" in neat upright hand-lettered pencil. Remove any garbled text.
```
