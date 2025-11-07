import sqlalchemy

def get_sql_connection(params):  
    database_connection = sqlalchemy.create_engine('postgresql://{0}:{1}@{2}/{3}'.
                                               format(params.username, params.password, 
                                                      params.ip, params.database))
    return database_connection