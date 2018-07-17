from __future__ import print_function
import os
import sys
import string
import copy
import argparse


# One simple method is to use the command line tools
# find . -type f -exec wc  {} \; | awk '{print $1}'|xargs

class LangCounter(object):
	def __init__(self, input_lang=None, input_stats_argv=None):
		# self.stats_argv: 
		# 'all' : total_lines, 'cmt' : comment_lines, 'code' : code_lines
		self.lang = None
		self.stats_argv = []
		self.counters = {'all':0, 'cmt':0, 'code':0}
		if input_lang != None:
			self.lang = copy.deepcopy(input_lang)
		if input_stats_argv != None:
			self.stats_argv = copy.deepcopy(input_stats_argv)
		return

	def __str__(self):
		res_str = ""
		for curr_stat in sorted(self.stats_argv):
			if len(res_str):
				res_str += "\n%s: %d lines of %s;" %(self.lang, self.counters[curr_stat], curr_stat)
			else:
				res_str += "%s: %d lines of %s;" %(self.lang, self.counters[curr_stat], curr_stat)
		return res_str


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
		return

	def counter_process_main(self):
		self.counter_init_counters()
		target_files = None
		for curr_lang in self.lang_argv:
			curr_extension = self.lang_extension_links[curr_lang]
			target_files = self.counter_get_files(self.root_dir, curr_extension)
			#print(target_files)

			if len(target_files)==0:
				print('No %s file found' %(curr_lang))
				continue
			else:
				for file in target_files:
					self.counter_code_handler(file, curr_lang)
				#print('%s: %s' %(curr_lang, (self.counters[curr_lang]) ))
		return

	def counter_get_files(self, t_dir, extension):
		target_files = []
		files = sorted(os.listdir(t_dir))
		for file in files:
			complete_filename = os.path.join(t_dir, file)
			if os.path.isdir(complete_filename):
				# this is a dir
				target_files += self.counter_get_files(complete_filename, extension)
			else:
				# this is a file
				if complete_filename.endswith(extension):
					target_files.append(complete_filename)
		return target_files

	def counter_init_counters(self):
		for lang in self.lang_argv:
			self.counters[lang] = LangCounter(lang, self.stats_argv)
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

		lang_counter = self.counters[lang]
		lang_counter.counters['cmt'] += comment_line_count
		lang_counter.counters['code'] += code_line_count
		lang_counter.counters['all'] += total_line_count
		return


def counter_main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--path', '-p', nargs=1, required=True,help='Please give the target path')
	parser.add_argument('--stats', '-s', nargs='*', choices=['all', 'cmt', 'code'], help='Please specify the target statistics')
	parser.add_argument('--lang', '-l', nargs='*', choices=['python', 'c', 'c++'], help='Please specify the target language(s)')
	args = parser.parse_args()

	#print(args)
	#print(args.lang, args.path)
	handler = CodeLineCounter(args.path, args.stats, args.lang)
	handler.counter_process_main()
	print(handler.counters['python'])
	return


def counter_simple_tester():
	counter_main()
	return



if __name__ == '__main__':
	counter_simple_tester()


