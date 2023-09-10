import unittest
from APIManager import APIManager


class TestApiManager(unittest.TestCase):
    def test_e2e(self):
        address = "1 Av Georges Pompidou Toulouse"
        expected_result = {'Orange': {'2G': "false",
                                      '3G': "true",
                                      '4G': "true"},

                           'SFR': {'2G': "true",
                                   '3G': "true",
                                   '4G': "true"},

                           'Bouygue': {'2G': "true",
                                       '3G': "true",
                                       '4G': "true"},

                           'Free': {'2G': "false",
                                    '3G': "true",
                                    '4G': "true"}
                           }
        result = APIManager.get_towers_coverage(address)

        self.assertEqual(result, expected_result)
