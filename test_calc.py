import unittest
from main import calculate_price

class MockCursor:
    def __init__(self, name, count):
        self.name = name
        self.count = count
        self.query_count = 0
    def execute(self, query, params):
        if "SELECT name" in query:
            self.query_count = 1
        else:
            self.query_count = 2
    def fetchone(self):
        if self.query_count == 1:
            return (self.name,)
        return (self.count,)

class TestCalculatePrice(unittest.TestCase):
    def test_has_orders(self):
        cursor = MockCursor("Гречка", 5)
        final, disc = calculate_price(1, 100.0, cursor)
        self.assertEqual(final, 100.0)
        self.assertEqual(disc, 0.0)
        
    def test_no_orders(self):
        cursor = MockCursor("Гречка", 0)
        final, disc = calculate_price(1, 100.0, cursor)
        self.assertEqual(final, 75.0)
        self.assertEqual(disc, 25.0)

if __name__ == '__main__':
    unittest.main()