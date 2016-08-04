import unittest
from mock import Mock
from model import Model, CharField, IntegerField


class User(Model):
    # These fields get declared in the class.
    # When you make an instance, it only saves the value
    first_name = CharField()
    age = IntegerField()
    sex = CharField()


class TestModel(unittest.TestCase):

    def setUp(self):
        self.cursor = Mock(lastrowid=1)
        self.u = User(self.cursor, first_name="pepi", age=10)

    def test_setup(self):
        User.setup_schema(self.cursor)
        self.cursor.execute.assert_called_with(
            'CREATE TABLE IF NOT EXISTS User (first_name text, age real, sex text)')

    def test_insert(self):
        user = User(self.cursor, first_name='pepi', age=10)
        User.setup_schema(self.cursor)
        user.insert()
        self.cursor.execute.assert_called_with(
            '''INSERT INTO User VALUES (?, ?, ?)''',
            ('pepi', '10', 'default_empty'))

    def test_update(self):
        user = User(self.cursor, first_name='pepi', age=10)
        User.setup_schema(self.cursor)
        user.insert()
        user.update()
        self.cursor.execute.assert_called_with(
            '''UPDATE User SET first_name = ?, age = ?, sex = ? WHERE rowid = 1''',
            ('pepi', '10', 'default_empty'))

    def test_save(self):
        user = User(self.cursor, first_name='pepi', age=10)
        User.setup_schema(self.cursor)

        user.save()
        self.cursor.execute.assert_called_with(
            '''INSERT INTO User VALUES (?, ?, ?)''',
            ('pepi', '10', 'default_empty'))

        user.first_name = 'NewName'
        user.save()
        self.cursor.execute.assert_called_with(
            '''UPDATE User SET first_name = ?, age = ?, sex = ? WHERE rowid = 1''',
            ('NewName', '10', 'default_empty'))


if __name__ == '__main__':
    unittest.main()
