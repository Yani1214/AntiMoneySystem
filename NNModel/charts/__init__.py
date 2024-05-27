from flask import Blueprint

###################################创建文件上传、人工文件处理蓝图对象###############################
charts_blueprint = Blueprint('charts_blueprint',__name__,url_prefix='/charts')

from . import views