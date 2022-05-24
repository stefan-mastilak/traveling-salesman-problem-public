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
import time
from lib.csv_reader import CsvReader


class SearchEngine(CsvReader):
    """
    Search engine
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.data = self.read_data()

    @staticmethod
    def __to_timestamp(date: str):
        """
        Method will convert datetime from string in format "%Y-%m-%dT%H:%M:%S" to the timestamp
        :param date: datetime string ("%Y-%m-%dT%H:%M:%S")
        :return: timestamp
        :rtype: float
        """
        return time.mktime(datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S").timetuple())

    @staticmethod
    def __to_datetime(timestamp: float):
        """
        Method will convert timestamp to datetime string in format "%Y-%m-%d %H:%M:%S"
        :param timestamp: timestamp
        :return: datetime as string ("%Y-%m-%d %H:%M:%S")
        :rtype: str
        """
        return datetime.datetime.fromtimestamp(timestamp)

    def __calc_duration(self, arr: float, dep: float):
        """
        Method will calculate duration based on arrival and departure timestamp
        :param arr: arrival timestamp
        :param dep: departure timestamp
        :return: duration
        :rtype: str
        """
        return str(self.__to_datetime(arr - dep)).split()[1]

    def search(self, org: str, des: str, bags=0):
        """
        Search flights
        :param org: origin (Origin airport code)
        :param des: destination (Destination airport code)
        :param bags: number of bags (0 by default)
        :return:
        """
        data = self.data
        org = str(org.upper())
        des = str(des.upper())
        result = []

        # Iterate over available flights:
        for flight in data:
            # get current flight details:
            _no = flight['flight_no']
            _org = flight['origin']
            _des = flight['destination']
            _dep = self.__to_timestamp(date=flight['departure'])
            _arr = self.__to_timestamp(date=flight['arrival'])
            _bags = int(flight['bags_allowed'])
            _price = float(flight['base_price']) + float(flight['bag_price'] * bags)

            # Direct flights:
            if org == _org and des == _des and bags <= _bags:
                direct = {"flights": flight,
                          "bags_allowed": _bags,
                          "bags_count": bags,
                          "destination": des,
                          "origin": org,
                          "travel_time": self.__calc_duration(_arr, _dep),
                          "total_price": _price}
                # append found direct flights to the result:
                result.append(direct)

            # Connection flights:

            # Return flights:

        return result



a = SearchEngine("example0.csv")
print(a.search(org='ECV', des="WIW", bags=2))
