import os
import sys
import pandas as pd

from process.PRE.data_model_1 import batch_data
from process.PRE.data_match_2 import batch_identity
from process.PRE.data_clean_3 import batch_name,batch_clean
from process.PRE.data_judge_4 import batch_judge

# 对数据进行初步特征提取
batch_data()

# 对数据进行空余特征填充
batch_identity()

# 对数据的对手户名补充身份证号
batch_name()

# 对无效数据进行清除
batch_clean()

# 对收付标志进行统一，并将需要人工处理的表格移动到别处
batch_judge()



