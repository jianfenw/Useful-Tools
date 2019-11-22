
import os
import sys
import csv
import collections

class CsvHandler(object):
	filename = None
	target_dic = collections.defaultdict(float)
	target_count_dic = collections.defaultdict(int)

	def __init__(self, target_file='./example.csv'):
		self.filename = target_file

	def handler(self):
		with open(self.filename) as fp:
			csv_reader = csv.reader(fp, delimiter=',')
			for idx, row in enumerate(csv_reader):
				if idx == 0:
					continue

				if len(row[3].strip()) == 0:
					continue
				if ('_24h' in row[2]) or ('_8h' in row[2]):
					continue

				if row[2] not in self.target_dic:
					self.target_dic[row[2]] = 0.0
					self.target_count_dic[row[2]] = 0
				self.target_dic[row[2]] += float(row[3])
				self.target_count_dic[row[2]] += 1

def main():
	csv_handler = CsvHandler(target_file='china_sites_20140513.csv')
	csv_handler.handler()
	print csv_handler.target_dic
	print csv_handler.target_count_dic

if __name__ == '__main__':
	main()