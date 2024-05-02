class Config:
    SECRET_KEY = 'Contraseña super secreta'


class DevelopmentConfig(Config):
    DEBUG = True
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'gestor_hotel'



config = {
    'development': DevelopmentConfig
}
