from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config   

# 建立 flask 應用
app = Flask(__name__)
app.config.from_object(Config)

# 建立資料庫連線
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# 匯入資料表定義
from models import *

@app.route('/')
def hello():
    return "<h1>資料庫已連上</h1>"

if __name__ == '__main__':
    app.run(debug=True)