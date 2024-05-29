import os
import json
import pymysql
import threading
from neo4j import GraphDatabase
from flask import Blueprint,request,jsonify,redirect, send_file, Response
from caseAnalysis import analysis_blueprint
from caseAnalysis.trace import kbknr
from caseAnalysis.main import predict
################################################基本配置#################################################
# 配置MySQL数据库连接参数
db_config = {
    'user': 'root',       # 替换为你的数据库用户名
    'password': 'XYZ67520x',   # 替换为你的数据库密码
    'host': 'localhost',           # 替换为你的数据库主机地址
    'database': 'anti-money',             # 数据库名称
    'charset': 'utf8mb4'           # 使用utf8mb4字符集
}

# 配置Neo4j数据库连接参数
uri = "bolt://localhost:7687"  # Neo4j默认URI
username = "neo4j"             # Neo4j默认用户名
password = "XYZ67520x"         
database = "test"
driver = GraphDatabase.driver(uri, auth=(username, password), database=database)

# 相关路径与参数
json_dir = 'NNModel/caseAnalysis/data/trans_flagged'
json_file = 'NNModel/caseAnalysis/data/high_risk_cards.txt'
suspicion_flag = {'DCLA', 'WCLA', 'MCLA', 'FT', 'SARRT'}
##################################################功能函数###############################################
def  load_suspicion_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    # 去掉每行的换行符并返回列表
    return [line.strip() for line in lines]

# def load_suspicion_data(suspicion_file_path):
#     with open(suspicion_file_path, 'r', encoding='utf-8') as file:
#         suspicion_data = json.load(file)
#     return suspicion_data

def process_json_file(file_path, suspicion_data):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    for item in data:
        trans_card = item.get("trans_card")
        cp_card = item.get("cp_card")
        if trans_card in suspicion_data or cp_card in suspicion_data:
            flagged = set(item.get("flagged", []))
            intersection = flagged & suspicion_flag
            if len(intersection) >= 3: # 交易标记交集个数大于等于3，则判断为可疑
                item["trans_is_suspicion"] = 1 # 可疑
            else:
                item["trans_is_suspicion"] = 0 # 不可疑
        else:
            item["trans_is_suspicion"] = 0 # 不可疑

    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def create_nodes_and_relationships(transaction, data):
    for record in data:
        trans_card = record.get('trans_card')
        trans_name = record.get('trans_name')
        id_number = record.get('id_number')
        trans_amount = record.get('trans_amount')
        label = record.get('trans_is_suspicion')
        trans_source = record.get('trans_source')
        py_indicator = record.get('py_indicator')
        cp_card = record.get('cp_card')
        cp_name = record.get('cp_name')
        cp_id = record.get('cp_id')


        # 创建节点1
        transaction.run(
            "MERGE (node1:Node1 {trans_card: $trans_card, trans_name: $trans_name, id_number: $id_number})",
            trans_card=trans_card, trans_name=trans_name, id_number=id_number
        )

        # 创建节点2
        transaction.run(
            "MERGE (node2:Node2 {cp_card: $cp_card, cp_name: $cp_name, cp_id: $cp_id})",
            cp_card=cp_card, cp_name=cp_name, cp_id=cp_id
        )

        # 创建节点1和节点2之间的关系，并设置关系属性
        if py_indicator == '1':
            transaction.run(
                "MATCH (node1:Node1 {trans_card: $trans_card}), (node2:Node2 {cp_card: $cp_card}) "
                "MERGE (node1)-[r:TRANSACTS_TO]->(node2) "
                "SET  r.trans_amount = $trans_amount, r.py_indicator = $py_indicator, "
                " r.label = $label, r.trans_source = $trans_source",
                trans_card=trans_card, cp_card=cp_card,
                trans_amount=trans_amount, py_indicator=py_indicator,
                label=label, trans_source=trans_source
            )
        elif py_indicator == '0':
            transaction.run(
                "MATCH (node1:Node1 {trans_card: $trans_card}), (node2:Node2 {cp_card: $cp_card}) "
                "MERGE (node2)-[r:TRANSACTS_TO]->(node1) "
                "SET  r.trans_amount = $trans_amount, r.py_indicator = $py_indicator, "
                " r.label = $label, r.trans_source = $trans_source",
                trans_card=trans_card, cp_card=cp_card,
                trans_amount=trans_amount, py_indicator=py_indicator,
                label=label, trans_source=trans_source
            )

def analysis_trans_data():
    '''
    1. 从anti-money数据库中搜集people表格中person_card列的所有值并进行去重处理，形成列表
    '''
    # 连接到数据库
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    try:
        # 执行查询语句，获取 person_card 列的所有值
        query = "SELECT person_card FROM people"
        cursor.execute(query)

        # 获取查询结果
        person_cards = cursor.fetchall()

        # 去重处理并形成列表
        unique_person_cards = list(set(card[0].strip() for card in person_cards if card[0].strip()))
        print(unique_person_cards)

        # '''
        # 2. 将列表传入 predict() 函数中进行批量处理，得到列表中每个卡号的嫌疑度，存储为json文件；
        # '''
        # for card in unique_person_cards:
        #     predict(card)

        # '''
        # 3. 对存储的json文件进行处理，对交易卡号和对手卡号赋值嫌疑度，并对flag标记进行判断，得出涉案交易，继续存储到json文件中
        # '''
        # suspicion_data = load_suspicion_data(json_file)
        
        # for root, _, files in os.walk(json_dir):
        #     for file in files:
        #         if file.endswith(".json"):
        #             file_path = os.path.join(root, file)
        #             print(file_path)
        #             process_json_file(file_path, suspicion_data)

        
        '''
        4. 将存有交易数据的json文件存入到neo4j中
        '''
        for root, _, files in os.walk(json_dir):
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json_to_neo4j = json.load(f)
                        # 将JSON数据存储到Neo4j中
                        with driver.session() as session:
                            session.write_transaction(create_nodes_and_relationships, json_to_neo4j)
                
            # 关闭数据库连接
            driver.close()

        print("已处理完成")

    finally:
        # 确保关闭游标和连接
        cursor.close()
        conn.close()
###########################################编写文件分析路由函数###########################################
@analysis_blueprint.route('/', methods=['POST'])
def analysis_file():
    data = request.json
    # 启动后台线程处理剩余的任务
    threading.Thread(target=analysis_trans_data).start()
    
    return jsonify({'result': 'ok','message':'已开始检测，请耐心等待'}), 200


@analysis_blueprint.route('/trace', methods=['POST'])
def trace_file():
    data = request.json
    trace_data,group_data = kbknr()
    return jsonify({'result': 'ok','data':trace_data,'group':group_data}), 200


@analysis_blueprint.route('/search', methods=['POST'])
def search_person():
    data = request.json
    print(data)
    person_id = data.get('data')

    # 连接到数据库
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    try:
    # 执行查询语句，获取 person_card 列的所有值
        query = """ SELECT DISTINCT person_name
                    FROM people
                    WHERE REPLACE(REPLACE(person_card, ' ', ''), '\t', '') = REPLACE(REPLACE(%s, ' ', ''), '\t', '') 
                    OR REPLACE(REPLACE(person_account, ' ', ''), '\t', '') = REPLACE(REPLACE(%s, ' ', ''), '\t', '')
                    OR REPLACE(REPLACE(person_id, ' ', ''), '\t', '') = REPLACE(REPLACE(%s, ' ', ''), '\t', '');
                """
        cursor.execute(query,(person_id, person_id,person_id))

    # 获取查询结果
        result = cursor.fetchall()
        print(result)
        person_name = [row[0] for row in result]

    finally:
    # 确保关闭游标和连接
        cursor.close()
        conn.close()

    return jsonify({'person': person_name})