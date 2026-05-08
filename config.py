from dotenv import load_dotenv
import os

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    # sqlite:////home/park/autosec_ai/autosec.db 형태로 반환
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'autosec.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")