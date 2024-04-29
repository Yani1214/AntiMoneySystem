import pandas as pd
import os
#############################################################对一人一表数据进行去重################################################
def trans_duplicate(file_path):
    # 读取CSV文件
    df = pd.read_csv(file_path, encoding='gb18030',dtype = str)

    # 去除重复行
    df.drop_duplicates(inplace=True)

    # 将去重后的数据写入新的CSV文件
    df.to_csv(file_path, index=False, encoding='gb18030')

def batch_duplicate():
    """
    遍历每个子目录，对一人一表去重
    """
    # 给定目录路径
    dir = 'database/people/'
    sub_dir= []
    for name in os.listdir(dir):
        sub_dir.append(name)
    for item in sub_dir:
        dir_path = dir + item
        print(dir_path)
        trans_duplicate(dir_path)