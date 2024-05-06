from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_restful import Resource

app = Flask(__name__)
CORS(app)
api = Api(app)


@app.route('/', methods=["GET"])
def index():
    return "Welcome to API v1, try /hello."

#################################################################################

# class Hello(Resource):
#     @staticmethod
#     def get():
#         return "[get] hello flask"

#     @staticmethod
#     def post():
#         return "[post] hello flask"


# api.add_resource(Hello, '/hello')

#######################################注册蓝图#################################
from process import upload_blueprint,byhand_blueprint


app.register_blueprint(upload_blueprint)
app.register_blueprint(byhand_blueprint)

################################################################################

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=3091)
    # 连不上的原因:跨域,下载了浏览器插件后解决