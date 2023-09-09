import unittest

from utils.Locator import Locator


class TestLocator(unittest.TestCase):
    """
    Test for Locator class
    """
    # Test all the checks
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
            "another closer one",
            context.exception.args[0])

    def test_init_Out_of_France(self):
        address = "1 Av Diagonal Barcelona"
        with self.assertRaises(AttributeError) as context:
            Locator(address)

        self.assertEqual(
            "Sorry, your location must be in France to return a "
            "precise result",
            context.exception.args[0])

    # Test the exactitude of the class
    def test_value_1(self):
        address = "47 Rue de la Durantière Nantes"
        locator = Locator(address)
        self.assertEqual(locator.latitude, 47.213287)
        self.assertEqual(locator.longitude, -1.601594)

        # Google records the address at
        # latitude: 47.21328924982242
        # longitude: -1.6015308067153338
        # The difference is around 10 meters.

    def test_value_2(self):
        address = "47 Rue Charles Dumont, Dijon"
        locator = Locator(address)
        self.assertEqual(locator.latitude, 47.3113753)
        self.assertEqual(locator.longitude, 5.0392644)

        # Google records the address at
        # latitude: 47.311447282792784
        # longitude: 5.039288654091115
        # The difference is around 10 meters.

    def test_value_3(self):
        address = "1 Av. Georges Pompidou, Toulouse"
        locator = Locator(address)
        self.assertEqual(locator.latitude, 43.6120665)
        self.assertEqual(locator.longitude, 1.457871)

        # Google records the address at
        # latitude: 43.61213702646373
        # longitude: 1.4577933548025355
        # The difference is around 10 meters.

