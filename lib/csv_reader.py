# REF: stefan.mastilak@gmail.com

"""
Data reader
"""

import os
import csv


class Reader(object):
    """
    Class for reading data from .csv file
    """

    def __init__(self, filename: str):
        """
        :param filename: csv filename with extension
        """
        self.filepath = os.path.join(os.getcwd(), "example", filename)

    def __get_raw_data(self):
        """
        Open a .csv file and read it line-by-line and return its content
        :return: content of file (list of its lines)
        :rtype: list
        """
        if os.path.exists(self.filepath):
            with open(file=self.filepath, mode='r') as csv_file:
                csv_reader = csv.reader(csv_file)
                content = [line for line in csv_reader]
                if content:
                    if len(content) > 1:
                        return content
                    else:
                        raise Exception(f"No data found in: {self.filepath}")
                else:
                    raise EOFError(f"Empty file: {self.filepath}")
        else:
            raise FileNotFoundError(f"Filepath doesn't exist: {self.filepath}")

    def read_data(self):
        """
        Read flight cases from .csv file.
        :return: formatted data - list of dicts (each dict is a flight case fetched from .csv file)
        :rtype: list
        """
        # data split:
        raw_data = self.__get_raw_data()
        header = {idx: val for idx, val in enumerate(raw_data[0])}
        flight_data = [i for i in raw_data[1:]]

        # data consistency check:
        for case in flight_data:
            if len(case) == len(header):
                pass
            else:
                raise ValueError(f"Inconsistent flight data - missing values")

        # format data
        formatted_data = []
        for line in flight_data:
            current = {}
            for idx, val in enumerate(line):
                current[header[idx]] = val
            # transform bags to integer:
            current["bags_allowed"] = int(current["bags_allowed"])
            # transform prices to floats:
            current["base_price"] = float(current["base_price"])
            current["bag_price"] = float(current["bag_price"])
            # append current flight case:
            formatted_data.append(current)

        # return formatted data:
        return formatted_data
