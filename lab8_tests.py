# lab8_tests.py  –  local self‑check for CS154 Lab 8
# --------------------------------------------------
import importlib, pyrtl
import ucsbcs154lab8_ptw as walker              # your RTL file

# ------------ helper: build a PTE -----------------
def pte(valid, wr, rd, dirty, ref, pfn22):
    """32‑bit PTE.  PFN occupies bits 0‑21 (22 bits)."""
    return (valid << 31) | (wr << 30) | (rd << 29) | \
           (dirty << 28) | (ref << 27) | (pfn22 & 0x3FFFFF)

# ------------ helper: run one walk ----------------
def run_walk(virt_addr, memimage, req_type):
    pyrtl.reset_working_block()      # fresh design each test
    importlib.reload(walker)

    sim_trace = pyrtl.SimulationTrace()
    sim = pyrtl.Simulation(tracer=sim_trace,
                           memory_value_map={walker.main_memory: memimage})

    for cyc in range(4):             # new_req high only on cycle 0
        sim.step({ walker.new_req_i      : 1 if cyc == 0 else 0,
                   walker.reset_i        : 0,
                   walker.virtual_addr_i : virt_addr,
                   walker.req_type_i     : req_type })

    done_cycle = next(i for i,v in
                      enumerate(sim_trace.trace['finished_walk_o']) if v == 1)

    return {k: sim_trace.trace[k][done_cycle] for k in
            ('physical_addr_o', 'error_code_o',
             'dirty_o', 'valid_o', 'ref_o')}

# ------------ constants derived from RTL ----------
VA        = 0xD0388DB3
index1    = (VA >> 22) & 0x3FF          # VA[31:22]
offset2   = (VA >> 12) & 0x3FF          # VA[21:12]

base_pfn  = walker.base_register.val    # 22‑bit PFN (0x3FFBFF)
L1_ADDR   = (base_pfn << 10) | index1   # walker’s first‑level access

L2_PFN    = 0x3FC35F                    # choose any 22‑bit PFN
L2_ADDR   = (L2_PFN << 10) | offset2    # walker’s second‑level access

# ------------ test‑suite --------------------------
TESTS = [
    ('clean‑read', {
        L1_ADDR: pte(1,1,1,0,0, L2_PFN),       # valid L1 entry
        L2_ADDR: pte(1,1,1,0,1, 0x061D26)      # valid final page (ref=1)
    }, 0, 0b000),

    ('page‑fault L1', {
        L1_ADDR: pte(0,1,1,0,0, L2_PFN)        # valid=0 ⇒ fault
    }, 0, 0b001),

    ('page‑fault L2', {
        L1_ADDR: pte(1,1,1,0,0, L2_PFN),
        L2_ADDR: pte(0,1,1,0,0, 0)             # valid=0 ⇒ fault
    }, 0, 0b001),

    ('write‑to‑RO page', {
        L1_ADDR: pte(1,1,1,0,0, L2_PFN),
        L2_ADDR: pte(1,0,1,0,1, 0x061D26)      # wr=0, rd=1
    }, 1, 0b010),

    ('read‑from‑NR page', {
        L1_ADDR: pte(1,1,1,0,0, L2_PFN),
        L2_ADDR: pte(1,1,0,0,1, 0x061D26)      # rd=0
    }, 0, 0b100),
]

# ------------ run with debug ----------------------
for name, memimg, rtype, exp_err in TESTS:
    out = run_walk(VA, memimg, rtype)

    # debug print if error code mismatches
    if out['error_code_o'] != exp_err:
        print(f'\nDEBUG  ({name})')
        print(f'  expected error_code_o : {exp_err:03b}')
        print(f'  got                  : {out["error_code_o"]:03b}')
        print(f'  L1_ADDR 0x{L1_ADDR:08X} = {memimg.get(L1_ADDR,0):08X}')
        print(f'  L2_ADDR 0x{L2_ADDR:08X} = {memimg.get(L2_ADDR,0):08X}')
        raise AssertionError(f'{name}: wrong error code')

    # original checks
    if exp_err == 0:
        assert out['physical_addr_o'] != 0, f'{name}: PA should be non‑zero'
    else:
        assert out['physical_addr_o'] == 0, f'{name}: PA should be zero on err'
    print(f'✓ {name} passed')

print('All local tests passed!')
