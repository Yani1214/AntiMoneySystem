import os
import sys
import re
import pandas as pd

##############################实现帐卡号和身份证号的匹配##############################
def process_account_number(account_number):
    if '_' in account_number:
        account_number = account_number.split('_')[0]
    if '-' in account_number:
        account_number = max(account_number.split('-'), key=len)
    return account_number

"""
1. 对每个交易流水号涉及到的交易人员进行汇总
"""
def identity(input_path,output_path):
    # 定义新文件的标题行
    new_file_headers = ["账户开户名称", "开户人证件号码", "交易卡号", "账号1", "账号2", "银行名称", "任务流水号", "备注"]

    # 创建一个新的DataFrame，用于存储整理后的信息
    new_df = pd.DataFrame(columns=new_file_headers)

    # 提取最末尾的文件夹名称作为任务流水号
    task_serial_number = os.path.basename(input_path)  

    print("开始遍历文件夹:", input_path)
    for filename in os.listdir(input_path):
        if "账户信息" in filename and "子账户信息" not in filename:
            print("处理文件:", filename)
            bank_name = filename.split("账户信息")[0]

            # 使用两个集合分别存储原始和处理后的交易账号
            original_transaction_accounts = set()
            processed_transaction_accounts = set()
            for trans_filename in os.listdir(input_path):
                if bank_name in trans_filename and "交易明细信息.csv" in trans_filename:
                    print(f"找到交易明细文件: {trans_filename}")
                    df_trans = pd.read_csv(os.path.join(input_path, trans_filename), encoding='gb18030', dtype=str)
                    for account in df_trans['交易账号\t'].unique():
                        original_transaction_accounts.add(account)
                        processed_transaction_accounts.add(process_account_number(account))

            acc_df = pd.read_csv(os.path.join(input_path, filename), encoding='gb18030', dtype=str)

            # 先检查原始账号是否有交易明细，如果没有，再检查处理后的账号
            acc_df['备注'] = acc_df['交易账号\t'].apply(lambda x: "有交易明细" if x in original_transaction_accounts or process_account_number(x) in processed_transaction_accounts else "无")
            
            acc_df = acc_df.rename(columns={'账户开户名称\t': '账户开户名称', '开户人证件号码\t': '开户人证件号码', '交易卡号\t': '交易卡号', '交易账号\t': '账号1'})
            acc_df['账号2'] = ''
            acc_df['银行名称'] = bank_name

            acc_df['交易卡号'] = acc_df['交易卡号'].apply(lambda x: x.split("_", 1)[0] if '_' in x else x)
            acc_df['账号1'] = acc_df['账号1'].apply(lambda x: x.split("_", 1)[0] if '_' in x else x)


            ####### 加'\t'将其转换为字符串，但是后面会多一个tab制表格，后续处理需要消除########
            acc_df['任务流水号'] = task_serial_number+ '\t'

            acc_df['交易卡号'] = acc_df['交易卡号']+ '\t'
            acc_df['账号1'] = acc_df['账号1']+ '\t'

            acc_df = acc_df[new_file_headers]

            new_df = pd.concat([new_df, acc_df], ignore_index=True)

    # 将列转换成字符串
    new_df = new_df.astype(str)

    # 创建存储身份信息的文件夹
    os.makedirs(output_path, exist_ok=True)

    output_file_path = os.path.join(output_path, f"{task_serial_number}.csv")
    new_df.to_csv(output_file_path, index=False, encoding='gb18030')
    print(f"账户信息整理完成！文件保存在：{output_file_path}")

"""
2. 合并所有的交易人员信息
"""
def conbine(input_path,conbine_file):
    combined_df = pd.DataFrame()

    for file_name in os.listdir(input_path):
        file_path = os.path.join(input_path, file_name)

        if file_name.endswith('.csv'):
            # 检查文件是否为空
            if os.stat(file_path).st_size == 0:
                print(f"Skipping empty file: {file_name}")
                continue

            try:
                # 使用on_bad_lines='skip'来跳过格式错误的行
                temp_df = pd.read_csv(file_path, dtype=str, encoding='gb18030', on_bad_lines='skip')
                combined_df = pd.concat([combined_df, temp_df], ignore_index=True)
            except pd.errors.EmptyDataError:
                print(f"No data in file: {file_name}, skipping.")
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    combined_df.to_csv(conbine_file, index=False, encoding='gb18030')

"""
3. 利用汇总表将身份信息填充至每个交易明细表格中
"""
def identity_match(read_path,input_path):
    identity_df = pd.read_csv(read_path, dtype=str, encoding='gb18030')
    identity_df['交易卡号'] = identity_df['交易卡号'].str.strip().str.replace('\t', '')
    identity_df['账号1'] = identity_df['账号1'].str.strip().str.replace('\t', '')

    print("完成合并数据的读取和初步清洗。")
    print("DataFrame列名：", identity_df.columns.tolist())

    # 构建查找映射，使用正确的列名
    identity_map = {row['交易卡号']: (row['账户开户名称'], row['开户人证件号码']) for index, row in identity_df.iterrows()}
    if '账号1' in identity_df.columns:
        identity_map.update({row['账号1']: (row['账户开户名称'], row['开户人证件号码']) for index, row in identity_df.iterrows()})

    # 遍历并处理每个交易明细文件
    for file_name in os.listdir(input_path):
        if file_name.endswith('.csv'):
            file_path = os.path.join(input_path, file_name)

            if os.path.getsize(file_path) > 0:
                print(f"正在处理文件：{file_name}")
                
                # 读取并清洗交易明细文件
                transaction_df = pd.read_csv(file_path, dtype=str, encoding='gb18030', na_filter=False)

                transaction_df['交易卡号'] = transaction_df['交易卡号'].str.replace('\t', '')
                # transaction_df['交易卡号'].fillna(value = transaction_df['交易账号'], inplace=True)

                transaction_df['交易账号'] = transaction_df['交易账号'].str.replace('\t', '')
                # transaction_df['交易账号'].fillna(value= transaction_df['交易卡号'], inplace=True)

                for index, row in transaction_df.iterrows():
                    if row['交易卡号'] == '' and row['交易账号'] != '':
                        transaction_df.at[index, '交易卡号'] = row['交易账号']
                    if row['交易账号'] == '' and row['交易卡号'] != '':
                        transaction_df.at[index, '交易账号'] = row['交易卡号']

                # 使得交易账号和交易卡号都不包含空格，从而好匹配交易证件号码和交易户名
                transaction_df['交易账号'] = transaction_df['交易账号'].str.strip().str.replace('\t', '')
                transaction_df['交易卡号'] = transaction_df['交易卡号'].str.strip().str.replace('\t', '')
                print("完成交易明细文件的读取和清洗。")

                # 更新数据(第一部分)
                for index, row in transaction_df.iterrows():
                    card_number = row['交易卡号']
                    if card_number in identity_map:
                        transaction_df.at[index, '交易户名'], transaction_df.at[index, '交易证件号码'] = identity_map[card_number]
                    else:
                        # 如果交易卡号匹配不上，记录未找到匹配项的信息
                        print(f"未找到匹配项 {index}: 卡号 {card_number}，尝试使用 '账号1' 进行匹配。")
                        if '交易账号' in row and row['交易账号'] in identity_map:
                            transaction_df.at[index, '交易户名'], transaction_df.at[index, '交易证件号码'] = identity_map[row['交易账号']]
                            print(f"使用 '账号1' 成功匹配 {index}: 账号 {row['交易账号']}。")
                        else:
                            print(f"使用 '账号1' 也未找到匹配项 {index}: 账号 {row.get('交易账号', 'N/A')}。")

                transaction_df = transaction_df.astype(str)    
                ####### 将交易卡号和交易账号通过"\t"转换为字符串，但是会有一个制表格存在，后续处理需要消除 #######
                column_data = transaction_df['交易卡号'].astype(str)
                transaction_df['交易卡号'] = column_data + "\t"

                column_data = transaction_df['交易账号'].astype(str)
                transaction_df['交易账号'] = column_data + "\t"
                
                # 保存更新后的文件
                transaction_df.to_csv(file_path, index=False, encoding='gb18030')
                print(f"保存更新后的文件：{file_name}\n")

"""
拓：批量化处理交易流水文件
"""
def batch_identity():
    """
    1.获取给定目录下的所有子目录名称，并存储到列表中
    """
    # 给定目录路径
    dir_1 = 'NNModel/process/database/raw/'
    dir_2 = 'NNModel/process/database/cooked/'
    new_dir = 'NNModel/process/database/identity/'
    conbine_file = 'NNModel/process/database/identity/combined_data.csv'
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
    2.遍历每个子目录，对每个子目录进行人员身份提取、身份信息合并、身份信息填充
    """
    for item in sub_dir:
        dir_path_1 = dir_1 + item
        identity(dir_path_1,new_dir)
        conbine(new_dir,conbine_file)
    for item in sub_dir:
        dir_path_2 = dir_2 + item
        # print(dir_path_2)
        identity_match(conbine_file,dir_path_2)
