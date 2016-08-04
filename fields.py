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