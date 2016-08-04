class Query(object):

    def __init__(self, table_class=None, fields=None):
        self.table = table_class.table
        self.cursor = table_class.cursor
        if not fields:
            self.selected_fields = 'SELECT * FROM {} '.format(self.table)
        else:
            temp = ', '.join([f.name for f in fields])
            self.selected_fields = 'SELECT {} FROM {} '.format(temp, self.table)
        self.lim = 1

    def __repr__(self):
        return "Query object: Table: {} | Fields: {}".format(self.table, self.selected_fields)

    def where(self):
        pass

    # how many rows to fetch
    def limit(self, count):
        self.lim = count
        return self

    def get(self):
        self.cursor.execute(self.selected_fields)
        return self.cursor.fetchmany(self.lim)
