
import signal
import sys
import time

class Foo(object):
	_name = "Foo"

	def __init__(self):
		signal.signal(signal.SIGTSTP, self.sigsusp_handler)
		signal.signal(signal.SIGINT, self.sigint_handler)

	def sigsusp_handler(self, signum, frame):
		# signal.SIGTSTP = 18; frame
		print "Receive a signal[%d]!" %(signum), frame
		return

	def sigint_handler(self, signum, frame):
		# signal.SIGSUSP = 2; frame
		print "Receive a signal[%d]!" %(signum), frame
		sys.exit(0)
		return


if __name__ == "__main__":
	foo = Foo()
	while True:
		time.sleep(1)
