import unittest
from mock import Mock
from model import Model, CharField, IntegerField
from database import *
from query import *


class Gibson(Model):
    # These fields get declared in the class.
    # When you make an instance, it only saves the value
    name = CharField()
    year = IntegerField()
    pick_ups = CharField()


class TestPostgre(unittest.TestCase):

    def setUp(self):
        self.postgre_db = PostgreDatabase('gibsons')
        self.postgre_db.create_tables(Gibson)
        self.cursor = Mock()
        self.postgre_db.cursor = self.cursor
        self.g = Gibson(name="Les Paul", year=1950, pick_ups='P90')

    def test_setup(self):
        self.postgre_db.create_tables(Gibson)
        self.cursor.execute.assert_called_with(
            'CREATE TABLE IF NOT EXISTS gibsons.Gibson ('
            'rowid SERIAL, PRIMARY KEY (rowid), '
            'name varchar(50), year int, pick_ups varchar(50))')

    def test_placeholders(self):
        self.assertEqual(self.postgre_db.placeholders(Gibson), "(%s, %s, %s)")

    def test_row_values(self):
        self.assertEqual(row_values(self.g), ("Les Paul", '1950', 'P90'))

    def test_insert(self):
        self.postgre_db.insert('Gibson', self.g)
        self.cursor.execute.assert_called_with(
            'INSERT INTO gibsons.Gibson (name, year, pick_ups) VALUES (%s, %s, %s) RETURNING rowid', ("Les Paul", '1950', 'P90'))

    def test_select(self):
        self.postgre_db.insert('Gibson', self.g)
        q = Gibson.select()
        self.assertEqual(q.query, "SELECT * FROM gibsons.Gibson ")

    # def test_update(self):
    #     self.postgre_db.insert('Gibson', self.g)
    #     self.g.save()
    #     self.g.name = 'Updated Gibson!'
    #     self.g.save()
    #     self.postgre_db.update('Gibson', self.g)
    #     self.cursor.execute.assert_called_with(
    #         "UPDATE gibsons.Gibson SET name = %s, year = %s, pick_ups = %s WHERE rowid = 0", ('Updated Gibson!', '1950', 'P90'))

    def test_where(self):
        self.postgre_db.create_tables(Gibson)
        q = self.g.select().where(Gibson.year > 5)
        self.assertEqual(q.query, "SELECT * FROM gibsons.Gibson WHERE year>%s ")

    def test_contains(self):
        self.postgre_db.create_tables(Gibson)
        print self.g.table
        q = self.g.select().where(Gibson.year.contains("Last"))
        self.assertEqual(q.query, 'SELECT * FROM gibsons.Gibson WHERE year LIKE %s ')
        q.limit(10).get()
        self.cursor.execute.assert_called_with(
            'SELECT * FROM gibsons.Gibson WHERE year LIKE %s ', ['%Last%'])

    def test_starts_with(self):
        self.postgre_db.create_tables(Gibson)
        q = self.g.select().where(Gibson.year.startswith("Last"))
        print q.query
        self.assertEqual(q.query, 'SELECT * FROM gibsons.Gibson WHERE year LIKE %s ')
        q.limit(10).get()
        self.cursor.execute.assert_called_with(
            'SELECT * FROM gibsons.Gibson WHERE year LIKE %s ', ['Last%'])

    def test_ends_with(self):
        self.postgre_db.create_tables(Gibson)
        q = self.g.select().where(Gibson.year.endswith("Last"))
        self.assertEqual(q.query, 'SELECT * FROM gibsons.Gibson WHERE year LIKE %s ')
        q.limit(10).get()
        self.cursor.execute.assert_called_with(
            'SELECT * FROM gibsons.Gibson WHERE year LIKE %s ', ['%Last'])

    def test_in(self):
        self.postgre_db.create_tables(Gibson)
        q = self.g.select().where(Gibson.year > 5).where(Gibson.year.in_('120', '50'))
        q.get()
        self.cursor.execute.assert_called_with(
            'SELECT * FROM gibsons.Gibson WHERE year>%s AND year IN (%s,%s) ', [5, '120', '50'])

        q = self.g.select().where(Gibson.year.in_('120', '50'))
        q.get()
        self.cursor.execute.assert_called_with(
            'SELECT * FROM gibsons.Gibson WHERE year IN (%s,%s) ', ['120', '50'])

    def test_or(self):
        self.postgre_db.create_tables(Gibson)
        q = self.g.select().where(and_(Gibson.year > 5, Gibson.name == "Gosho"))
        q.get()
        self.cursor.execute.assert_called_with(
            'SELECT * FROM gibsons.Gibson WHERE (year>%s AND name=%s) ', [5, 'Gosho'])


if __name__ == '__main__':
    unittest.main()
