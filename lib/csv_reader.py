# REF: stefan.mastilak@gmail.com

"""
Data reader
"""

import os


class CsvReader(object):
    """
    Class for reading data from .csv file
    NOTE: I'm not sure if csv module is allowed, even if its part of standard lib. So I'm creating my own reader :-)
    """

    def __init__(self, filepath):
        """
        :param filepath: full path to csv file
        """
        self.filepath = filepath

    def __get_raw_data(self):
        """
        Open a .csv file and read it line-by-line and return its content
        :return: content of file (list of its lines)
        :rtype: list
        """
        if os.path.exists(self.filepath):
            with open(file=self.filepath, mode='r') as file:
                content = []
                for line in file.readlines():
                    content.append(line.replace("\n", ""))
                if content:
                    if len(content) > 1:
                        return content
                    else:
                        raise Exception(f"No flight data found in: {self.filepath}")
                else:
                    raise EOFError(f"Empty file: {self.filepath}")
        else:
            raise FileNotFoundError(f"Provided filepath doesn't exist: {self.filepath}")

    def read(self):
        """
        Read flight cases from .csv file.
        :return: formatted data - list of dicts (each dict is a flight case fetched from .csv file)
        :rtype: list
        """
        # split data:
        raw_data = self.__get_raw_data()
        header = {idx: val for idx, val in enumerate(raw_data[0].split(sep=","))}
        flight_data = [i.split(sep=",") for i in raw_data[1:]]

        # consistency check:
        for case in flight_data:
            if len(case) == len(header):
                pass
            else:
                raise ValueError(f"Inconsistent flight data")

        # format data
        # NOTE: organise flight case into the list of dicts, where each dict represents one flight case
        # NOTE values from original header are used as keys in each flight case dict

        formatted_data = []
        for line in flight_data:
            current = {}
            for idx, val in enumerate(line):
                current[header[idx]] = val
            formatted_data.append(current)

        # return formatted data:
        return formatted_data
