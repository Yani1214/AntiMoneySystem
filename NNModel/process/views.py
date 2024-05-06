import os
import sys
import zipfile
from werkzeug.utils import secure_filename
from flask import Blueprint,request,jsonify,redirect
from process import upload_blueprint,byhand_blueprint

###########################################辅助函数定义###########################################

ZIP_FOLDER = 'NNModel/process/database/zip/'
UPLOAD_FOLDER = 'NNModel/process/database/raw/'
FILE_PATH = 'NNModel/process/PRE/main.py'

def unzip_file(zip_file, extract_to):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            file_info.filename = file_info.filename.encode('cp437').decode('gbk')  # 将文件名进行解码
            zip_ref.extract(file_info, extract_to)

def execute_another_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        script = f.read()
        exec(script)
###########################################编写文件上传视图函数###################################

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

        return jsonify({'message': '上传成功', 'filename': filename}), 200
    

###########################################编写人工数据处理视图函数#################################################
@byhand_blueprint.route('/byhand', methods=['POST'])
def byhand_file():
    # 获取前端请求，动态传输每个交易文件父文件夹名称、交易表名称、文件修改日期，并在前端展示

    
    # 获取people文件夹，并打包成压缩包下载至本地

    # 点击“重新上传”按钮，将manual文件夹的所有文件进行覆盖

    # 点击“核验完成”按钮，将manual文件夹的所有文件移动到cooked文件夹