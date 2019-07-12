import collections
import json


class JsonDumper(object):
    data_cache_ = collections.defaultdict()
    count_val_entry_ = 0
    count_list_entry_ = 0

    def __init__(self, capacity):
        self.capacity_ = capacity

    def add_key_val(self, key, val):
        self.data_cache_[key] = val
        self.count_val_entry_ += 1

    def add_key_list(self, key, target_list):
        self.data_cache_[key] = target_list
        self.count_list_entry_ += 1

    def dump_to_json(self, filename):
        if not filename:
            filename = './data.json'
        with open(filename, 'w') as outfile:
            json.dump(self.data_cache_, outfile, indent = 4)


def main():
    json_dumper = JsonDumper(10)
    json_dumper.add_key_val(10, 20)
    json_dumper.add_key_list('names', ['bob', 'jane', 'ming', 'hell'])
    json_dumper.dump_to_json(None)


if __name__ == '__main__':
    main()
