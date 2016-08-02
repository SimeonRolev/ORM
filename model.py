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
        self.value = value

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __repr__(self):
        return "Field: name={}, value={}".format(self.name, self.value)


class IntegerField(Field):
    def __repr__(self):
        return "IntegerField: name={}, value={}".format(self.name, self.value)


class CharField(Field):
    def __repr__(self):
        return "CharField: name={}, value={}".format(self.name, self.value)


class ModelMetaClass(type):

    def __new__(cls, name, bases, _dict):

        columns = {key: type(value)
                   for key, value in _dict.items()
                   if isinstance(value, Field)}

        # for k, v in columns.items():
        #     print "NAME: {} | TYPE: {}".format(k, v)

        _dict['columns'] = columns
        _dict['table'] = name

        return type.__new__(cls, name, bases, _dict)


class Model(object):

    __metaclass__ = ModelMetaClass

    def __init__(self, **kwargs):

        self.fields = []
        self.table = self.__class__.__dict__['table']

        # Creating instances of the fields from the class dict into the instance
        for field, field_type in self.__class__.__dict__['columns'].items():
            # self.__dict__[field] = field_type()
            setattr(self, field, field_type())
            self.fields.append(field)
        self.fields.sort()

        # Setting the values of the fields
        for key, value in kwargs.items():
            self.__dict__[key].value = value
            self.__dict__[key].name = key

        # print "Try to create table if not existing: {}".format(self.table)

        self.row = []
        for f in self.fields:
            if f in kwargs:
                self.row.append(kwargs[f])
            else:
                self.row.append('null')

        user_add = "INSERT INTO {} VALUES {}".format(self.table, tuple(self.row))
        self.queries = [user_add]

    def __setattr__(self, key, value):
        # print "SETATTER, KEY: {}".format(key)
        self.__dict__[key] = value

    def __getattr__(self, item):
        return self.__dict__[item]

class User(Model):
    firstname = CharField()
    age = IntegerField()
    sex = CharField()


u = User(firstname='Petyr', age=10, sex="Male")
u2 = User(firstname='Gosho', age=20)
print "USER: " + str(u2.__dict__)
u2.age = 500
print "USER: " + str(u2.__dict__)
# print "USER 2: " + str(u2.__dict__)
# print "U2 AGE: " + str(u2.age)
# print "CLASS USER AGE " + str(User.age)

print u2.age
