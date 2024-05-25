import pymysql
import pandas as pd
import os
###############################################将一人一表存入MySQL数据量中######################################################
def people_list():
    # 获取当前文件的绝对路径
    file_path = os.path.dirname(__file__)
    parent_dir = os.path.dirname(file_path)

    # 给定目录路径
    dir = 'database\\people\\'
    sub_file= []
    sub_dir=[]
    for name in os.listdir(dir):
        sub_file.append(name)
    for item in sub_file:
        dir_path = dir + item
        abs_path = os.path.join(parent_dir, dir_path)
        # 防止斜杠被转义去掉（注意，所有路径一定都要英文才可以！！！不然mysql识别不了中文字符，读不进去！！！）
        abs_path = abs_path.replace('\\', '\\\\')
        sub_dir.append(abs_path)
    print(sub_dir)
    return sub_dir

# MySQL连接配置
HOST = 'localhost'
USER = 'root'
PASSWORD = 'XYZ67520x'
DATABASE = 'anti-money'

def person_to_db():
    # 准备要导入的CSV文件列表
    csv_files = people_list()

    # MySQL连接
    connection = pymysql.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
    cursor = connection.cursor()

    # 循环导入CSV文件
    for csv_file in csv_files:
        # 提取文件名作为表名（假设文件名中不包含扩展名）
        table_name = os.path.splitext(os.path.basename(csv_file))[0]
        
        # 创建表（收付标志原来有空的，这里没有选择填充，保留空值）
        create_table_query = f'''CREATE TABLE IF NOT EXISTS {table_name} (
            trans_id INT PRIMARY KEY,
            trans_card VARCHAR(255),
            trans_account VARCHAR(255),
            trans_name VARCHAR(255),
            id_number VARCHAR(255),
            trans_time DATETIME,
            trans_amount DECIMAL(10, 2),
            trans_balance VARCHAR(255),
            py_indicator VARCHAR(255),
            cp_card VARCHAR(255),
            cp_name VARCHAR(255),
            cp_id VARCHAR(255),
            summary VARCHAR(255),
            merchant_code VARCHAR(255),
            trans_type VARCHAR(255),
            label INT,
            is_more_median INT,
            is_more_mean INT,
            is_more_qualite25 INT,
            is_more_qualite75 INT,
            time_interval VARCHAR(255),
            trans_frequency INT,
            trans_source VARCHAR(255)
            )
            '''
        cursor.execute(create_table_query)
        
        # 导入数据
        load_data_query = f'''LOAD DATA INFILE '{csv_file}' INTO TABLE {table_name} FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS'''
        cursor.execute(load_data_query)
        
        # 提交更改
        connection.commit()

    # 关闭连接
    cursor.close()
    connection.close()

def people_to_db():
    # 准备要导入的CSV文件列表
    csv_file = 'database\\identity\\people.csv'
    # 获取当前文件的绝对路径
    file_path = os.path.dirname(__file__)
    parent_dir = os.path.dirname(file_path)
    abs_path = os.path.join(parent_dir, csv_file)
    abs_path = abs_path.replace('\\', '\\\\')

    # MySQL连接
    connection = pymysql.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
    cursor = connection.cursor()

    # 提取文件名作为表名（假设文件名中不包含扩展名）
    table_name = os.path.splitext(os.path.basename(csv_file))[0]
    
    # 创建表
    create_table_query = f'''CREATE TABLE IF NOT EXISTS {table_name} (
        person_name VARCHAR(255),
        person_id VARCHAR(255),
        person_card VARCHAR(255),
        person_account VARCHAR(255),
        bank_name VARCHAR(255),
        task_id VARCHAR(255),
        summary VARCHAR(255),
        label INT,
        person_number VARCHAR(255),
        manual_review VARCHAR(255),
        id INT,
        )
        '''
    cursor.execute(create_table_query)
    
    # 导入数据
    load_data_query = f'''LOAD DATA INFILE '{abs_path}' INTO TABLE {table_name} FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS'''
    cursor.execute(load_data_query)
    
    # 提交更改
    connection.commit()

    # 关闭连接
    cursor.close()
    connection.close()

def people_standard_to_db():
    # 准备要导入的CSV文件列表
    csv_file = 'database\\identity\\people_standard.csv'
    # 获取当前文件的绝对路径
    file_path = os.path.dirname(__file__)
    parent_dir = os.path.dirname(file_path)
    abs_path = os.path.join(parent_dir, csv_file)
    abs_path = abs_path.replace('\\', '\\\\')

    # MySQL连接
    connection = pymysql.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
    cursor = connection.cursor()

    # 提取文件名作为表名（假设文件名中不包含扩展名）
    table_name = os.path.splitext(os.path.basename(csv_file))[0]
    
    # 创建表
    create_table_query = f'''CREATE TABLE IF NOT EXISTS {table_name} (
        person_name VARCHAR(255),
        person_id VARCHAR(255),
        person_card VARCHAR(255),
        person_account VARCHAR(255),
        bank_name VARCHAR(255),
        label INT,
        person_number VARCHAR(255)
        )
        '''
    cursor.execute(create_table_query)
    
    # 导入数据
    load_data_query = f'''LOAD DATA INFILE '{abs_path}' INTO TABLE {table_name} FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS'''
    cursor.execute(load_data_query)
    
    # 提交更改
    connection.commit()

    # 关闭连接
    cursor.close()
    connection.close()