
import sys
from event_arrival import *

DEFAULT_BATCH_SIZE = 32

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
        """
        if depart_time > self._ddl:
            print "Y d=%d; arv=%d; ddl=%d;" %(depart_time, self._arrival_time, self._ddl)
        """

        return (depart_time > self._ddl)

    def service_time(self):
        return self._service_time


# |TaskQueue| is a packet queue associated with an NFV (sub)chain.
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

    def size(self):
        return len(self._packets_queue)

    def empty(self):
        return (len(self._packets_queue) == 0)

    def set_arrival_rate(self, arrival_rate):
        self._arrival_rate = arrival_rate

    def set_service_time(self, service_time):
        self._service_time = service_time

    def set_delay_slo(self, delay_slo):
        self._delay_slo = delay_slo

    def simulate_packet_arrivals(self, start, end):
        now = max(self._last_arrival_time, start)

        done = False
        while not done:
            now += next_arrival_period(pattern='exponential', pps=self._arrival_rate)
            new_packet = Task(now, \
                next_sevice_period(self._service_time), \
                self._delay_slo)
            self.enqueue_packet(new_packet)

            if now > end:
                done = True
                self._last_arrival_time = now

    def enqueue_packet(self, task):
        self._packets_queue.append(task)
        self._last_arrival_time = task._arrival_time

    def peek_earliest_deadline(self):
        if len(self._packets_queue) > 0:
            return self._packets_queue[0]._ddl

        return sys.maxint

    def peek_least_slack(self):
        if len(self._packets_queue) > 0:
            return self._packets_queue[0]._slack

        return sys.maxint

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


def test_taskqueue_process_batch():
    NUM_PACKETS = 65
    arrival_time = 0
    service_times = [100 for i in range(32)] + \
        [2000 for i in range(32)] + \
        [1000 for i in range(1)]
    delay_slo = 1000000
    assert(len(service_times) == NUM_PACKETS)

    taskq = TaskQueue("ACL")
    for i in range(NUM_PACKETS):
        new_packet = Task(arrival_time, service_times[i], delay_slo)
        taskq.enqueue_packet(new_packet)

    processing_batch_results = [(32, 3200), (32, 64000), (1, 1000)]
    batch_size_time = []
    while not taskq.empty():
        batch, batch_time = taskq.process_batch(arrival_time)
        batch_size_time.append((len(batch), batch_time))

    assert(batch_size_time == processing_batch_results)


def run_all_tests():
    test_taskqueue_process_batch()

    print "Pass all task/taskqueue tests."

if __name__ == '__main__':
    run_all_tests()
