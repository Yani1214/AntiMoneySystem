import os
import json
import pymysql
import threading
from neo4j import GraphDatabase
from flask import Blueprint,request,jsonify,redirect, send_file, Response
from charts import charts_blueprint


################################################基本配置#################################################
# 配置MySQL数据库连接参数
db_config = {
    'user': 'root',       # 替换为你的数据库用户名
    'password': 'XYZ67520x',   # 替换为你的数据库密码
    'host': 'localhost',           # 替换为你的数据库主机地址
    'database': 'test',             # 数据库名称
    'charset': 'utf8mb4'           # 使用utf8mb4字符集
}

# 配置Neo4j数据库连接参数
uri = "bolt://localhost:7687"  # Neo4j默认URI
username = "neo4j"             # Neo4j默认用户名
password = "XYZ67520x"         
database = "test"
driver = GraphDatabase.driver(uri, auth=(username, password), database=database)

json_dir = 'NNModel/caseAnalysis/data/trans_flagged'
##################################################功能函数###############################################
def pie_json(file_path):
    name_list = []
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    for item in data:
        trans_is_suspicion = item.get("trans_is_suspicion")
        trans_name = item.get("trans_name")
        cp_name = item.get("cp_name")
        if trans_is_suspicion == 1:
            name_list.append(trans_name)
            name_list.append(cp_name)
    return name_list
            
def pie_counts(transaction, trans_names):
    results = []
    for trans_name in trans_names:
        result = transaction.run(
            """
                MATCH (n1)-[r:TRANSACTS_TO {label: 1}]->(n2) 
                WHERE n1.trans_name = $name OR n2.cp_name = $name
                RETURN COUNT(r) AS count
            """, 
            name=trans_name
        )
        count = result.single()["count"]
        results.append({"name": trans_name, "count": count})
    return results

###########################################编写交易数据分布展示函数###########################################
@charts_blueprint.route('/group', methods=['POST'])
def charts_draw():
    # data = request.json

    ##########################################################饼状图####################################################

    pie_names=[]
    # 1. 在trans_flagged的文件夹中进行遍历，对其中每个文件中的每个对象，定位trans_is_suspicion为1的对象，并将其trans_name加入到空列表中
    for root, _, files in os.walk(json_dir):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                # print(file_path)
                pie_names.extend(pie_json(file_path))
    pie_names = list(set(pie_names))
    # 2. 对存有名字的列表中的每个值在neo4j中进行遍历，如果trans_is_suspicion=为1且trans_name为对应的名字，则计数器加1
    pie = []
    with driver.session() as session:
         pie = session.write_transaction(pie_counts, pie_names)

    print(pie)
    # 3. 将人名和对应计数器结果做成列表形式；收集列表人名所有计数器结果，返回到前端饼状图上
    text = {
        "main": "涉案交易分布图",
        "sub": '每人所占的涉案交易条数'
    }

    ##########################################################柱状图######################################################

    bar=[]
    line=[]
    for bar_name in pie_names:
        # 连接到数据库
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        try:
        # 执行查询语句，获取 person_card 列的所有值
            query1 = """ SELECT DISTINCT person_number FROM people_standard
                        WHERE person_name = %s
                    """
            cursor.execute(query1,(bar_name,))

        # 获取查询结果
            person_number = cursor.fetchall()

            # 去除 \r 并转换为浮点数
            print(person_number)
            float_number = float(person_number[0][0].replace("\r", ""))
            # 转换为整数并转换为字符串
            person_number = str(int(float_number))

            person_table = f"person_{person_number}"
        # 分别查询不同 trans_amount 范围的条数
            quries2 = [
                f"SELECT COUNT(*) FROM {person_table} WHERE trans_amount < 1000",
                f"SELECT COUNT(*) FROM {person_table} WHERE trans_amount BETWEEN 1000 AND 5000",
                f"SELECT COUNT(*) FROM {person_table} WHERE trans_amount BETWEEN 5000 AND 10000",
                f"SELECT COUNT(*) FROM {person_table} WHERE trans_amount BETWEEN 10000 AND 50000",
                f"SELECT COUNT(*) FROM {person_table} WHERE trans_amount BETWEEN 50000 AND 100000",
                f"SELECT COUNT(*) FROM {person_table} WHERE trans_amount > 100000"
            ]
            counts = []
            # 执行每个查询并获取结果
            for query in quries2:
                cursor.execute(query)
                count = cursor.fetchone()[0]
                counts.append(count)

            # 构建结果字典
            result_bar = {
                "name": bar_name,
                "counts": counts
            }
            bar.append(result_bar)
            # print(bar)

    ###############################################################折线图##################################################    

            query3 = f'''    
                SELECT 
                SUM(MONTH(trans_time) BETWEEN 1 AND 2) AS jan_feb_count,
                SUM(MONTH(trans_time) BETWEEN 3 AND 4) AS mar_apr_count,
                SUM(MONTH(trans_time) BETWEEN 5 AND 6) AS may_jun_count,
                SUM(MONTH(trans_time) BETWEEN 7 AND 8) AS jul_aug_count,
                SUM(MONTH(trans_time) BETWEEN 9 AND 10) AS sep_oct_count,
                SUM(MONTH(trans_time) BETWEEN 11 AND 12) AS nov_dec_count
                FROM {person_table}
                WHERE YEAR(trans_time) = 2020 '''

            cursor.execute(query3)

            # 将结果格式化成字典
            result_line = {
                "name": bar_name,
                "counts": list(cursor.fetchone())
            }

            # 遍历 counts 列表，将 Decimal 类型转换为整数
            result_line['counts'] = [int(count) for count in result_line['counts']]  
            line.append(result_line) 

        
        finally:
        # 确保关闭游标和连接
            cursor.close()
            conn.close()
        
    print(line)

    # 关闭数据库连接
    driver.close()
    return jsonify({'pie': pie,'bar':bar,'line':line,'text':text})



@charts_blueprint.route('/person', methods=['POST'])
def person_draw():
    data = request.json
    print(data)
    person_name = data.get('data')
    # 连接到数据库
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    try:
    # 执行查询语句，获取 person_card 列的所有值
        query = """ SELECT DISTINCT person_number FROM people_standard
                    WHERE person_name = %s
                """
        cursor.execute(query,(person_name,))

    # 获取查询结果
        person_number = cursor.fetchall()

        # 去除 \r 并转换为浮点数
        print(person_number)
        float_number = float(person_number[0][0].replace("\r", ""))
        # 转换为整数并转换为字符串
        person_number = str(int(float_number))

        person_table = f"person_{person_number}"


    # ############################################################饼状图##############################################################
        pie=[]
        query1 = f"""
        SELECT cp_name, COUNT(*) as total_count
        FROM {person_table}
        GROUP BY cp_name;
        """

        cursor.execute(query1)
        pie_results = cursor.fetchall()
        # 将查询结果转换为字典列表
        pie = [{'name': row[0], 'count': row[1]} for row in pie_results]

        # 按照counts属性对字典列表进行排序
        pie = sorted(pie, key=lambda x: x['count'], reverse=True)

        # 保留排序后的前五个字典，剩余的字典合并为一个新的字典表示为“其他”
        top_five = pie[:5]
        other_count = sum(entry['count'] for entry in pie[5:])
        pie = top_five + [{'name': '其他', 'count': other_count}]

        print(pie)

        text = {
            "main": "交易对手分布图",
            "sub": '每个交易对手所占的交易条数'
        }

    # #############################################################柱状图##############################################################

        bar=[]  
    # 分别查询不同 trans_amount 范围的条数
        quries2 = [
            f"SELECT COUNT(*) FROM {person_table} WHERE trans_amount < 1000",
            f"SELECT COUNT(*) FROM {person_table} WHERE trans_amount BETWEEN 1000 AND 5000",
            f"SELECT COUNT(*) FROM {person_table} WHERE trans_amount BETWEEN 5000 AND 10000",
            f"SELECT COUNT(*) FROM {person_table} WHERE trans_amount BETWEEN 10000 AND 50000",
            f"SELECT COUNT(*) FROM {person_table} WHERE trans_amount BETWEEN 50000 AND 100000",
            f"SELECT COUNT(*) FROM {person_table} WHERE trans_amount > 100000"
        ]
        counts = []
        # 执行每个查询并获取结果
        for query2 in quries2:
            cursor.execute(query2)
            count = cursor.fetchone()[0]
            counts.append(count)

        # 构建结果字典
        result_bar = {
            "name": person_name,
            "counts": counts
        }
        bar.append(result_bar)
        print(bar)

    # ############################################################条形图##############################################################

        line=[]
        query3 = f'''    
            SELECT 
            SUM(MONTH(trans_time) BETWEEN 1 AND 2) AS jan_feb_count,
            SUM(MONTH(trans_time) BETWEEN 3 AND 4) AS mar_apr_count,
            SUM(MONTH(trans_time) BETWEEN 5 AND 6) AS may_jun_count,
            SUM(MONTH(trans_time) BETWEEN 7 AND 8) AS jul_aug_count,
            SUM(MONTH(trans_time) BETWEEN 9 AND 10) AS sep_oct_count,
            SUM(MONTH(trans_time) BETWEEN 11 AND 12) AS nov_dec_count
            FROM {person_table}
            WHERE YEAR(trans_time) = 2020 '''

        cursor.execute(query3)

        # 将结果格式化成字典
        result_line = {
            "name": person_name,
            "counts": list(cursor.fetchone())
        }

        # 遍历 counts 列表，将 Decimal 类型转换为整数
        result_line['counts'] = [int(count) for count in result_line['counts']]  
        line.append(result_line)

    finally:
    # 确保关闭游标和连接
        cursor.close()
        conn.close()

    return jsonify({'pie': pie,'bar':bar,'line':line,'text':text})