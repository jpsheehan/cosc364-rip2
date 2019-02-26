#include <stdio.h>
#include <unistd.h>
#include <string.h>

#include "main.h"
#include "config.h"

/**
 * Checks the arguments passed in, loads the configuration and starts the servers.
 */
int main(int argc, char *argv[])
{
  if (argc != 2)
  {
    print_bad_usage(argv[0]);
    return EXIT_BAD_USAGE;
  }
  else
  {
    FILE *file = NULL;

    if (strcmp(argv[1], "--") == 0)
    {
      // read the configuration from stdin
      printf("%s", "Reading configuration from standard input... ");
      file = stdin;
    }
    else if (access(argv[1], F_OK) != -1)
    {
      // read the configuration from the file.
      printf("Reading configuration from '%s'... ", argv[1]);
      file = fopen(argv[1], "r");
    }
    else
    {
      // if the file doesn't exist
      print_bad_filename(argv[1]);
      return EXIT_BAD_FILENAME;
    }

    Config *config = config_load(file);
    fclose(file);
    printf("Done!\n");

    if (config != NULL)
    {
      config_save(config, stdout);
    }
    else
    {
      printf("An error occurred reading the configuration file.\n");
      return EXIT_BAD_CONFIGURATION;
    }

    return EXIT_OK;
  }
}

/**
 * Prints the usage of this program.
 */
void print_bad_usage(char program_name[])
{
  printf("Usage: %s [ -- | filename ]\n", program_name);
}

/**
 * Prints the error message when the user supplies a filename that doesn't exist.
 */
void print_bad_filename(char filename[])
{
  printf("Error! File does not exist: \"%s\"\n", filename);
}