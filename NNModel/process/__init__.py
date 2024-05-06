from flask import Blueprint

###################################创建文件上传、人工文件处理蓝图对象###############################
upload_blueprint = Blueprint('upload_blueprint',__name__,url_prefix='/process')
byhand_blueprint = Blueprint('byhand_blueprint',__name__,url_prefix='/process')


from . import views