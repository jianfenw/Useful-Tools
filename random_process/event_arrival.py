
import time
import math
import random

SEC_TO_NSEC = 1000000000

cache_index = 0
random_number_cache = [(1.0 - random.random()) for i in range(10000)]


# Returns an inter-arrival time (ns) of a random process.
# |pps| is the packet arrival rate in pps.
# Pattern must be 'exponential' or 'uniform'
def next_arrival_period(pattern='exponential', pps=1.0):
    if pattern == 'exponential':
        return int(-math.log(1.0 - random.random()) * 10**9 / pps)
    elif pattern == 'uniform':
        return int(1 * 10**9 / pps)

def next_sevice_period(avg_service_time=100):
    return int(avg_service_time)



# These are experiments on profiling randon() runtime.
def rand():
    return 1.0 - random.random()

def rand_exp():
    return -math.log(1.0 - random.random())

def rand_exp_time():
    return -math.log(1.0 - random.random()) * 10**9

def fake_rand():
    global cache_index
    global random_number_cache

    num = random_number_cache[cache_index]
    cache_index = 0 if cache_index == len(random_number_cache) - 1 else cache_index + 1
    return num

# Generates a large number of packets to verify that the average
# arrival rate is accurate.
def test_packet_arrival(pps):
    if pps <= 0:
        return

    NUM_PACKETS = 1000000

    curr_count, total_time = 0, 0
    while curr_count < NUM_PACKETS:
        total_time += next_arrival_period(pattern='exponential', pps=pps)
        curr_count += 1

    total_time_in_sec = total_time / 10**9
    expected_time = NUM_PACKETS / pps
    assert(0.7 * expected_time < total_time_in_sec < 1.3 * expected_time)

def run_arrival_tests():
    test_packet_arrival(100)
    test_packet_arrival(1000)
    test_packet_arrival(10000)

def run_profiling_number_generator():
    COUNT_RANDOM_NUMBERS = 10000000

    start = time.time()
    for i in range(COUNT_RANDOM_NUMBERS):
        next_arrival_period(pattern='exponential', pps=1000)
    end = time.time()
    print "Generating random numbers:", end-start

    start = time.time()
    for i in range(COUNT_RANDOM_NUMBERS):
        next_sevice_period(avg_service_time=1000)
    end = time.time()
    print "Generating fixed numbers:", end-start

    a = [1]
    start = time.time()
    for i in range(COUNT_RANDOM_NUMBERS):
        tmp = a[0]
    end = time.time()
    print "Referencing fixed numbers:", end-start

def run_profiling_rand():
    COUNT_RANDOM_NUMBERS = 10000000

    start = time.time()
    for i in range(COUNT_RANDOM_NUMBERS):
        tmp = rand()
    end = time.time()
    print "Rand:", end-start

    start = time.time()
    for i in range(COUNT_RANDOM_NUMBERS):
        tmp = rand_exp()
    end = time.time()
    print "Rand-Exp:", end-start

    start = time.time()
    for i in range(COUNT_RANDOM_NUMBERS):
        tmp = rand_exp_time()
    end = time.time()
    print "Rand-Exp-Time:", end-start

    start = time.time()
    for i in range(COUNT_RANDOM_NUMBERS):
        tmp = fake_rand()
    end = time.time()
    print "Fake Rand:", end-start


def run_all_tests():
    run_arrival_tests()
    print "Pass all task/taskqueue tests."


if __name__ == '__main__':
    run_all_tests()
    
    run_profiling_number_generator()
    # Results:
    # Generating random numbers: 4.39991092682
    # Generating fixed numbers: 1.69778513908
    # Referencing fixed numbers: 0.345868110657
    # Hence, we decide to reuse a large pool of random numbers.

    run_profiling_rand()
