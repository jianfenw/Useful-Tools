
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include <iostream>
#include <unistd.h>

uint64_t rdtsc() {
    unsigned int lo, hi;
    __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
    return ((uint64_t)hi << 32) | lo;
}


const int NUM_COUNTS = 50000000;

int main() {
    uint64_t start = rdtsc();
    int i = 0;
    uint64_t tmp;
    while (i < NUM_COUNTS) {
        tmp = rdtsc();
        ++i;
    }
    uint64_t end = rdtsc();

    std::cout << "RDTSC cycle cost = " 
        << (end-start) / NUM_COUNTS << " cycles;" << std::endl;
}
