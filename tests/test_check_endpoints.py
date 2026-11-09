import unittest

from scripts.check_endpoints import validate


class CountsSchemaTests(unittest.TestCase):
    def test_observed_responses(self):
        for payload in ([None, 297210, None], [3591, 0, 11267]):
            with self.subTest(payload=payload):
                self.assertTrue(validate("counts", payload))

    def test_rejects_invalid_counts(self):
        for payload in (
            {}, [], [1, 2], [1, 2, 3, 4], [None, None, None],
            [None, "297210", None], [None, True, None],
            [True, 0, 1], [1, 0, False], [-1, 0, 1],
            [1, -1, 1], [1, 0, -1], [1.5, 0, 1],
        ):
            with self.subTest(payload=payload):
                self.assertFalse(validate("counts", payload))


if __name__ == "__main__":
    unittest.main()
