# Mood → 설정

사용자가 무드를 말로 주면 두 가지 방법이 있다.

1. `--mood "원문 그대로"`: `moods.py`의 한/영 키워드 사전이 축으로 바꾼다. 빠르고, 매칭된 키워드가 출력된다. 걸린 키워드는 원문에 나온 순서대로 적용되므로, 서로 부딪히면(바다 vs 비) 원문에서 뒤에 나온 쪽이 이긴다. 배경 설명을 앞에, 핵심 장면을 뒤에 둔다.
2. `--mood-set energy=.. brightness=.. ...`: Claude가 원문을 읽고 축을 직접 정한다. 사전에 없는 표현("퇴근길 버스 창가", "할머니 집 다락방")은 이쪽이 정확하다.

둘을 같이 주면 `--mood`로 해석한 뒤 `--mood-set` 값이 덮어쓴다. 실행 시 `mood:` 줄에 최종 축이 찍히므로 의도와 다르면 고쳐서 다시 돌린다.

## 축

| 축 | 값 | 바뀌는 것 |
|---|---|---|
| `energy` | 0-1 | BPM(lofi 66-88, newage 56-76), 드럼·하이햇 밀도, comp·베이스 패턴, 멜로디 리듬(0.3 미만이면 긴 음 위주), 아르페지오 밀도, 벨 개수 |
| `brightness` | 0-1 | 키 높이, 키보드·멜로디 low-pass cutoff, 팔레트 선택 |
| `mode` | major / minor / 생략 | 진행 bank (minor: 단조·dorian 중심) |
| `space` | 0-1 | 리버브 길이·wet (lofi 1.6-3.2s, newage 4-7s) |
| `texture` | vinyl, rain, fire, birds, night, ocean, none | 배경 질감 (lofi는 바이닐이 항상 옅게 깔림) |
| `palette` | 아래 표 | 악기 조합 (생략하면 energy·brightness·힌트로 고름) |
| `prog` | lofi 진행 이름 | 진행 고정 |
| `genre` | lofi / newage / jazz / chiptune / bossa | `--genre auto`일 때 장르 |

## 팔레트

**lofi**: `rhodes-piano`(Rainy Window), `piano-vibes`, `guitar-flute`(나일론 기타 comp + 플루트, warm pad), `rhodes-guitar`, `piano-musicbox`(오르골 멜로디), `rhodes-choir`(choir pad), `rhodes-trumpet`(뮤트 트럼펫), `piano-clarinet`, `guitar-marimba`, `piano-kalimba`, `jazzguitar-vibes`

**newage**: `piano-strings`(Tidewater), `piano-choir`, `harp-flute`, `guitar-piano`, `celesta-piano`, `piano-pad`, `rhodes-flute`, `piano-oboe`(목가적), `harp-clarinet`, `guitar-flute`, `harp-vibes`

**lofi 진행**: major `ii-V-I-vi` `neo-soul` `sunlit` `descending` `four-chord` `royal-road` `backdoor` / minor `minor-drift` `dorian-night` `melancholy` `descending` `rain-minor` `aeolian-walk`

**bossa**: `guitar-flute`, `guitar-vibes`, `guitar-piano`, `guitar-trumpet`, `guitar-clarinet`, `guitar-sax`, `guitar-solo`(나일론 기타가 리드까지). 키워드: 보사·보사노바·삼바·브라질·휴양·바캉스·테라스

**jazz**: `piano-trio`, `vibes-trio`, `tenor-quartet`(테너 색소폰), `trumpet-quartet`(뮤트 트럼펫), `guitar-trio`. chiptune은 팔레트 없음(음색 고정)

**newage 진행 쌍**: major tide·drift·lift·open·morning·glow·plateau·horizon / minor dusk·nocturne·lament·ember·hollow

## 예시 해석

| 무드 | 축 |
|---|---|
| 비 오는 새벽, 쓸쓸한데 따뜻하게 | lofi, energy .3, brightness .15, minor, texture rain, hint warm |
| 햇살 좋은 봄날 아침 산책, 기타 | lofi, brightness .75, major, texture birds, palette guitar-* |
| 명상, 바다, 잔잔한 힐링 | newage, energy 0, space 1, texture ocean |
| 이별 후 혼자 걷는 밤, 몽환적 피아노 | newage, minor, brightness .1, space .8, texture night, hint dream |
| 겨울 벽난로 앞 재즈 카페 | lofi, prog neo-soul, palette rhodes-piano, texture fire |
| 공부할 때 틀어둘 집중용 | lofi, energy .45, texture vinyl |

모든 팔레트·진행·질감 조합은 QC를 통과하는지 렌더해서 확인했다 (2026-11-11). 새 팔레트나 질감을 추가하면 같은 확인을 한다.
