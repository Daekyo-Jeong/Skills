# 생성 프롬프트 템플릿

한 장씩 개별 생성한다. 본문 내용에 맞게 변수를 교체하고, 여러 장을 한 이미지에 합치지 않는다.

브리프 파일(`./brief/<slug>-NN.md`)에 아래 내용을 그대로 채워 넣고, 생성 시 모델시트(`assets/dkdk-board-ink-bw.png`)를 `-i`로 반드시 첨부한다 (SKILL.md 3단계).

```text
Generate one standalone 16:9 horizontal Korean article illustration.

Visual DNA:
Pure white background. Minimalist black hand-drawn line art. Slightly wobbly pen lines. Lots of empty white space. Sparse red/orange/blue handwritten Korean (한글) annotations. Clean absurd product-sketch feeling. No gradients, no shadows, no paper texture, no complex background, no commercial vector style, no PPT infographic look, no cute mascot poster, no children's illustration, no realistic UI.

Recurring IP character required:
dkdk, a hand-drawn anthropomorphic walrus self-portrait character: big round body with a low stable center of gravity, short thick limbs, two short blunt downward tusks, simple dot eyes (emotion only via eyebrows, whisker angle and posture), thick dark rounded-square glasses, neatly groomed mustache-beard blending into walrus vibrissae, small man-bun hair knot, plain dark t-shirt (solid dark fill — the visual anchor of the scene), light shorts, one small crossbody bag, bare flipper feet. Drawn as clean black ink line art matching the overall sketch style. dkdk must perform the core conceptual action, not decorate the scene. Deadpan, serious, slightly bizarre — never cute, never mascot-like.

Theme:
{이 삽화의 주제}

Structure type:
{구조 유형: 워크플로 / 시스템 부분도 / 전후 대비 / 상태 변화 / 개념 은유 / 방법 계층 / 지도 경로 / 미니 만화 분할}

Core idea:
{이 그림이 전달할 핵심 의미}

Composition:
{구체 화면: dkdk가 어디서 무엇을 하는가, 주요 오브젝트는 무엇인가, 정보가 어떻게 흐르는가}

Suggested elements:
{요소1} / {요소2} / {요소3} / {요소4}

Korean handwritten labels (한글, keep each label 2-6 characters, max 3-6 labels total):
{라벨1} / {라벨2} / {라벨3} / {선택 라벨4}

Color use:
Black for main line art and dkdk (dark tee filled solid). Orange for main flow/path/arrows. Red only for key warnings/problems/results. Blue only for secondary notes or feedback/system state.

Constraints:
One image explains only one core structure. Keep the main subject around 40%-60% of the canvas. Preserve at least 35% blank white space. Use at most 3-6 short handwritten Korean labels — fewer labels means fewer typos; Korean text must be spelled exactly as given. Do not write a title in the top-left corner. Do not write the structure type on the image. Do not make it a formal diagram, course slide, or dense explainer. Invent a fresh visual metaphor for this specific article; do not copy prior compositions. It should be clear but not instructional, interesting but not childish, strange but clean.

Character identity reference:
The attached image is the official dkdk character model sheet. Match the character EXACTLY as drawn there — especially the face: dot eyes placed INSIDE the glasses lenses, the large rounded muzzle mass occupying the lower half of the face, the dense neatly-groomed whisker/beard mass (not sparse individual whisker lines), tusk shape and placement, head proportions, man-bun size. Only translate the rendering into loose hand-drawn ink sketch linework to match the illustration style; do not change any anatomical proportions or facial layout.
```

마지막 "Character identity reference" 블록은 고정 문구다 — 모델시트를 `-i`로 첨부할 때 항상 프롬프트에 포함시킨다.

## 수정 반복 프롬프트

easel continue의 `--note`로 사용:

좌상단 제목 제거:

```text
Remove only the handwritten title "{지울 텍스트}" and its underline from the top-left corner. Fill that area with the same clean white background. Preserve everything else exactly: characters, labels, paths, line style, composition, aspect ratio.
```

엉뚱함 강화:

```text
Regenerate with the same core meaning and simple layout, but make dkdk more central to the conceptual action. dkdk should be doing the strange work that explains the idea, not standing beside the diagram. Keep it clean, sparse, hand-drawn, and not cute.
```

한글 오타 수정:

```text
Keep the exact same composition. Fix the Korean labels: they must read exactly "{라벨1}", "{라벨2}", "{라벨3}" — short, clean handwritten Korean. Remove any garbled or extra text.
```
