class BaseConfig:
    SECRET_KEY = '610100'
    PER_PAGE_COUNT = 10


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@127.0.0.1:3306/flask_database?charset=utf8mb4"
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_HOST = '127.0.0.1'
    CACHE_REDIS_PORT = 6379
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_USE_SSL = True
    MAIL_PORT = 465
    MAIL_USERNAME = '1137952368@qq.com'
    MAIL_PASSWORD = 'nhdzmwcdrljqhfag'
    MAIL_DEFAULT_SENDER = '1137952368@qq.com'
