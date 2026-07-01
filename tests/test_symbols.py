import unittest

from eastmoney.symbols import code_to_secid


class TestCodeToSecid(unittest.TestCase):
    def test_shanghai(self) -> None:
        self.assertEqual(code_to_secid("600519"), "1.600519")
        self.assertEqual(code_to_secid("sh600519"), "1.600519")

    def test_shenzhen(self) -> None:
        self.assertEqual(code_to_secid("000001"), "0.000001")
        self.assertEqual(code_to_secid("300750"), "0.300750")

    def test_beijing(self) -> None:
        self.assertEqual(code_to_secid("830799"), "0.830799")


if __name__ == "__main__":
    unittest.main()
