import unittest

from utils.Locator import Locator


class TestLocator(unittest.TestCase):
    def test_init_None(self):
        address = None
        with self.assertRaises(AttributeError) as context:
            Locator(address)

        self.assertEqual(
            "Sorry, no address has been recognized, check the url!",
            context.exception.args[0])

    def test_init_addres_not_find(self):
        address = "ThisIsNotAnAddress"
        with self.assertRaises(AttributeError) as context:
            Locator(address)

        self.assertEqual(
            "Sorry, we weren't able to find your address, please try "
            "another close one",
            context.exception.args[0])

    def test_init_Out_of_France(self):
        address = "1 Av Diagonal Barcelona"
        with self.assertRaises(AttributeError) as context:
            Locator(address)

        self.assertEqual(
            "Sorry, your location must be in France to return a "
            "precise result",
            context.exception.args[0])
