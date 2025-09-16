import unittest


class TestDemo(unittest.TestCase):
    def setUp(self):
        pass


    def test_demo(self):
        pass

    def test_add(self):
        self.assertEqual(1+2,3)

if __name__ == '__main__':
    unittest.main()