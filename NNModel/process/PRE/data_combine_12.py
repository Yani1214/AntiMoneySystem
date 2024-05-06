import pandas as pd
import os
###################################################重新构建people_standard.csv表##################################################

"""
1. 提取people文件夹下所有表格中的trans_card,trans_account,trans_name,id_number/cp_card,cp_name,cp_id和trans_source列
"""
def people_to_standard():
    # 创建people_standard.csv表
    columns = ['person_name', 'person_id', 'person_card', 'person_account', 'bank_name', 'label', 'person_number']
    people_name = ['杨小琴', '苟兴兵', '何年碧', '何顺京', '胡秋艳', '李春荣', '李菊英', '孙翊章', '王庆凤', '颜爱中', '余英', '张柱碧']
    all_results = pd.DataFrame()
    df = pd.DataFrame(columns=columns)

    # 提取people文件夹下所有表格中特定列的值
    folder_path = "NNModel/process/database/people"
    if os.path.exists(folder_path):
        csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]
        for file in csv_files:
            df_person = pd.read_csv(os.path.join(folder_path, file),dtype=str)
            unique_trans = df_person[['trans_name', 'trans_card', 'trans_account', 'id_number','trans_source']].drop_duplicates()
            unique_cp = df_person[['cp_name', 'cp_card','cp_id','trans_source']].drop_duplicates()
            unique_cp = unique_cp.assign(cp_account = unique_cp['cp_card'])
            new_column_order = ['cp_name', 'cp_card', 'cp_account', 'cp_id', 'trans_source']
            unique_cp = unique_cp.reindex(columns=new_column_order)
            unique_cp.rename(columns={"cp_name": "trans_name", "cp_card": "trans_card", "cp_account": "trans_account","cp_id": "id_number"}, inplace=True)
        
            # 将提取出来的值进行合并，并写入all_results中
            combined_data = pd.concat([unique_trans, unique_cp])
            all_results = pd.concat([all_results, combined_data])
            all_results = pd.concat([all_results, unique_trans])

        all_results.drop_duplicates(inplace=True)
        df['person_name'] = all_results['trans_name']
        df['person_id'] =  all_results['id_number']
        df['person_card'] =  all_results['trans_card']
        df['person_account'] = all_results['trans_account']
        df['bank_name'] =  all_results['trans_source']

        df['label'] = ''
        for index, row in df.iterrows():
            if (row['person_name'] in people_name):
                df.loc[index, 'label'] = 1
            else:
                df.loc[index, 'label'] = 0
    

    """
    2. 根据people_standard.csv的person_name列在person.csv中的person_name查找其person_number列，并将其填充到people_standard.csv的person_number列
    """
    filepath = 'NNModel/process/database/identity/people.csv'
    if os.path.exists(filepath):
        person_df = pd.read_csv(filepath,dtype=str,encoding='utf-8')

        # 只选择 'person_name' 和 'person_number' 列
        selected_columns = ['person_name', 'person_number']
        person_selected = person_df[selected_columns]

        # 去除重复值
        person_selected_unique = person_selected.drop_duplicates()
        person_selected_unique = person_selected_unique[person_selected_unique["person_number"].str.strip().fillna("") != ""]

        # 将 person_name 和 person_number 列转换为字典
        person_dict = dict(zip(person_selected_unique['person_name'], person_selected_unique['person_number']))


        # 在 people_standard_df 中根据 person_name 列查找对应的 person_number 列
        df['person_number'] = ''
        df['person_number'] = df['person_name'].map(person_dict)
        df = df[df["person_number"].str.strip().fillna("") != ""]

        # 将填充后的结果保存回 people_standard.csv
        df.to_csv('NNModel/process/database/identity/people_standard.csv', index=False,encoding='utf-8')
