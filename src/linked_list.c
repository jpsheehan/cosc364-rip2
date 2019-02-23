#include <stdlib.h>
#include "linked_list.h"

/**
 * Creates a new linked list with the first element having a specific value.
 */
LinkedList *linked_list_create(void *value)
{
  LinkedList *ll = malloc(sizeof(LinkedList));
  if (ll)
  {
    ll->value = value;
    ll->next = NULL;
  }
  return ll;
}

/**
 * Appends a new node with a specific value to the end of a linked list.
 * 
 * Returns a pointer to the appended node.
 */
LinkedList *linked_list_append(LinkedList *head, void *value)
{
  LinkedList *tail = linked_list_last(head);
  tail->next = linked_list_create(value);
  return tail->next;
}

/**
 * Gets the length of the list in O(n) time.
 */
size_t linked_list_length(LinkedList *head)
{
  if (!head)
  {
    return (size_t)0;
  }

  size_t length = 1;
  LinkedList *index = head;
  while (index->next)
  {
    index = index->next;
    length++;
  }
  return length;
}

/**
 * Frees the entire linked list from the head to the tail.
 * Note that this doesn't free the values inside each node.
 */
void linked_list_destroy(LinkedList *head)
{
  if (head)
  {
    LinkedList *this = head;
    LinkedList *next = this->next;
    while (this)
    {
      free(this);
      this = next;
      next = this->next;
    }
  }
}

/**
 * Returns a pointer to the last node in the linked list.
 */
LinkedList *linked_list_last(LinkedList *head)
{
  LinkedList *index = head;
  while (index->next != NULL)
  {
    index = index->next;
  }
  return index;
}