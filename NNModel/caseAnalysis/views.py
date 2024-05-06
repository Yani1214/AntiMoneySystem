from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from config import DevelopmentConfig

from main import predict

############
# 初始化操作 #
############
app = Flask(__name__)
# 根据运行环境选择性地加载配置类
app.config.from_object(DevelopmentConfig)  # 或者 ProductionConfig
print(app.config['SQLALCHEMY_DATABASE_URI'])  # 获取配置选项的值
print(app.config['DEBUG'])  # 获取 DEBUG 配置选项的值
# 数据库初始化
db = SQLAlchemy()
Base = declarative_base()
db.init_app(app)


##########
# 路由函数 #
##########
@app.route('/index/info')
def index():
    return "网站主页"


@app.route('/detect/<card>', methods=["GET", "POST"])
def detect(card):
    # if request.method == "GET":
    #     card = request.args.get("card_id")
    #     # comment = request.values.get("content")
    # if request.method == "POST":
    #     if request.content_type.startswith('application/json'):
    #         # comment = request.get_json()["content"]
    #         card = request.json.get('card_id')
    #     elif request.content_type.startswith('multipart/form-data'):
    #         card = request.form.get('card_id')
    #     else:
    #         card = request.values.get("card_id")
    print(card)
    print(type(card))
    ret = predict(card, 2)
    return ret


if __name__ == '__main__':
    app.run()
