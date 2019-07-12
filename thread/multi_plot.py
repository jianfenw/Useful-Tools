import numpy as np
from math import sqrt
from matplotlib.path import Path
from joblib import Parallel, delayed
import time
import sys

## Check if one line segment contains another. 
def check_paths(path):
    #global a
    tmp = 0
    for i in range(10000):
        tmp = i*i*1
        for j in range(10000):
            tmp = sqrt(tmp+1)
    return tmp

if __name__ == '__main__':
    ## Create pairs of points for line segments
    a = zip(np.random.rand(5000,2),np.random.rand(5000,2))
    a = [Path(x) for x in a]

    b = zip(np.random.rand(300,2),np.random.rand(300,2))

    now = time.time()
    if len(sys.argv) >= 2:
        res = Parallel(n_jobs=int(sys.argv[1])) (delayed(check_paths) (Path(points)) for points in b)
    else:
        res = [check_paths(Path(points)) for points in b]
    print "Finished in", time.time()-now , "sec"