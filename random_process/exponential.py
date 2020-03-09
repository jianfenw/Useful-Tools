
import math
import random

# All times are counted in ns.

DEFAULT_BATCH_SIZE = 32
SYSTEM_RUNTIME = 10 ** 9


# Returns an inter-arrival time (ns) of a random process.
# |arrival_rate| is represented in Packet Per Second.
# Pattern must be 'exponential' or 'uniform'
def next_arrival_period(pattern='exponential', arrival_rate=1.0):
	if pattern == 'exponential':
		return int(-math.log(1.0 - random.random()) * 10**9 / arrival_rate)
	if pattern == 'uniform':
		return int(1 * 10**9 / arrival_rate)

def next_sevice_period(avg_service_time=100):
	return int(avg_service_time)


# A task is an NFV processing associated with a packet.
class Task(object):
	_arrival_time = None
	_service_time = None
	_depart_time = None
	_delay_slo = None
	_ddl = None
	_slack = None

	def __init__(self, arrival_time, service_time, delay_slo):
		self._arrival_time = arrival_time
		self._service_time = service_time
		self._delay_slo = delay_slo
		self._ddl = arrival_time + delay_slo
		self._slack = self._ddl - service_time

	# Returns true if the task violates its latency SLOs.
	def is_violating_slo(self, depart_time):
		# assert(depart_time >= _arrival_time)
		return (depart_time > self._ddl)

	def service_time(self):
		return self._service_time


class TaskQueue(object):
	_task_name = ""
	_packets_queue = []

	_arrival_rate = None
	_service_time = None
	_delay_slo = None

	_packets_counter = 0;
	_slo_violation_counter = 0
	_cpu_usage_counter = 0

	_last_arrival_time = 0

	def __init__(self, task_name):
		self._task_name = task_name
		self._packets_queue = []
		self._last_arrival_time = 0

	def is_empty(self):
		return (len(self._packets_queue) == 0)

	def set_arrival_rate(self, arrival_rate):
		self._arrival_rate = arrival_rate

	def set_service_time(self, service_time):
		self._service_time = service_time

	def set_delay_slo(self, delay_slo):
		self._delay_slo = delay_slo

	def enqueue_packet(self, task):
		self._packets_queue.append(task)
		self._last_arrival_time = task._arrival_time

	# This function picks a batch of packets from the task queue.
	def process_batch(self, current_time):
		batch = []
		while len(self._packets_queue) > 0 and len(batch) < DEFAULT_BATCH_SIZE:
			# The oldest packet has not 'arrived' yet.
			if self._packets_queue[0]._arrival_time > current_time:
				break

			batch.append(self._packets_queue.pop(0))

		batch_service_time = 0
		for packet in batch:
			batch_service_time += packet.service_time()

		return batch, batch_service_time

	def packets_counter(self):
		return self._packets_counter

	def slo_violation_counter(self):
		return self._slo_violation_counter

	def cpu_usage_counter(self):
		return self._cpu_usage_counter


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
		START_TIME = self._wall_clock_time - self._epoch_ns
		if START_TIME < 0:
			START_TIME = 0

		# Refills packets for all existing tasks.
		for task_name, task in self._schedulable_tasks.items():
			# assert(task._arrival_rate != None)
			# The start point of |task|.
			now = max(task._last_arrival_time, START_TIME)

			while now <= self._wall_clock_time + self._epoch_ns:
				random_time = next_arrival_period(pattern='exponential', arrival_rate=task._arrival_rate)
				now += random_time
				new = Task(now, \
					next_sevice_period(task._service_time), task._delay_slo)

				task.enqueue_packet(new)

	def has_packets_left(self):
		for task_name, task in self._schedulable_tasks.items():
			if not task.is_empty():
				return True
		return False

	# This is the core scheduling algorithm.
	# Dynamically reschedule all existing tasks according to their queue info
	# and the processing time.
	def on_scheduling(self):
		core = 0
		for task_name, task in self._schedulable_tasks.items():
			if not task.is_empty():
				self._scheduling_scheme[core] = [task]
				core += 1

	def post_scheduling(self):
		START_TIME = self._wall_clock_time

		for core, tasks in self._scheduling_scheme.items():
			now = START_TIME

			# Runs |tasks| on |core| until the end of this epoch.
			while now < self._wall_clock_time + self._epoch_ns:
				task = None
				batch, batch_time = None, 0
				for task in tasks:
					batch, batch_time = task.process_batch(now)
					# Picks the first one queue that has packets.
					if batch_time > 0:
						break

				# No packets available.
				if len(batch) == 0:
					break
				now += batch_time

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
	# 1s: 100000 tasks. Each service time < 10000 ns;
	task0.set_arrival_rate(10000)
	task0.set_service_time(500)
	task0.set_delay_slo(5000000)

	task1 = TaskQueue("ACL -> NAT")
	task1.set_arrival_rate(10000)
	task1.set_service_time(100)
	task1.set_delay_slo(5000000)

	task2 = TaskQueue("ACL -> UrlFilter")
	task2.set_arrival_rate(10000)
	task2.set_service_time(800)
	task2.set_delay_slo(5000000)

	sched.add_task(task0)
	sched.add_task(task1)
	sched.add_task(task2)

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
