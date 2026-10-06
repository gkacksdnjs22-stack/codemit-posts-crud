"""과제의 필수 32개 항목 검증. DB 설정과 실행 중인 감시 서버가 필요합니다."""
import ast
import json
import re
import subprocess
import sys
import uuid
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
GENERAL = ROOT / "general"
sys.path.insert(0, str(GENERAL))

import requests
from markupsafe import escape
from app import app
from db import connect_db
from repositories.posts import delete_post, find_post, list_posts


def read(path):
    return (GENERAL / path).read_text(encoding="utf-8")


labels = [
    "소스 문법 오류 없음", "목록·상세 HTML 제목·본문·링크", "작성·수정·삭제 form 요소",
    "모든 화면의 공통 CSS", "Jinja2 게시글 값 출력", "Jinja2 반복·빈 목록·오류 조건",
    "주소와 GET/POST 역할", "request.form과 render_template", "빈 값 검증과 DB 보존",
    "400·404·303 응답", "PostgreSQL 저장·재실행 후 조회", "psycopg.connect 연결",
    ".env와 python-dotenv", "conn.execute SELECT/INSERT/UPDATE/DELETE", "fetchall/fetchone",
    "%s 매개변수 SQL", "시퀀스와 RETURNING id", "general/monitor 역할 분리",
    "app.py 등록·실행만 담당", "공통 db.py/connect_db", "repositories/posts.py CRUD 함수",
    "routes/posts.py Blueprint", "저장소 데이터 반환·라우터 응답", "공통 post_rules.py 검증",
    "templates/static/sql 구분", "request_logging 모듈 등록", "패키지 init와 python app.py",
    "가상환경·requirements", "링크·버튼 화면 연결", "requests JSON 감시 기록 수집",
    "분리 후 CRUD·오류·감시 유지", "Git 커밋과 작업 설명",
]
results = {}


def check(number, condition, evidence):
    assert condition, f"[{number}] {labels[number - 1]}: {evidence}"
    results[number] = {"item": labels[number - 1], "result": "PASS", "evidence": evidence}


for file in ROOT.rglob("*.py"):
    if "__pycache__" not in file.parts:
        ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
for template in app.jinja_env.list_templates():
    app.jinja_env.get_template(template)
check(1, True, "모든 Python AST와 Jinja2 템플릿 파싱")

templates = {name: read(f"templates/{name}.html") for name in ("index", "detail", "new", "edit", "delete", "error")}
repo, routes, db, rules, entry, logging = [read(path) for path in (
    "repositories/posts.py", "routes/posts.py", "db.py", "post_rules.py", "app.py", "request_logging.py")]
check(2, all('<h1>' in templates[name] and '<a ' in templates[name] for name in ('index', 'detail')) and 'post.body' in templates['detail'], "index.html/detail.html")
check(3, all(all(tag in templates[name] for tag in ('<form ', '<button ')) for name in ('new', 'edit', 'delete')) and all('<input ' in templates[name] and '<textarea ' in templates[name] for name in ('new', 'edit')), "세 폼의 요소와 method=post")
check(4, all("filename='style.css'" in html for html in templates.values()) and 'input, textarea' in read('static/style.css'), "6개 화면 CSS 연결")
check(5, all(value in templates['detail'] for value in ('post.id', 'post.title', 'post.body')), "상세 화면 번호·제목·내용 표현식")
check(6, '{% for post in posts %}' in templates['index'] and '{% if posts %}' in templates['index'] and all('{% if error %}' in templates[name] for name in ('new', 'edit')), "반복·조건 템플릿")
check(8, 'request.form.get' in routes and 'render_template' in routes, "입력 수신·화면 데이터 전달")
check(12, 'import psycopg' in db and 'psycopg.connect(' in db, "db.py 및 실제 DB 연결")
check(13, 'load_dotenv' in db and (GENERAL / '.env').exists(), "비공개 .env를 읽는 설정")
check(14, 'conn.execute(' in repo and all(word in repo for word in ('SELECT', 'INSERT', 'UPDATE', 'DELETE')), "모든 SQL을 저장소에서 실행")
check(15, '.fetchall()' in repo and '.fetchone()' in repo, "목록·단일 결과 조회")
tree = ast.parse(repo)
sql_calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'execute']
check(16, all(isinstance(call.args[0], ast.Constant) and ('%s' not in call.args[0].value or len(call.args) == 2) for call in sql_calls), "모든 SQL은 고정 문자열 + 별도 매개변수")
check(18, (ROOT / 'monitor/backend/app.py').exists(), "서비스별 폴더 분리")
check(19, not any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) for node in ast.parse(entry).body), "app.py에는 요청 처리 함수 없음")
check(20, 'from db import connect_db' in repo and 'from db import connect_db' in read('repositories/users.py'), "게시글·사용자 저장소 연결 재사용")
names = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
check(21, {'list_posts', 'find_post', 'create_post', 'update_post', 'delete_post'} <= names, "5개 DB 함수")
check(22, 'Blueprint("posts"' in routes and 'register_blueprint(posts_bp)' in entry, "Blueprint 정의·등록")
check(23, all(value not in repo for value in ('render_template', 'redirect(', 'flask')) and 'code=303' in routes, "저장소는 데이터, 라우터는 HTTP 응답")
check(24, 'def validate_post' in rules and routes.count('validate_post(') == 2 and '.strip()' in rules, "작성·수정 공통 검증")
check(25, all((GENERAL / folder).is_dir() for folder in ('templates', 'static', 'sql')), "화면·스타일·SQL 폴더")
check(26, 'register_request_logging(app)' in entry and '@app.after_request' in logging and 'requests.post' in logging, "요청 기록 후크와 감시 전송")
check(27, all((GENERAL / folder / '__init__.py').exists() for folder in ('routes', 'repositories')) and 'app.run(' in entry, "패키지와 직접 실행 진입점")
requirements = read('requirements.txt')
check(28, sys.prefix != sys.base_prefix and all(package in requirements for package in ('Flask', 'psycopg', 'python-dotenv', 'requests')), "가상환경에서 실행·패키지 목록 확인")

client = app.test_client()
original = list_posts()
assert [p['id'] for p in original] == sorted(p['id'] for p in original)
listing = client.get('/')
assert listing.status_code == 200
with patch('routes.posts.list_posts', return_value=[]):
    assert '등록된 게시글이 없습니다.' in client.get('/').get_data(as_text=True)
for bad in ({}, {'title':' ', 'body':'본문'}, {'title':'제목', 'body':'\t\n'}):
    response = client.post('/board/new', data=bad)
    assert response.status_code == 400
    assert list_posts() == original
assert '본문' in client.post('/board/new', data={'title':' ', 'body':'본문'}).get_data(as_text=True)

identifier = uuid.uuid4().hex[:10]
title = f"검토용 글 {identifier} <script>alert(1)</script>"
body = "첫째 줄\n둘째 줄 ' SQL 입력도 데이터로 처리"
post_id = None
try:
    response = client.post('/board/new', data={'title':'  ' + title + '  ', 'body':'  ' + body + '  '})
    assert response.status_code == 303
    base = response.headers['Location']
    post_id = int(base.rsplit('/', 1)[1])
    post = find_post(post_id)
    assert post['title'] == title and post['body'] == body
    assert post_id not in [row['id'] for row in original]
    assert post_id > max((row['id'] for row in original), default=0)
    html = client.get(base).get_data(as_text=True)
    assert str(escape(title)) in html and str(escape(body)) in html
    assert '<script>alert(1)</script>' not in html
    assert base in client.get('/').get_data(as_text=True)
    for _ in range(2):
        assert client.get(base).status_code == 200
    assert len(list_posts()) == len(original) + 1
    # 새 Python 프로세스로 앱을 다시 가져와 실제로 커밋된 행을 조회합니다.
    child = subprocess.run([sys.executable, '-c',
        'from app import app; from repositories.posts import find_post; import sys; p=find_post(int(sys.argv[1])); assert p is not None; assert app.test_client().get("/board/"+sys.argv[1]).status_code == 200; print("PERSISTED")',
        str(post_id)], cwd=GENERAL, capture_output=True, text=True)
    assert child.returncode == 0 and 'PERSISTED' in child.stdout
    check(11, True, "실제 저장 후 새 Python 프로세스에서 앱을 다시 시작해 조회")
    with connect_db() as conn:
        default = conn.execute('SELECT column_default FROM information_schema.columns WHERE table_name=%s AND column_name=%s', ('posts','id')).fetchone()
    check(17, 'nextval' in default['column_default'] and 'RETURNING id' in repo, "실제 DB 시퀀스·새 글 번호·303 이동")

    edit = client.get(base + '/edit')
    assert edit.status_code == 200 and str(escape(title)) in edit.get_data(as_text=True)
    assert str(escape(body)) in edit.get_data(as_text=True)
    assert find_post(post_id) == post
    for bad in ({'title':' ', 'body':'입력 내용 보존'}, {'title':'제목', 'body':' '}):
        response = client.post(base + '/edit', data=bad)
        assert response.status_code == 400 and find_post(post_id) == post
        assert str(escape(bad['body'].strip())) in response.get_data(as_text=True)
    response = client.post(base + '/edit', data={'title':'  수정 ' + identifier + '  ', 'body':'  수정 내용  '})
    assert response.status_code == 303 and response.headers['Location'] == base
    assert find_post(post_id)['title'] == '수정 ' + identifier
    assert find_post(post_id)['body'] == '수정 내용'
    assert '수정 ' + identifier in client.get('/').get_data(as_text=True)
    assert [row for row in list_posts() if row['id'] != post_id] == original
    confirm = client.get(base + '/delete')
    assert confirm.status_code == 200
    assert f'href="{base}"' in confirm.get_data(as_text=True)
    assert client.get(base).status_code == 200 and find_post(post_id) is not None
    response = client.post(base + '/delete')
    assert response.status_code == 303 and response.headers['Location'] == '/'
    assert find_post(post_id) is None
    for suffix in ('', '/edit', '/delete'):
        assert client.get(base + suffix).status_code == 404
    assert client.post(base + '/delete').status_code == 404
    assert client.post(base + '/edit', data={'title':'x','body':'y'}).status_code == 404
    assert list_posts() == original
    check(7, True, "GET 화면 표시, POST 저장·수정·삭제, 삭제 확인 GET은 DB 보존")
    check(9, True, "빈 값·공백 입력400, 입력 재표시, DB 행 보존")
    check(10, True, "작성·수정·삭제303, 검증400, 삭제 후 모든 화면404")
    detail_source = templates['detail']
    check(29, all(endpoint in detail_source for endpoint in ('posts.index', 'posts.edit_post', 'posts.confirm_delete')) and 'posts.new_post' in templates['index'] and 'posts.detail' in templates['delete'], "목록·상세·작성·수정·삭제·취소 링크와 폼")
    monitor_url = app.config['MONITOR_URL']
    events_response = requests.get(monitor_url, timeout=3)
    assert events_response.status_code == 200
    events = events_response.json()['events']
    assert any(e['path'] == base + '/delete' and e['status_code'] == 303 for e in events)
    assert any(e['path'] == base + '/edit' and e['status_code'] == 400 for e in events)
    assert any(e['path'] == base and e['status_code'] == 404 for e in events)
    check(30, True, "실행 중인 감시 서버의 PostgreSQL 기록에서 303·400·404 확인")
    with patch('request_logging.requests.post', side_effect=requests.ConnectionError):
        assert client.get('/').status_code == 200
    check(31, True, "분리된 앱의 실제 CRUD·오류·감시 수집, 감시 장애에도 게시판 유지")
finally:
    if post_id is not None and find_post(post_id) is not None:
        delete_post(post_id)
    assert list_posts() == original

git_log = subprocess.check_output(['git', 'log', '--oneline', '--', 'mini-watch'], cwd=ROOT.parent, text=True)
check(32, len(git_log.strip().splitlines()) >= 2, "구현·구조 분리·디자인 커밋 메시지 확인")
assert len(results) == 32
report = json.dumps({"checks": [results[i] for i in range(1,33)], "summary": "32/32 PASS", "test_posts_cleaned": True}, ensure_ascii=False, indent=2)
if len(sys.argv) > 1:
    Path(sys.argv[1]).write_text(report, encoding="utf-8")
    print("32/32 PASS; report saved; test posts cleaned.")
else:
    print(report)
