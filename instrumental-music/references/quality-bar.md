# Quality bar

2026-11-11 사용자 승인: "Rainy Window"(lo-fi), "Tidewater"(new age) 두 곡 모두 "너무 훌륭하다, 항상 이 정도 퀄리티를 확정하고 싶다".

## 레퍼런스 실측 (qc.py)

| 지표 | Rainy Window | Tidewater | lofi 창 | newage 창 |
|---|---|---|---|---|
| integrated LUFS | -13.97 | -15.00 | -14 ±1 | -15 ±1 |
| true peak dBTP | -1.2 | -2.6 | ≤ -0.1 | ≤ -0.1 |
| crest dB | 14.7 | 15.3 | 9-20 | 10-22 |
| loudness range LU | 3.7 | 2.4 | 1.5-12 | 1.0-14 |
| low (<250 Hz) | 0.48 | 0.46 | 0.30-0.80 | 0.15-0.75 |
| mid (250-4k) | 0.51 | 0.52 | 0.18-0.65 | 0.20-0.80 |
| high (>4k) | 0.004 | 0.020 | 0.001-0.08 | 0.002-0.08 |
| stereo corr | 0.80 | 0.34 | > 0.2 | > 0.2 |
| 길이 s | 123 | 125 | 90-330 | 90-360 |

`make.py --genre rainy-window|tidewater`로 다시 렌더한 결과도 위 값과 소수 둘째 자리까지 같다 (원본 mp3와 비교).

Tidewater는 `loudnorm I=-16` 설정이었지만 실측 -15.0 LUFS다. 사용자가 승인한 소리가 이쪽이므로 QC 목표를 -15로 둔다.

## QC 오탐 점검

통과한 곡을 일부러 망가뜨려 확인:
- +12 dB → loudness, true_peak, clipping 실패
- 40-46초 무음 → silence 실패
- 한쪽 채널 위상 반전 → stereo, spectrum 실패

## 생성 변주 검증 (seed 100-102 lofi, 300-302 newage)

6/6 첫 시도에 통과, 멜로디 반음 충돌 0%, 키 밖 음 0%. 같은 seed 재렌더 시 디코딩 PCM md5 동일.
