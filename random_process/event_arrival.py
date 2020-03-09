
import math
import random

# Returns an inter-arrival time (ns) of a random process.
# |pps| is the packet arrival rate in pps.
# Pattern must be 'exponential' or 'uniform'
def next_arrival_period(pattern='exponential', pps=1.0):
    if pattern == 'exponential':
        return int(-math.log(1.0 - random.random()) * 10**9 / pps)
    if pattern == 'uniform':
        return int(1 * 10**9 / pps)

def next_sevice_period(avg_service_time=100):
    return int(avg_service_time)

# Generates a large number of packets to verify that the average
# arrival rate is accurate.
def test_packet_arrival(pps):
    if pps <= 0:
        return

    NUM_PACKETS = 100000

    curr_count, total_time = 0, 0
    while curr_count < NUM_PACKETS:
        total_time += next_arrival_period(pattern='exponential', pps=pps)
        curr_count += 1
    
    print "PPS = %d:" %(pps)
    print "It takes %d msec to generate 100000 packets" %(total_time / 10**6)


if __name__ == '__main__':
    test_packet_arrival(100)

    test_packet_arrival(1000)

    test_packet_arrival(10000)
