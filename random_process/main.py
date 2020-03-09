
import math
from event_arrival import *
from task_queue import Task, TaskQueue

# All times are counted in ns.
SYSTEM_RUNTIME = 5 * 10 ** 9


class ExperimentalScheduler(object):
	_CPU_CORES = None
	_schedulable_tasks = {}
	# |_epoch_ns| is the minimal time granularity of rescheduling tasks.
	_epoch_ns = 10000000

	# The current scheduling scheme.
	_scheduling_scheme = {}

	# Counts the number of CPU * epoch.
	_cpu_usage_counter = 0
	_epoch_counter = 0

	# Global timer.
	_wall_clock_time = 0

	def __init__(self, cores_count):
		self._CPU_CORES = cores_count
		self._schedulable_tasks = {}
		self._cpu_usage_counter = 0
		self._epoch_counter = 0
		self._wall_clock_time = 0

	def add_task(self, task):
		self._schedulable_tasks[task._task_name] = task

	def pre_scheduling(self):
		# The start and end timestamp of the current epoch.
		START_TIME = self._wall_clock_time
		END_TIME = self._wall_clock_time + self._epoch_ns

		# Refills packets that arrives between |START_TIME| and
		# |END_TIME|.
		for task_name, task in self._schedulable_tasks.items():
			task.simulate_packet_arrivals(START_TIME, END_TIME)

	def has_packets_left(self):
		for task_name, task in self._schedulable_tasks.items():
			if not task.empty():
				return True
		return False

	# This is the core dynamic scheduling algorithm.
	# Dynamically reschedule all existing tasks according to 
	# queue info and the processing time.
	def on_scheduling(self):
		core = 0
		for task_name, task in self._schedulable_tasks.items():
			if not task.empty():
				self._scheduling_scheme[core] = [task]
				core += 1

	# This is the per-core task scheduling algorithm.
	# Least Slack First (LSF) or Earliest Deadline First (EDF).
	def post_scheduling(self):
		START_TIME = self._wall_clock_time

		for core, tasks in self._scheduling_scheme.items():
			# |now| is a per-core local time.
			now = START_TIME

			# Runs |tasks| on |core| until the end of this epoch.
			while now < self._wall_clock_time + self._epoch_ns:
				task = None
				batch, batch_time = None, 0
				for task in tasks:
					batch, batch_time = task.process_batch(now)
					# Picks the first queue that has packets.
					if batch_time > 0:
						break

				# No packets available.
				if len(batch) == 0:
					now += 500
					continue

				now += batch_time
				#print "batch size = %d; batch time = %d" %(len(batch), batch_time)

				for packet in batch:
					if packet.is_violating_slo(now):
						task._slo_violation_counter += 1
				task._packets_counter += len(batch)

		self._cpu_usage_counter += len(self._scheduling_scheme)
		self._epoch_counter += 1
		self._wall_clock_time += self._epoch_ns

	def statistics_report(self):
		total_packets = 0
		total_slo_violations = 0
		total_cpu_usage = 0

		print("Statistics Report:")
		for task_name, task in self._schedulable_tasks.items():
			print("\t* %s:" %(task._task_name))
			print("\tPackets In Queue: %d" %(len(task._packets_queue)))
			print("\tTotal Packets: %d" %(task._packets_counter))
			print("\tPackets Violating SLOs: %d" %(task._slo_violation_counter))
			print("\tPercentage of bad packets: %d%%" \
				%(100 * task._slo_violation_counter / task._packets_counter))

			total_packets += task.packets_counter()
			total_slo_violations += task.slo_violation_counter()
			total_cpu_usage += task.cpu_usage_counter()


		print("Total packets: %d" %(total_packets))
		print("Total SLO violations: %d [%d%%]" \
			%(total_slo_violations, 100 * total_slo_violations / total_packets))
		print("Total CPU usage: %d" %(self._cpu_usage_counter))
		print("Total epoch [%d ms]: %d" %(self._epoch_ns / 10**6, self._epoch_counter))
		print("Avg CPU usage: %f" %(self._cpu_usage_counter / float(self._epoch_counter)))


def main():
	sched = ExperimentalScheduler(16)

	task0 = TaskQueue("CHACHA")
	# 1s: 100000 tasks. Each service time < 1000 ns;
	task0.set_arrival_rate(100000)
	task0.set_service_time(1000)
	task0.set_delay_slo(5000000)

	task1 = TaskQueue("ACL -> NAT")
	task1.set_arrival_rate(10000)
	task1.set_service_time(100)
	task1.set_delay_slo(5000000)

	"""
	task2 = TaskQueue("ACL -> UrlFilter")
	task2.set_arrival_rate(10000)
	task2.set_service_time(800)
	task2.set_delay_slo(5000000)
	"""

	sched.add_task(task0)
	sched.add_task(task1)
	#sched.add_task(task2)

	while sched._wall_clock_time < SYSTEM_RUNTIME:
		sched.pre_scheduling()

		sched.on_scheduling()

		sched.post_scheduling()

	while sched.has_packets_left():
		sched.on_scheduling()
		sched.post_scheduling()

	sched.statistics_report()


if __name__ == '__main__':
	main()