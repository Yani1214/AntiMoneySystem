# coding=utf-8
import datetime
import bcrypt

from flask_cors import CORS
from flask_restful import Api

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from uuid import uuid4
from collections import defaultdict
# from sqlalchemy.orm import sessionmaker
import json
import re

app = Flask(__name__)
CORS(app)
api = Api(app)


# 设置数据库连接地址
# 设置第一个数据库连接地址
DB_URI_1 = 'mysql+pymysql://root:XYZ67520x@localhost:3306/mealpass?charset=utf8mb4'
app.config['SQLALCHEMY_BINDS'] = {
    'db1': DB_URI_1,
    'db2': 'mysql+pymysql://root:XYZ67520x@localhost:3306/test?charset=utf8mb4'
}
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

def clean_card_number(card):
    # 去除所有空白字符，包括空格、制表符等
    return re.sub(r'\s+', '', card)


# 创建用户表
class User(db.Model):
    __bind_key__ = 'db1'
    __tablename__ = 'user'
    id = db.Column(db.String(36), primary_key=True, unique=True, nullable=False)
    avatar = db.Column(db.Text, default='https://gravatar.kuibu.net/avatar/5c04c6164bbf04f3e6bcbd01dfd00e03?s=100')
    username = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, default='Vchs0bbdk2pr/Ac6DsHruw==')
    email = db.Column(db.String(255))
    nickname = db.Column(db.String(255))
    status = db.Column(db.String(255), default='1')
    createdAt = db.Column(db.DateTime, default=datetime.datetime.now)
    updatedAt = db.Column(db.DateTime, default=datetime.datetime.now)
    remark = db.Column(db.String(255), default='')


@app.route('/')
def hello_world():
    hashed = bcrypt.hashpw("123456".encode('utf-8'), salt)
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
    
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({
            "code": 400,
            "msg": "用户已存在"
        })
    
    new_user = User(id=user_id, username=username, password=en_password, nickname=nickname, email=email)
    db.session.add(new_user)
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
    
    user = User.query.filter_by(username=username).first()
    if user:
        try:
            is_valid = bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8'))
            if is_valid:
                return jsonify({
                    "code": 200,
                    "msg": "登录成功",
                    "userInfo": {
                        "id": user.id,
                        "avatar": user.avatar,
                        "nickname": user.nickname
                    }
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

    
#############################################################################
# 定义第二个数据库的模型
class People(db.Model):
    __bind_key__ = 'db2'
    __tablename__ = 'people'
    id = db.Column(db.Integer, primary_key=True)
    person_number = db.Column(db.String(255))
    person_name = db.Column(db.String(255))
    person_id = db.Column(db.String(255))
    person_card = db.Column(db.String(255))
    person_account = db.Column(db.String(255))
    bank_name = db.Column(db.String(255))
    task_id = db.Column(db.String(255))
    summary = db.Column(db.String(255))
    label = db.Column(db.Integer)
    # model_result = db.Column(db.String(255))
    manual_review = db.Column(db.String(255))

    def __init__(self, person_number, person_name, person_id, person_card, person_account, bank_name, task_id, summary, label, manual_review=None):
        self.person_number = person_number
        self.person_name = person_name
        self.person_id = person_id
        self.person_card = person_card
        self.person_account = person_account
        self.bank_name = bank_name
        self.task_id = task_id
        self.summary = summary
        self.label = label
        self.manual_review = manual_review


@app.route('/getUserInfo', methods=['GET'])
def get_user_info():
    query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)

    try:
        base_query = People.query
        if query:
            base_query = base_query.filter(People.person_name.like(f"%{query}%"))

        users = base_query.all()
        
        user_dict = defaultdict(lambda: {
            'person_number': None,
            'person_name': None,
            'person_id': None,
            'person_card': [],
            'person_account': [],
            'labels': [],
            'manual_review': None,
        })

        for user in users:
            if user_dict[user.person_number]['person_number'] is None:
                user_dict[user.person_number]['person_number'] = user.person_number
                user_dict[user.person_number]['person_name'] = user.person_name
                user_dict[user.person_number]['person_id'] = user.person_id
                user_dict[user.person_number]['manual_review'] = user.manual_review

            cleaned_person_card = user.person_card.strip() if user.person_card else None
            cleaned_person_account = user.person_account.strip() if user.person_account else None

            if cleaned_person_card:
                user_dict[user.person_number]['person_card'].append(cleaned_person_card)
                user_dict[user.person_number]['labels'].append(user.label)  # 添加标签
            if cleaned_person_account:
                user_dict[user.person_number]['person_account'].append(cleaned_person_account)

        merged_results = []
        for key, value in user_dict.items():
            merged_results.append({
                'person_number': value['person_number'],
                'person_name': value['person_name'],
                'person_id': value['person_id'],
                'person_card': value['person_card'],  # 保持顺序
                'person_account': value['person_account'],  # 保持顺序
                'labels': value['labels'],  # 保持顺序
                'manual_review': value['manual_review'],
            })

        total = len(merged_results)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_results = merged_results[start:end]

        return jsonify({
            'total': total,
            'items': paginated_results
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            'error': 'An error occurred while fetching user info.'
        }), 500


@app.route('/saveManualReview', methods=['POST'])
def save_manual_review():
    try:
        data = request.json
        person_number = data.get('person_number', None)
        manual_review = data.get('manual_review', None)
        print("Received data:", data)  # 打印请求数据
        if not person_number or not manual_review:
            return jsonify({'error': 'Invalid input.'}), 400

        # 使用 db2 绑定查找所有对应的用户记录 .with_bind_key('db2')
        users = People.query.filter_by(person_number=person_number).all()
        if not users:
            return jsonify({'error': 'User not found.'}), 404

        # 更新所有记录的人工审核字段
        for user in users:
            user.manual_review = manual_review

        # 使用 db2 绑定进行提交
        # db.get_engine(app, bind='db2').execute(db.session.commit())
        db.session.commit()
        return jsonify({'message': 'Manual review saved successfully.'}), 200

    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()  # 出错时回滚
        return jsonify({'error': 'An error occurred while saving manual review.'}), 500
    
@app.route('/getSuspicionData', methods=['GET'])
def get_suspicion_data():
    try:
        with open('NNModel/caseAnalysis/data/suspicion_card.json', 'r') as file:
            suspicion_data = json.load(file)
        return jsonify(suspicion_data)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            'error': 'An error occurred while fetching suspicion data.'
        }), 500
    
@app.route('/updateLabel', methods=['POST'])
def update_label():
    try:
        data = request.get_json()
        person_number = data['person_number']
        card = clean_card_number(data['card'])
        label = data['label']
        print(label)
        
        # 打印接收到的数据
        print(f"Received data: person_number={person_number}, card={card}, label={label}")
        
        # 更新数据库，找到符合 person_number 的所有记录
        users = People.query.filter_by(person_number=person_number).all()
        
        # 打印查询到的用户记录
        print(f"Found users: {users}")
        
        if users:
            matched_users = [user for user in users if clean_card_number(user.person_card) == card]
            if matched_users:
                for user in matched_users:
                    print("label")
                    print(label)
                    user.label = label
                db.session.commit()
                return jsonify({'success': True})
            else:
                return jsonify({'success': False, 'message': 'Card not found'}), 404
        else:
            return jsonify({'success': False, 'message': 'User not found'}), 404
    except Exception as e:
        db.session.rollback()  # 出现错误时回滚事务
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while updating label.'}), 500
#######################################注册蓝图#################################
from process import upload_blueprint,byhand_blueprint
from caseAnalysis import analysis_blueprint
from charts import charts_blueprint

app.register_blueprint(upload_blueprint)
app.register_blueprint(byhand_blueprint)
app.register_blueprint(analysis_blueprint)
app.register_blueprint(charts_blueprint)

################################################################################

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3091)
