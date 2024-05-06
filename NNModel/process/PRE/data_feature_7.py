import pandas as pd
import os
from process.PRE.caculate import cal_median,cal_mean,cal_quantile_75,cal_quantile_25

#############################################################对交易明细数据构造新的特征############################################################
# 交易金额是否超过中位数、平均数、分位数
def is_more_median(file_path):
    # 读取CSV文件
    df = pd.read_csv(file_path, encoding='gb18030',dtype=str)
    df['交易金额'] = df['交易金额'].astype(float)
    # 计算交易金额的中位数
    median_value = cal_median()
    # 判断交易金额是否大于等于中位数，并创建新列
    df['is_more_median'] = df['交易金额'].apply(lambda x: 1 if x >= median_value else 0)
    df = df.astype(str)
    # 保存修改后的CSV文件
    df.to_csv(file_path, index=False, encoding='gb18030')

def is_more_mean(file_path):
    # 读取CSV文件
    df = pd.read_csv(file_path, encoding='gb18030',dtype=str)
    df['交易金额'] = df['交易金额'].astype(float)
    # 计算交易金额的平均数
    median_value = cal_mean()
    # 判断交易金额是否大于等于平均数，并创建新列
    df['is_more_mean'] = df['交易金额'].apply(lambda x: 1 if x >= median_value else 0)
    df = df.astype(str)
    # 保存修改后的CSV文件
    df.to_csv(file_path, index=False, encoding='gb18030')

def is_more_qualite_25(file_path):
    # 读取CSV文件
    df = pd.read_csv(file_path, encoding='gb18030',dtype=str)
    df['交易金额'] = df['交易金额'].astype(float)
    # 计算交易金额的25分位数
    median_value = cal_quantile_25()
    # 判断交易金额是否大于等于25分位数，并创建新列
    df['is_more_qualite25'] = df['交易金额'].apply(lambda x: 1 if x >= median_value else 0)
    df = df.astype(str)
    # 保存修改后的CSV文件
    df.to_csv(file_path, index=False, encoding='gb18030')

def is_more_qualite_75(file_path):
    # 读取CSV文件
    df = pd.read_csv(file_path, encoding='gb18030',dtype=str)
    df['交易金额'] = df['交易金额'].astype(float)
    # 计算交易金额的75分位数
    median_value = cal_quantile_75()
    # 判断交易金额是否大于等于75分位数，并创建新列
    df['is_more_qualitie75'] = df['交易金额'].apply(lambda x: 1 if x >= median_value else 0)
    df = df.astype(str)
    # 保存修改后的CSV文件
    df.to_csv(file_path, index=False, encoding='gb18030')

# 该卡号距离上一次交易的交易时间间隔（分钟）
def time_interval(file_path):
    # 读取CSV文件
    df = pd.read_csv(file_path, encoding='gb18030',dtype=str)

    # # 将交易时间修改为时间格式
    # df['交易时间'] = pd.to_datetime(df['交易时间'].str.rstrip(), format='%Y-%m-%d %H:%M:%S')

    # 使用条件语句判断日期时间格式
    if df['交易时间'].str.contains(':').any():  # 如果日期时间字符串包含冒号，则认为是年月日时分秒的格式
        df['交易时间'] = pd.to_datetime(df['交易时间'].str.rstrip(), format='%Y-%m-%d %H:%M:%S')
    else:  # 否则认为是只有年月日的格式
        df['交易时间'] = pd.to_datetime(df['交易时间'].str.rstrip(), format='%Y-%m-%d')
    # 按照交易时间从小到大排序
    df_sorted = df.sort_values(by=['交易卡号', '交易时间'])
    # 计算每两行之间的交易时间列的差值，只有当交易卡号相同时才计算差值，否则差值为0（以小时为单位）
    df_sorted['time_interval'] = df_sorted.groupby('交易卡号')['交易时间'].diff().dt.total_seconds().fillna(0) / 3600
    # 将交易时间列再次转换为字符串格式
    column_data = df_sorted['交易时间'].astype(str)
    df_sorted['交易时间'] = column_data + "\t"
    # 保存修改后的CSV文件
    df_sorted.to_csv(file_path, index=False, encoding='gb18030')

# time_interval("test\\cooked\\5104614320210702112732\\中国农业银行交易明细信息.csv")

# 在该时间段前两张卡已经交易的次数
def trans_frequency(file_path):
    # 读取CSV文件
    df = pd.read_csv(file_path, encoding='gb18030',dtype=str)
    # 按照交易时间从小到大排序
    df = df.sort_values(by=['交易卡号', '交易时间'])
    # df = df.sort_values(by= '交易时间' )
    # 创建一个空的列表来存储每一行的频率值
    frequency_list = []

    # 遍历每一行
    for index, row in df.iterrows():
        # 获取当前行的交易卡号和交易对手账卡号
        transaction_card = row['交易卡号']
        opponent_card = row['交易对手账卡号']
        
        # 初始化频率为0
        frequency = 0
        
        # 遍历该行之前的所有数据
        for i in range(index):
            # 如果对应两个列的值均有重复，则频率加1
            if (df.at[i, '交易卡号'] == transaction_card) and (df.at[i, '交易对手账卡号'] == opponent_card):
            # if ((df.at[i, '交易卡号'] == transaction_card and df.at[i, '交易对手账卡号'] == opponent_card) or (df.at[i, '交易卡号'] == opponent_card and df.at[i, '交易对手账卡号'] == transaction_card)):
                frequency += 1
        
        # 将频率值添加到列表中
        frequency_list.append(frequency)

    # 将频率列表赋值给新列
    df['trans_frequency'] = frequency_list

    # 将结果写入新的CSV文件
    df.to_csv(file_path, index=False, encoding='gb18030') 

# trans_frequency("test\\cooked\\5104614320210702112732\\中国农业银行交易明细信息.csv")
###################################################################批量处理交易表格#############################################################
def batch_feature():
    """
    1.获取给定目录下的所有子目录名称，并存储到列表中
    """
    # 给定目录路径
    dir = 'NNModel/process/database/cooked/'
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
            is_more_median(target_path)
            is_more_mean(target_path)
            is_more_qualite_25(target_path)
            is_more_qualite_75(target_path)
            time_interval(target_path)
            trans_frequency(target_path)
