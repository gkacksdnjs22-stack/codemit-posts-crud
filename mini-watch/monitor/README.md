# 수업 감시 서비스 연결

수업 감시 코드를 `C:\work\mini-watch-day03-start\monitor\backend`에서
현재 프로젝트의 `monitor/backend`로 복사했습니다. 원본은 유지했습니다.
기존 서비스와 포트 충돌을 피하기 위해 복사한 서버는 5300번을 사용합니다.
현재 일반 서비스는 `http://127.0.0.1:5300/api/events`로
method, path, status_code를 포함한 요청 기록을 JSON으로 전달합니다.
같은 주소에 GET 요청을 보내면 최근 기록을 확인할 수 있습니다.
수집 기록은 별도 PostgreSQL 데이터베이스 `monitor_db`에 저장합니다.

감시 서버를 끄더라도 일반 서비스는 계속 동작합니다.
수업의 일반 서비스 로그인 API·연습 파일·SQL·화면 자료도 현재 프로젝트에 통합했습니다.
