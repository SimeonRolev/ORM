import sqlite3
from query import Query

conn = sqlite3.connect('people.db')
# cursor = conn.cursor()


class Field(object):

    order_num = 0

    def __init__(self, name=None, primary_key=False,
                 max_length=None, null=True,
                 default=None, sql_type='text'):

        self.order_num = Field.order_num + 1
        Field.order_num += 1

        if sql_type not in ('text', 'real'):
            raise AttributeError("The SQL Field type can only be text or real")
        self.sql_type = sql_type
        self.name = name  # The metaclass sets the self.name to name of the Field in the definition (ex. firstname)
        self.primary_key = primary_key
        self.max_length = max_length
        self.null = null
        self.default = default

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        return getattr(obj, '_' + self.name)

    def __set__(self, obj, value):
        """ The __set__ method creates an attribute in the OBJ INSTANCE
        called _name_of_the_Field_in_the_definition """

        return setattr(obj, '_' + self.name, value)

    def __repr__(self):
        return "Field: name={}".format(self.name)


class IntegerField(Field):

    def __init__(self):
        return super(IntegerField, self).__init__(default=0, sql_type='real')

    def __repr__(self):
        return "IntegerField: name={}, order: {}".format(self.name, self.order_num)

    def __set__(self, obj, value):
        try:
            float(value)
        except:
            if value != 'null':
                raise AttributeError("An IntegerField can only be initialized with a number!")
        return setattr(obj, '_' + self.name, value)


class CharField(Field):

    def __init__(self):
        return super(CharField, self).__init__(default='default_empty')

    def __repr__(self):
        return "CharField: name={}, order: {}".format(self.name, self.order_num)

    def __set__(self, obj, value):
        if not isinstance(value, str):
            raise AttributeError("A CharField can only be initialized with a string!")
        return setattr(obj, '_' + self.name, value)


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
        _dict['cursor'] = None

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
    def row_columns_ordered(cls):
        result = list()
        for key in sorted(cls.columns, key=lambda x: cls.columns[x].order_num):
            result.append(key)
        return result

    @classmethod
    def row_schema(cls):
        result = ''
        for key in sorted(cls.columns, key=lambda x: cls.columns[x].order_num):
            result += "{} {}, ".format(key, cls.columns[key].sql_type)
        return result[:-2]

    def row_values(self):
        result = list()
        row = [key for key in sorted(self.columns, key=lambda x: self.columns[x].order_num)]
        for value in row:
            result.append(str(getattr(self, value)))
        return tuple(result)

    @classmethod
    def setup_schema(cls, cursor):
        cursor.execute('''CREATE TABLE IF NOT EXISTS {} ({})'''.format(cls.table, cls.row_schema()))

    @classmethod
    def select(cls, *args):
        fields = list()

        if not args:
            for col in cls.columns:
                fields.append(col)
            return Query(cls, fields)

        else:
            for col in args:
                if col not in cls.columns:
                    raise AttributeError("{} table has no column {}".format(cls.table, col))
                fields.append(col)

        return Query(cls, fields)

        # result = '''SELECT {} from {}'''.format(result, cls.table)
        # return result

    def insert(self):
        query = """INSERT INTO {} VALUES {}""".format(self.table, self.qmarks())
        self.cursor.execute(query, self.row_values())
        conn.commit()
        self._id = self.cursor.lastrowid

    def set_of_update(self):
        # task_owner = ? ,task_remaining_hours = ?,task_impediments = ?,task_notes = ? WHERE task_id= ?
        result = ''
        for col in self.row_columns_ordered():
            result += '{} = ?, '.format(col)
        return result[:-2]

    def update(self):
        temp = [getattr(self, key) for key in self.row_columns_ordered()]
        query = """UPDATE {} SET {} WHERE {}""".format(self.table, self.set_of_update(), 'rowid = ' + str(self._id))
        self.cursor.execute(query, self.row_values())
        conn.commit()

    def save(self):
        if hasattr(self, '_id'):
            self.update()
        else:
            self.insert()


class User(Model):
    # These fields get declared in the class.
    # When you make an instance, it only saves the value
    first_name = CharField()
    age = IntegerField()
    sex = CharField()


c = conn.cursor()
u = User(c, first_name='Pesho', age=10)
u.save()
u.first_name = 'Kondio'
u.save()
