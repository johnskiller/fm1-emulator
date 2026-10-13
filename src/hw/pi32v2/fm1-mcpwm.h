/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef HW_PI32V2_FM1_MCPWM_H
#define HW_PI32V2_FM1_MCPWM_H

#include "system/memory.h"
#include "cpu.h"

typedef struct FM1PocMcpwm {
    MemoryRegion mmio;
    uint32_t words[1024];
} FM1PocMcpwm;

/* Map the register file at 0x15000. */
void fm1_mcpwm_init(FM1PocMcpwm *mcpwm, Object *owner);

#endif
