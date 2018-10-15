# -*- coding: utf-8 -*-
"""
Created on 2016年10月6日

@author: albin
"""

import os
import xml.etree.cElementTree as ET
from threading import Lock

import petl

_DEFAULT_DB_CFG_PATH = os.path.join(os.path.expanduser("~"), 'cfg', 'db.xml')
_DEFAULT_DB_ID = "crs"
_LOCK = Lock()


class Connector(object):
    """
    This class obtains a connection and a cursor to a schema.

    :param file:
        configuration file, an object or a file path.
    :type file:
        ``basestring`` or a ``xml.etree.ElementTree.Element``

    :param ID:
        schema identify
    :type ID:
        ``str``

    :param info:
        optional parameter for customization.
    :type info:
        ``dict``

    :structure Connector{
                    -module
                    -connection
                    -cursor
                };

    E.g., create a Connector, config read from configuration file:
        >>> c = Connector('wddp', 'db.xml')
        >>> c.cursor.execute('insert into ...')
        >>> c.connection.commit()
        >>> c.close()

    E.g., auto close resource and auto commit, config read from default configuration file:
        >>> with Connector() as cusor:
        >>>    cursor.execute('insert into ...')
    E.g., specify cursor type
        >>> from MySQLdb.cursors import  DictCursor
        >>> with Connector(cursorclass=DictCursor) as dict_cursor:
        >>>    dict_cursor.execute(sql)
    """

    def __init__(self, ID=None, file=None, **info):
        ID = ID or _DEFAULT_DB_ID
        file = file or _DEFAULT_DB_CFG_PATH
        root = ET.ElementTree(file=file).getroot() if isinstance(file, (unicode, str)) else file
        try:                                                   # fetch xml_node by ID
            node = root.find("./*[@id='%s']" % ID)
        except SyntaxError:
            node = self.find_node(root, ID)
        self.module = node.find('./driver').attrib['module']  # get_content module name
        info.update(node.find('./connection').attrib)         # get_content and attach connection config
        self.__connect(info)                                  # obtain a connection
        self.cursor = self.connection.cursor()                # create a cursor

    def __enter__(self):
        """context manager that returns a Connector"""
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        """commit if successful otherwise rollback"""
        if exc_type:
            self.connection.rollback()
        else:
            self.connection.commit()
        self.close()
        return False

    def __connect(self, info):
        """convert digital basestring to integer and obtain a connection object."""
        if 'port' in info:
            info.update(port=int(info['port']))
        self.connection = __import__(self.module).connect(**info)

    def close(self):
        self.connection.close()

    def request(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    @staticmethod
    def find_node(root, ID):
        for connector in root:
            if connector.attrib['id'] == ID:
                return connector


class Connector2(Connector):
    def __init__(self, ID=None, file=None, **info):
        Connector.__init__(self, ID, file, **info)

    def __enter__(self):
        return self

    def request(self, sql):
        temp = petl.fromdb(self.connection, sql)
        return petl.wrap([row for row in temp])

    def write(self, table, table_name, mode='insert'):
        write(self.cursor, table, table_name, mode, self.module)


class Queries(object):
    _sql = None

    def __init__(self, connector):
        self.connector = connector
        self.buffered = None

    def request(self, **kwargs):
        sql = self.sql(**kwargs)
        print sql
        self.buffered = self.connector.request(sql)
        return self.buffered

    def sql(self, **kwargs):
        return self._sql.format(**kwargs)


def write(cursor, table, table_name, mode='insert', module='MySQLdb'):
    """
    load table to $table_name.

    :param cursor:
        database agent
    :type
        Cursor

    :param table:
        data container
    :type table
        ``petl.util.base.Table`` or double list like this: [['field_name', ...], ['value_object', ...], ...]

    :param table_name:
        table name
    :type table_name:
        ``str``

    :param mode
        truncate and than insert if mode equal 'trunc';
        insert data if mode equal 'insert';
        insert and replace row where pk has exit if mode equal 'replace'
    :type mode
        ``str``={'trunc'|'insert'|'replace'}
    """

    if 'MYSQL' in module.upper():
        cursor.execute('SET SQL_MODE=ANSI_QUOTES')

    if mode == 'trunc':
        res = petl.todb(table, cursor, table_name)
    elif mode == 'insert':
        res = petl.appenddb(table, cursor, table_name)
    elif mode == 'replace':
        with _LOCK:
            petl.io.db.SQL_INSERT_QUERY = 'REPLACE INTO %s (%s) VALUES (%s)'
            res = petl.appenddb(table, cursor, table_name)
            petl.io.db.SQL_INSERT_QUERY = 'INSERT INTO %s (%s) VALUES (%s)'
    else:
        raise ValueError("Argument mode must be {'trunc'|'insert'|'replace'}, not '%s'" % mode)
    return res


def DBWriter(data, table, mode='update'):
    import log_module
    home = os.path.expanduser("~")
    log = log_module.log_module(os.path.join(home, 'log', 'dbImport'))

    with Connector('crs', os.path.join(home, 'cfg', 'db.xml')) as cursor:
        cursor.execute('SET SQL_MODE=ANSI_QUOTES')

        if mode == 'update':
            cursor.execute('DROP TABLE IF EXISTS ' + table)
            data.todb(cursor, table, create=True, dialect='mysql')
            log.write('update {0} rows to table {1}'.format(len(data) - 1, table))

        else:
            petl.io.db.SQL_INSERT_QUERY = 'REPLACE INTO %s (%s) VALUES (%s)'
            data.appenddb(cursor, table)
            petl.io.db.SQL_INSERT_QUERY = 'INSERT INTO %s (%s) VALUES (%s)'
            log.write('append {0} rows to table {1}'.format(len(data) - 1, table))
