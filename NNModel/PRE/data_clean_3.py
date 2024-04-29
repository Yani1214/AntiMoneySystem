import os
import pandas as pd
import time

##############################################对方证件号码的填充####################################
def name_match(file_path,input_path):
    # 读取 conbine_data.csv 表格
    # conbine_data_df = pd.read_csv('database\identity\combined_data.csv', encoding='gb18030',dtype=str)
    conbine_data_df = pd.read_csv(file_path, encoding='gb18030',dtype=str)

    # 建立 "账户开户名称" 到 "开户人证件号码" 的映射
    mapping = dict(zip(conbine_data_df['账户开户名称'], conbine_data_df['开户人证件号码']))

    # 读取另外一个 CSV 表格
    # other_data_df = pd.read_csv('test\\cooked\\5104614320210702112732\\广发银行股份有限公司交易明细信息.csv', encoding='gb18030',dtype=str)
    other_data_df = pd.read_csv(input_path, encoding='gb18030',dtype=str)

    # 遍历 other_data_df 中的每一行
    for index, row in other_data_df.iterrows():
        # 检查当前行的 "对手户名" 是否在映射中
        opponent_name = row['对手户名']
        if opponent_name in mapping:
            # 如果在映射中找到匹配项，则将对应的 "开户人证件号码" 赋给 "对手证件号码" 列
            other_data_df.at[index, '对手身份证号'] = mapping[opponent_name]

    # 将更新后的数据写回到新的 CSV 文件中
    # other_data_df.to_csv('test\\cooked\\5104614320210702112732\\广发银行股份有限公司交易明细信息.csv', index=False, encoding='gb18030')
    other_data_df.to_csv(input_path, index=False, encoding='gb18030')

def batch_name():
    """
    1.获取给定目录下的所有子目录名称，并存储到列表中
    """
    # 给定目录路径
    dir_1 = 'database/raw/'
    dir_2 = 'database/cooked/'
    conbine_file = 'database/identity/combined_data.csv'
    sub_dir= []
    # 遍历目录中的所有文件和子目录
    for item in os.listdir(dir_1):
        # 获取子目录的完整路径
        item_path = os.path.join(dir_1, item)
        # 判断是否是一个目录
        if os.path.isdir(item_path):
            sub_dir.append(item)
    # print(sub_dir)

    """
    2.遍历每个子目录，对每个子目录进行对手身份证号的填充
    """
    for item in sub_dir:
        dir_path_2 = dir_2 + item
        # print(dir_path_2)
        for name_path in os.listdir(dir_path_2):
            file_path = os.path.join(dir_path_2, name_path)
            name_match(conbine_file,file_path)

################################对方交易账户或对方户名为空数据的清除####################################
def blank_clean(input_path,output_path):
    # 1. 使用pandas读取csv表格，对特定三列的值全部除去制表符
    df = pd.read_csv(input_path, encoding='gb18030',dtype=str)

    # 去除制表符
    columns_to_strip = ['交易对手账卡号', '对手户名','交易金额','交易余额']
    df[columns_to_strip] = df[columns_to_strip].apply(lambda x: x.str.replace('\t', ''))
    # 将空字符串转换为0
    df['交易金额'] = pd.to_numeric(df['交易金额'], errors='coerce').fillna(0)
    df['交易余额'] = pd.to_numeric(df['交易余额'], errors='coerce').fillna(0)
    # 将交易金额转换为浮点类型，从而取绝对值
    df['交易金额'] = df['交易金额'].astype(float).abs()
    df['交易余额'] = df['交易余额'].astype(float)

    # 2. 遍历该表格每一行的值，若其中两列的值为空, 则将该行进行去除，并移动到另外的表格中
    # 新建一个空的 DataFrame 用于存放移除的行
    removed_rows_df = pd.DataFrame(columns=df.columns)

    # 遍历每一行
    for index, row in df.iterrows():
        # 判断两列是否为空
        print(row['交易对手账卡号'])
        # time.sleep(0.1)  # 增加0.1秒的等待时间
        # 去除制表符
        columns_to_strip = ['交易对手账卡号', '对手户名']
        df[columns_to_strip] = df[columns_to_strip].apply(lambda x: x.str.strip())

        if row['交易对手账卡号'] in ['\\N', '-', ''] or row['对手户名'] in ['\\N', '-','']:
            # 移除该行并添加到另外的 DataFrame 中
            removed_rows_df = removed_rows_df._append(row)
            df.drop(index, inplace=True)

    removed_rows_df['交易对手账卡号'] = removed_rows_df['交易对手账卡号'] + '\t'
    # 将移除的行保存到新的 CSV 文件
    removed_rows_df.to_csv(output_path, index=False, encoding='gb18030')

    # 加制表符防止科学计数法
    df['交易对手账卡号'] = df['交易对手账卡号']+ '\t'

    # 将处理后的 DataFrame 保存回原始 CSV 文件
    df.to_csv(input_path, index=False, encoding='gb18030')

def batch_clean():
    """
    1.获取给定目录下的所有子目录名称，并存储到列表中
    """
    # 给定目录路径
    dir = 'database/cooked/'
    new_dir = 'database/blank/'
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
    2.遍历每个子目录，并对其中的所有交易表格进行无效数据筛除
    """
    for item in sub_dir:
        dir_path = dir + item
        new_dir_path = new_dir + item
        os.makedirs(new_dir_path, exist_ok=True)
        # 获取目录中所有文件的文件名
        files = os.listdir(dir_path)
        for file in files:
            input_path = os.path.join(dir_path, file)
            output_path = os.path.join(new_dir_path, file)
            blank_clean(input_path,output_path)
