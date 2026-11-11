---
name: instrumental-music
description: 외부 생성형 음악 AI(Suno 등) 없이 코드만으로 로우파이(lo-fi hip hop)·뉴에이지(ambient piano) instrumental 트랙을 만든다. 품질이 검증된 장르 preset + seed 재현 + 자동 품질 검사(LUFS·피크·클리핑·스펙트럼·다이내믹·화성 충돌) + 변주 N개 중 최고 선택. "로우파이 만들어줘", "뉴에이지 곡", "BGM 만들어", "instrumental 음악 생성", "lofi 트랙", "seed 42로 다시" 같은 요청이면 이 스킬을 쓴다.
---

# instrumental-music

Python MIDI(FluidSynth) + numpy DSP **hybrid 엔진**으로 곡을 렌더한다. 피아노·EP·스트링은 SoundFont로, 드럼·베이스·패드·벨·바이닐·파도 같은 질감은 DSP로 만들고, stem 레벨을 RMS로 맞춘 뒤 마스터링한다.

기준선은 사용자가 승인한 두 곡이다. 이 스킬의 목표는 **매번 그 품질을 보장하는 것**이다.

| 레퍼런스 | 장르 | 재현 명령 |
|---|---|---|
| Rainy Window | lo-fi, 74 BPM, C major ii-V-I-vi, EP + 피아노 멜로디 | `make.py --genre rainy-window` |
| Tidewater | new age, 66 BPM, D major, 피아노 아르페지오 + 스트링 + 벨 + 파도 | `make.py --genre tidewater` |

## 원칙

1. **sound chain은 고정, 작곡만 바꾼다.** 음색·이펙트 체인·stem 레벨·마스터 LUFS는 레퍼런스와 동일한 코드다. seed가 바꾸는 건 키, 템포, 스윙, 코드 진행(큐레이션된 bank), 곡 구조, 그루브, 멜로디뿐이다. 품질을 깨는 변수는 애초에 노출하지 않는다.
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
```

출력: `<genre>_<seed>.mp3`, `<genre>_<seed>.json`(plan·QC 지표·악보 요약), `report.json`(통과 여부·점수순). 3변주 기준 약 30-60초(병렬 렌더).

요청 처리 순서:
1. 장르를 lofi / newage 중 고른다. 둘 다 아니면 가장 가까운 쪽을 쓰고 그렇게 말한다(새 장르는 아래 "preset 추가").
2. `--variants 3`으로 돌린다. 분위기 요청(밝게, 느리게, 짧게)은 `--set`으로 반영한다: `bpm`, `key`(반음 offset), `prog`, `form`.
3. `report.json` 1위를 기본 추천으로, 나머지도 같이 전달한다. seed를 반드시 함께 알려준다.
4. 사용자가 고른 곡은 seed로 언제든 재현된다.

## preset 선택지

**lofi** (`presets/lofi.py`, -14 LUFS)
- `prog`: `ii-V-I-vi`(Rainy Window), `descending`, `minor-drift`, `neo-soul`
- `form`: `classic`(intro4 A8 B8 break4 A'8 out4), `straight`, `long`
- `bpm` 70-82, `swing` 0.05-0.09, `key` -4..+3 (C 기준), `kick`/`comp`/`bassline` 0-2, `keys_prog` 4=Rhodes 0=piano, `mel_prog` 0=piano 11=vibes, `vinyl` 4-7

**newage** (`presets/newage.py`, Tidewater와 같은 -16 LUFS 설정, 실측 약 -15)
- `pair` 0-4: 진행 두 개 조합 (tide/drift/dusk/lift/open)
- `form`: `classic`(intro4 A8 B8 C8 out4), `short`, `return`
- `bpm` 60-72, `key` -3..+3 (D 기준), `arp` 0-2

## 품질 검사 (`scripts/qc.py`)

단독 실행도 된다: `python3 qc.py track.mp3 --genre lofi`. 하드 체크 하나라도 실패하면 탈락.

| 체크 | 기준 |
|---|---|
| loudness | integrated LUFS가 장르 목표 ±1 LU (lofi -14, newage -15) |
| true_peak | ≤ -0.1 dBTP (4x oversampling) |
| clipping | full scale 샘플 < 0.001% |
| silence | 곡 본문에 2초 넘는 -50 dBFS 이하 구간 없음 |
| stereo | L/R 상관 > 0.2 (모노 호환) |
| crest / loudness range | 장르 창 안 (과압축·과다이내믹 방지) |
| spectrum | low/mid/high 에너지 비율이 장르 창 안 |
| harmony | 멜로디의 코드 반음 충돌 ≤ 8%, 키 밖 음 ≤ 5% |

창은 두 레퍼런스 실측값에 여유를 둬서 정했다. 값과 근거는 [references/quality-bar.md](references/quality-bar.md). 점수(0-100)는 통과한 변주끼리 순위를 매기는 용도다. **QC는 기술적 결함을 거르는 장치지 귀를 대신하지 않는다.** 사용자 피드백으로 기준이 바뀌면 quality-bar.md와 `PROFILES`를 같이 고친다.

## preset 추가 / 수정

- 새 장르는 `presets/<genre>.py`에 `plan(seed) -> dict`, `render(plan, out_path) -> score dict`를 구현하고 `make.py`의 `GENRES`, `qc.py`의 `PROFILES`에 등록한다.
- 코드 진행·리듬은 bank에 추가만 한다. 진행을 추가하면 같은 seed의 기존 결과가 바뀔 수 있으니, 승인된 곡은 해당 커밋 + seed로 기록하거나 fixed preset(`rainy_window.py`처럼)으로 박제한다.
- DSP 음색 함수는 `engine.py`. 여기를 바꾸면 모든 장르 음색이 바뀌므로 레퍼런스 두 곡을 다시 렌더해 QC 지표가 그대로인지 확인한다.

## 알려진 약점

- 피아노 음색은 FluidR3 GM 수준. 더 좋은 SoundFont(예: Salamander Grand, GeneralUser GS)를 `MUSIC_SF2`로 지정하면 엔진 수정 없이 바뀐다. 바꾼 뒤엔 레퍼런스 QC를 다시 본다.
- 장르는 두 개뿐. 곡 길이는 약 2-2.5분(`form=long`/`return`으로 조금 더 길게).
