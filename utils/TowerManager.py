import os
import pandas as pd

from math import sqrt
from databases.datascripts import csv_name, operator_code
from utils.Locator import Locator


class TowerManager:
    def __init__(self, location, database=None, networks=None):
        # Check location and store it
        self.location = location
        self.check_location()

        # Check database and store it
        self.database = database
        self.check_database()

        # Check and store the networks
        self.networks = networks
        self.check_networks()

        # Attributes
        self.tower_indexes = {}
        self.towers_coverage = {}

    def check_location(self):
        """
        Check for the location
        """
        # Check the location is an object from the Locator class
        if not isinstance(self.location, Locator):
            raise AttributeError("The location provided "
                                 "is not a Locator!")

    def check_database(self):
        """
        Checks for the database
        """
        # Check database exists, if not, provide the local one
        if self.database is None:
            # CAUTION! this path is assumed to be launched only from the
            # JG_API_papernest file!
            db_dir = os.path.join(os.getcwd(), 'databases')
            db_path = os.path.join(db_dir, csv_name)
            self.database = pd.read_csv(db_path, sep=";")

        # Ensure database has the minimal expected columns
        expected_columns = {'Operateur',
                            'Latitude', 'Longitude',
                            '2G', '3G', '4G'}
        if not expected_columns.issubset(self.database.columns):
            raise AttributeError("Database does not contain the"
                                 " minimum expected columns!")

    def check_networks(self):
        """
        Check for the networks
        """
        # Check networks exists, in case not, provide a usual one
        if self.networks is None:
            self.networks = ['2G', '3G', '4G']

        # Check networks is a list for further use
        if not isinstance(self.networks, list):
            raise AttributeError("networks provided is expected to be a"
                                 " list!")

        # Check at networks are database clumns
        if not set(self.networks).issubset(self.database.columns):
            raise AttributeError("Provided networks are not in the "
                                 "database!")

    def location_coverage(self):
        # Reduce the database to a more handleable amount
        self.database = self.reduced_database()

        # Find the closest towers
        self.locate_closest_towers()

        # Find coverage of the closest towers
        self.find_towers_coverage()

    def reduced_database(self, area=1):
        """
        Method to reduce the database around the specific location
        provided

        Parameters:
        -----------
        area: (int)
            Distance to square around the location to look for towers.
        return:
        -------
        pandas.DataFrame: a reduction of the given database
        """
        ret = self.database.loc[(self.database['Latitude'] > (self.location.latitude - area))
                                & (self.database['Latitude'] < (self.location.latitude + area))
                                & (self.database['Longitude'] > (self.location.longitude - area))
                                & (self.database['Longitude'] < (self.location.longitude + area))]
        if len(set(ret['Operateur'])) < 4:
            return self.reduced_database(area=area + 1)
        else:
            return ret

    def locate_closest_towers(self):
        """
        Get the database index of the closest towers for the location
        """

        # Set all saved distances to 100 in order to be able to find a
        # closer one by comparison.
        minimums = dict()
        for op in set(self.database['Operateur']):
            minimums[op] = (100.0, 0)

        # Compare distance between location and all towers
        # on the database
        for index, row in self.database.iterrows():
            # Get the distance between the two points
            dist_lat = self.location.latitude - row['Latitude']
            dist_ln = self.location.longitude - row['Longitude']
            dist = sqrt((dist_lat ** 2) + (dist_ln ** 2))

            # Check if distance is shorter than the previous saved
            if dist < minimums[int(row['Operateur'])][0]:
                minimums[int(row['Operateur'])] = (dist, index)

        # Fill the dictionary for each operator with the database index
        # of the closest tower
        for operator, values in minimums.items():
            self.tower_indexes[operator] = values[1]

    def find_towers_coverage(self):
        """
        Function that provides the coverage of a set of given towers
        """
        # Dictionary to that convert 1 in true and 0 in false to avoid
        # unnecessary ifs for expected output
        t_f = {1: 'true', 0: 'false'}

        # Loop to find the closest tower per operator.
        for operator, index in self.tower_indexes.items():
            # Create an empty dictionary for every operator
            self.towers_coverage[operator_code[operator]] = dict()

            # Fill those dictionaries with the networks and true or
            # false as value depending on their coverage on the database
            for net in self.networks:
                self.towers_coverage[operator_code[operator]][net] = t_f[self.database.at[index, net]]
