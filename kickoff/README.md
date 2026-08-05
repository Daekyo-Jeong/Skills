# 🎬 kickoff

> 프로젝트 시작 루틴(**spec → plan → design brief**)을 한 번의 명령으로 묶은, **에이전트 중립** 워크플로.

새 프로젝트를 시작할 때마다 거치는 똑같은 3단계 — 요구사항을 정리·검토해서 **`spec.md`**, MVP 단위로 쪼개서 **`plan.md`**, 디자인 AI에게 넘길 **`design-brief.md`** — 를 하나로 묶었다. 현재 폴더 상태를 보고 알아서 다음 단계로 데려간다.

**Claude Code뿐 아니라 Codex·Cursor·Copilot 등 `AGENTS.md`를 읽는 에이전트라면 어디서든 동작한다.** 워크플로 본질은 도구 중립 [`AGENTS.md`](AGENTS.md) 한 파일에 있고, Claude Code는 `/kickoff` 슬래시 명령으로 더 매끄럽게 쓴다.

핵심은 문서 생성기가 아니라 **일하는 방식**을 고정한 것이다 — 검토 먼저, 검증 가능한 단위, 문서끼리 역할 안 겹치게.

## 무엇을 해주나

| 단계 | 하는 일 |
|---|---|
| **① spec** | 바로 문서부터 쓰지 않는다. 먼저 같이 대화하며 빠진 결정·리스크·줄일 스코프를 짚고, **합의된 다음에** `spec.md`를 쓴다. |
| **② plan** | 검증 가능한 MVP 슬라이스로 쪼갠다. 각 단계는 🤖(AI 자동검증) / 🧑(사람 판단) 게이트로 나뉘고, 진행하며 체크하는 **살아있는 문서**. |
| **③ brief** | `spec`과 함께 디자인 AI에게 넘기는 입력. 받을 산출물 형식(Figma/HTML/…)과 **❌ 하지 말 것**까지 명시. |

## 어떤 에이전트에서 쓰나

워크플로 본질은 `AGENTS.md` 한 파일에 담겨 있다. `AGENTS.md`는 여러 AI 코딩 에이전트가 공통으로 읽는 관례라(Codex CLI, Cursor, GitHub Copilot, Aider, Zed, Windsurf 등), 그 파일을 프로젝트에 두면 대부분의 에이전트가 이 워크플로를 따른다.

| 에이전트 | 적용 방법 |
|---|---|
| **Claude Code** | 스킬로 설치 → `/kickoff` 슬래시 명령 + 자동 트리거 (가장 매끄러움) |
| **Codex · Cursor · Copilot · Aider · Zed · Windsurf 등** | `AGENTS.md`를 프로젝트 루트에 두거나, 도구의 지침 파일에 내용을 포함 |
| **Cline** | 아직 `AGENTS.md`를 읽지 않으므로 심볼릭: `ln -s AGENTS.md .clinerules` |

## 설치

**Claude Code (스킬):**

```bash
git clone https://github.com/Daekyo-Jeong/kickoff.git ~/.claude/skills/kickoff
```

재시작하면 어느 프로젝트에서든 `/kickoff`. (Windows는 `%USERPROFILE%\.claude\skills\kickoff\`)

**다른 에이전트 / 특정 프로젝트에 적용:**

```bash
git clone https://github.com/Daekyo-Jeong/kickoff.git
cp kickoff/AGENTS.md       your-project/
cp -r kickoff/references    your-project/
```

또는 `AGENTS.md` 내용을 쓰는 도구의 전역/프로젝트 지침에 붙여 넣는다.

## 사용법

```
/kickoff            # 폴더 상태를 보고 다음 단계 자동 진행 (spec → plan → brief)
/kickoff spec       # spec 단계 강제 (요구사항 청취 → 검토 대화 → 합의 후 작성)
/kickoff plan       # plan 생성, 이미 있으면 동기화 (체크/진행기록 갱신)
/kickoff brief      # design-brief 단계 (spec만 있으면 가능)
/kickoff status     # 세 문서의 현재 상태 + plan 진행률만 요약
```

> 슬래시 명령은 Claude Code 기준. 다른 에이전트에서는 "프로젝트 시작하자 / spec 만들자 / plan 짜자 / 디자인 브리프 만들어"처럼 자연어로 요청하면 `AGENTS.md`의 같은 절차를 따른다.

인자 없이 부르면 현재 프로젝트 루트를 보고 **다음에 할 단계**를 자동으로 정한다:

1. spec 없음 → **spec**
2. spec 있음 + plan 없음 → **plan**
3. spec·plan 있음 + brief 없음 → **brief**
4. 셋 다 있음 → 현재 상태 요약 + 살아있는 plan 동기화 제안

기존 작업물(`SPEC.md`, `CMS_Spec.md` 같은 변형 파일명 포함)은 대소문자·부분 매칭으로 감지해서 **말없이 덮어쓰지 않는다.** 여러 프로젝트를 담은 상위 폴더에서 호출하면, 단계를 진행하기 전에 어느 폴더가 이번 프로젝트인지 먼저 확인한다.

## 구조

```
kickoff/
├── AGENTS.md                     # 워크플로 본질 (도구 중립, single source) — 모든 에이전트가 읽음
├── SKILL.md                      # Claude Code 진입점 (/kickoff 슬래시 + 핵심 가드) → AGENTS.md 위임
├── references/                   # spec/plan/brief 템플릿 (공유)
│   ├── spec-template.md
│   ├── plan-template.md
│   └── brief-template.md
├── README.md
└── LICENSE
```

생성되는 문서는 **한글 본문 + 영어 라벨/경로/코드** 혼용이며, 템플릿은 출발점일 뿐 프로젝트 성격에 맞게 가감한다.

## 라이선스

[MIT](LICENSE) © 2026 Daekyo-Jeong
