import pandas as pd
import os
#########################################################对交易记录打标签###################################################################
def trans_label(file_path):
    # 读取CSV文件
    df = pd.read_csv(file_path, encoding='gb18030',dtype=str)

    # 十二个嫌疑人的名字列表
    people = ['杨小琴', '苟兴兵', '何年碧', '何顺京', '胡秋艳', '李春荣', '李菊英', '孙翊章', '王庆凤', '颜爱中', '余英', '张柱碧']
    df['交易户名'] = df['交易户名'].str.replace('\t', '')
    df['交易户名'] = df['交易户名'].str.replace(' ', '')
    df['对手户名'] = df['对手户名'].str.replace('\t', '')
    df['对手户名'] = df['对手户名'].str.replace(' ', '')
    # 定义函数来判断是否匹配其中一个人的名字
    def check_names(row):
        if row['交易户名'] in people and row['对手户名'] in people:
            return 1
        else:
            return 0
    # 添加标签列
    df['label'] = df.apply(check_names, axis=1)

    # 保存修改后的CSV文件
    df.to_csv(file_path, index=False, encoding='gb18030')

def batch_trans():
    """
    1.获取给定目录下的所有子目录名称，并存储到列表中
    """
    # 给定目录路径
    dir = 'database/cooked/'
    sub_dir= []
    # 遍历目录中的所有文件和子目录
    for item in os.listdir(dir):
        # 获取子目录的完整路径
        item_path = os.path.join(dir, item)
        # 判断是否是一个目录
        if os.path.isdir(item_path):
            sub_dir.append(item)
    # print(sub_dir)
        
    """
    2.遍历每个子目录，对每个交易明细文件判断收付标志，并进行相应的修改
    """
    for item in sub_dir:
        dir_path = dir + item
        # 获取目录中所有文件的文件名
        files = os.listdir(dir_path)
        for file in files:
            target_path = os.path.join(dir_path, file)
            trans_label(target_path)

##############################################################对交易人员打标签##################################################################
def person_label(file_path):
    df = pd.read_csv(file_path, encoding='gb18030',dtype=str)
    df['账户开户名称'] = df['账户开户名称'].str.replace('\t', '')
    df['账户开户名称'] = df['账户开户名称'].str.replace(' ', '')
    
    # 十二个嫌疑人的名字列表
    people = ['杨小琴', '苟兴兵', '何年碧', '何顺京', '胡秋艳', '李春荣', '李菊英', '孙翊章', '王庆凤', '颜爱中', '余英', '张柱碧']

    # 定义函数来判断是否匹配其中一个人的名字
    def check_names(row):
        if row['账户开户名称'] in people:
            return 1
        else:
            return 0
    # 添加标签列
    df['label'] = df.apply(check_names, axis=1)

    # 保存修改后的CSV文件
    df.to_csv(file_path, index=False, encoding='gb18030')

def batch_person():
    file_path= 'database/identity/combined_data.csv'
    person_label(file_path)