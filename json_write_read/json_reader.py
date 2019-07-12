from __future__ import print_function
import collections
import json


class JsonReader(object):
    data_cache_ = None
    filename_ = None

    def __init__(self, filename):
        if not filename:
            self.filename_ = './data.json'
        else:
            self.filename_ = filename
        with open(self.filename_, 'r') as read_file:
            self.data_cache_ = json.load(read_file)

    def print_data(self):
        for index, (key, val) in enumerate(self.data_cache_.items()):
            print("ln %d: key=" % (index), key, ", val=",
                  self.data_cache_[key])


def main():
    json_reader = JsonReader('./data.json')
    json_reader.print_data()


if __name__ == '__main__':
    main()
