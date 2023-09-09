import pandas as pd
import pyproj

# Name that will be used by default in all the classes when a database
# is needed but not provided. CSV MUST be in the same folder as this
# file
csv_name = '2018_01_Sites_mobiles_2G_3G_4G_France_metropolitaine_L93.csv'

# Operators that are coded. When a decoder is needed, this dict is
# imported
operator_code = {20801: 'Orange',
                 20810: 'SFR',
                 20815: 'Free',
                 20820: 'Bouygue'}


def remove_na_values(path):
    """
    Function created to clean and rewrite the database in case at some
    point it grows and the NA problem persists or pandas parameters
    fails.

    Parameters:
    -----------
    path: (str)
        CSV path file
    """
    data_frame = pd.read_csv(path, sep=';')
    index_to_delete = []
    for index, row in data_frame.iterrows():
        try:
            int(row['x'])
            int(row['y'])
        except ValueError:
            index_to_delete.append(index)

    for i in index_to_delete:
        data_frame = data_frame.drop(index=i)

    data_frame.to_csv(path, index=False, sep=';')


def lamber93_to_gps(x, y):
    """
    Function provided by the question.
    Given two variables regarding a location in lamber93 format, returns
    that same location in gps latitude and longitude

    Parameters:
    -----------
    x: (int)
        first value regarding the location
    y: (int)
        second value regarding the location

    Return:
    -------
    tuple of int:
        first value on the tuple is the latitude
        second value on the tuple is the longitude
    """
    lambert = pyproj.Proj('+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs')
    wgs84 = pyproj.Proj('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
    long, lat = pyproj.transform(lambert, wgs84, x, y)
    return lat, long


def lamber93_to_gps_on_file(path):
    """
    Function that when given a standard csv file containing location
    under the title of 'x' and 'y', for the first and second values,
    changes them to latitude and longitude and rewrites the csv file.

    Parameters:
    -----------
    path: (str)
        Path to the csv file
    """
    data_frame = pd.read_csv(path, sep=';')
    for index, row in data_frame.iterrows():
        lat, long = lamber93_to_gps(row['x'], row['y'])
        data_frame.at[index, 'x'] = lat
        data_frame.at[index, 'y'] = long

    data_frame.rename(columns={'x': 'Latitude', 'y': 'Longitude'}, inplace=True)
    data_frame.to_csv(path, index=False, sep=';')
