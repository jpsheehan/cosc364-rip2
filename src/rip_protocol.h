#ifndef _H_RIP_PROTOCOL
#define _H_RIP_PROTOCOL

#include <stdint.h>
#include <stdlib.h>

struct s_rip_header
{
  uint16_t router_id;
  uint32_t metric;
};

typedef struct s_rip_header RipHeader;

/**
 * Allocates a new RipHeader on the heap.
 */
RipHeader *rip_header_create(uint16_t router_id, uint32_t metric);

/**
 * Frees the memory associated with the RipHeader.
 */
void rip_header_destroy(RipHeader *rip_header);

#endif