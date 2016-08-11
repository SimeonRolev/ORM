import sqlite3
import psycopg2 as PG
import MySQLdb as mysql


from database import SqliteDatabase, PostgreDatabase, MySQLDatabase
from query import Query, and_, or_
from fields import Field, CharField, IntegerField


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

        return type.__new__(cls, name, bases, _dict)


class Model(object):

    __metaclass__ = ModelMetaClass
    database = None

    def __init__(self, **kwargs):

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

        self.__class__.placeholder = self.database.placeholder

    def insert(self):
        self.database.insert(self.table, self)

    def update(self):
        self.database.update(self.table, self)

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

    def __repr__(self):
        return "FN: {} | age {}".format(self.first_name, self.age)


class School(Model):
    # These fields get declared in the class.
    # When you make an instance, it only saves the value
    name = CharField()
    age = IntegerField()
    students_count = IntegerField()


# sqlite_db = SqliteDatabase('people.db')
# sqlite_db.create_tables(User)
# user = User(first_name='Ivan', age=20, is_active=False)

# user.save()
# user.first_name = 'Grozdan'
# user.save()

# postgre_db = PostgreDatabase('schools')
# postgre_db.create_tables(School)
# school = School(name="Naiden Gerov", age=120, students_count=50)
# school.save()
# school.name = "Updated"
# school.save()
# print School.select().where(School.name.contains("Updated")).limit(10).get()

# con = mysql.connect(host="localhost", user="Simeon Rolev", passwd="password", db="schools")
#
# ms_database = MySQLDatabase('MySqlSchools')
# ms_database.create_tables(School)
# s = School(name="Naiden Gerov", age=120, students_count=50)
# s.save()
# s.name = "Last Update"
# s.save()
# print School.select().where(School.age > 50).get()

# conn = PG.connect(database='postgres', user='postgres', password='password', host='localhost')
# pg_cursor = conn.cursor()
# # pg_cursor.execute('CREATE SCHEMA rolev_schema')
# pg_cursor.execute('CREATE TABLE rolev_schema.gibsons('
#                   'rowid INT CONSTRAINT rowid PRIMARY KEY,'
#                   'name varchar(300))')
# conn.commit()

