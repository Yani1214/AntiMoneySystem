import pandas as pd
import numpy as np
import statistics
import os
######################################获得所有交易明细的交易金额列表#########################################
def get_amount(folder_paths,column_name):
    # '''
    # 1. 记录cooked文件夹下的所有子文件夹名称
    # '''
    # # 存储文件夹下所有子文件夹名称
    # sub_dir= []            
    # # 存储所有CSV文件的交易金额列
    # all_values = []

    # 遍历目录中的所有文件和子目录
    # for item in os.listdir(folder_path):
    #     # 获取子目录的完整路径
    #     item_path = os.path.join(folder_path, item)
    #     # 判断是否是一个目录
    #     if os.path.isdir(item_path):
    #         sub_dir.append(item)

    # """
    # 2.将所有csv表格的”交易金额“列的值存入列表
    # """
    # for item in sub_dir:
    #     dir_path = folder_path + item
    #     # 获取目录中所有文件的文件名
    #     files = os.listdir(dir_path)
    #     for file in files:
    #         target_path = os.path.join(dir_path, file)
    #         # 读取CSV文件
    #         df = pd.read_csv(target_path, encoding='gb18030',dtype=str)
    #         # 检查交易金额列是否存在
    #         if column_name in df.columns:
    #             # 将交易金额列的值添加到列表中
    #             all_values.extend(df[column_name].tolist())
    
    # return all_values

    all_values = []
    for folder_path in folder_paths:
        file_paths = [os.path.join(folder_path, file) for file in os.listdir(folder_path)]
        for file_path in file_paths:
            # 判断获得的路径是文件夹还是文件
            if not os.path.isdir(file_path):
                df = pd.read_csv(file_path, encoding='gb18030',dtype=str)
                # 获取文件中的交易金额数据
                if column_name in df.columns:
                    # 将交易金额列的值添加到列表中
                    all_values.extend(df[column_name].tolist())
            # 如果是文件夹
            else:
                file_names = [os.path.join(file_path, file) for file in os.listdir(file_path)]
                for file_name in file_names:
                    df = pd.read_csv(file_name, encoding='gb18030',dtype=str)
                    # 获取文件中的交易金额数据
                    if column_name in df.columns:
                        # 将交易金额列的值添加到列表中
                        all_values.extend(df[column_name].tolist())
    return all_values
#################################################################计算中位数##############################################################
def cal_median():
    folder_path = ['database/cooked/','database/special_people']
    column_name = "交易金额"
    all_values = get_amount(folder_path,column_name)
    print(all_values)
    # 将列表转换为数值类型，无法转换的值将被设为 NaN
    numeric_data = pd.to_numeric(all_values, errors='coerce')
    # 检查数组是否为空
    if numeric_data.size > 0:
        # 计算中位数
        median_value = statistics.median(numeric_data)
        return median_value
    else:
        return None

#################################################################计算平均数##############################################################
def cal_mean():
    folder_path = ['database/cooked/','database/special_people']
    column_name = "交易金额"
    all_values = get_amount(folder_path,column_name)
    # 将列表转换为数值类型，无法转换的值将被设为 NaN
    numeric_data = pd.to_numeric(all_values, errors='coerce')
    # 检查数组是否为空
    if numeric_data.size > 0:
        # 计算平均数
        median_value = statistics.mean(numeric_data)
        return median_value
    else:
        return None

#################################################################计算分位数##############################################################
def cal_quantile_25():
    folder_path = ['database/cooked/','database/special_people']
    column_name = "交易金额"
    all_values = get_amount(folder_path, column_name)
    # 将列表转换为数值类型，无法转换的值将被设为 NaN
    numeric_data = pd.to_numeric(all_values, errors='coerce')
    # 转换为 DataFrame 对象
    numeric_data_df = pd.DataFrame(numeric_data, columns=[column_name])
    # 删除 NaN 值
    numeric_data_cleaned = numeric_data_df.dropna()
    # 检查数组是否为空
    if numeric_data_cleaned.size > 0:
        # 计算分位数
        quantile_value = np.percentile(numeric_data_cleaned[column_name], 25)  # 计算第25百分位数（即四分之一分位数）
        return quantile_value
    else:
        return None
    
def cal_quantile_75():
    folder_path = ['database/cooked/','database/special_people']
    column_name = "交易金额"
    all_values = get_amount(folder_path, column_name)
    # 将列表转换为数值类型，无法转换的值将被设为 NaN
    numeric_data = pd.to_numeric(all_values, errors='coerce')
    # 转换为 DataFrame 对象
    numeric_data_df = pd.DataFrame(numeric_data, columns=[column_name])
    # 删除 NaN 值
    numeric_data_cleaned = numeric_data_df.dropna()
    # 检查数组是否为空
    if numeric_data_cleaned.size > 0:
        # 计算分位数
        quantile_value = np.percentile(numeric_data_cleaned[column_name], 75)  # 计算第75百分位数（即四分之三分位数）
        return quantile_value
    else:
        return None