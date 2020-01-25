
import signal
import sys
import time

def sigint_handler(sig, frame):
	print "Clean up!"
	# signal.SIGINT = 2; frame
	print sig, type(sig)
	print frame, type(frame)
	sys.exit(0)

def sigsusp_handler(sig, frame):
	print "Clean up!"
	# signal.SIGINT = 2; frame
	print sig, type(sig)
	return

if __name__ == "__main__":
	signal.signal(signal.SIGINT, sigint_handler)
	signal.signal(signal.SIGTSTP, sigsusp_handler)
	print "Press Ctrl+C to exit; Ctrl+Z to peek the program state."

	while True:
		time.sleep(1)

	# Cause the process to sleep until a signal is received.
	signal.pause()
