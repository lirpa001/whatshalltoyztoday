from app import app
from deta import App

deta_app = App(app)

@app.route('/hello')
def hello():
    return "Hello, Deta!"

if __name__ == "__main__":
    app.run()
