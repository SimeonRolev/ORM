import unittest
from mock import Mock
from model import Model, CharField, IntegerField
from database import MySQLDatabase
from database import *
from query import *


class School(Model):
    # These fields get declared in the class.
    # When you make an instance, it only saves the value
    name = CharField()
    age = IntegerField()
    students_count = IntegerField()


class TestMySql(unittest.TestCase):

    def setUp(self):
        self.ms = SqliteDatabase('MySqlSchools')
        self.ms.create_tables(School)
        self.cursor = Mock()
        self.ms.cursor = self.cursor
        self.s = School(name="Stefan Karadja", age=100, students_count=150)

    def test_setup(self):
        self.ms.create_tables(School)
        self.cursor.execute.assert_called_with(
            'CREATE TABLE IF NOT EXISTS School ('
            'name text, age real, students_count real)')

    def test_placeholders(self):
        self.assertEqual(self.ms.placeholders(School), "(?, ?, ?)")

    def test_row_values(self):
        self.assertEqual(row_values(self.s), ("Stefan Karadja", '100', '150'))

    def test_insert(self):
        self.ms.insert('School', self.s)
        self.cursor.execute.assert_called_with(
            'INSERT INTO School VALUES (?, ?, ?)', ('Stefan Karadja', '100', '150'))

    def test_where(self):
        self.ms.create_tables(School)
        q = self.s.select().where(School.age > 5)
        self.assertEqual(q.query, "SELECT * FROM School WHERE age>? ")

    def test_contains(self):
        self.ms.create_tables(School)
        q = self.s.select().where(School.age.contains("Last"))
        self.assertEqual(q.query, 'SELECT * FROM School WHERE age LIKE ? ')
        q.limit(10).get()
        self.cursor.execute.assert_called_with(
            'SELECT * FROM School WHERE age LIKE ? ', ['%Last%'])

    def test_starts_with(self):
        self.ms.create_tables(School)
        q = self.s.select().where(School.age.startswith("Last"))
        self.assertEqual(q.query, 'SELECT * FROM School WHERE age LIKE ? ')
        q.limit(10).get()
        self.cursor.execute.assert_called_with(
            'SELECT * FROM School WHERE age LIKE ? ', ['Last%'])

    def test_ends_with(self):
        self.ms.create_tables(School)
        q = self.s.select().where(School.age.endswith("Last"))
        self.assertEqual(q.query, 'SELECT * FROM School WHERE age LIKE ? ')
        q.limit(10).get()
        self.cursor.execute.assert_called_with(
            'SELECT * FROM School WHERE age LIKE ? ', ['%Last'])

    def test_in(self):
        self.ms.create_tables(School)
        q = self.s.select().where(School.age > 5).where(School.age.in_('120', '50'))
        q.get()
        self.cursor.execute.assert_called_with(
            'SELECT * FROM School WHERE age>? AND age IN (?,?) ', [5, '120', '50'])

        q = self.s.select().where(School.age.in_('120', '50'))
        q.get()
        self.cursor.execute.assert_called_with(
            'SELECT * FROM School WHERE age IN (?,?) ', ['120', '50'])

    def test_or(self):
        self.ms.create_tables(School)
        q = self.s.select().where(and_(School.age > 5, School.name == "Gosho"))
        q.get()
        self.cursor.execute.assert_called_with(
            'SELECT * FROM School WHERE (age>? AND name=?) ', [5, 'Gosho'])


if __name__ == '__main__':
    unittest.main()
