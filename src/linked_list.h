#ifndef _H_LINKED_LIST
#define _H_LINKED_LIST

#include <stddef.h>

struct s_linked_list
{
  void *value;
  struct s_linked_list *next;
};

typedef struct s_linked_list LinkedList;

LinkedList *linked_list_create(void *value);

LinkedList *linked_list_append(LinkedList *head, void *value);

size_t linked_list_length(LinkedList *head);

void linked_list_destroy(LinkedList *head);

LinkedList *linked_list_last(LinkedList *head);

#endif
