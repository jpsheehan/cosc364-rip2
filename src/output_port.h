#ifndef _H_OUTPUT_PORT
#define _H_OUTPUT_PORT

#include <stdio.h>
#include <stdint.h>

struct s_output_port
{
  uint16_t port_number;
  uint16_t link_cost;
  uint16_t router_id;
};

typedef struct s_output_port OutputPort;

OutputPort *output_port_create(uint16_t port_number,
                               uint16_t link_cost, uint16_t router_id);

void output_port_destroy(OutputPort *op);

void output_port_print(OutputPort *op, FILE *fd);

#endif
