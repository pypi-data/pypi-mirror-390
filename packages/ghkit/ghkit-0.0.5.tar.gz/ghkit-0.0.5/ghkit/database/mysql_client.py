from contextlib import contextmanager
from typing import Any, Dict, List

import pymysql
from dbutils.pooled_db import PooledDB, PooledSharedDBConnection


class AttrDict(dict):
    """
    例子::

        d = AttrDict()
        d.name = "foo"
        print(d.name)
    """

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as e:
            raise AttributeError(name) from e

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        self.pop(name, None)

    def require(self, *params):
        """看字典是否拥有必要的key，不存在则抛出异常

        Args:
            params: key的名称
        """
        for param in params:
            if not self.get(param):
                raise ValueError(f"{param} is required")


OP = AttrDict(
    AND="AND",
    OR="OR",
    ADD="+",
    SUB="-",
    MUL="*",
    DIV="/",
    BIN_AND="&",
    BIN_OR="|",
    XOR="#",
    MOD="%",
    EQ="=",
    LT="<",
    LTE="<=",
    GT=">",
    GTE=">=",
    NE="!=",
    IN="IN",
    NOT_IN="NOT IN",
    IS="IS",
    IS_NOT="IS NOT",
    LIKE="LIKE",
    ILIKE="ILIKE",
    BETWEEN="BETWEEN",
    REGEXP="REGEXP",
    IREGEXP="IREGEXP",
    CONCAT="||",
    BITWISE_NEGATION="~",
)


class MySQLClient:
    """
    例子::

        db = MySQLClient(host=mysql_host, port=mysql_port, user=mysql_user, passwd=mysql_password, db=mysql_database)

    Args:
        host: 服务器地址
        port: 服务器端口
        user: 用户名
        passwd: 密码
        db: 数据库名
        charset: 连接字符集
        mincached: 空闲时连接池最小连接数
        maxcached: 空闲时连接池最大连接数
        logger: 日志对象
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: str = None,
        passwd: str = None,
        db: str = None,
        charset: str = "utf8mb4",
        mincached: int = 1,
        maxcached: int = 5,
        logger=None,
        **kwargs,
    ):
        self._pool = PooledDB(
            pymysql,
            host=host,
            port=port,
            db=db,
            user=user,
            passwd=passwd,
            charset=charset,
            mincached=mincached,
            maxcached=maxcached,
            **kwargs,
        )
        self._log = logger

    def select_one(
        self,
        table: str,
        conds=None,
        fields=None,
        extra="",
        prefix_sql: str = None,
        page=None,
        page_size=None,
        debug_sql=True,
        conn=None,
    ) -> Dict:
        """查询一行

        例子::

            db.select_one("users", conds={"id": 1})，得到{"id": 1, "name": "foo"}

        Args:
            table:  表名
            conds:  条件, 可传{"name": "foo"}/{"name~": "foo"}（等于/不等于） or {"age": [10, 20]}/{"age~": [10, 20]}（在范围内/不在范围内）
                            or {"date>=", "1970-08-08"}（大于）
            fields: 字段名, 默认为*, 可传"id, name, ..."
            prefix_sql: 查询语句中WHERE之前的sql
            extra:  额外，比如order by, group by, ...
            page:   页数
            page_size: 每页消息数
            debug_sql:
            conn:
        Returns:
            字典
        """
        return self._select(
            table,
            one=True,
            conds=conds,
            fields=fields,
            prefix_sql=prefix_sql,
            extra=extra,
            page=page,
            page_size=page_size,
            debug_sql=debug_sql,
            conn=conn,
        )

    def select_all(
        self,
        table: str,
        conds=None,
        fields=None,
        prefix_sql: str = None,
        extra="",
        page=None,
        page_size=None,
        debug_sql=True,
        conn=None,
        flat=False,
    ) -> List[Dict]:
        """查询所有行

        例子::

            db.select_all("users", conds={"name": "foo"})，得到[{"id": 1, "name": "foo"}, {"id": 2, "name": "bar"}]

        Args:
            table:  表名
            conds:  条件, 可传{"name": "foo"}/{"name~": "foo"}（等于/不等于） or {"age": [10, 20]}/{"age~": [10, 20]}（在范围内/不在范围内）
                            or {"date>=", "1970-08-08"}（大于）
            fields: 字段名, 默认为*, 可传"id, name, ..."
            prefix_sql: 查询语句中WHERE之前的sql
            extra:  额外，比如order by, group by, ...
            page:   页数
            page_size: 每页消息数
            debug_sql:
            conn:
            flat:   当select_one为False 查询多条且只查询的字段只有一个时进行数据扁平化处理
                    True: select id from user 返回从 [{"id": 1}, {"id": 2}] => [1, 2]

        Returns:
            列表
        """
        return self._select(
            table,
            one=False,
            conds=conds,
            fields=fields,
            prefix_sql=prefix_sql,
            extra=extra,
            page=page,
            page_size=page_size,
            debug_sql=debug_sql,
            conn=conn,
            flat=flat,
        )

    def _select(
        self,
        table: str,
        conds: Dict = None,
        fields: str = None,
        one: bool = False,
        prefix_sql: str = None,
        extra: str = "",
        page: int = None,
        page_size: int = None,
        debug_sql: bool = True,
        conn: PooledSharedDBConnection = None,
        flat=False,
    ):
        if not table:
            raise ValueError("table is required")

        conds, params = self.make_pair(conds)
        sql, params = self.build_query(
            table,
            fields=fields,
            conds=conds,
            params=params,
            prefix_sql=prefix_sql,
            extra=extra,
            page=page,
            page_size=page_size,
        )
        return self.exec(sql, params, select_one=one, debug_sql=debug_sql, conn=conn, flat=flat)

    def add(
        self,
        table: str,
        params: Dict = None,
        on_repeat: Dict = None,
        debug_sql: bool = True,
        conn: PooledSharedDBConnection = None,
    ) -> int:
        """增加一行

        例子::

            db.add("users", {"name": "foo", "info": "boo"})

        Args:
            table:
            params: 数据库字段:值
            on_repeat: 如遇到重复行，值同params
            debug_sql:
            conn:
        Returns:
            最后插入的行id
        """
        return self.add_multi(table, [params], on_repeat=on_repeat, debug_sql=debug_sql, conn=conn)

    def add_multi(
        self,
        table: str,
        rows: List[Dict] = None,
        on_repeat: Dict = None,
        debug_sql: bool = True,
        conn: PooledSharedDBConnection = None,
    ) -> int:
        """增加多行

        例子::

            db.add_multi("users", [{"name": "foo", "info": "boo"}, {"name": "foo2", "info": "boo2"}])

        Args:
            table:     表名
            rows:      [params], params同add
            on_repeat: 如遇到重复行，值同params
            debug_sql:
            conn:
        Returns:
            最后插入的行id
        """
        if not rows:
            raise ValueError("add_multi rows is required")

        first_row = rows[0]
        fields = ",".join(first_row.keys())

        value_formats = []
        values = []
        for row in rows:
            value_formats.append(f"({self.get_formats(row)})")
            values.extend(list(row.values()))
        value_formats_str = ",".join(value_formats)

        sql = f"""
                INSERT INTO {table} ({fields}) VALUES {value_formats_str}
              """

        if on_repeat:
            update_fields, update_values = self.make_pair(on_repeat)
            sql += " ON DUPLICATE KEY UPDATE " + " , ".join(update_fields)
            values.extend(update_values)

        return self.exec(sql, values, debug_sql=debug_sql, conn=conn)

    def update(
        self,
        table: str,
        sets: Dict = None,
        conds: Dict = None,
        debug_sql: bool = True,
        conn: PooledSharedDBConnection = None,
    ):
        """更新行

        例子::

            db.update("users", sets={"name": "foo"}, conds={"id": 1})

        Args:
            table: 表名
            sets:  key是字段名，value是更新值
            conds: 查询条件，用法同select_one
            debug_sql:
            conn:
        """
        sets, s_params = self.make_pair(sets)
        conds, c_params = self.make_pair(conds)
        sql = f"UPDATE {table} SET "

        sql += ",".join(sets)

        sql += " WHERE " + " AND ".join(conds)

        return self.exec(sql, s_params + c_params, debug_sql=debug_sql, conn=conn)

    def delete(
        self,
        table: str,
        conds: Dict = None,
        debug_sql: bool = True,
        conn: PooledSharedDBConnection = None,
    ):
        """删除行

        Args:
            table: 表名
            conds: 查询条件，用法同select_one
            debug_sql:
            conn:

        """
        conds, params = self.make_pair(conds)

        sql = f" DELETE FROM {table} "

        sql += " WHERE " + " AND ".join(conds)

        return self.exec(sql, params, debug_sql=debug_sql, conn=conn)

    def delete_all(self, table, debug_sql=True, conn=None):
        """删除所有行

        Args:
            table: 表名
            debug_sql:
            conn:
        """
        sql = f""" DELETE FROM {table} """

        return self.exec(sql, debug_sql=debug_sql, conn=conn)

    @contextmanager
    def transaction(self):
        """支持事务

        例子1::

            with db.transaction() as conn:
                db.add(data1, conn=conn)
                db.delete(data2, conn=conn)

        例子2::

            with db.transaction() as conn:
                db.exec("INSERT INTO table1 VALUES ...", conn=conn)
                db.exec("DELETE FROM table2 WHERE ...", conn=conn)
        """
        conn = self.get_connection()
        try:
            conn.begin()
            yield conn
            conn.commit()
        finally:
            # PooledDB因为设置reset会自动rollback
            conn and conn.close()

    def get_connection(self) -> PooledSharedDBConnection:
        """获取mysql连接池的一个连接"""
        return self._pool.connection()

    def exec(
        self,
        sql: str,
        params: List[Any] = None,
        select_one: bool = None,
        debug_sql: bool = True,
        conn: PooledSharedDBConnection = None,
        flat: bool = False,
    ):
        """执行SQL语句

        例子1::

            db.exec("UPDATE users SET name=%s where id=%s", ["foo", 1])

        例子2::

            db.exec("SELECT * FROM users", select_one=False)

        Args:
            sql:        sql语句，包含占位符
            params:     占位符对应的值
            select_one: 查询语句时用到，有两种模式，True: 查一条: {"id": 1, "name": "foo"}，
                        False: 查所有： [{"id": 1, "name": "foo"}]
            debug_sql:  是否写日志
            conn:       mysql连接，事务操作时用到，传入conn时，不commit和close
            flat:       当select_one为False 查询多条且只查询的字段只有一个时进行数据扁平化处理
                        True: select id from user 返回从 [{"id": 1}, {"id": 2}] => [1, 2]

        Returns:
            查询语句，根据select_one的值，返回一行或所有行
            非查询语句，返回最后生效的行id
        """
        if debug_sql and self._log:
            # 将sql拼接上参数
            debug_sql_str = self._rm_line_break(sql) % tuple(params or [])
            self._log.debug(f"mysql_exec: {debug_sql_str}")
        connection = conn or self.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(sql, params)
            if not conn:
                connection.commit()

            result = {}
            if select_one is None:
                result = cursor.lastrowid
            elif select_one:
                if cursor.rowcount:
                    result = dict(
                        zip(
                            [col[0] for col in cursor.description],
                            cursor.fetchone(),
                        )
                    )
            else:
                field_names = [col[0] for col in cursor.description]
                if flat and len(field_names) == 1:
                    # 当select_one为False 查询多条且只查询的字段只有一个时和需要数据扁平化处理
                    # eg. select id from user 返回从 [{"id": 1}, {"id": 2}] => [1, 2]
                    result = [row[0] for row in cursor.fetchall()]
                else:
                    result = [dict(zip(field_names, row)) for row in cursor.fetchall()]
            return result
        except Exception as e:
            if self._log:
                self._log.error(
                    f"exec sql error: {e}, sql({self._rm_line_break(sql)}), params({params})"
                )
            raise
        finally:
            cursor and cursor.close()
            if not conn:
                connection and connection.close()

    @staticmethod
    def get_formats(contents: Any) -> str:
        """动态生成sql的占位符，根据contents长度生成若干个%s

        例子::

            get_formats([1, 2, 3]) 得到 "%s, %s, %s"
            get_formats({"a": 1, "b": 2}) 得到 "%s, %s"

        Args:
            contents: 列表

        Returns:
            含有占位符的sql语句
        """
        return ",".join(["%s" for _ in range(len(contents))])

    @classmethod
    def get_in_formats(cls, field: str, contents: List[Any]) -> str:
        """动态生成sql的in语句

        例子::

            get_in_formats("id", [1, 2, 3]) 得到 "id in (%s, %s, %s)"

        Args:
            field: 数据库字段名
            contents: 字段的所有值

        Returns:
            含有字段名和占位符的sql语句
        """
        return f"{field} in ({cls.get_formats(contents)})"

    @classmethod
    def get_not_in_formats(cls, field: str, contents: List[Any]) -> str:
        """动态生成sql的not in语句

        例子::

            get_not_in_formats("id", [1, 2, 3]) 得到 "id not in (%s, %s, %s)"

        Args:
            field: 数据库字段名
            contents: 字段的所有值

        Returns:
            含有字段名和占位符的sql语句
        """
        return f"{field} not in ({cls.get_formats(contents)})"

    @classmethod
    def get_op_formats(cls, field, contents, op=OP.IN):
        """

        Args:
            field:
            contents:
            op: OP.IN or OP.NOT_IN, default: OP.IN

        Returns:

        """
        return f"{field} {op} ({cls.get_formats(contents)})"

    @classmethod
    def build_query(
        cls,
        table: str,
        fields: str = None,
        conds: List[str] = None,
        params: List[Any] = None,
        prefix_sql: str = None,
        extra: str = "",
        page: int = None,
        page_size: int = None,
    ) -> List[Any]:
        """创建查询语句与参数, 供db.execute执行

        Args:
            table:  表名
            fields: 字段名
            conds:  查询条件, e.g. ["name=%s", "age in (%s, %s)"]
            params: 占位符的参数, e.g. ["foo", 1, 2]
            prefix_sql: 查询语句中WHERE之前的sql
            extra:
            page:
            page_size:
        Return:
            [sql, params]
        """
        sql = prefix_sql if prefix_sql else f"SELECT {fields or '*'} FROM {table} "

        if page:
            page_size = int(page_size)
            extra += f" LIMIT {(int(page) - 1) * page_size},{page_size} "

        if not conds:
            return [f"{sql} {extra}", None]
        sql += " WHERE " + " AND ".join(conds)
        return [f"{sql} {extra}", params]

    @staticmethod
    def _rm_line_break(s: str) -> str:
        """去掉换行符和内部空格，然后用空格串起来，比如sql为了可读性，会有换行符，但是日志采集时，最好是只有一行

        Args:
            s (str): 字符串

        Returns:
            str: 字符串
        """
        return " ".join(row.strip() for row in s.splitlines())

    @classmethod
    def make_pair(cls, args: Dict = None):
        """
        根据args生成conds, params
        >>> MySQLClient.make_pair({"name__is_not": None, "phone__like": "%123%", "age__not_in": [20, 30]})
        (['name IS NOT %s', 'phone LIKE %s', 'age NOT IN (%s,%s)'], [None, '%123%', 20, 30])
        >>> MySQLClient.make_pair({"name__is": None, "age__lt": 100})
        (['name IS %s', 'age < %s'], [None, 100])
        """
        conds, params = [], []
        for key, value in args.items():
            if "__" in key:
                field_name, op = key.rsplit("__", 1)
            else:
                field_name, op = key, "EQ"
            if not hasattr(OP, op.upper()):
                raise AttributeError(f"field '{field_name}' flag '{op}' is not available")
            op = OP.get(op.upper())
            if isinstance(value, list):
                c = cls.get_op_formats(field_name, value, op)
                conds.append(c)
                params.extend(value)
            else:
                c = f"{field_name} {op} %s"
                conds.append(c)
                params.append(value)
        return conds, params
