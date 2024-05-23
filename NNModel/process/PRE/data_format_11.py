import pandas as pd
import numpy as np
import os
##########################################################将列名改为英文，并增加交易id##############################################
''' 
修改一人一表的列名为英文名，增加唯一编号，并且修改为uft-8供mysql使用
'''
def data_standardization(file_path):
    # 读取CSV文件
    df = pd.read_csv(file_path, encoding='gb18030',dtype = str)

    # 重新命名列名
    new_columns = ['trans_card', 'trans_account','trans_name','id_number', 'trans_time', 'trans_amount','trans_balance', 'py_indicator', 'cp_card', 'cp_name', 'cp_id', 'summary', 'merchant_code', 'trans_type','label','is_more_median','is_more_mean','is_more_qualite25','is_more_qualite75','time_interval','trans_frequency','trans_source']  # 在里添加你想要的新列名
    df.columns = new_columns

    # 添加id列
    df.insert(0, 'trans_id', range(1, len(df) + 1))
    # 将"进"改写成0，"出"改写成1
    print(df['py_indicator'])
    df['py_indicator'] = df['py_indicator'].str.strip().apply(lambda x: 0 if x == '进' or x == '转入' else (1 if x == '出' or x == '转出' else x))
    print(df['py_indicator'])

    # 保存修改后的CSV文件（注意，必须是uft-8才可以，不然mysql识别不了字符，存不进去）
    df.to_csv(file_path, index=False, encoding='utf-8')

''' 
根据顺序生成新的文件名
'''
def rename_files(old_path, dir,i):
    new_filename = f"person_{i}.csv" 
    new_path = os.path.join(dir, new_filename)
    os.rename(old_path, new_path)
    print(f"Renamed {old_path} to {new_filename}")

''' 
将编号写入combined_data.csv中，修改其列名为英文列名，并进行重新存储
'''
def fill_name_munber(name_to_number):
    df = pd.read_csv('NNModel/process/database/identity/combined_data.csv', encoding='gb18030',dtype = str)
    # 删除不要的“账号2”列
    df.drop(columns=['账号2'], inplace=True)
    # 修改列名和增加列名
    new_columns = ['person_name', 'person_id','person_card','person_account', 'bank_name', 'task_id','summary', 'label','manual_review','id']  # 添加新列名
    df.columns = new_columns
    # 去除person_name为空的行
    df = df.dropna(subset=['person_name'])
    # 添加id列,填充person_number列
    df["person_number"] = df["person_name"].map(name_to_number)
    df['manual_review'] = ''
    df['id'] = ''
    # 将df文件存储到新路径
    df.to_csv('NNModel/process/database/identity/people.csv', index=False, encoding='utf-8')
        

def batch_standard():
    """
    遍历每个子目录，对一人一表进行英文标准化和英文文件命名
    """
    # 给定目录路径
    dir = 'NNModel/process/database/people/'
    sub_dir= []
    name_to_number = {}  # 存储文件名到数字的映射字典
    i = 1
    for name in os.listdir(dir):
        sub_dir.append(name)
    for item in sub_dir:
        dir_path = dir + item
        file_name = os.path.splitext(item)[0]
        print(file_name)
        print(dir_path)
        # 对人名和数字进行映射
        name_to_number[file_name] = i
        data_standardization(dir_path)
        rename_files(dir_path,dir,i) 
        i += 1
    fill_name_munber(name_to_number)
    