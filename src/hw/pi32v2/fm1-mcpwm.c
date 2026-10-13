/* SPDX-License-Identifier: GPL-2.0-or-later */
/* MCPWM timers and output channels (WL82 MCPWM1/3, at 0x15000). Melodee
 * drives its four matrix LED rows through MCPWM1/3 in independent H/L
 * mode: timer blocks at 0x15000+12*i and channel blocks at 0x15064+16*i
 * for i in {1, 3}, with the channel/timer enable word at 0x150e4, covers
 * the whole 0x15000 SFR page: 1.3.1 also sweeps every channel block with
 * a 32-word stride while disabling them. The register file is modeled;
 * the PWM waveform itself is not, because no modeled output consumes it
 * (the LED matrix is panel hardware). */
#include "qemu/osdep.h"
#include "fm1-mcpwm.h"
#include "fm1-sfr.h"

#define FM1_MCPWM_WORDS 1024

static uint64_t mcpwm_read(void *opaque, hwaddr offset, unsigned size)
{
    FM1PocMcpwm *p = opaque;
    return p->words[offset / 4];
}

static void mcpwm_write(void *opaque, hwaddr offset, uint64_t value,
                        unsigned size)
{
    FM1PocMcpwm *p = opaque;
    p->words[offset / 4] = value;
}

static const MemoryRegionOps mcpwm_ops = {
    .read = mcpwm_read, .write = mcpwm_write, .endianness = DEVICE_LITTLE_ENDIAN,
    .valid = {.min_access_size = 4, .max_access_size = 4},
    .impl = {.min_access_size = 4, .max_access_size = 4},
};

void fm1_mcpwm_init(FM1PocMcpwm *p, Object *owner)
{
    memory_region_init_io(&p->mmio, owner, &mcpwm_ops, p, "fm1.mcpwm",
                          FM1_MCPWM_WORDS * 4);
    fm1_sfr_map(0x15000, &p->mmio);
}
