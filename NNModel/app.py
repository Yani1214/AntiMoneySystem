# coding=utf-8
import datetime
import bcrypt

from flask_cors import CORS
from flask_restful import Api

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from uuid import uuid4

app = Flask(__name__)
CORS(app)
api = Api(app)


# 设置数据库连接地址
DB_URI = 'mysql+pymysql://root:12345678@localhost:3306/mealpass?charset=utf8mb4'
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
# 是否追踪数据库修改，一般不开启, 会影响性能
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 是否显示底层执行的SQL语句
app.config['SQLALCHEMY_ECHO'] = True

app.config['DEBUG'] = True

# 初始化db,关联flask 项目
db = SQLAlchemy(app)

metadata_obj = MetaData()

# 生成盐
salt = bcrypt.gensalt()

# 创建用户表
user_table = Table(
    "user",
    metadata_obj,
    Column('id', String(36), nullable=False, unique=True, comment='ID'),
    Column('avatar', Text, nullable=True, default='', comment='用户头像'),
    Column('username', String(255), nullable=False, comment='用户名'),
    Column('password', String(255), nullable=False, default='Vchs0bbdk2pr/Ac6DsHruw==', comment='密码'),
    Column('email', String(255), comment='邮箱'),
    Column('nickname', String(255), comment='昵称'),
    Column('status', String(255), default='1', comment='状态'),
    Column('createdAt', DateTime, default=datetime.datetime.now(), comment='创建时间'),
    Column('updatedAt', DateTime, default=datetime.datetime.now(), comment='更新时间'),
    Column('remark', String(255), default='', comment='用户备注')
)


@app.route('/')
def hello_world():
    hashed = bcrypt.hashpw("admin".encode('utf-8'), salt)
    print(f"Hashed Password: {hashed.decode('utf-8')}")
    # 返回加密后的字符串
    return hashed


@app.route('/register', methods=["POST"])
def user_register():
    user_form = request.get_json()
    user_id = uuid4()
    username = user_form["username"]
    password = user_form["password"]
    nickname = user_form["nickname"]
    email = user_form["email"]
    en_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    select_user = select(user_table).filter_by(username=username)
    select_user_result = db.session.execute(select_user).fetchall()
    if len(select_user_result) > 0:
        return jsonify({
            "code": 400,
            "msg": "用户已存在"
        })
    insert_user = insert(user_table).values(id=user_id, username=username, password=en_password, nickname=nickname, email=email, status=1)
    db.session.execute(insert_user)
    db.session.commit()
    return jsonify({
        "code": 200,
        "msg": "success",
        "status": 1
    })


@app.route('/login', methods=['POST'])
def user_login():
    user_form = request.get_json()
    username = user_form["username"]
    password = user_form["password"]
    select_user = select(user_table).filter_by(username=username)
    result = db.session.execute(select_user).fetchall()
    print(len(result))
    if len(result) > 0:
        user = result[0]
        try:
            is_valid = bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8'))
            if is_valid:
                return jsonify({
                    "code": 200,
                    "msg": "登录成功"
                })
            else:
                return jsonify({
                    "code": 400,
                    "msg": "密码错误"
                })
        except ValueError:
            return jsonify({
                    "code": 400,
                    "msg": "登录失败"
                })
    else:
        return jsonify({
            "code": 400,
            "msg": "用户名或密码错误"
        })


#######################################注册蓝图#################################
from process import upload_blueprint,byhand_blueprint
from caseAnalysis import analysis_blueprint

app.register_blueprint(upload_blueprint)
app.register_blueprint(byhand_blueprint)
app.register_blueprint(analysis_blueprint)

################################################################################

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3091)
