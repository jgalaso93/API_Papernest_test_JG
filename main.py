import os
import pandas as pd

from math import sqrt
from fastapi import FastAPI
from geopy.geocoders import Nominatim
from databases.datascripts import csv_name

app = FastAPI()

# The nature of the database and for optimization purposes, the read
# dataframe is located as a global parameter to avoid multiple loads
# of the same file.
database_dir = os.path.join(os.getcwd(), 'databases')
df = pd.read_csv(os.path.join(database_dir, csv_name), sep=";")


@app.get("/JG-papernest-test")
def get_towers_coverage(address=None):
    """
    Main function for the API. Gets the call from the URL and process
    the data from it

    Parameters:
    -----------
    Address: (str)
        An actual address that can be located

    Return:
    -------
    In case there's no address: (str) Error Message
    In case address can't be located: (str) Error Message
    In case address can be located: (dict) Operators and their coverage
    """
    # Check for the parameters
    parameter_error = check_parameters(address)
    if parameter_error:
        return parameter_error

    # Get the location from that address
    location = get_location(address)

    # Check for the location
    location_error = check_location(location)
    if location_error:
        return location_error

    # Get the closest towers per Operator to the location
    tower_indexes = locate_closer_towers(location)

    # The result needs to be structured in the expected output
    return provide_towers_coverage(tower_indexes)


def check_parameters(address):
    """
    Function to check previous configuration.
    For instance has a low value, but in case more checks need to be
    performed, add them here.

    Parameters:
    -----------
    address: (str)
        The address to process

    Return:
    -------
    In case there all checks are correct: None
    In case there is a failed check: (str) Error message
    """
    # Check 1: address is not None
    if address is None:
        return "Sorry, no address has been recognized, check the url!"

    return None


def check_location(location):
    """
    Function to check location is as expected.

    Parameters:
    -----------
    location: (geopy.geocoders.geolocator)
        The location referenced to be processed

    Return:
    -------
    In case there all checks are correct: None
    In case there is a failed check: (str) Error message
    """
    # Check 1: location is not None
    if location is None:
        return ("Sorry, we weren't able to find your address,"
                " please try another close one")

    # Check 2: location is in France
    if location.latitude < 41.59101 or location.latitude > 51.03457 \
            or location.longitude < -4.65 or location.longitude > 9.45:
        return ("Sorry, your location must be in France to return a "
                "precise result")
    return None


def get_location(address):
    """
    Function that given a street name address returns a geolocation

    Parameters:
    -----------
    address: (str)
        The address to process

    Return:
    -------
    (geopy.geocoders.geolocator) The location to be processed
    """
    geolocator = Nominatim(user_agent='JG-papernest')
    return geolocator.geocode(str(address))


def locate_closer_towers(location):
    """
    Given a location, and being a specific database loaded, returns the
    closest tower per operator.

    Parameters:
    -----------
    location: (geopy.geocoders.geolocator)
        The location to be processed

    Return:
    -------
    (dict) The closest tower (value) per Operator code (key)
    """
    lat = location.latitude
    long = location.longitude

    # Since the process will look the minimal distance between two
    # point, the values start for 100 on all the operator cases, so the
    # true minimal will be smaller. The second value will be the index
    # where this tower is located on the database.
    ops = set(df['Operateur'])
    mins = dict()
    for op in ops:
        mins[op] = (100.0, 0)

    # Per tower, we check if it is closer than the previous registered,
    # and in case it is, save it as the closer and its index.
    for index, row in df.iterrows():
        mn = mins[int(row['Operateur'])]
        d_lat = lat - row['Latitude']
        d_ln = long - row['Longitude']
        dist = sqrt((d_lat ** 2) + (d_ln ** 2))
        if dist < mn[0]:
            mins[int(row['Operateur'])] = (dist, index)

    # Once the closest towers are located, create a dictionary only
    # containing the operators and the index in the database of the
    # closest tower.
    tower_indexes = dict()
    for operator, values in mins.items():
        tower_indexes[operator] = values[1]

    return tower_indexes


def provide_towers_coverage(tower_indexes):
    """
    Function that provides the coverage of a set of given towers

    Parameters:
    tower_indexes: (dict)
        The tower from which the coverage will be returned. The key is
        requested to be the operator code of the given tower. The value
        has to be the index in the database of the tower.

    Return:
    -------
        (dict of dict) Dictionary which key is the operator name and the
        value a second dictionary containing the three possible networks
    """
    # These values may be not sufficient in case the amount of operators
    # increase more than expected.
    operator_code = {20801: 'Orange',
                     20810: 'SFR',
                     20815: 'Free',
                     20820: 'Bouygue'}

    # Not necessary but convenient for easier reading later
    t_f = {1: 'true', 0: 'false'}
    towers = {}

    # Added the networks as list for flexibility in case of need
    networks = ['2G', '3G', '4G']

    # Loop to create the final output
    for operator, index in tower_indexes.items():
        # Per operator creates a second dictionary
        towers[operator_code[operator]] = dict()

        # Fill the second dictionary with the networks coverages
        # specified in the database under the column named as the
        # network. The values are transformed from 1 and 0 to true and
        # false
        for net in networks:
            towers[operator_code[operator]][net] = t_f[df.at[index, net]]

    return towers
