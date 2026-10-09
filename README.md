# 수익률 레시피

https://yieldrecipe.com/ — 투자 계산과 데이터 검증을 배우는 Hugo 사이트입니다.

## 공개 범위

- `content/posts/`: 계산 예제와 실제 원문 검산. `content_kind`, `evidence_label`, 날짜, 설명이 필요합니다.
- `content/tools/`: 복리·비용·손실 예산 도구와 공식·입력·한계 설명.
- `assets/js/calculations.js`: 네트워크와 DOM에 의존하지 않는 계산 함수.
- `static/research/`: 다운로드 가능한 입력, Python 코드, 기대 결과.
- `archive/`: 발행에서 제외하거나 다시 쓴 원문. Hugo 출력에는 포함하지 않습니다.
- `static/brand/`: Higgsfield CLI / Recraft 벡터 원본, 웹용 파생 SVG와 PNG, 생성 이력.

일일·주간·자동 종목 보고서는 이 사이트의 발행 범위가 아닙니다. report-service의 내부 수집·분석·거래 신호 전달과 공개 학습 콘텐츠를 구분합니다. 기존 JSON 보고서가 들어오면 CI가 발행을 차단합니다. 이 검사는 사실관계의 자동 승인이나 애드센스 승인을 뜻하지 않습니다.

## 로컬 검증

Hugo extended 0.163.2, Node.js 24, Python 3.12를 사용합니다.

```sh
hugo --gc --minify
node --test tests/calculations.test.mjs
python -m unittest discover -s tests -v
python scripts/verify-editorial-archive.py public
python scripts/verify-learning-site.py public
python static/research/report-verdicts/reproduce.py --source-root .
python static/research/compounding/reproduce.py
python static/research/learning/reproduce.py
hugo server
```

PR에서도 같은 검사를 실행하고, main 빌드가 통과하면 GitHub Pages로 배포합니다. `hugo.toml`의 baseURL과 `static/CNAME`은 계속 yieldrecipe.com을 사용합니다. 원문 보존 검사는 SHA-256을 확인합니다. 기대 결과는 계산 로직에 맞춰 자동 갱신하지 말고 변경 이유와 독립 검산을 확인해야 합니다.

## 광고와 소유확인

AdSense 게시자 ID, ads.txt, Google·네이버 소유확인은 유지합니다. `adsenseEnabled = false`에서는 광고 스크립트를 요청하지 않습니다. 소유확인은 메타태그와 ads.txt로 할 수 있습니다. 실제 광고를 켜기 전 계정의 동의·개인정보 메시지 설정과 공개 방침을 맞추고, 검토한 글에만 `ad_eligible: true`를 지정해야 합니다. 도구·정책·목록·404에는 광고 코드를 출력하지 않습니다. 임의의 자체 쿠키 배너로 Google 인증 CMP 요건을 충족했다고 간주하지 않습니다.

참고: https://support.google.com/adsense/answer/7584263

## 콘텐츠 개편 기록

2026-10-09에 핵심 글 7편을 가상 예제 중심으로 다시 쓰고 13편을 보관했습니다. 검산 가능한 기존 글 2편은 유지했습니다. 새 계산 도구 3개, 학습 경로, 작성·정정 원칙을 추가했습니다. 수정 전 원문은 `archive/revisions/2026-10-09/manifest.json`, 제외 글은 `archive/manifest.json`으로 추적합니다. 근거 없는 수익 성과나 사람의 검수 이력을 만들어 넣지 않습니다.