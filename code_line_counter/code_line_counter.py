#!/usr/bin/python

from __future__ import print_function
import os
import sys
import string
import copy
import argparse



# One simple method is to use the command line tools
# find . -type f -exec wc  {} \; | awk '{print $1}'|xargs

class LangCounter(object):
	def __init__(self, input_lang=None):
		# self.stats_argv: 
		# 'all' : total_lines, 'cmt' : comment_lines, 'code' : code_lines
		self.lang = None
		self.stats_argv = []
		self.total_lines = 0
		self.comment_lines = 0
		self.code_lines = 0
		if input_lang != None:
			self.lang = copy.deepcopy(input_lang)
		return

	def __str__(self):

		return


class CodeLineCounter(object):
	"""
	This is the code line counter class.
	It can output counts for total lines of code, comment lines, and code lines 
	respectively.
	For now, the counter class only supports python, C and C++ code files.
	"""
	def __init__(self, t_dir=None, stats=None, lang_argv=None):
		self.root_dir = None
		self.stats_argv = []
		self.lang_argv = []
		self.extensions = []
		self.counters = {}
		self.comment_symbols = {'python':'#', 'c':'//', 'c++':'//'}
		self.lang_extension_links = {'python':'.py', 'c':'.c', 'c++':'.cpp'}
		self.extension_lang_links = {'.py':'python', '.c':'c', '.cpp':'c++'}

		if t_dir != None:
			self.root_dir = copy.deepcopy(t_dir[0])
		if stats != None:
			self.stats_argv = copy.deepcopy(stats)
		if lang_argv != None:
			self.lang_argv = copy.deepcopy(lang_argv)
			for lang in self.lang_argv:
				self.extensions.append( self.lang_extension_links[lang] )

		print("root: '%s', stats: %s, lang: %s" %(self.root_dir, str(self.stats_argv), str(lang_argv)))
		return

	def counter_process_main(self):
		self.counter_init_counters()

		target_files = []
		for root, _, files in os.walk(self.root_dir):
			#print(files)
			for f in files:
				fullpath = os.path.join(root, f)
				for extension in self.extensions:
					if fullpath.endswith(extension):
						target_files.append( (fullpath, self.extension_lang_links[extension]) )

		if len(target_files)==0:
			print('No files found')
			return

		for file in target_files:
			print('file: %s' %(file[0]))
			self.counter_code_handler(file[0], file[1])

		return

	def counter_init_counters(self):
		for lang in self.lang_argv:
			self.counters[lang] = 0
		return

	def counter_code_handler(self, filename, lang):
		with open(filename) as f:
			total_line_count = 0
			blank_line_count = 0
			code_line_count = 0
			comment_line_count = 0
			for line in f:
				total_line_count += 1
				no_space_line = line.strip()
				if not no_space_line:
					blank_line_count += 1
				elif no_space_line.startswith(self.comment_symbols[lang]):
					comment_line_count += 1
				else:
					code_line_count += 1

		self.counters[lang] += total_line_count
		print(total_line_count, blank_line_count, comment_line_count, code_line_count)
		return


def counter_main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--path', '-p', nargs=1, required=True,help='Please give the target path')
	parser.add_argument('--stats', '-s', nargs='*', choices=['all', 'cmt', 'code'], help='Please specify the target statistics')
	parser.add_argument('--lang', '-l', nargs='*', choices=['python', 'c', 'c++'], help='Please specify the target language(s)')
	args = parser.parse_args()

	#print(args)
	#print(args.lang, args.path)
	counter = CodeLineCounter(args.path, args.stats, args.lang)
	counter.counter_process_main()
	return


def counter_simple_tester():
	counter_main()
	return



if __name__ == '__main__':
	counter_simple_tester()


