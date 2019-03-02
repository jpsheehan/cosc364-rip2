#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "config.h"
#include "output_port.h"
#include "linked_list.h"

#define MIN_ID 1
#define MAX_ID 64000
#define MIN_PORT 1024
#define MAX_PORT 64000
#define BUFFER_START_SIZE 2

/**
 * Reads the output ports from the config and updates the struct.
 */
void process_output_ports(Config *config, char *str)
{
  // get the first token
  char *token = strtok(str, ",");

  while (token)
  {
    // extract the port number
    uint16_t port_number, link_cost, router_id;
    if (sscanf(token, "%hu-%hu-%hu", &port_number, &link_cost, &router_id) == 3)
    {
      OutputPort *output_port = output_port_create(port_number, link_cost, router_id);

      // create a new linked list (if this is the first input port)
      //  -or-
      // append this port to the existing linked list
      if (config->output_ports == NULL)
      {
        config->output_ports = linked_list_create(output_port);
      }
      else
      {
        linked_list_append(config->output_ports, output_port);
      }
    }

    // get the next token
    token = strtok(NULL, ",");
  }
}

/**
 * Reads the input ports from the config and updates the struct.
 */
void process_input_ports(Config *config, char *str)
{
  // get the first token
  char *token = strtok(str, ",");

  while (token)
  {
    // extract the port number
    uint16_t port;
    if (sscanf(token, "%hu", &port) == 1)
    {
      // create a new linked list (if this is the first input port)
      //  -or-
      // append this port to the existing linked list
      if (config->input_ports == NULL)
      {
        config->input_ports = linked_list_create((void *)(uintptr_t)port);
      }
      else
      {
        linked_list_append(config->input_ports, (void *)(uintptr_t)port);
      }
    }

    // get the next token
    token = strtok(NULL, ",");
  }
}

/**
 * Reads the router id from the config and updates the struct.
 */
void process_router_id(Config *config, char *str)
{
  sscanf(str, "%hu", &config->router_id);
}

/**
 * Modifies the configuration depending on what the contents of the line is.
 */
void process_line(Config *config, char *line)
{
  // each line in the configuration file is in the format:
  // <option> <value>
  //
  // so we compare the <option> to several expected options and perform a
  // specific task based on the <value>
  char *first_space_ptr = strchr(line, ' ');
  if (first_space_ptr)
  {
    size_t option_len = first_space_ptr - line;
    if (option_len)
    {
      char *value = first_space_ptr + 1;

      if (strncmp(line, "router-id", option_len) == 0)
      {
        process_router_id(config, value);
      }
      else if (strncmp(line, "input-ports", option_len) == 0)
      {
        process_input_ports(config, value);
      }
      else if (strncmp(line, "output-ports", option_len) == 0)
      {
        process_output_ports(config, value);
      }
    }
  }
}

/**
 * Loads the configuration data from an open file.
 * 
 * Returns NULL if the configuration is invalid or could not be read.
 */
Config *config_load(FILE *fd)
{
  Config *config = NULL;
  config = malloc(sizeof(Config));

  // the buffer will grow depending on how much data is read. It will attempt to read in the entire file at once.
  char *buffer = NULL;
  long buffer_size = BUFFER_START_SIZE;
  buffer = malloc(buffer_size);

  long file_length = -1;

  if (config && buffer)
  {

    // read the entire file into the buffer
    fread(buffer, 1, buffer_size, fd);
    while (!feof(fd))
    {
      // double the size of the buffer and reallocate the memory
      buffer_size *= 2;
      buffer = realloc(buffer, buffer_size);

      // read the next chunk
      fread(buffer + buffer_size / 2, 1, buffer_size / 2, fd);
    }

    // get the actual number of bytes read
    file_length = ftell(fd);

    // perhaps add an extra byte for the null terminator
    if (file_length == buffer_size)
    {
      buffer_size += 1;
      buffer = realloc(buffer, buffer_size);
    }

    // add the null terminator
    buffer[file_length] = '\0';

    // get the first line
    char *line = buffer;

    while ((line - buffer) < file_length)
    {
      char *eol = strchr(line, '\n');

      if (eol)
      {
        // remove the newline
        *eol = '\0';
      }
      else
      {
        eol = line + strlen(line);
      }

      // remove the (possible) carriage return
      char *cr = strchr(line, '\r');
      if (cr)
      {
        *cr = '\0';
      }

      process_line(config, line);

      // get the next line
      line = eol + 1;
    }

    free(buffer);

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
  if (config->input_ports)
  {
    index = config->input_ports;
    fprintf(fd, "input-ports ");
    fprintf(fd, "%lu", (uint64_t)index->value);
    while (index->next)
    {
      index = index->next;
      fprintf(fd, ", %lu", (uint64_t)index->value);
    }
    fprintf(fd, "%c", '\n');
  }

  // print the output-ports one at a time with a comma and a space in between
  if (config->output_ports)
  {
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
  }

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
  if (!config)
  {
    return false;
  }

  indexInput = config->input_ports;
  indexOutput = config->output_ports;

  // router_id must be a positive integer between 1 and 64000
  if (config->router_id < MIN_ID || config->router_id > MAX_ID)
  {
    return false;
  }

  // Check for a null list
  if (!indexInput || !indexOutput)
  {
    return false;
  }
  // Loop over the input_ports linked list
  while (indexInput)
  {
    if ((uintptr_t)indexInput->value < MIN_PORT || (uintptr_t)indexInput->value > MAX_PORT)
    {
      return false;
    }
    if (!is_unique(indexInput->next, (uintptr_t)indexInput->value))
    {
      return false;
    }
    indexInput = indexInput->next;
  }
  // Loop over the output_ports linked list
  while (indexOutput)
  {
    if ((uintptr_t)indexOutput->value < MIN_PORT || (uintptr_t)indexOutput->value > MAX_PORT)
    {
      return false;
    }
    if (!is_unique(indexOutput->next, (uintptr_t)indexOutput->value))
    {
      return false;
    }
    // Checking that outport port is not already in use by an input port
    if (!is_unique(config->input_ports, (uintptr_t)indexOutput->value))
    {
      return false;
    }
    indexOutput = indexOutput->next;
  }

  // timers (not implemented yet):
  // - these should have a ratio of 6

  // TODO: Implement timers

  return true;
}

/**
 * Returns true if a given integer is not contained in a linked list. 
 */
bool is_unique(LinkedList *ll, uint16_t num)
// We pass a pointer to the next element in the list from the port of interest and then check from there
// So we expect to find no occurances of the port num in the remainder of the linked list
{
  while (ll)
  {
    if ((uintptr_t)ll->value == num)
    {
      return false;
    }
    ll = ll->next;
  }
  return true;
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
