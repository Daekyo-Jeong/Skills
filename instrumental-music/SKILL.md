---
name: instrumental-music
description: 외부 생성형 음악 AI(Suno 등) 없이 코드만으로 로우파이(lo-fi hip hop)·뉴에이지(ambient piano)·재즈 트리오·칩튠 instrumental 트랙을 만든다. 무드를 말로 주면("비 오는 새벽, 쓸쓸한데 따뜻하게") 템포·장단조·악기 팔레트·빗소리 같은 질감으로 바꿔 생성하고, 자동 품질 검사(LUFS·피크·스펙트럼·화성 충돌) 통과작 중 최고를 고른다. seed로 재현. "로우파이 만들어줘", "뉴에이지 곡", "재즈", "칩튠", "이런 분위기 BGM", "instrumental 음악 생성", "seed 42로 다시" 같은 요청이면 이 스킬을 쓴다.
---

# instrumental-music

Python MIDI(FluidSynth) + numpy DSP **hybrid 엔진**으로 곡을 렌더한다. 피아노·EP·스트링은 SoundFont로, 드럼·베이스·패드·벨·바이닐·파도 같은 질감은 DSP로 만들고, stem 레벨을 RMS로 맞춘 뒤 마스터링한다.

기준선은 사용자가 승인한 두 곡이다. 이 스킬의 목표는 **매번 그 품질을 보장하는 것**이다.

| 레퍼런스 | 장르 | 재현 명령 |
|---|---|---|
| Rainy Window | lo-fi, 74 BPM, C major ii-V-I-vi, EP + 피아노 멜로디 | `make.py --genre rainy-window` |
| Tidewater | new age, 66 BPM, D major, 피아노 아르페지오 + 스트링 + 벨 + 파도 | `make.py --genre tidewater` |

## 원칙

1. **처리 체인은 고정, 고르는 건 검증된 bank 안에서만.** 이펙트 체인 구조·stem 레벨 비율·마스터 LUFS는 레퍼런스와 같은 코드다. 무드와 seed가 바꾸는 건 키, 템포, 진행, 구조, 그루브, 악기 팔레트, 배경 질감, 필터 밝기, 공간감, 멜로디이고 전부 QC 통과를 확인한 후보 목록에서 고른다. 품질을 깨는 자유 변수는 노출하지 않는다.
2. **멜로디는 규칙으로 만든다.** 펜타토닉 안에서, 강박·긴 음은 코드톤, 경과음은 순차진행이고 코드와 반음 충돌 금지. 1-2마디 motif를 5-6마디에서 반복, 4·8마디는 긴 cadence.
3. **같은 seed = 같은 곡** (디코딩된 PCM md5까지 동일 확인). 마음에 든 곡은 seed만 기록하면 된다.
4. **QC 통과 못 하면 버린다.** 실패한 변주는 seed+1000으로 자동 재생성(기본 4회).

## 사용법

처음 한 번:
```bash
bash scripts/setup.sh        # fluidsynth, ffmpeg, GM SoundFont, numpy/scipy/pretty_midi/pyloudnorm
```

생성:
```bash
cd scripts
python3 make.py --genre lofi --variants 3 --out ~/Music/claude      # 변주 3개, QC, 순위
python3 make.py --genre newage --variants 3 --out ~/Music/claude
python3 make.py --genre lofi --seed 102 --out out                    # 특정 곡 재현
python3 make.py --genre lofi --seed 7 --set bpm=76 key=2 prog=descending   # plan 일부 고정
python3 make.py --mood "비 오는 새벽, 쓸쓸한데 따뜻하게" --variants 3 --out out     # 무드 → 장르·설정 자동
python3 make.py --genre newage --mood-set energy=0.2 brightness=0.7 texture=birds palette=harp-flute
```

출력: `<genre>_<seed>.mp3`, `<genre>_<seed>.json`(plan·QC 지표·악보 요약), `report.json`(통과 여부·점수순). 3변주 기준 약 30-60초(병렬 렌더).
mp3는 기본 224k. 스트리밍처럼 용량이 중요하면 `--bitrate 128k`(또는 `MUSIC_BITRATE=128k`). 곡은 같고 파일만 작아진다.

요청 처리 순서:
1. **무드가 있으면 무드부터.** 원문을 `--mood`로 넘기고, 사전에 없을 법한 표현이면 [references/moods.md](references/moods.md)를 보고 `--mood-set`으로 축(energy, brightness, mode, space, texture, palette)을 직접 정한다. 출력의 `mood:` 줄이 의도와 맞는지 확인한다.
2. 장르는 무드에서 추론된다(명상·바다·몽환 → newage, 그 외 lofi). 사용자가 장르를 말하면 `--genre`로 고정. 둘 다 아니면 가장 가까운 쪽을 쓰고 그렇게 말한다.
3. `--variants 3`으로 돌린다. 세부 지시(더 느리게, 키 올려)는 `--set`으로: `bpm`, `key`(반음 offset), `prog`, `form`, `palette`, `texture`.
4. `report.json` 1위를 기본 추천으로, 나머지도 같이 전달한다. seed와 무드 설정을 함께 알려준다.
5. 사용자가 고른 곡은 같은 seed + 같은 무드 설정으로 언제든 재현된다.

## preset 선택지

무드 축·팔레트·질감 전체 목록과 해석 예시는 [references/moods.md](references/moods.md).

**lofi** (`presets/lofi.py`, -14 LUFS)
- `prog`: `ii-V-I-vi`(Rainy Window), `descending`, `minor-drift`, `neo-soul`
- `form`: `classic`(intro4 A8 B8 break4 A'8 out4), `straight`, `long`
- `prog` 추가: `dorian-night`, `melancholy`, `sunlit`, `four-chord`, `royal-road`, `backdoor`, `rain-minor`, `aeolian-walk`
- `palette`: `rhodes-piano`, `piano-vibes`, `guitar-flute`, `rhodes-guitar`, `piano-musicbox`, `rhodes-choir`, `rhodes-trumpet`, `piano-clarinet`, `guitar-marimba`, `piano-kalimba`, `jazzguitar-vibes`
- `kit`: `dusty`(Rainy Window), `soft`(사이드스틱, 어두운 버스), `punch`(붐뱁), `tape`(포화·먹먹). energy로 후보가 갈린다
- `scale`: 멜로디 `pent`(펜타토닉) / `diatonic`(7음), `wow` 0.8-2.2 테이프 흔들림, `vinyl_db` -46..-40 바이닐 바닥 크기
- `bpm` 59-95(energy), `swing` 0.05-0.09, `key` -5..+5 (C 기준), `kick`/`comp`/`bassline` 0-3, `texture`(지정 없으면 vinyl·none·rain·night 중)
- `--chapters`: 구간별 무드 변화 JSON 배열(곡 순서). 챕터마다 energy·brightness·space 차이(±0.3), texture, lead(악기), drums(full/light/off), label. 주 구간(A·B·A2·B2)에 순서대로 나눠 담고(break는 앞 챕터를 잇는다), 키·템포·진행·팔레트는 곡 전체 그대로. 4개 이상이면 `long` 형식. 구간 시작·끝(초)은 `<genre>_<seed>.json`의 `score.sections`와 report.json `sections`. 형식은 `scripts/chapters.py`. 지금은 lofi만 반영(다른 장르는 무시)

**newage** (`presets/newage.py`, Tidewater와 같은 -16 LUFS 설정, 실측 약 -15)
- `pair`: 진행 두 개 조합 (tide/drift/dusk/lift/open/nocturne/lament/morning/glow/plateau/horizon/ember/hollow)
- `palette`: `piano-strings`, `piano-choir`, `harp-flute`, `guitar-piano`, `celesta-piano`, `piano-pad`, `rhodes-flute`, `piano-oboe`, `harp-clarinet`, `guitar-flute`, `harp-vibes`
- `form`: `classic`(intro4 A8 B8 C8 out4), `short`, `return`
- `bpm` 50-78(energy), `key` -4..+4 (D 기준), `arp` 0-4, `texture`(지정 없으면 ocean·birds·none 중)

**jazz** (`presets/jazz.py`, -15 LUFS, 초안: 레퍼런스 곡 승인 전)
- 스윙 8분, 피아노 rootless comping, 콘트라베이스 워킹(코드 첫 박 근음, 마지막 박 반음/5도 접근음), 브러시 킷(GM 40)
- `prog`(head): `two-five`, `rhythm`, `backdoor`, `turnaround` / minor `falling-leaves`, `minor-blue`. bridge는 head에 맞춰 정해짐
- `palette`: `piano-trio`, `vibes-trio`, `tenor-quartet`, `trumpet-quartet`, `guitar-trio`
- `form`: `standard`(intro4 A8 A8 B8 A8 피아노솔로8 A8 out4), `long`(솔로 16)
- `bpm` 86-144(energy), `key` -5..+3, `swing` 0.12-0.16, `brushes` swirl(energy<0.4)/ride, `texture`(지정 없으면 none·vinyl·night·rain 중, none 비중 2/5)

**chiptune** (`presets/chiptune.py`, -14 LUFS, 초안: 레퍼런스 곡 승인 전)
- 전부 DSP: 사각파 리드(늦게 걸리는 vibrato + 3/4박 echo), 사각파 아르페지오, 4bit 삼각파 베이스, 노이즈 드럼. 고음은 low-pass로 깎는다
- `pair`: hero/town/sky/mixo, minor cave/quest
- `form`: `classic`, `long`, `lead_duty`·`arp_duty` 0.125-0.5, `arp_rate` 4/6, `bassline` octave/root-fifth/pulse
- `bpm` 96-140(energy), `half_time`(energy<0.3)

**bossa** (`presets/bossa.py`, -15 LUFS, 초안: 레퍼런스 곡 승인 전)
- 스트레이트 8분, 나일론 기타 comping(2마디 싱코페이션 패턴 4종), 콘트라베이스 근음-5도 점4분, 림 클릭 보사 클라베(3-2/2-3)·셰이커·작은 킥
- `prog`(head): `sunny-two-five`, `terrace`, `promenade`, `side-step` / minor `saudade`, `low-tide`. bridge는 head에 맞춰 정해짐
- `palette`: `guitar-flute`, `guitar-vibes`, `guitar-piano`(현악 패드), `guitar-trumpet`, `guitar-clarinet`(현악 패드), `guitar-sax`, `guitar-solo`
- `form`: `standard`(intro4 A8 A8 B8 A8 솔로8 A8 out4), `long`(솔로 16), `bpm` 99-131(energy), `texture`(지정 없으면 none·ocean·birds 중)

## 품질 검사 (`scripts/qc.py`)

단독 실행도 된다: `python3 qc.py track.mp3 --genre lofi`. 하드 체크 하나라도 실패하면 탈락.

| 체크 | 기준 |
|---|---|
| loudness | integrated LUFS가 장르 목표 ±1 LU (lofi -14, newage -15, jazz -15, bossa -15, chiptune -14) |
| true_peak | ≤ -0.1 dBTP (4x oversampling) |
| clipping | full scale 샘플 < 0.001% |
| silence | 곡 본문에 2초 넘는 -50 dBFS 이하 구간 없음 |
| stereo | L/R 상관 > 0.2 (모노 호환) |
| crest / loudness range | 장르 창 안 (과압축·과다이내믹 방지) |
| spectrum | low/mid/high 에너지 비율이 장르 창 안 |
| harmony | 멜로디의 코드 반음 충돌 ≤ 8%, 키 밖 음 ≤ 5% |

창은 두 레퍼런스 실측값에 여유를 둬서 정했다. jazz·bossa·chiptune은 레퍼런스 곡이 승인되기 전이라 창을 넓게 둔 초안이다. 값과 근거는 [references/quality-bar.md](references/quality-bar.md). 점수(0-100)는 통과한 변주끼리 순위를 매기는 용도다. 다만 점수는 레퍼런스에 가까울수록 높아서, 여러 곡을 계속 만드는 앱은 1위만 고르면 곡들이 서로 닮는다. 그런 앱은 통과작 중에서 최근 곡과 가장 다른 것을 고르는 편이 낫다(dkdk-tape 워커가 그렇게 한다). **QC는 기술적 결함을 거르는 장치지 귀를 대신하지 않는다.** 사용자 피드백으로 기준이 바뀌면 quality-bar.md와 `PROFILES`를 같이 고친다.

## preset 추가 / 수정

- 새 장르는 `presets/<genre>.py`에 `plan(seed) -> dict`, `render(plan, out_path) -> score dict`를 구현하고 `make.py`의 `GENRES`, `qc.py`의 `PROFILES`에 등록한다.
- 코드 진행·리듬은 bank에 추가만 한다. 진행을 추가하면 같은 seed의 기존 결과가 바뀔 수 있으니, 승인된 곡은 해당 커밋 + seed로 기록하거나 fixed preset(`rainy_window.py`처럼)으로 박제한다.
- DSP 음색 함수는 `engine.py`. 여기를 바꾸면 모든 장르 음색이 바뀌므로 레퍼런스 두 곡을 다시 렌더해 QC 지표가 그대로인지 확인한다.

## 알려진 약점

- 피아노 음색은 FluidR3 GM 수준. 더 좋은 SoundFont(예: Salamander Grand, GeneralUser GS)를 `MUSIC_SF2`로 지정하면 엔진 수정 없이 바뀐다. 바꾼 뒤엔 레퍼런스 QC를 다시 본다.
- 장르는 다섯 개(jazz·bossa·chiptune은 초안). 질감은 6종(vinyl, rain, fire, birds, night, ocean). 곡 길이는 약 2-2.5분(`form=long`/`return`으로 조금 더 길게).
