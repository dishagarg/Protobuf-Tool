import unittest
import pbtool


class TestTutorial(unittest.TestCase):
    def setUp(self):
        self.mod = pbtool.compile('./tests/tutorial.proto')

    def test(self):
        instance = self.mod.Person()
        pbtool.fill(instance, {
            'name': 'Hullo',
            'email': 'foo@bar.com',
            'id': 999,
            'phone': []
        })
        instance.SerializeToString()

    def test_missing_required(self):
        instance = self.mod.Person()
        pbtool.fill(instance, {
            'name': 'Hullo',
            'email': 'foo@bar.com',
            'phone': []
        })
        self.assertRaises(Exception, instance.SerializeToString)

    def test_missing_optional(self):
        instance = self.mod.Person()
        pbtool.fill(instance, {
            'name': 'Hullo',
            'id': 999,
            'phone': []
        })
        instance.SerializeToString()

    def test_repeated(self):
        instance = self.mod.Person()
        pbtool.fill(instance, {
            'name': 'Hullo',
            'id': 999,
            'phone': [
                {'number': '1-800-stuff'},
                {'number': '1-800-moar-stuff'}
            ]
        })
        instance.SerializeToString()

    def test_enum(self):
        instance = self.mod.Person()
        pbtool.fill(instance, {
            'name': 'Hullo',
            'id': 999,
            'phone': [
                {'number': '1-800-stuff', 'type': 'WORK'},
                {'number': '1-800-stuff', 'type': 'MOBILE'}
            ]
        })
        instance.SerializeToString()

    def test_enums_must_be_strings(self):
        instance = self.mod.Person()
        self.assertRaises(Exception, pbtool.fill, instance, {
            'name': 'Hullo',
            'id': 999,
            'phone': [
                {'number': '1-800-stuff', 'type': 1}
            ]
        })
