#ifndef _H_MAIN
#define _H_MAIN

#define EXIT_OK 0
#define EXIT_BAD_USAGE 1
#define EXIT_BAD_FILENAME 2

void print_bad_usage(char program_name[]);
void print_bad_filename(char filename[]);
int main(int argc, char *argv[]);

#endif
