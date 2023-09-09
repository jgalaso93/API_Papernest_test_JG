import os
import unittest
import pandas as pd

from unittest.mock import Mock

from databases.datascripts import csv_name
from utils.TowerManager import TowerManager
from utils.Locator import Locator


class TestTowerManager(unittest.TestCase):
    """
    Test for the TowerManager class.
    """
    def setUp(self):
        super().setUp()
        self.location = Locator("47 Rue Charles Dumont, Dijon")

        db_dir = os.path.join(os.getcwd(), '../databases')
        db_path = os.path.join(db_dir, csv_name)
        self.database = pd.read_csv(db_path, sep=";")

    # Test for all the checks that the class runs
    def test_init_location_wrong(self):
        location = "ThisIsNotALocator"
        with self.assertRaises(AttributeError) as context:
            TowerManager(location)

        self.assertEqual(
            "The location provided is not a Locator!",
            context.exception.args[0])

    def test_init_false_database(self):
        database = Mock()
        database.columns = ['a', 'b', 'c']

        with self.assertRaises(AttributeError) as context:
            TowerManager(self.location, database=database)

        self.assertEqual(
            "Database does not contain the minimum expected columns!",
            context.exception.args[0])

    def test_init_false_networks(self):
        with self.assertRaises(AttributeError) as context:
            TowerManager(self.location, database=self.database,
                         networks="NotAList")

        self.assertEqual(
            "networks provided is expected to be a list!",
            context.exception.args[0])

    def test_init_not_found_networks(self):
        with self.assertRaises(AttributeError) as context:
            TowerManager(self.location, database=self.database,
                         networks=['a', 'b', 'c'])

        self.assertEqual(
            "Provided networks are not in the database!",
            context.exception.args[0])

    # Test for the methods
    def test_reduced_database(self):
        # Generate a tower manager
        tower_mgr = TowerManager(self.location, database=self.database)

        # Get the reduced database and the expected reduced database
        reduced_db = tower_mgr.reduced_database(area=0.005)
        expected_data = {
                'Operateur': [20815, 20801, 20820, 20815, 20801, 20810],
                'Latitude': [47.3161189031995, 47.3158612131847,
                             47.3156110229021, 47.3123988803977,
                             47.3123169546005, 47.3123619512882],
                'Longitude': [5.03822342519584, 5.03956433132312,
                              5.03996532847678, 5.04339192770876,
                              5.04344177451172, 5.0434434870697],
                '2G': [0, 1, 1, 0, 1, 1],
                '3G': [1, 1, 1, 1, 1, 1],
                '4G': [1, 1, 1, 1, 1, 1]}

        expected_db = pd.DataFrame.from_dict(expected_data)

        # Check that both DataBases are the same size
        self.assertEqual(len(reduced_db), len(expected_db))

        # Check that the value of both of them is equal
        for i, index in enumerate(reduced_db.index):
            for c in reduced_db.columns:
                self.assertEqual(expected_db.loc[i][c],
                                 reduced_db.loc[index][c])

    def test_locate_closer_towers(self):
        tower_mgr = TowerManager(self.location, database=self.database)
        # Not needed but for speed purposes
        tower_mgr.database = tower_mgr.reduced_database()

        # Get the closest tower and the expected closest towers
        tower_mgr.locate_closest_towers()
        expected_towers_indexes = {20801: 57807,
                                   20810: 57808,
                                   20820: 57771,
                                   20815: 57805}

        # Check the expected and the result are the same
        self.assertEqual(expected_towers_indexes,
                         tower_mgr.tower_indexes)

    def test_tower_coverage(self):
        tower_mgr = TowerManager(self.location, database=self.database)
        # Not needed but for speed purposes
        tower_mgr.database = tower_mgr.reduced_database()

        # Necessary previous step
        tower_mgr.locate_closest_towers()

        # Get the towers coverage and the expected tower coverage
        tower_mgr.find_towers_coverage()
        expected_tower_coverage = {
            'Orange': {'2G': 'true', '3G': 'true', '4G': 'true'},
            'SFR': {'2G': 'true', '3G': 'true', '4G': 'true'},
            'Bouygue': {'2G': 'true', '3G': 'true', '4G': 'true'},
            'Free': {'2G': 'false', '3G': 'true', '4G': 'true'}
        }

        # Check the towers coverage and the expected towers coverage are
        # the same
        self.assertEqual(expected_tower_coverage,
                         tower_mgr.towers_coverage)
