import unittest
import tagcounter

class TestStringMethods(unittest.TestCase):

    def test_process_tag_calculating(self):
        self.assertEqual(tagcounter.process_tag_calculating(['title', 'title', 'meta', 'meta', 'meta']), {'title':2, 'meta':3})


if __name__ == '__main__':
    unittest.main()
