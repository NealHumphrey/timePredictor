import unittest
from app.main import ex


class MainTests(unittest.TestCase):

	def test_ex(self):
		result = ex()
		self.assertEqual(2,result)


if __name__ == '__main__':
    unittest.main()