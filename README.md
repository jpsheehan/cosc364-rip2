# cosc364-rip2

A routing daemon based on the RIP-2 specification. Read the [report](https://github.com/jpsheehan/cosc364-rip2/blob/master/doc/assignment.pdf).

Written by Will Cowper (<wgc22@uclive.ac.nz>) and Jesse Sheehan (<jps111@uclive.ac.nz>).

To run the program, execute

```bash
python3 src config_filename.conf
```

## Grade

Overall Grade: 96% / A+

Comments: Deductions to the ‘objective marks’ have been applied because the documentation
was good but not great on testing, and because in checking received packets you
forgot to test them for the metric values being larger than 16.


## Modules

A module is just a single part of the overall program. It would be useful to break the assignment down into discrete problems that can be dealt with individually.

### Configuration

The configuration module deals with the loading of configuration data from disk, and validating the contents of the data. All functions in this module should begin with `config_`.

## Tasks - Setup

- [X] Read in a configuration file and validate it
- [X] For each input port in the config file, open a UDP socket binding to that port. NO sockets are created for outputs, these only refer to input ports of neighbors.

- [X] Build the initial routing table from the config output ports

- [X] Enter main loop.

## Tasks - Main Loop

- [X] Print routing table to console

- [X] Periodically send routing table to socket for each input port. If any first hops in the table match the neighbor then change the metric to be infinite(16). This implements split horizon with poison reverse.

- [X] Periodically traverse routing table and update each age entry. If age is greater than timeout then set metric to infinite(16), reset the age and set garbage flag to TRUE. If garbage flag is TRUE and age > 6*timeout, delete the entry.

- [X] Read from sockets. Update the routing table if there is a new destination without infinite cost. For a known destination, if the table metric is greater than (packet metric + linkcost), reset age and update the table with new route. Reset the age of all entries in the table that were recieved but unchanged (i.e same dest,nexthop and cost). For routes with the same dest, nexthop and infinite cost, update cost to infinite (trigger update), reset age but set garbage flag to TRUE

- [X] Send triggered update only when routes become invald (i.e when router sets metric to 16). Triggered updates do not contain the entire routing table, only the routes that have had their metric set to 16.

- [X] Check incoming packets have a valid checksum and that the data is also legal in RIP => nexthop and destination routerID must be within the range of [1,64000] and not self routerID, cost non negative and clamps at 16.

### Configuration

- [X] Create some configuration files for testing.
- [X] Create some tests for the configuration file.
