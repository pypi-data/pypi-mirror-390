import os
import pymysql
import logging
from contextlib import contextmanager
from dbutils.pooled_db import PooledDB

logger = logging.getLogger("whisper_ai")

class WhisperDB_Pool:
    # 类级连接池，共享于所有实例
    _pool = None

    @classmethod
    def _get_pool(cls):
        if cls._pool is None:
            host = os.getenv("WHISPER_SERVER_HOST", "172.27.0.4")
            cls._pool = PooledDB(
                creator=pymysql,
                maxconnections=50,  # 增加最大连接数，根据服务器并发调整
                mincached=5,
                maxcached=20,
                blocking=True,
                maxusage=1000,
                setsession=[],      # 连接创建时执行的SQL语句列表
                host=host,
                user='RPA',
                password='Zxs123',
                database='zxs_order',
                charset='utf8mb4'   # 确保字符集支持中文
            )
        return cls._pool

    def __init__(self):
        # 初始化时不创建连接，延迟到 __enter__ 中从池获取
        self.connection = None

    @contextmanager
    def cursor(self):
        if self.connection is None:
            raise RuntimeError("WhisperDB must be used within a 'with' context to acquire a connection.")
        cur = self.connection.cursor()
        try:
            yield cur
        finally:
            try:
                cur.close()
            except Exception:
                pass

    def query(self, sql, params=None):
        with self.cursor() as cursor:
            cursor.execute(sql, params or ())
            return cursor.fetchall()

    def commit(self):
        if self.connection:
            self.connection.commit()

    def get_cursor(self):
        # 保留向后兼容，但强烈建议使用 cursor() 上下文管理器
        if self.connection is None:
            raise RuntimeError("WhisperDB must be used within a 'with' context to acquire a connection.")
        return self.connection.cursor()

    def close(self):
        # 在 __exit__ 中调用，释放连接回池
        if self.connection:
            self.connection.close()  # DBUtils 会自动释放回池
            self.connection = None

    # 实现上下文管理协议
    def __enter__(self):
        self.connection = self._get_pool().connection()
        # logger.info(f"Pool connections: {self._pool._connections}")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # 有异常时回滚，正常退出时提交
        if self.connection:
            if exc_type:
                try:
                    self.connection.rollback()
                except Exception:
                    pass
            else:
                try:
                    self.connection.commit()
                except Exception:
                    pass
            self.close()  # 释放连接回池
        if exc_type:
            print(f"Error: {exc_value}")