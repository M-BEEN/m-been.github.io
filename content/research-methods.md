---
title: "자료와 코드: 무엇을 다시 확인할 수 있나요?"
description: "실제 보고서 원문 집계와 가상 학습 예제를 구분하고, 파일별 실행 방법과 한계를 안내합니다."
lastmod: 2026-10-09
---

코드가 공개됐다는 사실만으로 글의 모든 주장이 재현되는 것은 아닙니다. 아래는 지금 내려받을 수 있는 입력·코드와 확인 가능한 범위입니다. **가상 예제의 정확한 계산과 실제 전략의 수익성은 서로 다른 검증입니다.**

## 실제 원문: 보고서 판정 집계

[보고서 판정 검산 글](/posts/note-verdict-backtest/)은 보관된 일일 보고서 61편에서 국내 종목 판정 558행을 다시 추출한 기록입니다. 실제 매매 체결 기록은 아닙니다.

- [판정 558행](/research/report-verdicts/verdicts.json)
- [원문 경로와 해시](/research/report-verdicts/source-index.json)
- [집계 코드](/research/report-verdicts/reproduce.py)
- [기대 결과](/research/report-verdicts/expected.json)

같은 폴더에 저장한 뒤 `python reproduce.py`를 실행합니다. 저장소 전체를 받았다면 `python static/research/report-verdicts/reproduce.py --source-root .`로 보관 원문 해시와 재추출 결과도 확인할 수 있습니다. Python 3.10 이상이며 별도 패키지는 필요 없습니다.

확인할 수 있는 것은 날짜별 건수, 코드·판정 추출과 날짜 조건입니다. 최초 공개 시각은 확보하지 못해 `null`이며, 수익률·매수 가능 시점·전략 성과는 이 자료로 재현되지 않습니다.

## 가상 예제: 수익률 분해와 복리

| 자료 | 파일 | 확인하는 범위 |
|---|---|---|
| 갭·장중 분해 | [CSV](/research/gap-overnight/sample.csv) · [코드](/research/gap-overnight/reproduce.py) · [기대 결과](/research/gap-overnight/sample-expected.json) | 네 행의 가상 가격에서 세 수익률 행 계산 |
| 복리·일간 배율 | [코드](/research/compounding/reproduce.py) | 세 가상 경로의 산술·기하평균과 이상적 일간 배율 계산 |
| 학습 노트 검산 | [코드](/research/learning/reproduce.py) · [기대 결과](/research/learning/expected.json) | 승률·평균, 비교 횟수, 비용, 수량, 비율 예제 |

갭 예제는 `python reproduce.py sample.csv`, 나머지는 해당 파일을 받은 폴더에서 `python reproduce.py`로 실행합니다. 동일한 이름의 파일을 서로 다른 폴더에 보관해 주세요. 출력과 기대 결과의 작은 부동소수점 차이는 허용 범위 안에서 비교합니다.

## 브라우저 계산 도구

[계산 모듈](https://github.com/M-BEEN/m-been.github.io/blob/main/assets/js/calculations.js)은 화면에서 사용하는 식을 제공합니다. [검증 테스트](https://github.com/M-BEEN/m-been.github.io/blob/main/tests/calculations.test.mjs)는 손계산 예제와 잘못된 입력, 0주와 전액 손실 등의 경계를 검사합니다.

사용자가 입력한 값은 계산 중 브라우저에만 있으며 새로고침하면 기본 예제로 돌아옵니다. CSV는 내려받기를 선택할 때 생성됩니다. CSV의 수치는 가정의 계산 결과이며 계좌 증빙이 아닙니다.

## 과거 자료와 정정

기존 일일·주간 보고서와 공개 범위에서 제외한 글은 [공개 저장소의 보관 폴더](https://github.com/M-BEEN/m-been.github.io/tree/main/archive)에 남깁니다. 해시는 원문 보존 상태를 확인하는 값으로 사실 인증이나 최초 게시 시각의 증거가 아닙니다.

기존 실험의 미재현 성과표는 현재 학습 글에서 철회하거나 가상 예제로 대체했습니다. 변경 이유와 수정 전 원문은 [개편 기록](/editorial-policy/#renewal)에 연결했습니다. 계산이 맞지 않는다면 임의로 입력을 고치지 말고 사용한 파일과 결과를 [연락처](/contact/)로 알려 주세요.
