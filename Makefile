CC = gcc
CFLAGS = -Wall -Wno-unknown-pragmas -Wstrict-prototypes -Wextra -g
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

$(BIN)/router: $(LIB)/main.o $(LIB)/config.o
	$(CC) $(CFLAGS) $^ -o $@

$(LIB)/config.o: $(SRC)/config.c
	$(CC) -c $(CFLAGS) $^ -o $@

$(LIB)/main.o: $(SRC)/main.c
	$(CC) -c $(CFLAGS) $^ -o $@

