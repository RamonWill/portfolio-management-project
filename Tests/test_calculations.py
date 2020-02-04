import unittest
import sys
from pathlib import Path

PARENT_PATH = Path(__file__).parent.parent
sys.path.insert(0, str(PARENT_PATH))

from Core.Calculations import Convertprice


class Test_Calculations(unittest.TestCase):
    # ALL tests must start with test_

    def test_Convertprice_64ths(self):
        self.assertEqual(Convertprice("108.015625"), "108-00+")
        self.assertEqual(Convertprice("105.265625"), "105-08+")
        self.assertEqual(Convertprice("99.421875"), "99-13+")
        self.assertEqual(Convertprice("98-26+"), 98.828125)
        self.assertEqual(Convertprice("103-27+"), 103.859375)
        self.assertEqual(Convertprice("103-30+"), 103.953125)

    def test_Convertprice_32nds(self):
        self.assertEqual(Convertprice("108.03125"), "108-01")
        self.assertEqual(Convertprice("105.71875"), "105-23")
        self.assertEqual(Convertprice("99.28125"), "99-09")
        self.assertEqual(Convertprice("98-19"), 98.59375)
        self.assertEqual(Convertprice("103-31"), 103.96875)

    def test_Convertprice_16ths(self):
        self.assertEqual(Convertprice("97.4375"), "97-14")
        self.assertEqual(Convertprice("100.9375"), "100-30")
        self.assertEqual(Convertprice("97-06"), 97.1875)
        self.assertEqual(Convertprice("100-26"), 100.8125)

    def test_Convertprice_8ths(self):
        self.assertEqual(Convertprice("92.5"), "92-16")
        self.assertEqual(Convertprice("92.125"), "92-04")
        self.assertEqual(Convertprice("101-24"), 101.75)
        self.assertEqual(Convertprice("101-20"), 101.625)

    def test_Convertprice_edge_cases(self):
        error_message = "Value Error.\nExamples 108.50 or 108-16"
        self.assertEqual(Convertprice("92.5a"), error_message)
        self.assertEqual(Convertprice("abucd.125"), error_message)
        self.assertEqual(Convertprice("[56.4]"), error_message)
        self.assertEqual(Convertprice("120.23.2"), error_message)
        self.assertEqual(Convertprice("203+03.3"), error_message)
        self.assertEqual(Convertprice("--203-10"), error_message)
        self.assertEqual(Convertprice("-20-3-10"), error_message)


# This allows us to run the test in the editor
if __name__ == "__main__":
    unittest.main()
