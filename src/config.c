#include <stdlib.h>
#include <stdio.h>

#include "config.h"
#include "output_port.h"

#define MIN_ID 1
#define MAX_ID 64000
#define MIN_PORT 1024
#define MAX_PORT 64000

/**
 * Loads the configuration data from an open file.
 * 
 * Returns NULL if the configuration is invalid or could not be read.
 */
Config *config_load(FILE *fd)
{
  Config *config = NULL;
  config = malloc(sizeof(Config));

  if (config)
  {
    // this is the hardcoded configuration from ./configs/one.conf:
    // router-id 1
    // input-ports 6110, 6201, 7345
    // output-ports 5000-1-1, 5002-5-4

    LinkedList *input_ports = linked_list_create((void *)6110);
    linked_list_append(input_ports, (void *)6201);
    linked_list_append(input_ports, (void *)7345);

    LinkedList *outport_ports = linked_list_create(output_port_create(5000, 1, 1));
    linked_list_append(outport_ports, output_port_create(5002, 5, 4));

    config->router_id = 1;
    config->input_ports = input_ports;
    config->output_ports = outport_ports;

    // TODO: Implement actual reading here

    if (!config_is_valid(config))
    {
      config_destroy(config);
      config = NULL;
    }
  }
  return config;
}

/**
 * Saves the configuration to a file.
 */
void config_save(Config *config, FILE *fd)
{
  LinkedList *index = NULL;

  // print the router-id
  fprintf(fd, "router-id %u\n", config->router_id);

  // print the input-ports one at a time with a comma and a space in between
  index = config->input_ports;
  fprintf(fd, "input-ports ");
  fprintf(fd, "%lu", (uint64_t)index->value);
  while (index->next)
  {
    index = index->next;
    fprintf(fd, ", %lu", (uint64_t)index->value);
  }
  fprintf(fd, "%c", '\n');

  // print the output-ports one at a time with a comma and a space in between
  index = config->output_ports;
  fprintf(fd, "output-ports ");
  output_port_print(index->value, fd);
  while (index->next)
  {
    index = index->next;
    fprintf(fd, "%s", ", ");
    output_port_print(index->value, fd);
  }
  fprintf(fd, "%c", '\n');

  fflush(fd);
}

/**
 * Returns true if the configuration is valid. The specification for a valid
 * configuration can be found in section 4.1 of the assignment spec.
 */
bool config_is_valid(Config *config)
{
  LinkedList *indexOutput = NULL;
  LinkedList *indexInput = NULL;
  // Checking for null pointer
  if (!config) {
    return false;
  }

  indexInput = config->input_ports;
  indexOutput = config->output_ports;
  // router_id must be a positive integer between 1 and 64000
  // TODO: should be unique?
  if (config->router_id < MIN_ID || config->router_id > MAX_ID) {
    return false;
  }

  // input_ports:
  // - a positive integer between 1024 and 64000 (inclusive)
  // - each port_number can occur only once in the list of input_ports

  // Check for a null list
  if (!indexInput || !indexOutput)
  {
    return false;
  }
  // Loop over the input_ports linked list
  // TODO: Check for duplicates
  while (indexInput)
  {
    if (indexInput->value < MIN_PORT || indexInput->value > MAX_PORT) 
    {
      return false;
    }
    indexInput = indexInput->next;
  }

  // Loop over the output_ports linked list
  // TODO: Check for duplicates and that output port is not shared with input

    while (indexOutput)
  {
    if (indexOutput->value < MIN_PORT || indexOutput->value > MAX_PORT) 
    {
      return false;
    }
    indexOutput = indexOutput->next;
  }

  // output_ports:
  //   port_number:
  //   - must satisfy the same conditions as the input_ports
  //   - none of the output port numbers should match the input_ports
  //   link_cost:
  //   - should conform to the conditions listed in the RIP RFC
  //   router_id:
  //   - should *probably* be unique amoungst all output_ports and the router_id
  //     of this configuration

  // timers (not implemented yet):
  // - these should have a ratio of 6

  // TODO: Implement timers

  return true;
}


/**
 * Returns true if a given integer only occurs once in a linked list. 
 */
void is_unique(Config *config, uint16_t num)
{
  // TODO: Implement
  //
}

/**
 * Frees the space used by the Config and its children.
 */
void config_destroy(Config *config)
{
  if (config)
  {

    // destroy the input ports
    linked_list_destroy(config->input_ports);

    if (config->output_ports)
    {
      // iterate through each output port and free it
      LinkedList *next = config->output_ports->next;
      output_port_destroy(config->output_ports->value);

      while (next)
      {
        LinkedList *this = next;
        next = this->next;
        output_port_destroy(this->value);
      }
    }
    // destroy the output ports
    linked_list_destroy(config->output_ports);

    // free the config struct
    free(config);
  }
}
