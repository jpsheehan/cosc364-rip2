#include <stdio.h>
#include <unistd.h>

#include "main.h"

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
    if (access(argv[1], F_OK) == -1)
    {
      print_bad_filename(argv[1]);
      return EXIT_BAD_FILENAME;
    }
    else
    {
      printf("The configuration file is located at '%s'\n", argv[1]);
      return EXIT_OK;
    }
  }
}

/**
 * Prints the usage of this program.
 */
void print_bad_usage(char program_name[])
{
  printf("Usage: %s path/to/config/file.txt\n", program_name);
}

/**
 * Prints the error message when the user supplies a filename that doesn't exist.
 */
void print_bad_filename(char filename[])
{
  printf("Error! File does not exist: \"%s\"\n", filename);
}