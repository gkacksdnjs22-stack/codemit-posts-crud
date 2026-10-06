# 게시글 CRUD 실습

Flask, Jinja2, PostgreSQL로 작성·조회·수정·삭제 기능을 구현한 게시판입니다.
수업 프로젝트는 [`mini-watch/`](mini-watch/)에 있습니다.

- [실행 방법과 파일 역할](mini-watch/README.md)
- [일반 서비스](mini-watch/general/)
- [감시 서비스](mini-watch/monitor/backend/)
- [필수 체크리스트 검증 프로그램](mini-watch/verify_submission.py)

실제 DB 비밀번호는 Git에 포함하지 않습니다. 각 서비스의 `.env.example`을
`.env`로 복사하고 접속 정보를 입력한 뒤 README의 SQL과 실행 순서를 따릅니다.

검증 프로그램은 DB와 감시 서버가 실행된 환경에서 다음처럼 실행합니다.

```powershell
.\.venv\Scripts\python.exe mini-watch\verify_submission.py
```

검증용 게시글만 생성·수정·삭제하며 기존 게시글이 유지되는지도 확인합니다.
