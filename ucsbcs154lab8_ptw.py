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
#page_fault = pyrtl.WireVector(bitwidth=1, name="page_fault")
state = pyrtl.Register(bitwidth=2, name="state")
base_register = pyrtl.Const(0x3FFBFF, bitwidth=22)

#--------------------------------------
addr = pyrtl.Register(32, 'addr') 

offset1 = virtual_addr_i[22:32]  
offset2 = virtual_addr_i[12:22] 
offset3 = virtual_addr_i[0:12]   

read_data = main_memory[addr]

IDLE = pyrtl.Const(0b00, 2)   
L1D  = pyrtl.Const(0b01, 2)  
L2D  = pyrtl.Const(0b10, 2)  
DONE = pyrtl.Const(0b11, 2)  

with pyrtl.conditional_assignment:
    with reset_i:
        state.next |= IDLE
        addr.next  |= pyrtl.Const(0)

    with state == IDLE:
        with new_req_i:
            addr.next  |= pyrtl.concat(base_register, offset1)
            state.next |= L1D
        with ~new_req_i:
            addr.next  |= addr
            state.next |= IDLE

    with state == L1D:
        with ~read_data[31]:                      
            state.next |= DONE        
        with read_data[31]:
            next_l2_addr = pyrtl.concat(read_data[0:22], offset2)
            addr.next    |= next_l2_addr
            state.next   |= L2D

    with state == L2D:
        state.next |= DONE
        addr.next  |= addr

    with state == DONE:
        state.next |= IDLE
        addr.next  |= addr

paddr_part  = read_data[0:20]     
val_bit     = read_data[31]
wr_bit      = read_data[30]
rd_bit      = read_data[29]
dirty_bit   = read_data[28]
ref_bit     = read_data[27]


page_fault_logic = ~val_bit & (state != IDLE)
l2_phase  = (state == L2D) | (state == DONE) 
write_err = l2_phase & req_type_i    & ~wr_bit
read_err  = l2_phase & ~req_type_i   & ~rd_bit

err_code = pyrtl.concat(read_err, write_err, page_fault_logic)
error_code_o <<= pyrtl.select(reset_i, pyrtl.Const(0, 3), err_code)

phys_addr = pyrtl.concat(paddr_part, offset3)
valid_translate = (state == DONE) & (err_code == 0)

physical_addr_o <<= pyrtl.select(valid_translate, phys_addr, pyrtl.Const(0, 32))
dirty_o         <<= pyrtl.select(state == DONE, dirty_bit, pyrtl.Const(0))
valid_o         <<= pyrtl.select(state == DONE, val_bit,   pyrtl.Const(0))
ref_o           <<= pyrtl.select(state == DONE, ref_bit,   pyrtl.Const(0))
finished_walk_o <<= (state == DONE)

#-------------------------------------------------------------------

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
    assert (sim_trace.trace["readable_o"][-1] == 0x1)

