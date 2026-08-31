---
name: dkdk-deploy
description: 대교 개인 프로젝트를 Vercel(team daekyo-projects) + Cloudflare DNS로 배포하고 *.dkdk.me 서브도메인을 연결하는 절차와 함정 모음. Use when the user says "X.dkdk.me 만들어서 배포", "버셀에 올려줘", "도메인 연결해줘", "개인 프로젝트 배포", asks how to deploy a personal (non-company) project to Vercel, wants a dkdk.me subdomain wired up, or is debugging a Vercel build/deploy failure on a dkdk project. 사내 배포(ix-works, interaction.hnine.com)는 이 스킬이 아니라 ix-infra-deploy를 쓴다.
---

# dkdk-deploy

개인 프로젝트를 `*.dkdk.me`로 내보내는 표준 절차. 매번 "절차 좀"부터 다시 밟지 않기 위한 스킬이다.

## 0. 지형 (먼저 알고 시작)

- **Vercel**: team **`daekyo-projects`** 소속으로 배포한다. 개인 계정 아님.
- **DNS**: `dkdk.me`는 **Cloudflare**가 관리. 서브도메인 연결 = CF에 CNAME 추가 + Vercel 프로젝트에 도메인 등록, 두 쪽 다 필요.
- **git author**: 커밋은 반드시 `Daekyo-Jeong <dk@dkdk.me>`. 다른 계정으로 커밋된 적이 있어 확정된 규칙이다.
- **push = 배포**: Vercel에 연결된 레포(예: `Daekyo-Jeong/dkdk-arcade` → arcade.dkdk.me)는 push 즉시 프로덕션 반영. **커밋은 자유롭게 쌓되 push는 대교 확인 후.**
- 기존 서브도메인: `feed`(디자인 뉴스), `log`(Solari 플립보드), `arcade`(보드게임), `wall`, `catalog`, `lab`(폐기, 방향 TBD).

## 1. 신규 배포 절차

### 1-1. 배포 전 로컬 검증
```bash
CI=true npm run build
```
그냥 `npm run build`는 통과해도 Vercel은 실패할 수 있다 — Vercel 환경은 `CI=true`라 CRA 등에서 **eslint warning이 error로 승격**된다(dkdk-lab 실사고: unused 변수 하나로 배포 실패). unused 변수/import는 그 자체로 배포 차단 사유로 취급한다.

### 1-2. Vercel 프로젝트 생성·배포 (CLI)
- **조회는 MCP, 생성·배포·설정은 CLI.** claude.ai Vercel MCP 토큰은 사실상 읽기 전용이라 프로젝트 생성·설정 변경이 403 난다.
- CLI 인증 토큰 위치(macOS): `~/Library/Application Support/com.vercel.cli/auth.json`
- **`--scope`에는 team slug가 아니라 `team_...` ID를 넘긴다.** slug가 개인 계정 이름과 비슷하면 CLI가 개인 계정으로 오인해 `The specified scope does not exist` / `You cannot set your Personal Account as the scope`를 뱉는다.

```bash
vercel link --scope team_XXXX          # 프로젝트 연결(신규면 생성 흐름)
vercel --prod --scope team_XXXX        # 프로덕션 배포
```
Git 레포 연결형이면 이후엔 push만으로 배포된다(→ §0의 push 확인 규칙).

### 1-3. 도메인 연결
1. Vercel 프로젝트 → Domains에 `X.dkdk.me` 추가 (`vercel domains add X.dkdk.me` 또는 대시보드).
2. Cloudflare `dkdk.me` 존에 CNAME 추가: `X` → `cname.vercel-dns.com`. **Proxy는 DNS only(회색 구름)로 시작**하는 게 검증이 쉽다 — Vercel이 인증서를 못 뽑으면 프록시부터 의심.
3. 확인: `dig X.dkdk.me CNAME +short` → `curl -I https://X.dkdk.me`.

반영이 안 보이면 순서대로: Vercel 도메인 상태(Invalid Configuration?) → CF 레코드 오타/프록시 → 브라우저·DNS 캐시. "깃 휘발" 같은 추측 말고 이 순서로 짚는다.

## 2. 비공개(로그인) 배포가 필요할 때

Vercel **Hobby 플랜은 프로덕션에 SSO를 못 건다**(프리뷰 전용, API로 시도하면 `invalid_sso_protection`). Password Protection은 Pro 유료. 시도하지 말고 처음부터:

- **Edge Middleware + GitHub OAuth**로 직접 게이트. 루트 `middleware.ts` + `api/auth/*`(Edge runtime). Next.js가 아닌 Vite 정적 사이트여도 Vercel이 인식한다.
- 게이트가 middleware 한 곳이라 페이지별 검사 누락이 구조적으로 없다.
- 세션은 HMAC 서명 쿠키. 서명키가 비었거나 짧으면 서명·검증 양쪽에서 예외를 던져 **닫히는 쪽으로 실패**시킨다.
- 로컬 dev에선 게이트를 안 태워 바로 볼 수 있게 한다(arcade 방식).

## 3. 함정 요약 (한 줄씩)

| 함정 | 처방 |
|---|---|
| 로컬 빌드 OK, Vercel만 실패 | `CI=true npm run build`로 재현 — warning 승격 |
| CLI가 scope를 거부 | slug 말고 `team_...` ID |
| MCP로 프로젝트 생성 403 | 조회=MCP, 쓰기=CLI |
| 프로덕션 SSO 설정 실패 | Hobby 제약 — middleware+OAuth로 우회 |
| 도메인 추가했는데 안 뜸 | Vercel 도메인 상태 → CF CNAME/프록시 → 캐시 순서로 |
| 커밋 author가 딴 계정 | `git config user.name "Daekyo-Jeong"` / `user.email "dk@dkdk.me"` 선확인 |

## 4. 마무리

배포 후에는 실제 URL을 `curl -I`와 브라우저 렌더 양쪽으로 확인하고, 대교에게는 **URL을 먼저** 준다. 새로 생긴 서브도메인·레포 연결·게이트 유무는 engram에 기록해 다음 배포가 이 지도를 이어받게 한다.
