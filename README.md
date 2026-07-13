# 한국증시 레시피

한국 증시 일일 보고서·주간 분석·투자 상식 — **https://m-been.github.io/**

Hugo + GitHub Pages(User Page). 콘텐츠는 `report-service`(self-hosted-stack)가 매 거래일
아침 `content/posts/` 에 Markdown 을 push 하면 Actions 가 빌드·배포한다.

## 왜 이 저장소인가 (blog-kr 에서 이전)

원래 `M-BEEN/blog-kr` 에서 `m-been.github.io/blog-kr/` 로 서빙했는데, 서브디렉터리라
**구글이 사이트 이름을 지정할 수 없었다**(사이트명은 도메인 단위로만 인식). 그 결과 검색결과에
사이트명이 `GitHub Pages documentation` 으로 노출됐다. 루트(User Page)로 옮겨 해결했다.

덤으로 `ads.txt` · `robots.txt` · `sitemap.xml` 이 전부 Hugo 가 만드는 루트 파일이 되면서
따로 관리할 필요가 없어졌다(루트에서만 유효한 파일들이다).

기존 `/blog-kr/...` URL 은 blog-kr 저장소가 새 주소로 리다이렉트한다.

## 구조

```
content/posts/    일일보고서·주간레시피(자동 발행) + 투자상식(수기)
content/          about · contact · privacy
layouts/          전면 커스텀 (PaperMod 미사용)
static/           css · js · 브랜드 · ads.txt · 서치콘솔 인증 파일
hugo.toml         baseURL = https://m-been.github.io/
```

- 일일·주간 글은 **JSON front matter + 빈 본문**이고 `layouts/single.html` 이 표·섹션을 렌더한다.
- 투자상식 글은 평범한 YAML front matter + Markdown 본문. `categories: ["투자상식"]` 만 맞추면 된다.
- 미래 날짜 글은 `buildFuture=false` 라 그날이 되어야 공개된다(예약 발행).

## 로컬

```bash
hugo server -D          # http://localhost:1313
hugo --gc --minify      # 빌드 검증
```

## AdSense 승인 후

1. `static/ads.txt` — `# google.com, pub-...` 줄의 `#` 을 제거하고 게시자 ID 입력
2. `hugo.toml` — `adsenseClient = "ca-pub-..."` (자동광고 스크립트 활성화)

## 발행 파이프라인 (중요)

`report-service` 가 이 저장소를 **발행 전용 conduit** 으로 쓴다. 발행 스크립트가 push 전에
`git reset --hard origin/main` 을 하므로, **서버 체크아웃에 커밋 안 한 파일을 두면 날아간다.**
디자인·콘텐츠 수정은 반드시 작업 PC 에서 커밋·push 할 것.
