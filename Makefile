CC = gcc
CFLAGS = -O -Wall -Wstrict-prototypes -Wextra -g
SRC = ./src
LIB = ./lib
BIN = ./bin

build: $(BIN)/router

run: $(BIN)/router
	$(BIN)/router

rebuild:
	make clean
	make build

clean:
	rm $(LIB)/*.o
	rm $(BIN)/router

$(BIN)/router: $(LIB)/main.o
	$(CC) $(CFLAGS) $^ -o $@

$(LIB)/main.o: $(SRC)/main.c
	$(CC) -c $(CFLAGS) $^ -o $@

