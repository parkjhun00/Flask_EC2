class SystemConfig:
  DEBUG = True

  SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{user}:{password}@{host}/{db-name}?charset=utf8'.format(**{
      'user': 'AWS',
      'password': 'password',
      'host': 'localhost',
      'db_name': 'AWS'
  })

Config = SystemConfig