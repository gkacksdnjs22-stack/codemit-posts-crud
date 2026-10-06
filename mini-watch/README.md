# Flask + PostgreSQL 게시판

## 역할

- `general/app.py`: 앱 생성, Blueprint·요청 기록 등록, 실행
- `general/routes/posts.py`: 게시판 HTTP 요청·응답
- `general/repositories/posts.py`: 게시글 SQL
- `general/post_rules.py`: 작성·수정 입력 검사
- `general/db.py`: `.env`를 읽어 DB 연결
- `general/request_logging.py`: 요청 기록을 감시 서버에 전달
- `general/routes/legacy.py`: 수업의 로그인·게시글 JSON API와 단계 화면
- `monitor/backend`: 수업 감시 서버 코드, `monitor_db`에 기록 저장

## 실행 (현재 작업 폴더의 PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r mini-watch\general\requirements.txt
.\.venv\Scripts\python.exe -m pip install -r mini-watch\monitor\backend\requirements.txt
```

각 서비스의 `.env.example`을 `.env`로 복사해 DB 정보를 입력합니다.
일반 서비스는 `general_db`, 감시 서비스는 `monitor_db`를 사용합니다.
`.env`는 Git에서 제외됩니다.

새 DB 환경에서는 각 `sql/create_database.sql`을 먼저 실행합니다.
일반 DB에서 `sql/posts.sql`, `sql/users.sql`, `sql/posts_sequence.sql`을,
감시 DB에서 `sql/http_events.sql`을 실행합니다.
테이블 생성 SQL은 초기 설치용입니다. 기존 테이블이 있는 DB에는 다시 실행하지 않습니다.

서로 다른 터미널에서 실행합니다.

```powershell
.\.venv\Scripts\python.exe mini-watch\monitor\backend\app.py
```

```powershell
.\.venv\Scripts\python.exe mini-watch\general\app.py
```

게시판: http://127.0.0.1:5000/

감시 기록: http://127.0.0.1:5300/api/events

수업 화면: http://127.0.0.1:5000/index.html

기존 수업 원본 `C:\work\mini-watch-day03-start`는 유지했습니다.
감시 포트는 원본과 충돌을 피하려고 5300으로 설정했습니다.
로그인 API `/auth/login`, 게시글 JSON API `/posts/<id>`를 유지했습니다.
로그인 전용 화면은 선택 과제이며 아직 추가하지 않았습니다.

## 확인 순서

1. 목록에서 작성 → 상세 → 목록으로 이동합니다.
2. 제목·내용이 공백뿐이면 400이며 DB가 변경되지 않는지 확인합니다.
3. 수정 폼의 기존 값과 저장 결과를 확인합니다.
4. 삭제 확인에서 취소 시 글이 유지되는지 확인합니다.
5. 삭제 확정 시 목록에서 없어지고 상세·수정·삭제 주소가 404인지 확인합니다.
6. 감시 기록에서 method, path, status_code가 수집되는지 확인합니다.

저장·수정·삭제 성공 후 응답은 303이며, 상세 화면 새로고침은 저장을 반복하지 않습니다.
