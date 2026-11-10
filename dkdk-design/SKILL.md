---
name: dkdk-design
description: dkdk 서비스 공통 디자인 시스템(종이·잉크·네온 그린, Pretendard + IBM Plex Mono). Use when building or restyling UI in any dkdk repo (dkdk 메인, dkdk-feed, dkdk-lab, dkdk-tape, dkdk-arcade, dkdk-mov, dkworld), adding a new *.dkdk.me service, picking colors/fonts/spacing/motion for a dkdk page, or checking whether a screen matches the dkdk look.
---

# dkdk-design

메인(dkdk.me)과 feed(feed.dkdk.me)의 실제 CSS에서 뽑은 공통 규칙. 전체 토큰·컴포넌트·차이점은 [references/DESIGN_SYSTEM.md](references/DESIGN_SYSTEM.md).

## 핵심 다섯 줄

1. **종이 `#fafafa` 위 잉크 `#111`.** 다크는 종이 `#171717`, 잉크 `#e2e2e2`로 토큰만 바꾼다.
2. **그린 `#00ff99`은 시스템, 핑크 `#ff7c7c`는 사람.** 둘 다 장식용 보조색으로 쓰지 않는다.
3. **본문은 Pretendard + 음수 자간, 라벨·메타는 IBM Plex Mono 대문자 + 양수 자간(+0.04~0.12em).**
4. **깊이는 그림자 대신 1px 잉크/rule 선.** 콘텐츠 면은 각지게(0~2px). 라운드·유리·그림자는 떠 있는 UI(메인 유리 프레임, 독)에만.
5. **빠른 모션.** 기본 이징 `cubic-bezier(0.2, 0.8, 0.2, 1)`, 호버 0.12~0.15s, 열기 0.24s. `prefers-reduced-motion`에서 전부 끈다.

## 작업 순서

1. 대상 repo의 기존 토큰 파일(메인 `src/index.css`, feed `app/globals.css`)을 먼저 읽는다. 이미 있는 토큰이 우선.
2. 새 서비스면 references 문서 §8의 최소 토큰 CSS로 시작한다.
3. 컴포넌트는 §6 어휘(모노 라벨, 잉크 반전 블록, 그린 활성 표시, 책등, 유리판+시트, goBar)에서 고른다.
4. 끝나면 §8 체크리스트로 검사한다. 모바일 기준은 640px.

## 하지 말 것

- 새 강조색 추가, 그린 면적 확대, 핑크를 일반 강조로 쓰기
- Galmuri·JetBrains Mono 등 다른 글꼴 도입
- 정의 안 된 토큰 참조(`--accent`, `--paper-dark` 사례가 실제로 있었다)
