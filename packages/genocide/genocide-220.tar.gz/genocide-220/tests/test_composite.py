# This file is placed in the Public Domain.


import unittest


from genocide.objects import Object
from genocide.persist import read, write


class TestComposite(unittest.TestCase):

    def testcomposite(self):
        obj = Object()
        obj.obj = Object()
        obj.obj.a = "test"
        self.assertEqual(obj.obj.a, "test")

    def testcompositeprint(self):
        obj = Object()
        obj.obj = Object()
        obj.obj.a = "test"
        fnm = write(obj)
        ooo = Object()
        read(ooo, fnm)
        self.assertTrue(ooo.obj)
