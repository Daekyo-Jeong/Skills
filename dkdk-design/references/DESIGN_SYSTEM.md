# dkdk 디자인 시스템

> 메인(dkdk.me, `dkdk`)과 feed(feed.dkdk.me, `dkdk-feed`)의 실제 CSS에서 추출한 공통 규칙.
> 다른 dkdk 서비스(lab, tape, arcade, mov, …)를 만들 때 이 문서를 기준으로 삼는다.
> 정본 구현: 메인 `src/index.css`, `src/components/Layout/Window.module.css` / feed `app/globals.css`.
> 추출일: 2026-11-10

## 0. 한 줄 요약

**종이(#fafafa) 위의 잉크(#111), 그리고 시스템 신호 하나(네온 그린 #00ff99).**
본문은 Pretendard, 메타·라벨·UI는 IBM Plex Mono 대문자. 모서리는 각지고, 선은 1px 잉크.
메인은 이 종이를 "유리 프레임에 끼운 시트"로, feed는 "신문 지면"으로 쓴다.

---

## 1. 색 (Color)

### 1.1 공통 코어 — 두 repo가 같은 값을 쓴다

| 토큰 | 값 | 의미 |
|---|---|---|
| `--paper` | `#fafafa` | 종이. 기본 배경 |
| `--ink` | `#111111` | 잉크. 본문·선·반전 면 |
| `--ink-60` | `rgba(17,17,17,.6)` | 보조 텍스트, 메타 |
| `--rule` | `rgba(17,17,17,.15)` | 얇은 구분선 |
| `--green` | `#00ff99` | **시스템 신호.** 활성, AI, 링크 이동 띠, 포커스 링 |

규칙
- 그린은 "시스템/기계가 하는 일"에만 쓴다. 장식용 배경으로 넓게 깔지 않는다(예외: 메인의 `signal` 시트, 책등 1/4).
- 그린 위 글자는 항상 `--ink`. 잉크 위 그린 글자(`.goBar`)도 허용.
- 포커스 링: `outline: 2px solid var(--green); outline-offset: 2px`.

### 1.2 메인 전용

| 토큰 | 값 | 의미 |
|---|---|---|
| `--human` | `#ff7c7c` | **사람.** 대교 본인·사람이 하는 일. 보조 강조로 두루 쓰지 않는다 |
| `--ink-light` | `#f9f9f9` | 어두운 바탕 위 글자 |
| `--ink-72` | `rgba(17,17,17,.72)` | 캡션 |
| 바탕 | `#2b302d` | 데스크톱(CRT 셰이더) 바탕 |
| `--glass` / `--glass-dim` | `rgba(249,249,249,.2)` / `.12` | 유리판(포커스/비포커스) |
| `--glass-line` / `-dim` | `rgba(249,249,249,.5)` / `.3` | 유리 테두리 |
| `--glass-shadow` | `0 8px 32px rgba(36,36,36,.3), inset 0 1px 0 rgba(249,249,249,.2)` | 유리 그림자 |
| 터미널 면 | `linear-gradient(145deg,#0e110f,#1a1d1b)` | 터미널 시트 |
| 버튼 면 | `linear-gradient(145deg,#242424,#3a3a3a)` | 독 아이콘, 닫기 버튼 |

### 1.3 feed 전용

| 토큰 | 라이트 | 다크 |
|---|---|---|
| `--paper` | `#fafafa` | `#171717` |
| `--ink` | `#111111` | `#e2e2e2` |
| `--ink-rgb` | `17,17,17` | `226,226,226` |
| `--ink-30` | `rgba(ink,.3)` | 〃 |
| `--hover-bg` | `#ebebeb` | `#242424` |
| `--surface-inverse` | `#111111` | `#0d0d0d` |

- feed는 `prefers-color-scheme`으로 다크 모드를 따른다. 메인은 다크 고정(바탕) + 라이트 시트.
- 그린은 다크에서도 `#00ff99` 그대로.

---

## 2. 타이포그래피

### 2.1 글꼴 (공통)

| 역할 | 글꼴 | 토큰 |
|---|---|---|
| 본문·헤드라인 | Pretendard Variable | 메인 `--font-sans`, feed `--font-serif`(이름만 serif, 실제는 Pretendard) |
| 메타·라벨·UI·터미널 | IBM Plex Mono (400/500/600) | `--font-mono` |
| 한글 고정폭 대체 | Nanum Gothic Coding | 메인만 |
| 레트로 숫자(시계) | VT323 | 메인 `--font-retro` |

- 로딩: Pretendard는 jsDelivr `pretendard@v1.3.9` dynamic-subset, Plex Mono는 Google Fonts.
- 한글 줄바꿈: `word-break: keep-all` (메인 body 기본).
- Galmuri, JetBrains Mono는 기각(인상이 달라지고, 이미 Plex Mono로 통일됨).

### 2.2 스케일 — 실제 쓰이는 값

| 역할 | 크기 | 굵기 / 자간 / 행간 | 비고 |
|---|---|---|---|
| 마스트헤드 | `clamp(36px, 7vw, 80px)` | 900 / -0.04em / 1, 대문자 | feed 헤더 |
| 대형 헤드라인 | `clamp(20px, 2.4vw, 38px)` | 800 / -0.02em / 1.1 | 카드 |
| 소형 헤드라인 | `clamp(14px, 1.4vw, 19px)` | 700 / -0.01em / 1.25 | 카드 |
| 본문 | 14–16px | 400 / – / 1.6 | 긴 글은 1.65–1.8, `max-width: 65ch` |
| 캡션 | 13px | 400 / 1.45–1.5 | |
| **모노 라벨** | 10–13px | 500–600 / **+0.04~0.12em** / 1, **대문자** | 탭, 카테고리, 메타, 유틸바 |
| 모노 마이크로 | 8.5–9px | +0.12em, 대문자 | 배지("LATEST") |

규칙: **산스는 음수 자간(-0.01 ~ -0.04em), 모노는 양수 자간(+0.04 ~ +0.12em) + 대문자.** 이 대비가 시스템의 목소리다.
컨테이너 안 글자는 `cqw` 단위 clamp를 쓴다(메인 패널: `clamp(15px, 3.6cqw, 20px)`).

---

## 3. 간격 · 레이아웃

| 항목 | 값 |
|---|---|
| 페이지 거터 | feed `clamp(16px, 4vw, 48px)` / 메인 `--desktop-inset: clamp(16px, 5vw, 72px)` |
| 기본 단위 | 4px 배수가 대부분(8, 12, 16, 20, 24). 카드 내부 20px, 큰 카드 24px |
| 콘텐츠 최대폭 | 1200px(서가), 1152px(피드), 읽기 720–760px |
| 그리드 | feed 카드 12열(`span 6` 대형, `span 3` 소형), 메인 패널 정렬 12×8 |
| 브레이크포인트 | **640px**(공통 모바일 기준), 768px, 900px. feed는 600/560도 일부 사용 |

---

## 4. 모양 (Radius · Border · Shadow)

| | 메인 | feed |
|---|---|---|
| 모서리 | 유리판 15px, 시트 10px, 독 아이콘 10px, 닫기 8px | **0** (각진 지면). 예외 2px, 원형 50% |
| 선 | 유리 `1px rgba(249,249,249,.3~.5)` | 잉크 `1px solid var(--ink)`, 강조 상단 `2px` |
| 그림자 | `--glass-shadow`, 아이콘 `0 2px 8px` | 거의 없음. 구분은 선(`box-shadow: 1px 0 0 var(--rule)`)으로 |
| 블러 | `backdrop-filter: blur(20px)` | 없음 |

공통 원칙: **시트(종이 면) 자체는 각지거나 작은 라운드, 깊이는 선으로 만든다.** 라운드와 그림자는 메인의 "유리 프레임"에만 있다.

---

## 5. 모션

| 토큰(제안) | 값 | 쓰임 |
|---|---|---|
| `--ease-out` | `cubic-bezier(0.2, 0.8, 0.2, 1)` | 메인 패널 열기·정렬, 부팅 — **기본 이징** |
| `--ease-page` | `cubic-bezier(0.3, 0.7, 0.2, 1)` | feed 뷰 전환 그룹 |
| `--ease-material` | `cubic-bezier(0.4, 0, 0.2, 1)` | 메인 독 아이콘(레거시) |
| 마이크로 | 0.12–0.15s ease | 호버 색·배경, 닫기 버튼, 책등 |
| 열기 / 닫기 | 0.24s ease-out / 0.16s ease-in | 패널 |
| 페이지 전환 | 160ms(old/new), 240ms(group) | feed `<ViewTransition>` |

규칙
- 빠르게. 사용자가 기다리는 전환은 만들지 않는다("never a slow dissolve").
- 모든 애니메이션은 `prefers-reduced-motion: reduce`에서 끈다(두 repo 모두 지킴).
- 호버 이동은 위로 몇 px(`translateY(-6px)` 책등, `-8px scale(1.1)` 독).
- 깜빡임: `blink 1.2s step-end` (로딩 중인 AI 태그).

---

## 6. 컴포넌트 패턴

### 공통 어휘
- **모노 대문자 라벨** — 탭, 카테고리, 메타, 유틸바. `--ink-60`, 호버 시 `--ink`.
- **잉크 반전 블록** — `background: var(--ink); color: var(--paper)`. 합계 셀, 책등, 링크 띠.
- **그린 활성 표시** — 활성 탭 배경, AI 태그 글자, 실행 중 점.
- **책장/책등(spine)** — 세로쓰기(`writing-mode: vertical-rl`) 900 굵기, 4색 순환(잉크 / 외곽선 / `#cbccc5` / 그린), 높이 72–100%. 메인 책장 패널과 feed 서가가 같은 은유.

### 메인
- **Window = 유리판 + 시트.** 유리판 padding 8px, 안에 시트 1장. 시트 종류 4가지:
  `paper`(종이) · `terminal`(터미널, 모노) · `signal`(그린) · `human`(핑크).
- **goBar** — 링크 패널 호버 시 아래에서 올라오는 40px 잉크 띠, 그린 모노 12px 글자로 목적지 표시.
- **닫기 버튼** — 좌상단 -9px, 28px, 호버 시 등장, 누르면 `--human`.
- **독** — 유리 위 50px 아이콘, 8px 간격.
- 모바일(≤640px): 유리 제거, 시트가 화면을 채우고 독으로 전환.

### feed
- **신문 지면.** 마스트헤드 → 유틸바(모노) → 1px 잉크 선 → 카테고리 탭 → 카드 그리드.
- **카드** — 오른쪽·아래 1px 잉크 선으로 칸을 나눔, 호버 `--hover-bg`. 이미지 카드는 하단 그라데이션 오버레이 + 흰 글자.
- **드롭다운** — 1px 잉크 테두리 + 상단 2px, 각진 모서리.

---

## 7. 두 repo의 차이 · 정리할 것

| 항목 | 메인 | feed | 권장 |
|---|---|---|---|
| 산스 토큰 이름 | `--font-sans` | `--font-serif` | `--font-sans`로 통일 |
| 다크 모드 | 없음(바탕만 어두움) | 있음 | 새 서비스는 feed 방식(토큰 스왑) |
| 모서리 | 라운드(유리) | 0 | 콘텐츠 면은 0~2px, 떠 있는 UI만 라운드 |
| `--human` 핑크 | 있음 | 없음 | 사람 관련 요소가 생기면 그때만 |

발견한 버그성 항목(이번에 고치진 않음)
- **feed 활성 탭 배경이 안 칠해짐**: `CategoryTabs.module.css:45`가 정의되지 않은 `var(--accent)`를 씀. 의도는 `--green`으로 보임.
- feed `Header.module.css:128` `var(--paper-dark)` 미정의 → 드롭다운 호버 배경 없음. `--hover-bg`가 맞아 보임.
- 메인 `index.css`에 레거시 독 토큰(`--primary-*`, `--background-*`, `--text-*` 등) 20여 개가 남아 있음. 일부는 새 토큰과 값이 같아 합칠 수 있음. `--primary-red`, `--border-secondary`는 주석 안에서만 참조.
- 메인 `index.css` 주석과 `spec.md`가 가리키는 `work/DESIGN_SYSTEM.md §13`은 repo 밖 파일이라 다른 repo에서 참조 불가.

---

## 8. 새 서비스에 적용할 때 (복붙용 최소 토큰)

```css
:root {
  --paper: #fafafa;
  --ink: #111111;
  --ink-rgb: 17, 17, 17;
  --ink-60: rgba(var(--ink-rgb), 0.6);
  --ink-30: rgba(var(--ink-rgb), 0.3);
  --rule: rgba(var(--ink-rgb), 0.15);
  --hover-bg: #ebebeb;
  --green: #00ff99;   /* 시스템 */
  --human: #ff7c7c;   /* 사람 */

  --font-sans: 'Pretendard Variable', Pretendard, system-ui, sans-serif;
  --font-mono: 'IBM Plex Mono', 'Nanum Gothic Coding', monospace;

  --gutter: clamp(16px, 4vw, 48px);
  --ease-out: cubic-bezier(0.2, 0.8, 0.2, 1);
}
@media (prefers-color-scheme: dark) {
  :root {
    --paper: #171717;
    --ink: #e2e2e2;
    --ink-rgb: 226, 226, 226;
    --hover-bg: #242424;
  }
}
body { background: var(--paper); color: var(--ink); font-family: var(--font-sans); word-break: keep-all; }
:focus-visible { outline: 2px solid var(--green); outline-offset: 2px; }
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation: none !important; transition: none !important; } }
```

체크리스트
- [ ] 그린은 시스템, 핑크는 사람에만 썼나
- [ ] 라벨·메타는 모노 대문자 + 양수 자간인가
- [ ] 헤드라인은 Pretendard 800–900 + 음수 자간인가
- [ ] 구분은 그림자 대신 1px 잉크/rule 선인가
- [ ] 640px에서 한 장씩 보이나
- [ ] reduced-motion에서 모션이 꺼지나
