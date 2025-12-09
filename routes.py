from flask import Blueprint


#建立一個藍圖blueprint 名子叫api
api_bp = Blueprint('api', __name__)

# 這裡之後會放所有路由
@api_bp.route('/test')
def test():
    return {'message': '後端活著。 API正常!'}