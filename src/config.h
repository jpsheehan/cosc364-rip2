#ifndef _H_CONFIG
#define _H_CONFIG

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include "linked_list.h"

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

bool is_input_unique(LinkedList *ll, uint16_t num);

bool is_output_unique(LinkedList *ll, uint16_t num);

#endif