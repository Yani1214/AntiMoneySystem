import os
import sys
import pandas as pd
from data_model_1 import batch_data
from data_match_2 import batch_identity
from data_clean_3 import batch_name,batch_clean
from data_judge_4 import batch_judge
from data_remove_5 import batch_reback
from data_label_6 import batch_trans,batch_person
from data_feature_7 import batch_feature
from data_people_8 import trans_people
from data_duplicate_9 import batch_duplicate
from data_special_10 import batch_csv,feature_to_fill,trans_to_fill,id_to_fill,person_to_fill,trans_to_people,src_to_fill
from data_format_11 import batch_standard
from data_combine_12 import people_to_standard
from data_to_MySQL import person_to_db,people_to_db,people_standard_to_db

# # 对数据进行初步特征提取
# batch_data()

# # 对数据进行空余特征填充
# batch_identity()

# # 对数据的对手户名补充身份证号
# batch_name()

# # 对无效数据进行清除
# batch_clean()

# # 对收付标志进行统一，并将需要人工处理的表格移动到别处
# batch_judge()

# # 将已经人工处理后的数据移动到原位
# batch_reback()

# 对交易数据和交易人员打标签
# batch_trans()
# batch_person()

# 将1-11人交易表格转换为标准的csv表格
# batch_csv()

# 对交易数据表格填充新的特征
# batch_feature()

# # 将每个人的相关交易数据各自存为一个表格
# trans_people()

# # 将之前不符合格式要求的special的工行数据进行处理，并加入到之前处理完的一人一表中
# feature_to_fill()
# src_to_fill()
# trans_to_fill()
# id_to_fill()
# person_to_fill()
# trans_to_people()

# # 对一人一表数据去重
# batch_duplicate()

# # 对一人一表和人员信息表进行英文标准化和编码标准化
# batch_standard()

# # 重新生成people_standard.csv表
# people_to_standard()

# # 将一人一表和人员信息表存入mysql
# person_to_db()
# people_to_db()
# people_standard_to_db()

