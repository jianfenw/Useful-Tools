
import copy
import math
from event_arrival import *
from task_queue import Task, TaskQueue
from plotting import scatter_group_curve_plot


# All times are counted in ns.
SYSTEM_RUNTIME = 5000000000
SAMPLE_PERCENTILES = [0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]
SAMPLE_COLORS = ['b', 'r', 'g', 'm', 'c', 'y', 'grey']


class ExperimentalScheduler(object):
    _CPU_CORES = None

    # Task names to TaskQueue.
    _schedulable_tasks = {}

    # |_epoch_ns| is the minimal time granularity of rescheduling tasks.
    _epoch_ns = 10000000

    # The current scheduling scheme. Cores to groups of TaskQueues.
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
        self.on_scheduling_naive_packing()
        #self.on_scheduling_naive_dedicating()

    # Naive dedicating.
    def on_scheduling_naive_dedicating(self):
        self._scheduling_scheme = {}
        core = 0
        for task_name, task in self._schedulable_tasks.items():
            self._scheduling_scheme[core] = [task]
            core += 1

    # Naive packing.
    def on_scheduling_naive_packing(self):  
        self._scheduling_scheme = {0: []}
        for task_name, task in self._schedulable_tasks.items():
            self._scheduling_scheme[0].append(task)

    # Dynamic packing.
    def on_scheduling_dynamic_packing(self):
        pass


    # This includes the per-core task scheduling process and
    # the packet-level accounting process.
    def post_scheduling(self):
        self.post_scheduling_edf()
        #self.post_scheduling_greedy()

        self._cpu_usage_counter += len(self._scheduling_scheme)
        self._epoch_counter += 1
        self._wall_clock_time += self._epoch_ns

    def post_scheduling_greedy(self):
        for core, tasks in self._scheduling_scheme.items():
            # |now| is a per-core local time.
            now = self._wall_clock_time

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
                #print "Batch size = %d; Batch time = %d" %(len(batch), batch_time)

                for packet in batch:
                    if packet.is_violating_slo(now):
                        task._slo_violation_counter += 1
                task._packets_counter += len(batch)

    # Earliest Deadline First (EDF).
    def post_scheduling_edf(self):
        for core, tasks in self._scheduling_scheme.items():
            # |now| is a per-core local time.
            now = self._wall_clock_time

            while now < self._wall_clock_time + self._epoch_ns:
                selected_task = tasks[0]
                earliest_ddl = tasks[0].peek_earliest_deadline()

                for i, task in enumerate(tasks[1:]):
                    tmp = task.peek_earliest_deadline()
                    if tmp < earliest_ddl:
                        earliest_ddl = tmp
                        selected_task = task

                # Operates on |selected_task|.
                batch, batch_time = selected_task.process_batch(now)
                if len(batch) == 0:
                    now += 500
                    continue

                now += batch_time

                for packet in batch:
                    if packet.is_violating_slo(now):
                        selected_task._slo_violation_counter += 1

                selected_task._packets_counter += len(batch)

    # Least Slack First (LSF).
    def post_scheduling_lsf(self):
        pass


    # Generates the statistics report.
    def show_statistics_report(self):
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

    def show_delay_distributions(self):
        delay_distributions = []

        for task_name, task in self._schedulable_tasks.items():
            count_samples = len(task._packet_delays)
            print count_samples, task.packets_counter()
            if count_samples <= 10:
                continue

            task._packet_delays.sort()
            color = SAMPLE_COLORS[len(delay_distributions)]
            canonical_pcts = []
            for pct in SAMPLE_PERCENTILES:
                index = int(math.ceil(count_samples * pct))
                if index >= count_samples:
                    index = count_samples - 1
                #print pct, count_samples, index
                canonical_pcts.append(task._packet_delays[index] / 1000)

            print "Task_name=%s, color=%s" %(task_name, color)
            print canonical_pcts
            delay_distributions += [(copy.deepcopy(canonical_pcts), color)]

        figure_title = "Latency Distribution"
        x_label = 'Percentile'
        y_label = 'Latency (usec)'
        scatter_group_curve_plot(SAMPLE_PERCENTILES, delay_distributions, x_label, y_label, figure_title, False)


def main():
    sched = ExperimentalScheduler(16)

    task0 = TaskQueue("CHACHA")
    # 1s: 100000 tasks. Each service time < 1000 ns;
    task0.set_arrival_rate(50000)
    task0.set_service_time(20000)
    task0.set_delay_slo(5000000)

    task1 = TaskQueue("ACL -> NAT")
    task1.set_arrival_rate(10000)
    task1.set_service_time(5000)
    task1.set_delay_slo(1000000)

    task2 = TaskQueue("ACL -> UrlFilter")
    task2.set_arrival_rate(20000)
    task2.set_service_time(10000)
    task2.set_delay_slo(2000000)

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

    sched.show_statistics_report()
    sched.show_delay_distributions()


if __name__ == '__main__':
    main()
