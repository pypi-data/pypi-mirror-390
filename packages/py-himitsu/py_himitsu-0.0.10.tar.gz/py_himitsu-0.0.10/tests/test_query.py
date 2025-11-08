import unittest
from himitsu import query

class TestQuery(unittest.TestCase):
    def test_init(self):
        q = query.Query("a=b c?=d e!=f global?!=secret opt")
        self.assertEqual("a=b c?=d e!=f global?!=secret opt", str(q))

    def test_dict_access(self):
        q = query.Query()

        q["pub"] = "bar"
        q["private!"] = "baz"
        q["opt?"] = "foo"

        self.assertTrue("private" in q)
        self.assertTrue("pub" in q)
        self.assertTrue("opt" in q)

        self.assertEqual("bar", q["pub"])
        self.assertEqual("baz", q["private"])
        self.assertEqual("foo", q["opt"])

        self.assertEqual("pub=bar private!=baz opt?=foo", str(q))

    def test_invalid_keys(self):
        err = False
        try:
            q = query.Query()
            q['"in\tvalid"'] = 'val'
        except ValueError:
            err = True

        self.assertEqual(True, err)


if __name__ == '__main__':
    unittest.main()

