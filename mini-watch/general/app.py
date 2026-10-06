from flask import Flask

from routes.posts import posts_bp
from request_logging import register_request_logging
from routes.legacy import legacy_bp

app = Flask(__name__)
app.json.ensure_ascii = False
app.register_blueprint(posts_bp)
app.register_blueprint(legacy_bp)
register_request_logging(app)


if __name__ == "__main__":
    app.run(debug=True)
