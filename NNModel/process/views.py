import os
import sys
import zipfile
import json
import tempfile
import glob
import shutil
import io
from zipfile import ZipFile
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint,request,jsonify,redirect, send_file, Response
from process import upload_blueprint,byhand_blueprint

###########################################辅助函数定义###########################################

ZIP_FOLDER = 'NNModel/process/database/zip/'
UPLOAD_FOLDER = 'NNModel/process/database/raw/'
FILE_PATH = 'NNModel/process/PRE/main.py'

IMPORT_FOLDER = 'NNModel/process/database/manual/'
FILE_ANALYSIS_PATH = 'NNModel/process/PRE/file_to_cooked.py'

# 文件上传解压
def unzip_file(zip_file, extract_to):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            file_info.filename = file_info.filename.encode('cp437').decode('gbk')  # 将文件名进行解码
            zip_ref.extract(file_info, extract_to)

def reunzip_file(zip_file, extract_to):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            file_info.filename = file_info.filename.encode('GB18030').decode('gbk')  # 将文件名进行解码
            zip_ref.extract(file_info, extract_to)

# 处理分析文件上传的文件内容
def execute_another_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        script = f.read()
        exec(script)

# 读取json格式的manual下子文件夹名称、子文件夹下文件名称和修改日期
def get_files_info(directory,files_info):
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            # 获取文件的创建时间
            created_time = datetime.fromtimestamp(os.path.getctime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
            # 获取父文件夹名称
            parent_folder_name = os.path.basename(os.path.abspath(directory))
            # 去掉文件名的后缀
            filename_without_extension = os.path.splitext(filename)[0]
            files_info.append({"missonNumber": parent_folder_name, "bank": filename_without_extension, "createdAt": created_time})
    # print(files_info)
    return files_info

# 判断文件夹是否为空
def is_empty_dir(directory):
    # 获取文件夹中的所有文件和子文件夹
    contents = os.listdir(directory)
    # 检查文件夹中的所有内容
    for item in contents:
        # 拼接子文件夹的完整路径
        item_path = os.path.join(directory, item)
        # 如果是文件夹，则递归调用该函数检查子文件夹是否为空
        if os.path.isdir(item_path):
            if not is_empty_dir(item_path):
                return False
        # 如果是文件，则说明文件夹不为空，直接返回 False
        elif os.path.isfile(item_path):
            return False
    # 所有子文件夹都为空，或者文件夹中没有任何内容，则返回 True
    return True
#################################################编写文件上传视图函数##############################################

@upload_blueprint.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)

        # 将zip文件存储到指定的文件夹中
        if not os.path.exists(ZIP_FOLDER):
            os.makedirs(ZIP_FOLDER)
        file.save(os.path.join(ZIP_FOLDER, filename))

        # 将zip文件解压到指定目录
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        unzip_file(os.path.join(ZIP_FOLDER, filename), UPLOAD_FOLDER)

        # 对数据开始进行分析处理和上传数据库
        execute_another_file(FILE_PATH)

        return jsonify({'message': '请到人工数据处理页面进一步处理', 'filename': filename}), 200
    

###########################################编写人工数据处理视图函数#################################################
# 获取前端请求，动态传输每个交易文件父文件夹名称、交易表名称、文件修改日期，并在前端展示
@byhand_blueprint.route('/byhand', methods=['POST'])
def byhand_file():
    data = request.json
    # 读取manual下子文件夹名称、子文件夹下文件名称和修改日期，并构造为json格式返回给前端

    # 给定目录路径
    dir = 'NNModel//process//database//manual//'
    sub_dir= []
    files_info = []
    # 遍历目录中的所有文件和子目录
    for item in os.listdir(dir):
        # 获取子目录的完整路径
        item_path = os.path.join(dir, item)
        # 判断是否是一个目录
        if os.path.isdir(item_path):
            sub_dir.append(item)
        
    for item in sub_dir:
        dir_path = dir + item
        data = get_files_info(dir_path,files_info)

    # print(data)
    processed_data = {"result": "Data processed successfully", "data": data}
    return jsonify(processed_data)  # 将处理后的数据以 JSON 格式返回给前端

# 获取manual文件夹，并打包成压缩包下载至本地
@byhand_blueprint.route('/byhand/export', methods=['POST'])
def byhand_file_export():
    # 要打包的文件夹路径
    folder_path = IMPORT_FOLDER

    # 创建一个临时的zip文件
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
        with ZipFile(temp_zip.name, 'w') as zip_file:
            # 使用 os.walk 遍历目标文件夹下的所有文件和子文件夹
            for root, _, files in os.walk(folder_path):
                for file in files:
                    # 构建文件的绝对路径
                    file_path = os.path.join(root, file)
                    # 计算文件在 Zip 文件中的相对路径
                    rel_path = os.path.relpath(file_path, folder_path)
                    # 将文件添加到 zip 文件中，使用相对路径
                    zip_file.write(file_path, rel_path)
        
        # 读取临时zip文件内容
        temp_zip.seek(0)
        zip_data = temp_zip.read()

    # 返回 ZIP 文件内容给前端
    return send_file(
        io.BytesIO(zip_data),
        mimetype='application/zip',
        as_attachment=True,
        download_name='manual.zip'
    )


# 点击“重新上传”按钮，将manual文件夹的所有文件进行覆盖
@byhand_blueprint.route('/byhand/import', methods=['POST'])
def byhand_file_import():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']

    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        # 将zip文件存储到指定的文件夹中
        if not os.path.exists(ZIP_FOLDER):
            os.makedirs(ZIP_FOLDER)
        file.save(os.path.join(ZIP_FOLDER, filename))
        # 将zip文件解压到指定目录
        if not os.path.exists(IMPORT_FOLDER):
            os.makedirs(IMPORT_FOLDER)
        reunzip_file(os.path.join(ZIP_FOLDER, filename), IMPORT_FOLDER)

        return jsonify({'message': '请核验已经上传的数据', 'filename': filename}), 200

# 点击“核验完成”按钮，将manual文件夹的所有文件移动到cooked文件夹
@byhand_blueprint.route('/byhand/detect', methods=['POST'])
def byhand_file_detecte():
    if(is_empty_dir(IMPORT_FOLDER)):
        return jsonify({'result': 'no','message':'文件夹已空'}), 200
    else:
        # 对数据开始进行分析处理和上传数据库
        execute_another_file(FILE_ANALYSIS_PATH)
        return jsonify({'result': 'ok','message':'成功传入至数据库'}), 200