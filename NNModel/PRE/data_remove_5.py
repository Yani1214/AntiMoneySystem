import os
from pathlib import Path
import shutil
import pandas as pd

################################将收付标志需要人工判断的表格移动至另外的文件夹中##############################################
def file_remove(folder_path,src_path):
    # 构建目的文件夹
    dst_folder = "database/manual/"
    # 提取源路径父文件夹
    directory, father_folder = os.path.split(folder_path)
    # 构造目的完整路径
    dst_path = Path(dst_folder) / father_folder
    os.makedirs(dst_path, exist_ok=True)
    # 使用shutil.move()函数移动文件
    shutil.move(src_path, dst_path)

######################################将人工处理完后的文件再次存储到之前的文件夹中#################################################
def file_reback(folder_path,src_path):
    # 构建目的文件夹
    dst_folder = "database/cooked/"
    # 提取源路径父文件夹
    directory, father_folder = os.path.split(folder_path)
    # 构造目的完整路径
    dst_path = Path(dst_folder) / father_folder
    # 使用shutil.move()函数移动文件
    shutil.move(src_path, dst_path)

def batch_reback():
    """
    1.获取给定目录下的所有子目录名称，并存储到列表中
    """
    # 给定目录路径
    dir = 'database/manual/'
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
    2.遍历每个子目录，对交易表格进行移动处理
    """
    for item in sub_dir:
        dir_path = dir + item
        # 获取目录中所有文件的文件名
        files = os.listdir(dir_path)
        for file in files:
            target_path = os.path.join(dir_path, file)
            file_reback(dir_path,target_path)