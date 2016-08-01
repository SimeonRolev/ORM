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
        return self.value

    def __set__(self, obj, value):
        obj.value = value

    def __repr__(self):
        return "Field: name={}, value={}".format(self.name, self.value)


class IntegerField(Field):
    def __repr__(self):
        return "IntegerField: name={}, value={}".format(self.name, self.value)


class CharField(Field):
    def __repr__(self):
        return "CharField: name={}, value={}".format(self.name, self.value)


class ModelMetaclass(type):

    def __new__(cls, name, bases, _dict):

        # Gathering all the fields, defined in the User
        fields_dict = {key: value
                       for key, value in _dict.items()
                       if isinstance(value, Field)}

        # Set the Field.name attribute to the name of the variable
        for key in fields_dict:
            # print "Setting {} to {}".format(fields_dict[key].name, key)
            fields_dict[key].name = key

        columns = [key for key in fields_dict]
        columns.sort()

        _dict['fields_dict'] = fields_dict
        _dict['columns'] = columns
        _dict['table'] = name

        return type.__new__(cls, name, bases, _dict)


class Model(object):

    __metaclass__ = ModelMetaclass

    id = IntegerField()
    id.db_type = 'INTEGER PRIMARY KEY AUTOINCREMENT'

    def __init__(self, cursor, **kwargs):
        self.cursor = cursor
        for key, value in kwargs.items():
            self.fields_dict[key].value = value

    @classmethod
    def pair_name_type(cls):
        result = ""
        for key, value in cls.fields_dict.items():
            if isinstance(value, CharField):
                result += "{} text, ".format(key)
            elif isinstance(value, IntegerField):
                result += "{} real, ".format(key)
        return result[:-2]

    @classmethod
    def setup_schema(cls):
        # cursor.execute('''CREATE TABLE {} ({})'''.format(cls.table, Model.pair_name_type()))
        return '''CREATE TABLE {} ({})'''.format(cls.table, User.pair_name_type())

    def save(self):
        connection.commit()

    def __str__(self):
        result = ""
        for field in self.fields_dict.items():
            if field is not None:
                result += str(field)
        return result


class User(Model):
    name = CharField()
    age = IntegerField()


gosho = User(cursor, name='Gosho', age=20)
pesho = User(cursor, name='Pesho', age=10)
print gosho
print pesho
