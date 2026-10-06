from flask import Blueprint, request, render_template
from werkzeug.security import check_password_hash
from repositories.posts import find_post
from repositories.users import find_user

legacy_bp = Blueprint("legacy", __name__)


@legacy_bp.get("/index.html")
def index_file():
    return render_template("lessons.html")



@legacy_bp.get("/step-<int:step>.html")
def step_page(step):
    if step < 1 or step > 6:
        return {"error": "단계 페이지를 찾을 수 없습니다."}, 404
    return render_template(f"step-{step:02d}.html")



@legacy_bp.post("/auth/login")
def login():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return {"error": "아이디와 비밀번호를 JSON으로 보내 주세요."}, 400

    username = data.get("username")
    password = data.get("password")
    if not isinstance(username, str) or not isinstance(password, str):
        return {"error": "아이디와 비밀번호를 문자열로 보내 주세요."}, 400
    if not username.strip() or not password.strip():
        return {"error": "아이디와 비밀번호를 모두 입력해 주세요."}, 400

    user = find_user(username.strip())
    if user is None or not check_password_hash(user["password_hash"], password):
        return {"error": "아이디 또는 비밀번호가 올바르지 않습니다."}, 401

    return {
        "message": "로그인 성공",
        "user": {"id": user["id"], "username": user["username"]},
    }



@legacy_bp.get("/posts/<int:post_id>")
def get_post(post_id):
    post = find_post(post_id)
    if post is None:
        return {"error": "게시글을 찾을 수 없습니다."}, 404
    return post

