# User.select(User.name, User.age).where(or_(User.name == 'Ivan', User.age > 10)).get(10)


def and_(*expressions):
    fields = [expr[0] for expr in expressions]
    result = ' AND '.join(fields)
    return '('+result+')', [expr[1] for expr in expressions]


def or_(*expressions):
    fields = [expr[0] for expr in expressions]
    result = ' OR '.join(fields)
    return '('+result+')', [expr[1] for expr in expressions]


class Query(object):

    def __init__(self, table_class=None, fields=None):
        if table_class.database.db_type == 'postgres':
            self.table = table_class.schema_and_table
        else:
            self.table = table_class.table
        self.cursor = table_class.cursor
        self.placeholder = table_class.placeholder

        if not fields:
            self.selected_fields = 'SELECT * FROM {} '.format(self.table)
        else:
            temp = ', '.join([f.name for f in fields])
            self.selected_fields = 'SELECT {} FROM {} '.format(temp, self.table)
        self.lim = 1
        self.query = self.selected_fields
        self.values = []

    def __repr__(self):
        return "Query object: Table: {} | Fields: {}".format(self.table, self.query)

    def where(self, expr):
        if 'WHERE' not in self.query:
            self.query += 'WHERE {} '.format(expr[0])
        else:
            self.query += 'AND {} '.format(expr[0])
        if hasattr(expr[1], '__iter__'):
            self.values.extend(expr[1])
        else:
            self.values.append(expr[1])

        self.query = self.query.replace('?', self.placeholder)
        return self

    # how many rows to fetch
    def limit(self, count):
        self.lim = count
        return self

    def get(self):
        self.cursor.execute(self.query, self.values)
        return self.cursor.fetchmany(self.lim)

    def first(self):
        self.cursor.execute(self.query, self.values)
        return self.cursor.fetchone()

    def one(self):
        self.cursor.execute(self.query, self.values)
        temp = self.cursor.fetchmany(2)
        if temp is None or len(temp) > 1:
            raise Exception("No such unique row in the table!")
        return temp[0]
