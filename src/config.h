#ifndef _H_CONFIG
#define _H_CONFIG

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include "linked_list.h"

struct s_output_port
{
  uint16_t port_number;
  uint16_t link_cost;
  uint16_t router_id;
};

typedef struct s_output_port OutputPort;

struct s_config
{
  uint16_t router_id;
  LinkedList *input_ports;
  LinkedList *output_ports;
};

typedef struct s_config Config;

Config *config_load(FILE *fd);

void config_save(Config *config, FILE *fd);

bool config_is_valid(Config *config);

void config_destroy(Config *config);

#endif