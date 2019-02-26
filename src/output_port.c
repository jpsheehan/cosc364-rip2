#include <stdlib.h>

#include "output_port.h"

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