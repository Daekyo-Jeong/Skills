---
name: kickoff
description: >-
  Drives the user's standard project-start ritual as one unified command. Three
  stages: (1) a dialogue-first spec.md, (2) an MVP-sliced living plan.md with
  🤖/🧑 verification gates, (3) a design-brief.md handed to a design AI. Invoke
  this whenever the user is starting a NEW project or feature and wants to
  scope it — when they say /kickoff, "프로젝트 시작하자", "spec 만들자", "spec.md 써줘",
  "plan 짜자", "MVP 단위로 계획", "디자인 브리프 만들어", "design brief", or describes goals
  and requirements for something they're about to build and asks you to help
  shape it. Also use to update an existing plan.md (check off MVPs, append
  progress). Don't trigger for unrelated doc writing, code edits, or general
  questions about an existing codebase.
---

# kickoff — 프로젝트 시작 3단계 워크플로

새 프로젝트를 시작할 때 따르는 `spec → plan → design-brief` 3단계를 `/kickoff` 하나로 묶은 스킬이다.

> **전체 절차의 정본은 [AGENTS.md](AGENTS.md)에 있다.** 이 스킬이 트리거되면 **먼저 `AGENTS.md`를 읽고 그대로 따라라** — 단계 판단 캐스케이드, 프로젝트 루트 확정, 변형 파일명 감지, 각 STAGE의 상세 절차, 템플릿(`references/*.md`)이 거기 있다. AGENTS.md는 도구 중립 single source라 Codex 등 다른 에이전트도 같은 파일을 읽는다. 여기 SKILL.md는 Claude Code용 진입점(슬래시 명령 + 핵심 가드)만 담는다.

## 슬래시 명령 라우팅

| 명령 | 동작 |
|---|---|
| `/kickoff` | 프로젝트 루트 확정 후, 상태 캐스케이드로 다음 단계 자동 (spec→plan→brief→done) |
| `/kickoff spec` | spec 단계 (없으면 생성, 있으면 개정 대화) |
| `/kickoff plan` | plan 단계 (없으면 생성, 있으면 **동기화** — 덮어쓰기 X) |
| `/kickoff brief` | design-brief 단계 (spec만 있으면 가능, plan 불필요) |
| `/kickoff status` | 세 문서 상태 + plan 진행률만 요약, 아무것도 안 씀 |

인자 없이 부르면 AGENTS.md의 캐스케이드(spec 없음→spec / +plan 없음→plan / +brief 없음→brief / 셋 다→status+동기화 제안)를 따른다.

## ⚠️ STAGE 1에서 절대 잊지 마라 (1번 실패 모드)

spec 단계에서 **바로 `spec.md`부터 쓰지 마라.** 이 워크플로의 가장 흔한 실패가 검토 대화를 건너뛰고 곧장 문서를 써버리는 것이다. 순서는 반드시: **요구사항 청취 → 빠진 결정·리스크·줄일 스코프·비목표를 능동적으로 제안하며 합의 → 그제서야 spec.md 작성 → 멈추고 사용자 검토.** (상세는 AGENTS.md의 STAGE 1.)

나머지 단계 로직·파일 감지 규칙·템플릿은 모두 **[AGENTS.md](AGENTS.md)** 를 따른다.
