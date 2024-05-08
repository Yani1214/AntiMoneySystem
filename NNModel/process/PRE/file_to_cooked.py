from process.PRE.data_remove_5 import batch_reback
from process.PRE.data_label_6 import batch_trans,batch_person
from process.PRE.data_feature_7 import batch_feature
from process.PRE.data_people_8 import trans_people
from process.PRE.data_duplicate_9 import batch_duplicate
from process.PRE.data_special_10 import batch_csv,feature_to_fill,trans_to_fill,id_to_fill,person_to_fill,trans_to_people,src_to_fill
from process.PRE.data_format_11 import batch_standard
from process.PRE.data_combine_12 import people_to_standard
from process.PRE.data_to_MySQL import person_to_db,people_to_db,people_standard_to_db

# 将已经人工处理后的数据移动到原位
batch_reback()

# 对交易数据和交易人员打标签
batch_trans()
batch_person()

# 将1-11人交易表格转换为标准的csv表格
# batch_csv()

# 对交易数据表格填充新的特征
batch_feature()

# 将每个人的相关交易数据各自存为一个表格
trans_people()

# # 将之前不符合格式要求的special的工行数据进行处理，并加入到之前处理完的一人一表中
# feature_to_fill()
# src_to_fill()
# trans_to_fill()
# id_to_fill()
# person_to_fill()
# trans_to_people()

# 对一人一表数据去重
batch_duplicate()

# 对一人一表和人员信息表进行英文标准化和编码标准化
batch_standard()

# 重新生成people_standard.csv表
people_to_standard()

# 将一人一表和人员信息表存入mysql
person_to_db()
people_to_db()
people_standard_to_db()