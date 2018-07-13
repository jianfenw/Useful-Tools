#!/usr/bin/python

import os
import sys
import string


# One simple method is to use the command line tools
# find . -type f -exec wc  {} \; | awk '{print $1}'|xargs

class CodeLineCounter(object):
	def __init__(self):
		self.root_dir = None
		self.line_count_python = 0
		self.line_count_c = 0
		self.line_count_cpp = 0
		return

	def counter_python_code_handler(self):
		return

	def counter_c_code_handler(self):
		return

	def counter_cpp_code_handler(self):
		return 



def counter_simple_tester():
	return

if __name__ == '__main__':
	counter_simple_tester()
