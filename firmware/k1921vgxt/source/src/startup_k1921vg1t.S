### Syntacore SCR* infra
###
### @copyright (C) Syntacore 2015-2020. All rights reserved.
### @author mn-sc
###
### @brief SCR* infra startup code

#include "arch.h"
#include "cache.h"
#include "ipi.h"
#include "memasm.h"
#include "common_asm.h"
#include "mpu.h"
#include "crt_common.h"

#define PLF_SMP_HART_NUM 2

##-----------------------------------------------------------------------------------------
## startup code

    .globl _start, main, exit, abort, trap_handler, trap_entry, _hart_halt, slave_hart_start, plf_init, app_init
    .weak exit, abort, trap_entry, trap_handler, app_init

    .option norvc

    .section ".startup.entry","ax",@progbits

##-----------------------------------------------------------------------------------------
## Entry point
_start:
    ## reset mstatus
    csrw  mstatus, zero
    zero_int_regs 1,31;

    ## setup gp
    load_addrword_abs gp, __global_pointer$

    ## setup MTVEC
    load_addrword_abs t0, trap_entry
    csrw  mtvec, t0

    ## setup MIE, MIP
    csrw  mie, zero
    csrw  mip, zero

    ## prepare disabling of caches: flush init sections
    load_addrword_pcrel t0, __TEXT_INIT_START__
    load_const_int32 t1, __TEXT_INIT_SIZE__
    cache_l1l2_flush t0, t1

    ## init FPU (if supported)
    csrr  a0, misa
    andi  a0, a0, (1 << ('F' - 'A')) | (1 << ('D' - 'A'))
    beqz  a0, 1f
    li    a0, (1 << 13) // mstatus.FS = 1 (initial)
    csrs  mstatus, a0
    csrw  fcsr, zero

    zero_f_regs 0, 31

    fsflags zero, zero  # reset fflags
    fsrm zero, zero     # reset RM
1:

    ## MPU setup
    MPU_DEFAULT_INIT;

    ## park/prep SMP slaves
    csrr  a0, mhartid
    bnez  a0, slave_hart_start

    ## init HART#0 sp, tp
    load_addrword_abs sp, __TLS0_BASE__
    mv    tp, sp
    csrw  mscratch, sp

    ## platform init
    load_addrword t0, plf_init
    jalr  t0

    ## application-specific initialization hook
    load_addrword t0, app_init
    jalr  t0

    ## main() args
    li    a0, 0
    li    a1, 0

    ## start main
    load_addrword t0, main
    load_addrword ra, exit
    jr    t0


##-----------------------------------------------------------------------------------------
trap_handler:
_hart_halt:
    ## disable interrupts
    csrci mstatus, 0xf
    csrw  mie, zero
1:  wfi
    j     1b

exit:
    nop

abort:
    j     _hart_halt


##-----------------------------------------------------------------------------------------
    .globl hart_start_table, slave_main
slave_hart_start:
    ## park unsupported harts
    li    a1, PLF_SMP_HART_NUM
    bgeu  a0, a1, _hart_halt

    ## init HART#1 sp, tp
    load_addrword_abs sp, __TLS0_BASE__
    slli  a0, a0, 12
    sub   sp, sp, a0
    mv    tp, sp
    csrw  mscratch, sp

    ## wait for master IPI cmd
1:
    csrrwi a1, SCR_CSR_IPI_MRDATA, 1
    bltz  a1, 1b

    ## start slave_main
    li    a0, 0
    li    a1, 0
    ##load_addrword t0, slave_main
    load_addrword t0, main
    load_addrword ra, exit
    jr    t0


##-----------------------------------------------------------------------------------------
## stubs
app_init:
    ret


##-----------------------------------------------------------------------------------------
### trap handler
    .section ".text.crt.trap_entry","ax",@progbits
    .align 6
    .type trap_entry, @function
trap_entry:
    ## save context
    context_save

    ## save mstatus priv stack
    csrr s0, mstatus

    ## load trap handler args
    csrr a0, mcause
    csrr a1, mepc
    mv   a2, sp

    ## setup gp
    load_addrword_abs gp, __global_pointer$

    ## call trap handler
    load_addrword t0, trap_handler
    jalr t0

    ## restore mstatus priv stack
    csrw mstatus, s0

    ## restore context
    context_restore
    mret
    .size trap_entry, .-trap_entry
