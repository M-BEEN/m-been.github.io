# m-been.github.io

GitHub Pages **User Page** — 루트 도메인(`https://m-been.github.io`)을 담당한다.

블로그 본체는 [M-BEEN/blog-kr](https://github.com/M-BEEN/blog-kr) 이며 `https://m-been.github.io/blog-kr/` 로 배포된다.
이 저장소는 콘텐츠를 갖지 않고, **루트에서만 유효한 파일들**을 서빙하는 역할만 한다.

## 왜 필요한가

`ads.txt`, `robots.txt`, 그리고 검색엔진에 제출하는 `sitemap.xml` 은 **도메인 루트에서만 유효**하다.
`/blog-kr/ads.txt` 처럼 하위 경로에 두면 크롤러와 AdSense가 읽지 않는다.
Project Page(blog-kr) 만으로는 루트를 점유할 수 없어 별도의 User Page 저장소가 필요하다.

| 파일 | 역할 |
|---|---|
| `index.html` | 루트 접속 → `/blog-kr/` 로 리다이렉트. `canonical` 로 중복 색인 방지 |
| `robots.txt` | 크롤러 허용 + 사이트맵 위치 안내 |
| `sitemap.xml` | 사이트맵 인덱스. 실제 글 목록인 `/blog-kr/sitemap.xml` 을 가리킨다 |
| `ads.txt` | AdSense 게시자 ID. **승인 후** 주석을 풀어 채운다 |
| `.nojekyll` | Jekyll 빌드를 끄고 파일을 그대로 서빙 |

## 배포

`main` 에 push 하면 GitHub Pages가 그대로 배포한다 (Settings → Pages → Source: `main` / `/`).
글이 추가돼도 이 저장소는 건드릴 필요가 없다 — 하위 사이트맵이 자동으로 갱신된다.

## AdSense 승인 후 할 일

1. `ads.txt` 에서 `# google.com, pub-...` 줄의 `#` 제거하고 게시자 ID 입력
2. blog-kr 의 `hugo.toml` 에서 `adsenseClient = "ca-pub-..."` 채우기 (자동광고 스크립트 활성화)
