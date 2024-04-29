import pandas as pd
import numpy as np
import csv
import os
###############################交易人员各自对应一个交易表格###########################################
def set_people(file_name, column_name):
    df = pd.read_csv(file_name, encoding='gb18030',dtype = str)
    unique_values = df[column_name].str.strip().unique().tolist()
    return [value for value in unique_values if pd.notna(value)]

def trans_people():
    # 1. 收集所有交易人名
    dir = 'database/cooked/'
    file_name = 'database/identity/combined_data.csv'
    column_name = '账户开户名称'
    new_dir = 'database/people/'
    os.makedirs(new_dir, exist_ok=True)
    
    # 2. 构建两个列表
    sub_dir= []
    for item in os.listdir(dir):
        # 获取子目录的完整路径
        item_path = os.path.join(dir, item)
        # 判断是否是一个目录
        if os.path.isdir(item_path):
            sub_dir.append(item)

    trans_people = set_people(file_name,column_name)
    trans_people = [item for item in trans_people if item != '']
    print(trans_people)

    # 3. 每次取列表中的一个值，构建输出表格
    for person in trans_people:
        person_name = person + '.csv'
        output_file = os.path.join(new_dir, person_name)
        time = 0

    # 4. 对于每个csv表格，查找匹配的行
        for item in sub_dir:
            dir_path = dir + item 
            print(dir_path)
            # 获取目录中所有文件的文件名
            files = os.listdir(dir_path)
            print(files)

            for file in files:
                for file in files:
                    input_file = os.path.join(dir_path, file)
                    df = pd.read_csv(input_file, encoding='gb18030',dtype = str)
                    df_new = pd.DataFrame(columns=df.columns)
                    df_new['交易来源'] = ''
                    for index, row in df.iterrows():
                        if str(row['交易户名']).strip() == person or str(row['对手户名']).strip() == person:
                            df_new = pd.concat([df_new, pd.DataFrame([row], columns=df.columns)])
                            index_new = str(file).rindex("交")
                            if index_new != -1:
                                df_new['交易来源'] = file[:index_new]
                    # 判断输出文件是否存在，如果存在则不写入列名
                    if time == 1 :
                        df_new.to_csv(output_file, index=False, encoding='gb18030', mode='a', header=False)
                    else:
                        df_new.to_csv(output_file, index=False, encoding='gb18030', mode='a')
                        time+=1