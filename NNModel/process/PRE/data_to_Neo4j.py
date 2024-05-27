from neo4j import GraphDatabase
import os
import csv
###########################################################将交易节点之间的关系存入Neo4j##################################################
# Neo4j数据库连接信息
uri = "bolt://localhost:7687"
username = "neo4j"
password = "XYZ67520x"
database = "anti-money"

# Neo4j数据库驱动
driver = GraphDatabase.driver(uri, auth=(username, password), database=database)

# 定义函数用于向数据库中写入数据
def write_to_neo4j(transaction, data):
    for row in data:
        # 解析CSV行数据
        trans_card = row['trans_card']
        trans_name = row['trans_name']
        id_number = row['id_number']
        trans_time = row['trans_time']
        trans_amount = row['trans_amount']
        trans_balance = row['trans_balance']
        label = row['label']
        trans_source = row['trans_source']
        py_indicator = row['py_indicator']
        cp_card = row['cp_card']
        cp_name = row['cp_name']
        cp_id = row['cp_id']
        

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
                "SET r.trans_time = $trans_time, r.trans_amount = $trans_amount, r.py_indicator = $py_indicator, "
                "r.trans_balance = $trans_balance, r.label = $label, r.trans_source = $trans_source",
                trans_card=trans_card, cp_card=cp_card, trans_time=trans_time,
                trans_amount=trans_amount, py_indicator=py_indicator,
                trans_balance=trans_balance, label=label, trans_source=trans_source
            )
        elif py_indicator == '0':
            transaction.run(
                "MATCH (node1:Node1 {trans_card: $trans_card}), (node2:Node2 {cp_card: $cp_card}) "
                "MERGE (node2)-[r:TRANSACTS_TO]->(node1) "
                "SET r.trans_time = $trans_time, r.trans_amount = $trans_amount, r.py_indicator = $py_indicator, "
                "r.trans_balance = $trans_balance, r.label = $label, r.trans_source = $trans_source",
                trans_card=trans_card, cp_card=cp_card, trans_time=trans_time,
                trans_amount=trans_amount, py_indicator=py_indicator,
                trans_balance=trans_balance, label=label, trans_source=trans_source
            )

                
# 遍历文件夹中的CSV文件
def process_csv_files(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            csv_path = os.path.join(folder_path, filename)
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                data = list(reader)
                with driver.session() as session:
                    session.write_transaction(write_to_neo4j, data)

# 调用函数处理CSV文件夹
folder_path = 'database/people'
process_csv_files(folder_path)

# 关闭数据库连接
driver.close()
