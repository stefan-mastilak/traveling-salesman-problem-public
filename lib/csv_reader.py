# REF: stefan.mastilak@gmail.com

"""
Data reader
"""

import os


class CsvReader(object):
    """
    Class for reading .csv data
    """

    def __init__(self, filepath):
        """
        :param filepath: full path to csv file
        """
        self.filepath = filepath

    def __get_raw_data(self):
        """
        Open a file and read it line-by-line
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
        description
        :return:
        """
        # split data:
        raw_data = self.__get_raw_data()
        header = {idx: val for idx, val in enumerate(raw_data[0].split(sep=","))}
        data = [i.split(sep=",") for i in raw_data[1:]]

        # consistency check:
        for i in data:
            if len(i) == len(header):
                pass
            else:
                raise ValueError(f"Inconsistent flight data")

        # format data:
        formatted_data = []
        for line in data:
            current = {}
            for idx, val in enumerate(line):
                current[header[idx]] = val
            formatted_data.append(current)

        return formatted_data
