import os
import pandas as pd

##############################实现自动化读取##############################
def data_cook(input_path):
    """
    1.输入目标csv文件路径
    """
    # input_path = input("请输入需要处理的文件路径：")
    # print(input_path)
    directory, file_name = os.path.split(input_path)
    pre_directory,after_directory = os.path.split(directory)
    combine_path = 'database/cooked/' + after_directory
    os.makedirs(combine_path, exist_ok=True)

    """    
    # 2.读取输入的目标csv文件路径
    """
    target_columns = ['交易卡号', '交易账号', '交易户名', '交易证件号码', '交易时间', '交易金额', '交易余额', '收付标志', '交易对手账卡号', '对手户名', '对手身份证号', '摘要说明', '商户代码', '交易类型']
    output_path = os.path.join(combine_path, file_name)
        # 读取CSV文件(要以字符串读取，不然会变成科学计数法)
    df = pd.read_csv(input_path, encoding='gb18030',dtype=str)
        #去除空格
    df.rename(columns=lambda x: x.strip(), inplace=True)
    #print("Column names:", df.columns)
        # 转换所有列为字符串类型
    df = df.astype(str)
        # 保留特定的列
    df_filtered = df[target_columns]
        # 将结果写入新的CSV文件
    df_filtered.to_csv(output_path, index=False, encoding='gb18030')

def batch_data():
    """
    1.获取给定目录下的所有子目录名称，并存储到列表中
    """
    # 给定目录路径
    dir = 'database/raw/'
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
    2.遍历每个子目录，并对其中的所有交易表格进行模板化处理
    """
    for item in sub_dir:
        dir_path = dir + item
        # 获取目录中所有文件的文件名
        files = os.listdir(dir_path)
        # 找出文件夹中名称包含“交易明细信息”的文件
        match_files = [f for f in files if '交易明细信息' in f]
        # print("Files matching '交易明细信息':", match_files)
        for file in match_files:
            target_path = os.path.join(dir_path, file)
            data_cook(target_path)
            print(target_path)
