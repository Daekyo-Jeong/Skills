---
name: dkdk-caricature
description: 대교 본인(사람 얼굴)을 흑연 연필 캐리커처로 그리는 3:4 단독 컷 생성. 웨이브 장발·얇은 사각 안경·팔자 콧수염·삼각 턱수염, 소품 하나를 진지하게 대하는 상반신. 하단 손글씨 캡션("대 미식가의 교양 넘치는 식사" 류)은 선택. "캐리커처", "dkdk 캐리커처", "내 캐리커처", "연필 캐리커처", "나 그려줘" 같은 요청이면 사용. 바다코끼리 dkdk 본문 삽화는 dkdk-walrus, 도트 디디는 didi.
---

# dkdk-caricature — 대교 연필 캐리커처

> 자매 스킬: `dkdk-walrus`(바다코끼리 수인화 본문 삽화), `didi`(픽셀 디디). 서로 대체하지 않는다.

## 핵심 포지션

대교 본인을 흰 종이 위 연필 한 자루로 그린 캐리커처 한 컷. 진지한 얼굴로 사소한 물건 하나를 귀한 의식처럼 대한다. 웃음은 "진지한 태도 ↔ 사소한 행위"의 격차에서 나온다. 캡션은 **선택 사항**: 기본은 캡션 없이 그림만, 사용자가 원하거나 캡션을 주면 넣는다. 귀엽거나 과장된 카툰이 아니다.

정답지는 `assets/reference-original.jpg`(대교가 직접 그린 원화). 모든 생성에 `-i`로 첨부한다.

`assets/examples/`는 통과한 생성 예시(선 질감·비율 참고용). 구도·소품을 베끼지 말 것.

## 먼저 읽을 레퍼런스

- `references/character.md`: 시그니처 5개, 부위별 규칙, 선 스타일, 표정·포즈, Do/Don't. **생성 전 필수.**
- `references/caption.md`: 캡션 문형과 손글씨 규칙 (캡션을 넣을 때만).
- `references/prompt-template.md`: 장당 프롬프트 (고정 아이덴티티 블록 포함).
- `references/qa-checklist.md`: 생성 후 검수.

## 워크플로

### 1. 소재 잡기

사용자에게서 받을 것: **소품 하나**(치킨, 커피, 키보드…) + **상황**. 없으면 2–3개 제안. 캡션은 기본 생략. 사용자가 원하면 `references/caption.md` 문형으로 1–2안 만들고, 캡션을 주면 그대로 쓴다.

### 2. 생성 (easel 백엔드)

dkdk-walrus와 같은 백엔드(easel의 gen.sh, Codex CLI, API 키 불필요). 원화를 반드시 `-i`로 첨부:

```bash
GENSH="$(dirname "$(readlink -f "$(which easel)")")/scripts/gen.sh"
REF="<이 스킬 폴더>/assets/reference-original.jpg"
cat ./brief/<slug>.md | "$GENSH" ./runs/<slug>.png -i "$REF"
```

- 장당 60–110초. 반드시 `run_in_background`로.
- 여러 시안이 필요하면 `easel start ./brief/<slug>.md`(발산 N장) → `easel continue --pick <n>`.
- 수정: `-i "$REF" -i <직전결과.png>` 둘 다 첨부 + 브리프에 수정 지시 추가.
- 확정된 모델시트(`assets/caricature-board.png`)가 생기면 원화와 함께 두 장 첨부한다.

### 3. 검수

`references/qa-checklist.md`. 얼굴 아이덴티티(시그니처 5)가 하나라도 깨지면 재생성. 한글 캡션이 깨지면 캡션을 줄이거나, 캡션 없이 생성 후 손글씨를 따로 얹는다.

### 4. 저장

`assets/<slug>-caricature/NN-<topic>.png`. runs/ 원본은 남기고, 기존 파일은 요청 없이 덮어쓰지 않는다.

## 출력 톤

짧게. 몇 장, 어떤 소품(·캡션), 저장 경로, 어느 장이 안정적인지만.
