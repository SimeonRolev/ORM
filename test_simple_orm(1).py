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
        cursor = Mock()
        self.u = User(cursor, first_name="pepi", age=10)

    def test_row_schema(self):
        self.assertEqual(self.u.row_schema(), 'first_name text, age real, sex text')

    def test_row_values(self):
        self.assertEqual(self.u.row_values(), ('pepi', '10', 'default_empty'))

    def test_setup(self):
        cursor = Mock()
        User.setup_schema(cursor)
        cursor.execute.assert_called_with(
            'CREATE TABLE IF NOT EXISTS User (first_name text, age real, sex text)')

    # def test_insert(self):
    #     cursor = Mock(lastrowid=1)
    #     user = User(cursor)
    #     User.setup_schema(cursor)
    #     user.insert(cursor)
    #     cursor.execute.assert_called_with('''INSERT INTO User VALUES (?, ?, ?)''', ('pepi', '10', 'default_empty'))

    # def test_save(self):
    #     cursor = Mock(lastrowid=1)
    #     # self.u.save()
    #     cursor.execute.assert_called_with('''INSERT INTO User VALUES ('pepi',10,'default_empty')''')

    # def test_update(self):
    #     cursor = Mock(lastrowid=1)
    #     self.u.insert(cursor)
    #     self.u.update(cursor)
    #     cursor.execute.assert_called_with(
    #         'UPDATE User SET first_name = ?, age = ?, sex = ? WHERE id = 1', ('pepi', '10', 'default_empty'))

    def test_validation(self):
        q = Question(None)
        q.count = 1
        with self.assertRaises(model.ValidationError):
            q.count = 'z'

    def test_char_filed(self):
        class Answer(model.Model):

            text = model.CharField(10)

        a = Answer(None)
        a.text = 'a'
        with self.assertRaises(model.ValidationError):
            a.text = 'aaaaaaaaaaaaaaaaaaaaaaaaaaa'


if __name__ == '__main__':
    unittest.main()
