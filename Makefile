CC = gcc
CFLAGS = -Wall -Wno-unknown-pragmas -Wstrict-prototypes -Wextra -g
SRC = ./src
LIB = ./lib
BIN = ./bin

build: $(BIN)/router

run: $(BIN)/router
	$(BIN)/router

rebuild:
	make cleang
	make build

clean:
	rm $(LIB)/*.o
	rm $(BIN)/router

debug: $(BIN)/router
	gdb --args $(BIN)/router ./configs/one.conf

$(BIN)/router: $(LIB)/main.o $(LIB)/config.o $(LIB)/linked_list.o $(LIB)/output_port.o
	$(CC) $(CFLAGS) $^ -o $@

$(LIB)/config.o: $(SRC)/config.c
	$(CC) -c $(CFLAGS) $^ -o $@

$(LIB)/linked_list.o: $(SRC)/linked_list.c
	$(CC) -c $(CFLAGS) $^ -o $@

$(LIB)/output_port.o: $(SRC)/output_port.c
	$(CC) -c $(CFLAGS) $^ -o $@

$(LIB)/main.o: $(SRC)/main.c
	$(CC) -c $(CFLAGS) $^ -o $@

