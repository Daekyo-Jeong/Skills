# Skills

Claude Code에서 쓰는 개인 스킬 모음. 각 폴더가 스킬 하나이며, `~/.claude/skills/`에 복사하면 바로 동작한다.

## 스킬 목록

| 스킬 | 설명 |
|---|---|
| [**kickoff**](./kickoff) | 프로젝트 시작 리추얼을 `/kickoff` 한 번으로 — 대화 기반 spec.md → MVP 단위 living plan.md → 디자인 브리프까지 3단계로 뽑아낸다. (원본: [Daekyo-Jeong/kickoff](https://github.com/Daekyo-Jeong/kickoff)) |
| [**dkdk-illustrations**](./dkdk-illustrations) | dkdk(바다코끼리 자화상 IP) 스타일의 한국어 본문 삽화 생성. 글을 소화해 shot list를 뽑고, 순백 배경 + 검정 손그림 + 소량의 빨강·주황·파랑 한글 주석 스타일로 장당 개별 생성한다. [ian-xiaohei-illustrations](https://github.com/helloianneo/ian-xiaohei-illustrations)를 dkdk IP + 한국어로 번안. |

## 설치

```bash
git clone https://github.com/Daekyo-Jeong/Skills.git
cp -R Skills/<skill-name> ~/.claude/skills/
```

## 참고

- **dkdk-illustrations**는 이미지 생성 백엔드로 [easel](https://github.com/Daekyo-Jeong)(Codex 데스크탑 앱 + ocx 프록시, API 키 불필요)을 사용한다. 다른 환경에서는 `SKILL.md`의 생성 단계를 각자의 이미지 생성 도구로 교체하면 된다.
- 스킬 구조는 Claude Code의 [Agent Skills](https://code.claude.com/docs/en/skills) 규격(SKILL.md + references/)을 따른다.
