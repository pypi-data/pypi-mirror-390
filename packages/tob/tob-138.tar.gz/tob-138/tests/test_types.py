# This file is placed in the Public Domain.


import unittest


from tob.marshal import dumps, loads
from tob.objects import Object, update


class TestTypes(unittest.TestCase):

    def test_dict(self):
        obj = loads(dumps({"a": "b"}))
        self.assertEqual(obj, {"a": "b"})

    def test_integer(self):
        obj = loads(dumps(1))
        self.assertEqual(obj, 1)

    def test_float(self):
        obj = loads(dumps(1.0))
        self.assertEqual(obj, 1.0)

    def test_string(self):
        obj = loads(dumps("test"))
        self.assertEqual(obj, "test")

    def test_true(self):
        obj = loads(dumps(True))
        self.assertEqual(obj, True)

    def test_false(self):
        obj = loads(dumps(False))
        self.assertEqual(obj, False)

    def test_object(self):
        ooo = Object()
        ooo.a = "b"
        obj = Object()
        update(obj, loads(dumps(ooo)))
        self.assertEqual(obj.a, "b")
