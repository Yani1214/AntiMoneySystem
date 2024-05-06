import pandas as pd
import os
import shutil
from process.PRE.data_feature_7 import is_more_median,is_more_mean,is_more_qualite_25,is_more_qualite_75,time_interval,trans_frequency
#######################################################处理工行表格########################################################### 
"""
1. 将涉案人员的涉案交易格式进行统一（杨小琴的比较特别，是先手动改成其他表的格式再统一进行处理的）
"""
def xlxs_to_csv(file_path,dst_dir):
    # 读取xlsx文件
    xlsx_file = pd.read_excel(file_path,dtype=str)
    xlsx_file.fillna('\t', inplace=True)
    file_name = os.path.splitext(file_path)[0]
    print(file_name)
    people_name = ['杨小琴', '苟兴兵', '何年碧', '何顺京', '胡秋艳', '李春荣', '李菊英', '孙翊章', '王庆凤', '颜爱中', '余英', '张柱碧']

    # 创建新的DataFrame用于存储处理后的数据
    csv_data = pd.DataFrame()

    # 1. 赋值给新csv表的“交易卡号”和”交易账号“列
    csv_data['交易卡号'] = xlsx_file['账号'].astype(str) + '\t'
    csv_data['交易账号'] = xlsx_file['账号'].astype(str) + '\t'

    # 2. 赋值给新csv表的”交易户名“列
    csv_data['交易户名'] = os.path.basename(file_name)

    csv_data['交易证件号码'] = '\t'

    # 3. 合并入账日期和入账时间列，并替换.为:，赋值给新csv表的”交易时间“列
    csv_data['交易时间'] = xlsx_file['入账日期'].astype(str) + ' ' + xlsx_file['入账时间'].astype(str).str.replace('.', ':') + '\t'

    # 4. 去除发生额列的逗号，赋值给新csv表的”交易金额“列
    csv_data['交易金额'] = xlsx_file['发生额'].astype(str).str.replace(',', '')

    # 5. 赋值给新csv表的”交易余额“列
    csv_data['交易余额'] = xlsx_file['余额'].astype(str).str.replace(',', '')

    # 6. 将借贷标志列的值替换为出和进，并赋值给新csv表的”交易金额“列
    csv_data['收付标志'] = xlsx_file['借贷标志'].apply(lambda x: '出' if x == '借' or '付' else '进')

    # 7. 赋值给新csv表的”交易对手账户“列
    csv_data['交易对手账卡号'] = xlsx_file['对方帐户'].astype(str) + '\t'

    # 8. 如果存在对手身份证号列，则赋值给新csv表的”对手身份证号“列，否则赋制表符
    if '交易对方身份证件' in xlsx_file.columns:
        csv_data['对手身份证号'] = xlsx_file['交易对方身份证件'].astype(str).str.replace('\'', ':') + '\t'
    else:
        csv_data['对手身份证号'] = '\t'

    # 9. 赋值给新csv表的”对手户名“列
    # 检查某一列的值是否包含列表中的任何一个字符串
    for search_string in people_name:
        # 遍历 DataFrame 中的每一行
        for index, row in xlsx_file.iterrows():
            # 检查搜索字符串是否是当前行指定列的子串
            if search_string in str(row['对方户名']):
                print(f"'{search_string}' 匹配成功")
            elif search_string in str(row['交易场所']):
                print(f"'{search_string}' 在交易场所中匹配成功")
                xlsx_file['对方户名'] = search_string
            elif search_string in str(row['注释']):
                print(f"'{search_string}' 在注释中匹配成功")
                xlsx_file['对方户名'] = search_string
    csv_data['对手户名'] = xlsx_file['对方户名']

    # 10. 赋值给新csv表的”摘要说明“列
    csv_data['摘要说明'] = xlsx_file['注释']

    # 11. 将制表符值赋给新csv表的”商号代码“列
    csv_data['商户代码'] = '\t'

    # 12. 将制表符值赋给新csv表的”交易类型“列
    csv_data['交易类型'] = '\t'

    # 13. 对涉案人员交易进行打标签处理
    csv_data['label'] = ''
    for index, row in csv_data.iterrows():
        if (row['对手户名'] in people_name) and (row['交易户名'] in people_name):
            csv_data.loc[index, 'label'] = 1
        else:
            csv_data.loc[index, 'label'] = 0
    # 将处理后的数据保存为csv文件
    csv_data.to_csv(dst_dir + os.path.basename(file_name) + '.csv', index=False, encoding='gb18030')

def batch_csv():
    # 给定目录路径
    dir = 'NNModel/process/database/special/'
    dst_dir = 'NNModel/process/database/special_people/'
    os.makedirs(dst_dir, exist_ok=True)
    sub_dir= []
    name_to_number = {}  # 存储文件名到数字的映射字典
    i = 1
    for name in os.listdir(dir):
        sub_dir.append(name)
    for item in sub_dir:
        dir_path = dir + item
        xlxs_to_csv(dir_path,dst_dir)

"""
2. 将csv表的特征进行补充构建
"""
def feature_to_fill():
    people_folder = 'NNModel/process/database/special_people'
    for filename in os.listdir(people_folder):
        file_path = os.path.join(people_folder, filename)
        is_more_median(file_path)
        is_more_mean(file_path)
        is_more_qualite_25(file_path)
        is_more_qualite_75(file_path)
        time_interval(file_path)
        trans_frequency(file_path)

def src_to_fill():
    people_folder = 'NNModel/process/database/special_people'
    for f_name in os.listdir(people_folder):
        f_path = os.path.join(people_folder, f_name)
        df = pd.read_csv(f_path,dtype=str, encoding='gb18030')
        df['交易来源'] = '中国工商银行'
        df.to_csv(f_path, index=False, encoding='gb18030')
"""
3. 将涉案交易填充在各自的涉案人员表格中
"""
def trans_to_fill():
# 设置文件夹路径
    folder_path = "NNModel/process/database/special_people"

    # 获取文件夹中的所有csv文件
    csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]

    # 循环处理每个csv文件
    for file in csv_files:
        # 读取csv文件
        df = pd.read_csv(os.path.join(folder_path, file),dtype=str, encoding='gb18030')

        opponent_name_column = "对手户名"
        
        # 循环处理csv文件的每一行
        for index, row in df.iterrows():
            opponent_name = str(row[opponent_name_column]).strip()
            opponent_csv_file = os.path.join(folder_path, opponent_name + ".csv")
            
            # 检查对手csv文件是否存在
            if os.path.exists(opponent_csv_file):
                opponent_df = pd.read_csv(opponent_csv_file,dtype=str, encoding='gb18030')
                
                # 检查当前行的数据是否在对手csv文件中出现
            if not any(row.equals(opponent_row) for _, opponent_row in opponent_df.iterrows()):
                    # 如果没有出现，则将该数据复制到对手csv文件中
                    opponent_df = pd.concat([opponent_df, pd.DataFrame([row])], ignore_index=True)
                    opponent_df.to_csv(opponent_csv_file, index=False, encoding='gb18030')
            else:
                # 如果对手csv文件不存在，则打印文件不存在
                print(f"将数据复制到{opponent_csv_file}表格中")
"""
4. 填充交易表格中的身份证号
"""
# 收集people.csv中属于people列表的人名-身份证号键值对（去重）
# 收集special_people/杨小琴.csv中属于people列表的人名-身份证号键值对（去重）
# 将二者收集到的键值对进行整合
# 通过这些键值对，对special_people文件夹下的文件进行“交易证件号码”列和“对手身份证号”列进行填充

def id_to_fill():
    # 读取people.csv文件
    people_df = pd.read_csv("NNModel/process/database/identity/combined_data.csv",dtype=str, encoding='gb18030')

    # 收集people列表中的人名-身份证号键值对并去重
    people_mapping = dict(zip(people_df['账户开户名称'], people_df['开户人证件号码']))
    people_mapping = {name: id_number for name, id_number in people_mapping.items() if pd.notna(id_number)}

    # 初始化一个空字典，用于收集special_people文件夹中的人名-身份证号键值对
    special_people_mapping = {}

    # 遍历special_people文件夹中的所有文件
    special_people_folder = "NNModel/process/database/special_people"
    for filename in os.listdir(special_people_folder):
        if filename.endswith(".csv"):
            file_path = os.path.join(special_people_folder, filename)
            # 读取文件
            special_people_df = pd.read_csv(file_path,dtype=str, encoding='gb18030')
            # 收集属于people列表的人名-身份证号键值对并去重
            for index, row in special_people_df.iterrows():
                if row['对手户名'] not in people_mapping and str(row['对手身份证号']).strip() != '':
                    special_people_mapping[row['对手户名']] = row['对手身份证号']

    # 合并两个字典
    combined_mapping = {**people_mapping, **special_people_mapping}
    print(combined_mapping)

    # 遍历special_people文件夹中的所有文件，填充“交易证件号码”列和“对手身份证号”列
    for filename in os.listdir(special_people_folder):
        if filename.endswith(".csv"):
            file_path = os.path.join(special_people_folder, filename)
            # 读取文件
            special_people_df = pd.read_csv(file_path,dtype=str, encoding='gb18030')
            # 填充列
            special_people_df['交易证件号码'] = special_people_df['交易户名'].map(combined_mapping)
            special_people_df['对手身份证号'] = special_people_df['对手户名'].map(combined_mapping)
            # 保存文件
            special_people_df.to_csv(file_path, index=False, encoding='gb18030')
    print("处理完成！")

"""
5. 将涉案人员的信息补充到combined_data.csv表格中
"""
# 将每个表格的人名-账号-身份证填充到combined_data中
def person_to_fill():
    ##### 将需要填充的数据进行汇总 #####
    # 遍历special_people文件夹中的所有文件
    special_people_folder = "NNModel/process/database/special_people"
    # 创建一个空的DataFrame来存储所有结果
    all_results = pd.DataFrame()
    for filename in os.listdir(special_people_folder):
        if filename.endswith(".csv"):
            file_path = os.path.join(special_people_folder, filename)
            # 读取文件
            df = pd.read_csv(file_path,dtype=str, encoding='gb18030')
            
            # 提取指定列的数据
            transaction_data = df[["交易户名", "交易证件号码", "交易卡号", "交易账号"]]
            counterparty_data = df[["对手户名", "对手身份证号", "交易对手账卡号"]]
            # 复制切片（视图之下操作会报错）
            counterparty_data = counterparty_data.copy()
            transaction_data = transaction_data.copy()

            #修改列名，方便之后的数据合并
            counterparty_data.rename(columns={"对手户名": "交易户名", "对手身份证号": "交易证件号码", "交易对手账卡号": "交易卡号"}, inplace=True)

            # 复制指定列
            new_column = counterparty_data["交易卡号"].copy()
            # 将复制的列添加到表中
            counterparty_data["交易账号"] = new_column
            
            # 合并数据
            combined_data = pd.concat([transaction_data, counterparty_data])
            # 将结果添加到总结果中
            all_results = pd.concat([all_results, combined_data])
    # 去重
    all_results.drop_duplicates(inplace=True)
    # 去除"交易卡号", "交易账号"为空的行
    all_results = all_results[(all_results["交易卡号"].str.strip() != "") & (all_results["交易账号"].str.strip() != "")]

    ###### 将all_results数据连接到people表中 ########
    # 创建一个空的DataFrame来存储所有结果
    people_data = pd.DataFrame()
    
    # 读取CSV文件
    dst_file = 'NNModel/process/database/identity/combined_data.csv'
    people_name = ['杨小琴', '苟兴兵', '何年碧', '何顺京', '胡秋艳', '李春荣', '李菊英', '孙翊章', '王庆凤', '颜爱中', '余英', '张柱碧']
    df_people = pd.read_csv(dst_file, dtype=str, encoding='gb18030')
    all_results.rename(columns={"交易户名": "账户开户名称", "交易证件号码": "开户人证件号码", "交易卡号": "交易卡号","交易账号":"账号1"}, inplace=True)
    all_results["账号2"] = '\t'
    all_results['银行名称'] = '中国工商银行'
    all_results['任务流水号'] = '\t'
    all_results['备注'] = '有交易明细'

    all_results["label"] = ''
    for index, row in all_results.iterrows():
        if row['账户开户名称'] in people_name:
            all_results.loc[index, 'label'] = 1
        else:
            all_results.loc[index, 'label'] = 0

    # print(all_results)

    people_data = pd.concat([df_people, all_results])
    # 去重
    people_data.drop_duplicates(inplace=True)
    # 去除账户开户名称为空值或只包含空格的行
    people_data = people_data[people_data["账户开户名称"].str.strip().fillna("") != ""]

    # 将处理后的数据保存为csv文件
    people_data.to_csv(dst_file, index=False, encoding='gb18030')


"""
6. 将涉案交易信息填充到一人一表中
"""
# 合并文件内容
def merge_files(source_file, dest_file):
    source_df = pd.read_csv(source_file, encoding='gb18030',dtype=str)
    dest_df = pd.read_csv(dest_file, encoding='gb18030',dtype=str)
    merged_df = pd.concat([dest_df, source_df], ignore_index=True)
    merged_df.to_csv(dest_file, index=False, encoding='gb18030')


def trans_to_people():
    src_directory = "NNModel/process/database/special_people"
    dst_directory = "NNModel/process/database/people"
    # 1. 收集某个目录下的所有文件名
    filenames = []
    for filename in os.listdir(dst_directory):
        if os.path.isfile(os.path.join(dst_directory, filename)):
            filenames.append(filename)
    # 2. 遍历另外一个目录下的每一个文件，如果该文件存在于列表中，则将里面的值接着那个目录下同名文件的数据进行复制；若不存在，则将该表复制到那个目录下
    for root, dirs, files in os.walk(src_directory):
        for file in files:
            if file in filenames:
                source_path = os.path.join(root, file)
                dest_path = os.path.join(dst_directory, file)
                merge_files(source_path, dest_path)
            else:
                # 如果文件不存在于列表中，则将该文件复制到目标目录
                source_path = os.path.join(root, file)
                dest_path = os.path.join(dst_directory, file)
                shutil.copy(source_path, dest_path)

