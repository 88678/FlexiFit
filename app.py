from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config   
from flask_cors import CORS

# 建立 flask 應用
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)  # 允許 React 連線

# 建立資料庫連線
db = SQLAlchemy(app)
migrate = Migrate(app, db)



# ====== 關鍵：延遲 import，避免循環 ======
# 千萬不要在上面 import models 或 routes！
# 在最下面才 import routes，確保 db 和 models 已經定義好
with app.app_context():     
    from models import *    # 匯入資料表定義(必須在db建立後)
    # from routes import api_bp   # 註冊 API 路由（必須在 models 匯入後）
    # app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def home():
    return "<h1>首頁</h1> <h3>後端啟動</h3>"

if __name__ == '__main__':
    app.run(debug=True)