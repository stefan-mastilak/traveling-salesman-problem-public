# REF: stefan.mastilak@gmail.com

"""
Search engine

Restrictions:
    - search on ALL available combinations
    - in case of a combination of A -> B -> C, the layover time in B should not be less than 1h and more than 6h
    - no repeating airports in the same trip
    - output is sorted by the final price of the trip

Optional arguments:
    - You may add any number of additional search parameters to boost your chances to attend:
        - bags: <integer> - number of requested bags (default 0)
        - return: <bool> - is it a return flight (default false)
"""

import datetime
import json
from lib.csv_reader import CsvReader


class SearchEngine(CsvReader):
    """
    Search engine
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.data = self.read_data()

    @staticmethod
    def __to_datetime(timestamp: float):
        """
        Method will convert timestamp to datetime string in format "%Y-%m-%d %H:%M:%S"
        :param timestamp: timestamp
        :return: datetime as string ("%Y-%m-%d %H:%M:%S")
        :rtype: str
        """
        return datetime.datetime.fromtimestamp(timestamp)

    @staticmethod
    def __calc_duration(arrival: float, departure: float):
        """
        Method will calculate duration based on arrival and departure timestamp
        :param arrival: arrival timestamp
        :param departure: departure timestamp
        :return: duration
        :rtype: str
        """
        return str(datetime.timedelta(seconds=arrival-departure))

    @staticmethod
    def __calc_price(base: float, bag: float, bags: int):
        """
        Calculate total flight price as sum of base flight price and price for bags
        :param base: base price of flight
        :param bag: bag price
        :param bags: number of bags
        :return:
        """
        return base + (bag * bags)

    @staticmethod
    def __to_seconds(hours: float):
        """
        Convert hours to seconds.
        :param hours: number of hours to convert
        :return: hours converted to seconds
        :rtype: int
        """
        return hours * 3600

    @staticmethod
    def __join_results(direct, connection):
        """
        Join direct and connection flights results
        :param direct: direct flights list
        :param connection: connection flights list
        :return: joined result
        :rtype: list
        """
        return [*direct, *connection]

    def get_direct_flights(self, org: str, des: str, bags=0):
        """
        Search for direct flights from source to destination.
        :param org: origin (Origin airport code)
        :param des: destination (Destination airport code)
        :param bags: number of bags (0 by default)
        :return: direct flights
        :rtype: dict
        """
        # Conversions:
        org = str(org.upper())
        des = str(des.upper())

        result = []

        # Iterate over all flights:
        for flight in self.data:
            # Get flight details:
            _org = flight['origin']
            _des = flight['destination']
            _dep = flight['departure']
            _arr = flight['arrival']
            _bags = flight['bags_allowed']
            _base_price = flight['base_price']
            _bag_price = flight['bag_price']

            # Check direct flights:
            if org == _org and des == _des and bags <= _bags:
                direct = {"flights": [flight],
                          "bags_allowed": _bags,
                          "bags_count": bags,
                          "destination": des,
                          "origin": org,
                          "travel_time": self.__calc_duration(arrival=_arr, departure=_dep),
                          "total_price": self.__calc_price(base=_base_price, bag=_bag_price, bags=bags)}

                # Append direct flights to the result:
                result.append(direct)

        # Return direct flights:
        return result

    def get_connection_flights(self, org: str, des: str, bags=0, min_time=1, max_time=6):
        """
        Search for connection flights from source to destination.
        :param org: origin (Origin airport code)
        :param des: destination (Destination airport code)
        :param bags: number of bags (0 by default)
        :param min_time: minimum time for connection in hours (1h by default)
        :param max_time: maximum time for connection in hours (6h by default)
        :return:
        """
        # Conversions:
        org = str(org.upper())
        des = str(des.upper())
        min_time = self.__to_seconds(hours=min_time)
        max_time = self.__to_seconds(hours=max_time)

        results = []
        conn_origins = []
        conn_destinations = []

        # Iterate over all flights:
        for flight in self.data:
            # Get flight details:
            _org = flight['origin']
            _des = flight['destination']
            _bags = flight['bags_allowed']

            # Get all flights from origin and not to destination:
            conn_origins.append(flight) if org == _org and des != _des and bags <= _bags else None

            # Get all flights to destination and not from origin:
            conn_destinations.append(flight) if des == _des and org != _org and bags <= _bags else None

        # Pair connections:
        for i in conn_origins:
            _org_des = i["destination"]
            _org_dep = i["departure"]
            _org_arr = i["arrival"]
            _org_bags = i["bags_allowed"]
            _org_base_price = i["base_price"]
            _org_bag_price = i["bag_price"]
            _org_total = self.__calc_price(base=_org_base_price, bag=_org_bag_price, bags=bags)

            for j in conn_destinations:
                _des_org = j["origin"]
                _des_dep = j["departure"]
                _des_arr = j["arrival"]
                _des_bags = j["bags_allowed"]
                _des_base_price = j["base_price"]
                _des_bag_price = j["bag_price"]
                _des_total = self.__calc_price(base=_des_base_price, bag=_des_bag_price, bags=bags)

                # Check connection flights:
                if _org_des == _des_org and min_time <= (_des_dep - _org_arr) <= max_time:
                    connection = {"flights": [i, j],
                                  "bags_allowed": _org_bags if _org_bags < _des_bags else _des_bags,
                                  "bags_count": bags,
                                  "destination": des,
                                  "origin": org,
                                  "total_price": _org_total + _des_total,
                                  "travel_time": self.__calc_duration(arrival=_des_arr, departure=_org_dep)
                                  }
                    # Append connection flight to the result:
                    results.append(connection)

        # Return connection flights:
        return results

    def search(self, org: str, des: str, bags=0, min_time=1, max_time=6):
        """
        Search method - searching of direct and connection flights from origin to destination.
        :param org:
        :param des:
        :param bags:
        :param min_time:
        :param max_time:
        :return:
        """
        direct = self.get_direct_flights(org, des, bags)
        connection = self.get_connection_flights(org, des, bags, min_time, max_time)
        result = self.__join_results(direct, connection)  # TODO: sort results by 'total_price'
        return json.dumps(result)


a = SearchEngine("example1.csv")
r = a.search(org='NIZ', des='NRX', bags=0)
print(r)
