# coding: utf-8

import re
from . import __name__ as MODULE_NAME
from . import errors
from . import driver
from .cursor import Cursor
from .lob import LOB
from .driver import DB_TYPE_BLOB, DB_TYPE_CLOB, DB_TYPE_NCLOB, DbType

p_client_locale = re.compile("CLIENT_LOCALE=(.*?);")

locale_mapping = {
            "zh_cn.57372": "utf8",
            "zh_cn.utf8": "utf8",
            "zh_cn.utf-8": "utf8",
            "zh_cn.5488": "gb18030",
            "zh_cn.gb18030": "gb18030",
            "zh_cn.gb18030-2000": "gb18030",
            "en_us.819": "utf8",
            "8859-1": "utf8",
            "gb": "gbk",
            "gb2312-80": "gbk",
        }

def get_client_locale(dsn):
    match = p_client_locale.search(dsn)
    if not match:
        return 'utf-8'                
    locale_8s = match.group(1)
    client_locale = locale_mapping.get(locale_8s.lower(), 'utf-8')
    return client_locale


class Connection(object):
    __module__ = MODULE_NAME

    def __init__(self, dsn, user, password):
        self._cyobj = None
        self._version = None
        cy_conn = driver.CyConnection(dsn, user, password)
        cy_conn.connect()
        self._cyobj = cy_conn
        self._client_locale = get_client_locale(dsn)        
        temp_cursor = self.cursor()
        temp_cursor.execute("set environment autocommit off")
        temp_cursor.close()
        
    def __repr__(self):
        cls_name = "{}.{}".format(self.__class__.__module__, self.__class__.__name__)
        if self._cyobj is None:
            return "<{cls_name} disconnected>".format(cls_name=cls_name)
        return "<{cls_name} to {username}@{dsn}>".format(cls_name=cls_name, username=self.username, dsn=self.dsn)

    def __del__(self):
        if self._cyobj is not None:
            self._cyobj.close(in_del=True)
            self._cyobj = None

    def __enter__(self):
        self._verify_connected()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self._cyobj is not None:
            self._cyobj.close(in_del=True)
            self._cyobj = None

    def _verify_connected(self):
        if self._cyobj is None:
            errors.raise_error(errors.ERR_NOT_CONNECTED)   
    
    def close(self):
        self._verify_connected()
        self._cyobj.close()
        self._cyobj = None

    def commit(self):
        self._verify_connected()
        self._cyobj.commit()

    def createlob(
        self, lob_type, data=None
    ):
        self._verify_connected()
        if lob_type not in (DB_TYPE_CLOB, DB_TYPE_NCLOB, DB_TYPE_BLOB):
            message = (
                "lob type should be one of gbase8sdb.DB_TYPE_BLOB, "
                "gbase8sdb.DB_TYPE_CLOB or gbase8sdb.DB_TYPE_NCLOB"
            )
            raise TypeError(message)
        impl = self._cyobj.create_temp_lob_impl(lob_type)
        lob = LOB._create_with_cyobj(impl)
        lob.encoding = self.client_locale
        if data:
            lob.write(data)
        return lob

    def cursor(self):
        self._verify_connected()
        return Cursor(self)
   
    def ping(self):
        self._verify_connected()
        self._cyobj.ping()

    def rollback(self):
        self._verify_connected()
        self._cyobj.rollback()
        
    def cancel(self):
        self._verify_connected()
        self._cyobj.cancel()
        
    @property
    def autocommit(self):
        self._verify_connected()
        return self._cyobj.autocommit

    @autocommit.setter
    def autocommit(self, value):
        self._verify_connected()
        self._cyobj.autocommit = value

    @property
    def dsn(self):
        self._verify_connected()
        return self._cyobj.dsn

    @property
    def inputtypehandler(self):
        self._verify_connected()
        return self._cyobj.inputtypehandler

    @inputtypehandler.setter
    def inputtypehandler(self, value):
        self._verify_connected()
        self._cyobj.inputtypehandler = value


    @property
    def outputtypehandler(self):
        self._verify_connected()
        return self._cyobj.outputtypehandler

    @outputtypehandler.setter
    def outputtypehandler(self, value):
        self._verify_connected()
        self._cyobj.outputtypehandler = value

    @property
    def transaction_in_progress(self):
        self._verify_connected()
        return self._cyobj.get_transaction_in_progress()

    @property
    def username(self):
        self._verify_connected()
        return self._cyobj.username

    @property
    def version(self):
        if self._version is None:
            self._verify_connected()
            self._version = ".".join(str(c) for c in self._cyobj.server_version)
        return self._version

    @property
    def warning(self):
        self._verify_connected()
        return self._cyobj.warning

    @property
    def client_locale(self):
        return self._client_locale



def connect(dsn, user, password):
    """
    创建数据库连接，并返回连接对象
    """
    if len(dsn) == 0 or len(user) == 0 or len(password) == 0:
        raise errors.raise_error(errors.ERR_INVALID_CONNECT_PARAMS)
    if isinstance(dsn, unicode):
        dsn = dsn.encode("utf-8")
    if isinstance(user, unicode):
        user = user.encode("utf-8")
    if isinstance(password, unicode):
        password = password.encode("utf-8")
    return Connection(dsn=dsn, user=user, password=password)
