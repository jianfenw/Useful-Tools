
CC = g++

.PHONY : all clean
FLAGS = -pthread
FLAGS += -fpermissive

all : rr fifo

rr : rr.cc
	$(CC) -o rr rr.cc $(FLAGS)

fifo : fifo.cc
	$(CC) -o fifo fifo.cc $(FLAGS)

clean:
	@rm *.o
	@rm rt || true
	@rm fifo || true
