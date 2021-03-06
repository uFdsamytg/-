import pymysql
from app.log import Logger
from app.configUtil import ConfigUtil
from sqlalchemy import create_engine

log = Logger().log()
config = ConfigUtil()


class MySqlDb:
    def __init__(self):
        self.dbConfig = config.getValue('db')
        self.host = self.dbConfig['host']
        self.username = self.dbConfig['username']
        self.password = self.dbConfig['password']
        self.port = self.dbConfig['port']
        self.db = self.dbConfig['dbName']
        self.charset = self.dbConfig['charset']

    def getConnect(self):
        """
        获取mysql数据库连接
        :return:
        """
        con = None
        try:
            con = pymysql.connect(
                host=self.host, user=self.username, passwd=self.password, port=self.port, db=self.db, charset=self.charset
            )
        except Exception as e:
            log.error(e)
            log.info("获取数据库连接失败,正在尝试重新连接...")
            for _ in range(5):
                try:
                    con = pymysql.connect(
                        host=self.host, user=self.username, passwd=self.password, port=self.port, db=self.db,
                        charset=self.charset
                    )
                    log.info("连接成功！")
                    break
                except Exception as e:
                    log.error(e)
        return con

    @staticmethod
    def getCursor(connect):
        """
        获取数据库游标
        :param connect:
        :return:
        """
        return connect.cursor()

    def getEngine(self):
        """
        获取pandas需要的Engine
        :return:
        """
        return create_engine(f'mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.db}')

    def insertDataList(self, sql, data):
        """
        插入一个集合数据
        :param sql:
        :param data:
        :return:
        """
        for entity in data:
            self.insertData(sql, entity)

    def insertData(self, sql, data):
        """
        执行插入语句
        :param sql:执行的sql
        :param data:需要插入的数据
        :return:
        """
        if sql is not None and sql != ' ':
            if data is not None:
                con = self.getConnect()
                cur = self.getCursor(con)
                cur.execute(sql, data)
                con.commit()
                # 关闭连接，关闭游标
                cur.close()
                con.close()
                log.info("数据插入成功")
            else:
                log.info("待插入数据不能为空")
        else:
            log.info("执行sql不能为空")

    def query(self, sql):
        """
        查询数据
        :param sql:
        :return:
        """
        if sql is not None and sql != " ":
            con = self.getConnect()
            cur = self.getCursor(con)
            cur.execute(sql)
            data = cur.fetchall()
            cur.close()
            con.close()
            return data
        else:
            log.info("执行sql不能为空")

    def getOne(self, sql):
        """
        查询数据
        :param sql:
        :return:
        """
        if sql is not None and sql != " ":
            con = self.getConnect()
            cur = self.getCursor(con)
            cur.execute(sql)
            data = cur.fetchone()
            cur.close()
            con.close()
            return data
        else:
            log.info("执行sql不能为空")

    def executeSql(self, sql):
        """
        执行sql语句
        :param sql:
        :return:
        """
        con = self.getConnect()
        cur = self.getCursor(con)
        try:
            if sql is not None and sql != " ":
                cur.execute(sql)
            else:
                log.info("执行sql不能为空")
        except Exception as e:
            log.error(e)
            con.rollback()
        else:
            con.commit()
        finally:
            # 关闭连接，关闭游标
            cur.close()
            con.close()

