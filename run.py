from app import create_app

app = create_app()

# python run.py로 직접 실행할 때만 동작
if __name__ == '__main__':
    app.run(debug=True)
