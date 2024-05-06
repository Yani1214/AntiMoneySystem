import pandas as pd
import os
from pathlib import Path
from process.PRE.data_remove_5 import file_remove

############################收付标志进行判断和统一######################################
def analyze_transactions(folder_path):
    for file_name in os.listdir(folder_path):
        file_path = Path(folder_path) / file_name
        if file_path.is_file() and file_path.suffix == '.csv':
            try:
                df = pd.read_csv(file_path, encoding='GB18030',dtype=str)

                if '交易余额' not in df.columns or '收付标志' not in df.columns:
                    print(f"跳过文件：{file_name}，因为缺少必要的字段。")
                    continue

                if df['交易余额'].isnull().all() or df['收付标志'].isnull().all():
                    print(f'文件 {file_path} 中“交易余额”或“收付标志”字段为空，已跳过。')
                    continue

                df['交易余额'] = pd.to_numeric(df['交易余额'], errors='coerce')
                df['交易金额'] = pd.to_numeric(df['交易金额'], errors='coerce')

                df['交易金额'] = pd.to_numeric(df['交易金额'], errors='coerce').abs()

                # 初始化计数器
                pre_transaction_count = 0  # 交易发生前的余额
                post_transaction_count = 0  # 交易发生后的余额
                normal_flag_count = 0  # 收付标志正常
                special_flag_count = 0  # 收付标志特殊

                # 初始化一个标志，用于记录是否有不满足条件的行
                all_skipped = True

                for i in range(1, len(df) - 1):  # 从第二行开始遍历，直到倒数第二行
                    previous_row = df.iloc[i - 1]
                    current_row = df.iloc[i]
                    next_row = df.iloc[i + 1]

                    if pd.isnull(current_row['交易余额']) or pd.isnull(current_row['收付标志']):
                        continue

                    case_1_1 = previous_row['交易余额'] - current_row['交易金额'] == current_row['交易余额']
                    case_1_2 = previous_row['交易余额'] + current_row['交易金额'] == current_row['交易余额']
                    case_2_1 = current_row['交易余额'] - current_row['交易金额'] == next_row['交易余额']
                    case_2_2 = current_row['交易余额'] + current_row['交易金额'] == next_row['交易余额']

                    if (case_1_1 or case_1_2) and (case_2_1 or case_2_2):
                        # print("交易余额字段暂时无法判断")
                        continue

                    if case_1_1 or case_1_2:
                        # print("交易余额是该笔交易发生后")
                        post_transaction_count += 1
                        if (case_1_1 and current_row['收付标志'] == '进\t') or (case_1_2 and current_row['收付标志'] == '出\t'):
                            # print("收付标志特殊")
                            special_flag_count += 1
                        else:
                            # print("收付标志正常")
                            normal_flag_count += 1

                    if case_2_1 or case_2_2:
                        # print("交易余额是该笔交易发生前")
                        pre_transaction_count += 1
                        all_skipped = False
                        if (case_2_1 and current_row['收付标志'] == '进\t') or (case_2_2 and current_row['收付标志'] == '出\t'):
                            # print("收付标志特殊")
                            special_flag_count += 1
                        else:
                            # print("收付标志正常")
                            normal_flag_count += 1
                if all_skipped:
                    print(f'文件 {file_path} 无法判断，请工作人员手动处理。\n')
                    # 将需要人工处理的文件移动至另外的文件夹中
                    file_remove(folder_path,file_path)

                
                if not all_skipped:
                    # 计算差值与和的百分比
                    transaction_diff = abs(pre_transaction_count - post_transaction_count)
                    transaction_sum = pre_transaction_count + post_transaction_count
                    flag_diff = abs(normal_flag_count - special_flag_count)
                    flag_sum = normal_flag_count + special_flag_count

                    if transaction_sum == 0 or flag_sum == 0 or transaction_diff < transaction_sum * 0.1 or flag_diff < flag_sum * 0.1:
                        print(f'统计结果接近，文件 {file_path} 无法判断，请工作人员手动处理。')
                        print(f'文件 {file_path} 统计结果:')
                        print(f'交易余额是该笔交易发生前的行数: {pre_transaction_count}')
                        print(f'交易余额是该笔交易发生后的行数: {post_transaction_count}')
                        print(f'收付标志正常的行数: {normal_flag_count}')
                        print(f'收付标志特殊的行数: {special_flag_count}\n')
                    else:
                        if pre_transaction_count > post_transaction_count:
                            print(f'文件 {file_path}交易余额是该笔交易发生前')
                        else:
                            print(f'文件 {file_path}交易余额是该笔交易发生后')
                        if normal_flag_count > special_flag_count:
                            print(f'收付标志正常\n')
                        else:
                            print(f'收付标志特殊\n')
                            for index, row in df.iterrows():
                                if row['收付标志'] == '进\t' :
                                    df.at[index, '收付标志'] = '出\t'
                                if row['收付标志'] == '出\t' :
                                    df.at[index, '收付标志'] = '进\t'
                            # 保存更新后的文件
                            df.to_csv(file_path, index=False, encoding='gb18030')
                            print(f'已修改完成\n')

            except Exception as e:
                print(f"处理文件 {file_name} 时发生错误：{e}")


def batch_judge():
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
        analyze_transactions(dir_path)
