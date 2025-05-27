import pyrtl
main_memory = pyrtl.MemBlock(bitwidth=32, addrwidth=32, name="main_mem")
virtual_addr_i = pyrtl.Input(bitwidth=32, name="virtual_addr_i")
new_req_i = pyrtl.Input(bitwidth=1, name="new_req_i")
reset_i = pyrtl.Input(bitwidth=1, name="reset_i")
req_type_i = pyrtl.Input(bitwidth=1, name="req_type_i")
physical_addr_o = pyrtl.Output(bitwidth=32,name="physical_addr_o")
dirty_o = pyrtl.Output(bitwidth=1, name="dirty_o")
valid_o = pyrtl.Output(bitwidth=1, name="valid_o")
ref_o = pyrtl.Output(bitwidth=1, name="ref_o")
error_code_o = pyrtl.Output(bitwidth=3, name="error_code_o")
finished_walk_o = pyrtl.Output(bitwidth=1, name="finished_walk_o")
page_fault = pyrtl.WireVector(bitwidth=1, name="page_fault")
state = pyrtl.Register(bitwidth=2, name="state")
base_register = pyrtl.Const(0x3FFBFF, bitwidth=22)

# Step 1 : Split input into the three offsets
# Step 2 : UPDATE STATE according to state diagram in instructions
# Step 3 : Determine physical address by walking the page table structure
# Step 4 : Determine the outputs based on the last level of the page table walk

if __name__ == "__main__":
    """
    These memory addresses correspond to the test that we walk through in the
    instructions
    This just does a basic walk from the first level to the last level where no
    errors should occur
    """
    memory = {
        4293918528: 0xC43FFC6B,
        4294029192: 0xAC061D26,
        1641180595: 0xDEADBEEF
    }
    sim_trace = pyrtl.SimulationTrace()
    sim = pyrtl.Simulation(tracer=sim_trace, memory_value_map={main_memory:
    memory})
    for i in range(3):
        sim.step({
            new_req_i: 1,
            reset_i: 0,
            virtual_addr_i: 0xD0388DB3,
            req_type_i: 0
    })
    sim_trace.render_trace(symbol_len=20)
    assert (sim_trace.trace["physical_addr_o"][-1] == 0x61d26db3)
    assert (sim_trace.trace["error_code_o"][-1] == 0x0)
    assert (sim_trace.trace["dirty_o"][-1] == 0x0)
    # assert (sim_trace.trace["readable_o"][-1] == 0x1)