import sqlite3


connection = sqlite3.connect('people.db')
cursor = connection.cursor()


class Field(object):
    def __init__(self, name=None, primary_key=False,
                 max_length=None, null=True,
                 default=None, value=None):

        self.name = name
        self.primary_key = primary_key
        self.max_length = max_length
        self.null = null
        self.default = default
        self.value = value

    def __get__(self, obj, type=None):
        pass

    def __set__(self, obj, value):
        pass


class IntegerField(Field):
    pass


class CharField(Field):
    pass


class ModelMetaclass(type):

    def __new__(cls, name, bases, _dict):

        result_dict = {key: value for key, value in _dict.items() if isinstance(value, Field)}
        columns = [key for key in result_dict]
        _dict['columns'] = columns

        return type.__new__(cls, name, bases, _dict)


class Model(object):

    __metaclass__ = ModelMetaclass

    id = IntegerField()
    id.db_type = 'INTEGER PRIMARY KEY AUTOINCREMENT'

    @classmethod
    def setup_schema(cls, cursor):
        pass

    def __init__(self, cursor, **kwargs):
        self.cursor = cursor
        for key, value in kwargs.items():
            print "KEY: {} VALUE {}".format(key, value)
            self.key = value

    def save(self):
        pass


class User(Model):
    name = CharField()
    age = IntegerField()
