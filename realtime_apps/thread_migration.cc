
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <sched.h>
#include <unistd.h>


int main(int argc, char *argv[]) {
    struct sched_param low_prio_param;
    struct sched_param high_prio_param;
    // param.sched_priority = sched_get_priority_max(SCHED_FIFO);
    high_prio_param.sched_priority = 41;
    low_prio_param.sched_priority = 40;

    int pid = atoi(argv[1]);

    sched_setscheduler(0, SCHED_FIFO, &high_prio_param);

    cpu_set_t master_core, sched_core_1, sched_core_2;
    CPU_ZERO(&master_core);
    CPU_SET(5, &master_core);

    CPU_ZERO(&sched_core_1);
    CPU_SET(6, &sched_core_1);

    CPU_ZERO(&sched_core_2);
    CPU_SET(7, &sched_core_2);

    if(sched_setaffinity(0, sizeof(cpu_set_t), &master_core) == -1) {
        exit(EXIT_FAILURE);
    }
    if(sched_setaffinity(pid, sizeof(cpu_set_t), &sched_core_1) == -1) {
        exit(EXIT_FAILURE);
    }

    sched_setscheduler(pid, SCHED_FIFO, &high_prio_param);

    int cmd = 0;
    while (1) {
        if (cmd == 0) {
            if (sched_setaffinity(pid, sizeof(cpu_set_t), &sched_core_1) == -1) {
                exit(EXIT_FAILURE);
            }
        } else {
            if(sched_setaffinity(pid, sizeof(cpu_set_t), &sched_core_2) == -1) {
                exit(EXIT_FAILURE);
            }
        }

        cmd = 1 - cmd;

        usleep(10000);
        yield();
    }

    return 0;
}
