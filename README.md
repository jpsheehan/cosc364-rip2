# cosc364-rip2

A routing daemon based on the RIP-2 specification.

Written by Will Cowper (<wgc22@uclive.ac.nz>) and Jesse Sheehan (<jps111@uclive.ac.nz>).

## Building

All object files are compiled to the `./lib/` folder, and the program is compiled to `./bin/router`.

To build the program, run

```bash
make
```

To run the program, run

```bash
make run
```

To clean the build tree, run

```bash
make clean
```

## Modules

A module is just a single part of the overall program. It would be useful to break the assignment down into discrete problems that can be dealt with individually.

### Configuration

The configuration module deals with the loading of configuration data from disk, and validating the contents of the data. All functions in this module should begin with `config_`.

## Tasks - Setup

- [ ] Read in a configuration file and validate it
- [ ] For each input port in the config file, open a UDP socket binding to that port. NO sockets are created for outputs, these only refer to input ports of neighbors.

- [ ] Build the initial routing table from the config output ports

- [ ] Enter main loop.

## Tasks - Main Loop

- [ ] Print routing table to console

- [ ] Periodically send routing table to socket for each input port. If any first hops in the table match the neighbor then change the metric to be infinite(16). This implements split horizon with poison reverse.

- [ ] Periodically traverse routing table and update each age entry. If age is greater than timeout then set metric to infinite(16) and garbage flag to TRUE. If age is greater than 6*timeout AND garbage is TRUE then delete the entry.

- [ ] Read from socket. Update the routing table if a new destination or a known destination with better cost is recieved.

- [ ] Send triggered update only when routes become invald (i.e when router sets metric to 16)

### Configuration

- [x] Create a struct for the configuration. A `typedef` for the struct should also be created. Some thought should be put into how to represent the input and output ports (array or linked list?).
- [x] Create a struct to represent an output port. A `typedef` for the struct should also be created.
- [ ] Create functions for parsing the configuration file. These should be split up into smaller functions so they can be easily tested in isolation.
- [ ] Create a `config_load` function for reading the configuration from a file and returning a pointer to the configuration. If the configuration is invalid or could not be read, then this returns `NULL`.
- [ ] Create a `config_save` function for writing the configuration to the specified file descriptor (this will likely be `stdout` for testing).
- [ ] Create some configuration files for testing.
- [ ] Create some tests for the configuration file.
