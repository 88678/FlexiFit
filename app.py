from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "後端成功運行"

if __name__ == '__main__':
    app.run(debug=True)