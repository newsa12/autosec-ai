from flask import Flask
from config import Config
from app.models.analysis import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    
    # 함수 내에 선언 -> 지연 로딩(lazy import)
    from app.routes.views import main_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')


    # HTTP 요청 없이 DB 사용하기 위해 app_context를 수동으로 생성
    with app.app_context():
        db.create_all()

    return app