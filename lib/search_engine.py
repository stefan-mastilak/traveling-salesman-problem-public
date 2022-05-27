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
from lib.csv_reader import Reader


class Searcher(Reader):
    """
    Search engine class
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
        return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%dT%H:%M:%S")

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
    def __hours_to_seconds(hours: float):
        """
        Convert hours to seconds.
        :param hours: number of hours to convert
        :return: hours converted to seconds
        :rtype: int
        """
        return hours * 3600

    def get_edges(self):
        """
        EXPERIMENTAL - Get all possible origin-destination pairs from the available flights
        NOTE: Not used
        """
        routes = []
        for i in self.data:
            routes.append([i["origin"], i["destination"]]) if [i["origin"], i["destination"]] not in routes else None
        return routes

    def get_nodes(self):
        """
        EXPERIMENTAL - Get all nodes from the routes(edges)
        NOTE: Not used
        """
        sources, destinations = zip(*self.get_edges())
        nodes = []
        for i in sources:
            nodes.append(i) if i not in nodes else None
        for j in destinations:
            nodes.append(j) if j not in nodes else None
        return nodes

    @staticmethod
    def __get_allowed_bags(flight: list):
        """
        Get allowed bags count as minimum of allowed baggage from all flights in flight chain
        :param flight: flight chain
        :return: minimum baggage count
        :rtype: int
        """
        max_no_of_bags = [f["bags_allowed"] for f in flight]
        return min(max_no_of_bags)

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

    def __get_trip_price(self, bags: int, flight: list):
        """
        Get total trip price as sum of each flight base_price and bag_price multiplied by number_of_bags
        :param bags: number of bags in the trip
        :param flight: flight chain
        :return: trip total price
        :rtype: float
        """
        prices = [self.__calc_price(base=f["base_price"], bag=f["bag_price"], bags=bags) for f in flight]
        return sum(prices)

    def __get_trip_duration(self, flight: list):
        """
        Get trip duration as subtraction of destination arrival timestamp and origin departure timestamp
        :param flight: flight chain
        :return: trip duration
        :rtype: str
        """
        start = self.__to_timestamp(flight[0]["departure"])
        end = self.__to_timestamp(flight[-1]["arrival"])
        return str(datetime.timedelta(seconds=end - start))

    def __transform_results(self, org, des, bags, flights: list):
        """
        Transform found flights to the desired output
        :param org: origin (Origin airport code)
        :param des: destination (Destination airport code)
        :param bags: number of bags
        :param flights: list of found flight chains
        :return: transformed results
        :rtype: list
        """
        transformed = []
        for flight in flights:
            current = {"flights": [f for f in flight],
                       "bags_allowed": self.__get_allowed_bags(flight=flight),
                       "bags_count": bags,
                       "destination": des,
                       "origin": org,
                       "total_price": self.__get_trip_price(bags=bags, flight=flight),
                       "travel_time": self.__get_trip_duration(flight=flight)
                       }
            transformed.append(current)
        return sorted(transformed, key=lambda p: p["total_price"])

    @staticmethod
    def __get_visitations(connection: list):
        """
        Get visited airport codes from the connection chain
        :param connection: connection flights chain
        :return: list of visited airports codes based on the passed connection flights chain
        :rtype: list
        """
        visitations = []
        for i in connection[:-1]:
            visitations.append(i["origin"]) if i["origin"] not in visitations else None
            visitations.append(i["destination"]) if i["destination"] not in visitations else None
        return visitations

    def __get_flights(self, org: str, des: str, bags=0, arr=None, initial=True):
        """
        Method for getting flights from origin to destination and connection flights from origin
        :param org: origin (Origin airport code)
        :param des: destination (Destination airport code)
        :param bags: number of bags (0 by default)
        :param arr: arrival datetime
        :param initial: True for getting initial flights
        """
        flights = []
        connections = []

        # Transform to arrival datetime to timestamp:
        if arr:
            arr = self.__to_timestamp(arr)

        # Iterate over flights:
        for f in self.data:

            # Get flights to destination:
            if initial:
                if f["origin"] == org and f["destination"] == des and f["bags_allowed"] >= bags:
                    flights.append([f]) if [f] not in flights else None
            else:
                if f["origin"] == org and f["destination"] == des and f["bags_allowed"] >= bags \
                        and arr + 21600 >= self.__to_timestamp(f["departure"]) >= arr + 3600:
                    flights.append([f]) if [f] not in flights else None

            # Get connection flights:
            if initial:
                if f["origin"] == org and f["destination"] != des and f["bags_allowed"] >= bags:
                    connections.append([f]) if [f] not in connections else None
            else:
                if f["origin"] == org and f["destination"] != des and f["bags_allowed"] >= bags \
                        and arr + 21600 >= self.__to_timestamp(f["departure"]) >= arr + 3600:
                    connections.append([f]) if [f] not in connections else None

        # Return flights and connections:
        return flights, connections

    def search(self, org: str, des: str, bags=0, max_conns=2):
        """
        Search method for:
        * direct flights from origin to destination
        * connection flights from origin to destination (maximum of connections is defined by parameter: max_conns)
        :param org: origin (Origin airport code)
        :param des: destination (Destination airport code)
        :param bags: number of bags (0 by default)
        :param max_conns: maximum of connections for the trip (2 by default)
        :return:
        :rtype:
        """
        # Input conversions:
        org = org.upper()
        des = des.upper()

        # 1) INITIAL SEARCH: (Get direct flights from origin to destination and connections from origin)
        flights, connections = self.__get_flights(org=org, des=des, bags=bags, initial=True)

        # 2) CONNECTIONS SEARCH: (Get next flights to destination and next connections)
        while max_conns > 0:
            # Clear new connections for current iteration:
            new_connections = []

            # Iterate over connections:
            for c in connections:
                # Get visited airports for current connection:
                visitations = self.__get_visitations(connection=c)

                # Check for new flights and new connections:
                if c[-1]["destination"] not in visitations:

                    new_flights, new_conns = self.__get_flights(org=c[-1]["destination"],
                                                                des=des,
                                                                bags=bags,
                                                                arr=c[-1]["arrival"],
                                                                initial=False)
                    # Save new flights to destination:
                    for nf in new_flights:
                        new = [i for i in c]
                        new.append(nf[-1])
                        flights.append(new) if new not in flights else None

                    # Save next connections:
                    for nc in new_conns:
                        new = [i for i in c]
                        new.append(nc[-1])
                        new_connections.append(new) if new not in new_connections else None

            # Decrement max_conns and reassign connections:
            max_conns -= 1
            connections = new_connections

        # 3) RETURN RESULTS: (Including transformation to desired output)
        flights = self.__transform_results(org, des, bags, flights)
        return flights
