import sqlite3
from query import Query
from fields import Field, CharField, IntegerField

conn = sqlite3.connect('people.db')


class ModelMetaClass(type):

    def __new__(cls, name, bases, _dict):

        columns = {key: value
                   for key, value in _dict.items()
                   if isinstance(value, Field)}

        # This iteration makes the name attribute of the instantiated Field equal to the name of the column
        for k, v in columns.iteritems():
            v.name = k

        _dict['columns'] = columns
        _dict['table'] = name
        _dict['sorted_columns'] = sorted(columns, key=lambda x: columns[x].order_num)
        _dict['cursor'] = conn.cursor()

        return type.__new__(cls, name, bases, _dict)


class Model(object):

    __metaclass__ = ModelMetaClass

    def __init__(self, cursor, **kwargs):

        self.cursor = cursor

        # Setting the values of the fields
        for key, value in self.columns.items():
            if key in kwargs:
                setattr(self, key, kwargs[key])
            elif value.default:
                setattr(self, key, value.default)
            else:
                if value.null:
                    setattr(self, key, 'null')
                else:
                    raise AttributeError("You must set a value to: {}".format(key))

    @classmethod
    def qmarks(cls):
        result = ''
        for _ in cls.columns:
            result += '?, '
        return '(' + result[:-2] + ')'

    @classmethod
    def row_schema(cls):
        result = ''
        for key in cls.sorted_columns:
            result += "{} {}, ".format(key, cls.columns[key].sql_type)
        return result[:-2]

    def row_values(self):
        result = list()
        row = [key for key in self.sorted_columns]
        for value in row:
            result.append(str(getattr(self, value)))
        return tuple(result)

    @classmethod
    def setup_schema(cls, cursor):
        cursor.execute('''CREATE TABLE IF NOT EXISTS {} ({})'''.format(cls.table, cls.row_schema()))

    def insert(self):
        query = """INSERT INTO {} VALUES {}""".format(self.table, self.qmarks())
        self.cursor.execute(query, self.row_values())
        conn.commit()
        self._id = self.cursor.lastrowid

    def set_of_update(self):
        result = ''
        for col in self.sorted_columns:
            result += '{} = ?, '.format(col)
        return result[:-2]

    def update(self):
        query = """UPDATE {} SET {} WHERE {}""".format(self.table, self.set_of_update(), 'rowid = ' + str(self._id))
        self.cursor.execute(query, self.row_values())
        conn.commit()

    def save(self):
        if hasattr(self, '_id'):
            self.update()
        else:
            self.insert()

    @classmethod
    def select(cls, *args):
        return Query(cls, args)


class User(Model):
    # These fields get declared in the class.
    # When you make an instance, it only saves the value
    first_name = CharField()
    age = IntegerField()
    sex = CharField()
