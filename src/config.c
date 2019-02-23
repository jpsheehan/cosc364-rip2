#include <stdlib.h>
#include <stdio.h>
#include "config.h"

#pragma region OutputPort

/**
 * Creates a new OutputPort struct on the heap.
 * 
 * Returns NULL if this fails.
 */
OutputPort *output_port_create(uint16_t port_number,
                               uint16_t link_cost, uint16_t router_id)
{
  OutputPort *op = malloc(sizeof(OutputPort));
  if (op != NULL)
  {
    op->port_number = port_number;
    op->link_cost = link_cost;
    op->router_id = router_id;
  }
  return op;
}

/**
 * Frees an OutputPort.
 */
void output_port_destroy(OutputPort *op)
{
  free(op);
}

/**
 * Converts an OutputPort to a string.
 * 
 * The resulting string is stored in the
 * second argument. This character array should be at least 18 characters long
 * to account for the longest possible string ("65536-65535-65535\0").
 * 
 * Returns the number of characters written.
 */
void output_port_print(OutputPort *op, FILE *fd)
{
  fprintf(fd, "%u-%u-%u", op->port_number, op->link_cost, op->router_id);
}

#pragma endregion

#pragma region Config

/**
 * Loads the configuration data from an open file.
 * 
 * Returns NULL if the configuration is invalid or could not be read.
 */
Config *config_load(FILE *fd)
{
  Config *config = malloc(sizeof(Config));
  if (config)
  {
    config->router_id = 1;
    config->input_ports = linked_list_create((void *)2000);
    config->output_ports = linked_list_create(output_port_create(3000, 1, 2));
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

#pragma endregion