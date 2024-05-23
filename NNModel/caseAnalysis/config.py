# 应用的配置设置
class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:2002104118tzq@localhost/anti-money'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 其他通用配置...


class DevelopmentConfig(Config):
    DEBUG = True
    # 开发环境特定配置...


class ProductionConfig(Config):
    DEBUG = False
    # 生产环境特定配置...
