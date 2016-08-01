class CharField(object):
    def __get__(self, instance, owner):
        pass

    def __set__(self, instance, value):
        instance.string = value

    def __init__(self, string=""):
        self.string = str(string)


class IntegerField(object):
    def __get__(self, instance, owner):
        pass

    def __set__(self, instance, value):
        try:
            float(value)
            instance.value = value
        except:
            raise AttributeError("IntegerField must be initialized with a number!")

    def __init__(self, value=0):
        try:
            float(value)
            self.value = value
        except:
            raise AttributeError("IntegerField must be initialized with a number!")