#ifndef _H_CONFIG
#define _H_CONFIG

#include <stdint.h>
#include <stdio.h>

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
  uint16_t *input_ports;
  OutputPort *output_ports;
};

typedef struct s_config Config;

/**
 * Loads the configuration data from an open file.
 * Returns NULL if the configuration is invalid or could not be read.
 */
Config *config_load(FILE *fd);

/**
 * Saves the configuration to a file.
 */
void config_save(Config *config, FILE *fd);

#endif