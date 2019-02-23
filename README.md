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

## Tasks

### Configuration

- [x] Create a struct for the configuration. A `typedef` for the struct should also be created. Some thought should be put into how to represent the input and output ports (array or linked list?).
- [x] Create a struct to represent an output port. A `typedef` for the struct should also be created.
- [ ] Create functions for parsing the configuration file. These should be split up into smaller functions so they can be easily tested in isolation.
- [ ] Create a `config_load` function for reading the configuration from a file and returning a pointer to the configuration. If the configuration is invalid or could not be read, then this returns `NULL`.
- [ ] Create a `config_save` function for writing the configuration to the specified file descriptor (this will likely be `stdout` for testing).
- [ ] Create some configuration files for testing.
- [ ] Create some tests for the configuration file.
