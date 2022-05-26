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
    def __to_datetime(timestamp: float):
        """
        Method will convert timestamp to datetime string in format "%Y-%m-%d %H:%M:%S"
        :param timestamp: timestamp
        :return: datetime as string ("%Y-%m-%d %H:%M:%S")
        :rtype: str
        """
        return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%dT%H:%M:%S")

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
    def __to_timestamp(date: str):
        """
        Method will convert datetime from string in format "%Y-%m-%dT%H:%M:%S" to the timestamp
        :param date: datetime string ("%Y-%m-%dT%H:%M:%S")
        :return: timestamp
        :rtype: float
        """
        return time.mktime(datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S").timetuple())

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

    def get_edges(self):
        """
        EXPERIMENTAL - Get all possible origin-destination pairs from the available flights
        """
        routes = []
        for i in self.data:
            routes.append([i["origin"], i["destination"]]) if [i["origin"], i["destination"]] not in routes else None
        return routes

    def get_nodes(self):
        """
        EXPERIMENTAL - Get all nodes from the routes
        """
        sources, destinations = zip(*self.get_edges())
        nodes = []
        for i in sources:
            nodes.append(i) if i not in nodes else None
        for j in destinations:
            nodes.append(j) if j not in nodes else None
        return nodes

    @staticmethod
    def __transform_nodes(nodes):
        tr_nodes = {}
        for idx, node in enumerate(nodes):
            tr_nodes[node] = idx
        return tr_nodes

    @staticmethod
    def __transform_edges(edges, mappings):
        tr_edges = []
        for idx, edge in enumerate(edges):
            tr_edges.append([mappings[edge[0]], mappings[edge[1]]])
        return tr_edges

    def calculate_routes(self, org, des):
        from lib.graph import Graph
        nodes = self.get_nodes()
        edges = self.get_edges()
        mappings = self.__transform_nodes(nodes)
        edges = self.__transform_edges(edges, mappings)
        print(mappings)

        graph = Graph(vertices=len(nodes))
        for i in edges:
            graph.addEdge(i[0], i[1])
        graph.printAllPaths(org, des)

    def get_flights(self, org: str, des: str, bags=0, arr=None, initial=True):
        """
        Method for getting direct flights from origin to destination and connection flights from origin
        :param org: origin (Origin airport code)
        :param des: destination (Destination airport code)
        :param bags: number of bags (0 by default)
        :param arr: arrival timestamp
        :param initial: True for getting initial flights
        """
        flights = []
        connections = []
        if arr:
            arr = self.__to_timestamp(arr)

        # iterate over flights:
        for f in self.data:

            # flight to destination:
            if initial:
                if f["origin"] == org and f["destination"] == des and f["bags_allowed"] >= bags:
                    flights.append([f]) if [f] not in flights else None
            else:
                if f["origin"] == org and f["destination"] == des and f["bags_allowed"] >= bags \
                        and arr+21600 >= self.__to_timestamp(f["departure"]) >= arr+3600:
                    flights.append([f]) if [f] not in flights else None

            # connection flight:
            if initial:
                if f["origin"] == org and f["destination"] != des and f["bags_allowed"] >= bags:
                    connections.append([f]) if [f] not in connections else None
            else:
                if f["origin"] == org and f["destination"] != des and f["bags_allowed"] >= bags \
                        and arr+21600 >= self.__to_timestamp(f["departure"]) >= arr+3600:
                    connections.append([f]) if [f] not in connections else None

        # return results:
        return flights, connections

    def do_search(self, org, des, bags=0, hops=2):
        search = self.get_flights(org, des, bags, initial=True)
        flights = search[0]
        connections = search[1]

        # search for next flights and connections:
        while hops > 0:
            new_connections = []
            # iterate over connections:
            for c in connections:
                # get visited airports for current connection:
                visitations = []
                for i in c[:-1]:
                    visitations.append(i["origin"]) if i["origin"] not in visitations else None
                    visitations.append(i["destination"]) if i["destination"] not in visitations else None

                if c[-1]["destination"] not in visitations:
                    new = self.get_flights(org=c[-1]["destination"], des=des, bags=bags, arr=c[-1]["arrival"], initial=False)
                    # save new flights to destination:
                    for fd in new[0]:
                        new_flight = [i for i in c]
                        new_flight.append(fd[-1])
                        flights.append(new_flight) if new_flight not in flights else None
                    # save new connections:
                    for nc in new[1]:
                        new_connection = [i for i in c]
                        new_connection.append(nc[-1])
                        new_connections.append(new_connection)

            hops -= 1
            connections = new_connections
        return flights


a = SearchEngine("example3.csv")
r = a.do_search(org='WUE', des='JBN', bags=2, hops=7)
print(len(r))
for i in r:
    print(f'{i}\n')
# r = a.get_connection_flights(org='WUE', des='JBN', bags=1)


