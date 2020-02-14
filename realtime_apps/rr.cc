#include <iostream>
#include <pthread.h>

#define NUM_THREADS     5

void* echo_func() {
	pthread_t this_t = pthread_self();
	struct sched_param params;
	params.sched_priority = sched_get_priority_max(SCHED_RR);
	pthread_setschedparam(this_t, SCHED_RR, &params);

	long tid = (long)this_t;

	std::cout << "Hello from thread[" << tid << "]" << std::endl;

	while (1) {
	}

	pthread_exit(NULL);
}

int main(int argc, char *argv[]) {
	pthread_t threads[NUM_THREADS];

	int i;
	for (i = 0; i < NUM_THREADS; ++i) {
		int ret = pthread_create(&(threads[i]), NULL, &echo_func, NULL);
		if (ret) {
			std::cout << "Error: failed to call pthread_create" << std::endl;
			exit(-1);
		}
	}
	pthread_exit(NULL);
}
