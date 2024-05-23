from flask import Blueprint

###################################创建文件上传、人工文件处理蓝图对象###############################
analysis_blueprint = Blueprint('analysis_blueprint',__name__,url_prefix='/analysis')

from . import views