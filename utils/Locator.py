from geopy.geocoders import Nominatim


class Locator:
    """
    Class to generate a Location and ensure has the necessary parameters
    when created. Expected to have a not None address, that can be found
    by the geolocator and that is inside the coordinates of France.

    Parameters:
    -----------
    address: (str)
        An actual address that will be used to create a Locator. It is
        expected to be a real address in France
    """
    def __init__(self, address):
        self.check_address_value(address)

        # Generate a location from the address
        geolocator = Nominatim(user_agent='JG-papernest')
        self.location = geolocator.geocode(str(address))

        # Check the location is not None
        self.check_location_value()

        # Get the coordinates of the location
        self.latitude = self.location.latitude
        self.longitude = self.location.longitude

        # Check the location is in France
        self.check_location()

    @staticmethod
    def check_address_value(address):
        """
        Check that the address is not None
        """
        if address is None:
            raise AttributeError("Sorry, no address has been "
                                 "recognized, check the url!")

    def check_location_value(self):
        """
        Method to check that the location can be found
        and it is not None
        """
        if self.location is None:
            raise AttributeError("Sorry, we weren't able to "
                                 "find your address, please "
                                 "try another close one")

    def check_location(self):
        """
        Method to check if the location is in France
        """
        if self.latitude < 41.59101 or self.latitude > 51.03457 \
                or self.longitude < -4.65 or self.longitude > 9.45:
            raise AttributeError("Sorry, your location must be in "
                                 "France to return a precise result")
