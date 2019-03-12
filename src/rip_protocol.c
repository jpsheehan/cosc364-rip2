#include "rip_protocol.h"

RipEntry *rip_entry_create(uint16_t router_id, uint32_t metric)
{
  RipEntry *rip_entry = NULL;
  rip_entry = malloc(sizeof(RipEntry));

  if (rip_entry)
  {
    rip_entry->router_id = router_id;
    rip_entry->metric = metric;
  }

  return rip_entry;
}

void rip_entry_destroy(RipEntry *rip_entry)
{
  free(rip_entry);
}
