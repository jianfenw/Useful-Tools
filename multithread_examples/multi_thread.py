
import time
import sys
from joblib import parallel_backend, Parallel, delayed
from math import sqrt
import collections
from timeit import default_timer as timer


def compute_sqrt(i, j):
	for num in range(i, j+1):
		tmp_res = num*num*num
		for time in range(100):
			tmp_res = sqrt(tmp_res)+1
			tmp_res *= sqrt(tmp_res)
		res_dic[num] = tmp_res
	return

def compute_sqrt_cmp(i, j):
	local_dic = collections.defaultdict(int)
	for num in range(i, j+1):
		tmp_res = num*num*num
		for time in range(5000):
			tmp_res = sqrt(tmp_res)+1
			tmp_res *= sqrt(tmp_res)
		local_dic[num] = tmp_res
	return local_dic


if __name__ == '__main__':
	"""
	res_dic = collections.defaultdict(int)
	start = timer()
	compute_sqrt(0, 80000-1)
	end = timer()
	print "Single core result list len: %d, time: %d" %(len(res_dic), (end-start)*10**6)

	# 1. Multi-process: functions will be running in different processes.
	# We use shared memory to achieve inter-process communication.
	res_dic = collections.defaultdict(int)
	start = timer()
	Parallel(n_jobs=2, require='sharedmem')(
		delayed(compute_sqrt)(10000*i, 10000*(i+1)-1) for i in range(8))
	end = timer()
	# Print out the final result
	print "Multi-process result list len: %d" %(len(res_dic)), ", time: %d" %((end-start)*10**6)
	

	
	#2. Multi-thread in multi-core: functions will be running in different processes.
	#We use shared memory to achieve inter-process communication.
	res_dic = collections.defaultdict(int)
	start = timer()
	with parallel_backend('threading', n_jobs=2):
		res = Parallel(n_jobs=8)(delayed(compute_sqrt_cmp)(10000*i, 10000*(i+1)-1) for i in range(8))

	end = timer()
	# Print out the final result
	print "Multi-process result list len: %d" %(len(res_dic)), ", time: %d" %((end-start)*10**6)
	"""
	now = time.time()
	res = collections.defaultdict(int)
	"""
	res_cmp = collections.defaultdict(int)
	for i in range(10):
		res_cmp[i] = i+1
	res.update(res_cmp)
	print res
	"""
	res_dic_list = []
	if len(sys.argv) >= 2:
		res_dic_list = (Parallel(n_jobs=int(sys.argv[1])) (delayed(compute_sqrt_cmp)(10000*i, 10000*(i+1)-1) for i in range(8)))
	else:
		print "Error: please specify the number cores"
	print "Finished in", time.time()-now , "sec"
	for res_dic in res_dic_list:
		res.update(res_dic)
	print len(res)

