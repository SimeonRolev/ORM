class Field(object):

    order_num = 0

    def __init__(self, name=None, primary_key=False,
                 max_length=None, null=True,
                 default=None, content_type='text'):

        self.order_num = Field.order_num + 1
        Field.order_num += 1

        if content_type not in ('text', 'real'):
            raise AttributeError("The SQL Field type can only be text or real")
        self.content_type = content_type
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

    def __eq__(self, other):
        return '{}{}?'.format(self.name, '='), other

    def __ne__(self, other):
        return '{}{}?'.format(self.name, '!='), other

    def __gt__(self, other):
        return '{}{}?'.format(self.name, '>'), other

    def __lt__(self, other):
        return '{}{}?'.format(self.name, '<'), other

    def __ge__(self, other):
        return '{}{}?'.format(self.name, '>='), other

    def __le__(self, other):
        return '{}{}?'.format(self.name, '<='), other

    def startswith(self, string):
        return "{} LIKE ?".format(self.name), string+'%'

    def endswith(self, string):
        return "{} LIKE ?".format(self.name), '%'+string

    def contains(self, string):
        return "{} LIKE ?".format(self.name), '%'+string+'%'

    def in_(self, *values):
        return "{} IN ({})".format(self.name, ','.join('?'*len(values))), values


class IntegerField(Field):

    def __init__(self):
        return super(IntegerField, self).__init__(default=0, content_type='real')

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
