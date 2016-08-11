import sqlite3
import psycopg2 as PG
import MySQLdb as MS
from warnings import filterwarnings
filterwarnings('ignore', category=MS.Warning)


placeholders = {'sqlite': '?',
                'mysql': '%s'}


def set_of_update(model):
    result = ''
    for col in model.sorted_columns:
        result += '{} = %s, '.format(col)
    return result[:-2]


def sql_row_schema(model, rowid=''):
    result = '{}'.format(rowid)
    for key in model.sorted_columns:
        result += "{} {}, ".format(key, model.columns[key].content_type)
    return result[:-2]


def row_values(model):
    result = list()
    row = [key for key in model.sorted_columns]
    for value in row:
        result.append(str(getattr(model, value)))
    return tuple(result)


def fields_tuple(model):
    result = ''
    for field in model.sorted_columns:
        result += '{}, '.format(field)
    return '(' + result[:-2] + ')'


class Database(object):

    def __init__(self):
        raise Exception("NOT IMPLEMENTED!")
        # self.placeholder = ''

    def create_tables(self, model):
        model.conn = self.conn
        model.cursor = self.cursor
        model.database = self
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS {} ({})'''.
                            format(model.table, sql_row_schema(model, self.rowid)))

    def insert(self):
        pass

    def update(self, table, model):
        query = """UPDATE {} SET {} WHERE {}""".format(table, set_of_update(model), 'rowid = ' + str(model._id))
        self.cursor.execute(query, row_values(model))
        self.conn.commit()

    def placeholders(self, model):
        result = ''  # a placeholder for the ID
        for _ in model.columns:
            result += '{}, '.format(self.placeholder)
        return '(' + result[:-2] + ')'

    def set_of_update(self, model):
        result = ''
        for col in model.sorted_columns:
            result += '{} = {}, '.format(col, self.placeholder)
        return result[:-2]


class SqliteDatabase(Database):

    def __init__(self, db_name):
        self.rowid = ''
        self.placeholder = '?'
        self.db_type = 'sqlite'

        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def insert(self, table, model):
        query = """INSERT INTO {} VALUES {}""".format(table, self.placeholders(model))
        self.cursor.execute(query, row_values(model))
        self.conn.commit()
        model._id = self.cursor.lastrowid


class PostgreDatabase(Database):

    def __init__(self, db_name):
        self.db_type = 'postgres'
        self.placeholder = '%s'
        self.rowid = 'rowid SERIAL, '
        self.conn = PG.connect(database='postgres', user='postgres', password='password', host='localhost')
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE SCHEMA IF NOT EXISTS {}".format(db_name))
        self.schema_name = db_name

    def postgre_row_schema(self, model):
        result = 'rowid SERIAL, PRIMARY KEY (rowid), '
        for key in model.sorted_columns:
            field_type = 'varchar(50)' if model.columns[key].content_type == 'text' else 'int'
            result += "{} {}, ".format(key, field_type)
        return result[:-2]

    def create_tables(self, model):
        model.conn = self.conn
        model.cursor = self.cursor
        model.database = self
        model.schema_and_table = self.schema_name + '.' + model.table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS {} ({})'''.
                            format(model.schema_and_table, self.postgre_row_schema(model)))

    def insert(self, table, model):
        query = """INSERT INTO {} {} VALUES {} RETURNING rowid""".format(model.schema_and_table,
                                                                       fields_tuple(model),
                                                                       self.placeholders(model))
        self.cursor.execute(query, row_values(model))
        self.conn.commit()
        model._id = self.cursor.fetchone()[0]
        print "MODEL ID: {}".format(model._id)

    def set_of_update(self, model):
        result = ''
        for col in model.sorted_columns:
            result += '{} = %s, '.format(col)
        return result[:-2]

    def update(self, table, model):
        query = """UPDATE {} SET {} WHERE {}""".format(model.schema_and_table, self.set_of_update(model), 'rowid = ' + str(model._id))
        print "EXECUTING POSTRGE QUERY: {} with {}".format(query, row_values(model))
        self.cursor.execute(query, row_values(model))
        self.conn.commit()


class MySQLDatabase(Database):

    def __init__(self, db_name):
        self.placeholder = '%s'
        self.rowid = 'rowid MEDIUMINT NOT NULL AUTO_INCREMENT, PRIMARY KEY (rowid), '
        self.db_type = 'mysql'

        self.conn = MS.connect(host="localhost", user="Simeon Rolev", passwd="password")
        self.cursor = self.conn.cursor()
        sql = 'CREATE DATABASE IF NOT EXISTS {}'.format(db_name)
        self.cursor.execute(sql)
        self.cursor.execute("USE {}".format(db_name))

    def insert(self, table, model):
        query = """INSERT INTO {} {} VALUES {}""".format(table, fields_tuple(model), self.placeholders(model))
        # print "EXECUTING {} with {}".format(query, self.row_values(model))
        self.cursor.execute(query, row_values(model))
        self.conn.commit()
        model._id = self.cursor.lastrowid
