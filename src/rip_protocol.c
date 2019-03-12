#include "rip_protocol.h"

RipHeader *rip_header_create(uint16_t router_id, uint32_t metric)
{
  RipHeader *rip_header = NULL;
  rip_header = malloc(sizeof(RipHeader));

  if (rip_header)
  {
    rip_header->router_id = router_id;
    rip_header->metric = metric;
  }

  return rip_header;
}

void rip_header_destroy(RipHeader *rip_header)
{
  free(rip_header);
}
