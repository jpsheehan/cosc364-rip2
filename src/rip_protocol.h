#ifndef _H_RIP_PROTOCOL
#define _H_RIP_PROTOCOL

#include <stdint.h>
#include <stdlib.h>

struct s_rip_entry
{
  uint16_t router_id;
  uint32_t metric;
};

typedef struct s_rip_entry RipEntry;

/**
 * Allocates a new RipEntry on the heap.
 */
RipEntry *rip_entry_create(uint16_t router_id, uint32_t metric);

/**
 * Frees the memory associated with the RipEntry.
 */
void rip_entry_destroy(RipEntry *rip_entry);

#endif