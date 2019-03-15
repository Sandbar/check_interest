import os
import pymysql
import pandas as pd
import time


class DataManager:

    def __init__(self,):
        self.__db_host = os.environ['mysql_db_host']
        self.__db_port = int(os.environ['mysql_db_port'])
        self.__db_pwd = os.environ['mysql_db_pwd']
        self.__db_name = os.environ['mysql_db_name']
        self.__db_user = os.environ['mysql_db_user']
        self.conn = self.create_db_connect()

    def create_db_connect(self):
        conn = pymysql.connect(host=self.__db_host, user=self.__db_user,
                               password=self.__db_pwd, db=self.__db_name,
                               port=self.__db_port)
        return conn

    def get_interests(self):
        sql = "SELECT * from dw_dim_interest"
        outs = pd.read_sql(sql, self.conn)
        outs.to_csv('data_{0}.csv'.format(str(round(time.time() * 1000))), index=False)
        return outs[['name', 'id']]

    def delete_interest(self, sid):
        sql = "DELETE FROM dw_dim_interest WHERE id={0}".format(sid)
        cursor = self.conn.cursor()
        cursor.execute(sql)
        self.conn.commit()

    def select_by_name(self, name):
        sql = '''SELECT id,name,type from dw_dim_interest where name="{0}"'''.format(name)
        outs = pd.read_sql(sql, self.conn)
        return outs.iloc[0]


if __name__ == '__main__':
    DM = DataManager()
    ans = DM.get_interests()
    print(ans)

