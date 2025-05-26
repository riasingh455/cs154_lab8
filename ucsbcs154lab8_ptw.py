# import pyrtl
# main_memory = pyrtl.MemBlock(bitwidth=32, addrwidth=32, name="main_mem")
# req_addr = pyrtl.Input(bitwidth=32, name="req_addr")
# req_new = pyrtl.Input(bitwidth=1, name="req_new")
# reset_i = pyrtl.Input(bitwidth=1, name="reset_i")
# req_type = pyrtl.Input(bitwidth=1, name="req_type")
# physical_addr_o = pyrtl.Output(bitwidth=32,name="physical_addr_o")
# dirty_o = pyrtl.Output(bitwidth=1, name="dirty_o")
# valid_o = pyrtl.Output(bitwidth=1, name="valid_o")
# ref_o = pyrtl.Output(bitwidth=1, name="ref_o")
# error_code_o = pyrtl.Output(bitwidth=3, name="error_code_o")
# finished_walk_o = pyrtl.Output(bitwidth=1, name="finished_walk_o")
# page_fault = pyrtl.WireVector(bitwidth=1, name="page_fault")
# state = pyrtl.Register(bitwidth=2, name="state")
# base_register = pyrtl.Const(0x3FFBFF, bitwidth=22)
# #----------------------------------------------------------
# addr = pyrtl.Register(32, 'addr')

# offset1 = req_addr[22:32]
# offset2 = req_addr[12:22]
# offset3 = req_addr[0:12]

# read_data = main_memory[addr]

# IDLE = pyrtl.Const(0b00, 2)
# L1_READ = pyrtl.Const(0b01, 2)
# L2_READ = pyrtl.Const(0b10, 2)

# with pyrtl.conditional_assignment:
#     with reset_i:
#         state.next |= IDLE
#         addr.next |= pyrtl.Const(0, 32)
#     with ~reset_i:
#         with state == IDLE:
#             with req_new:
#                 addr.next |= pyrtl.concat(base_register, offset1)
#                 state.next |= L1_READ
#             with ~req_new:
#                 state.next |= IDLE
#                 addr.next |= addr
        
#         with state == L1_READ:
#             with read_data[31]:
#                 next_addr = pyrtl.concat(read_data[0:22], offset2)
#                 addr.next |= next_addr
#                 state.next |= L2_READ
#             with ~read_data[31]:
#                 state.next |= IDLE
#                 addr.next |= addr
        
#         with state == L2_READ:
#             state.next |= IDLE
#             addr.next |= addr

# valid_bit = read_data[31]
# writable_bit = read_data[30]
# readable_bit = read_data[29]
# dirty_bit = read_data[28]
# ref_bit = read_data[27]

# page_fault <<= ~valid_bit & (state != IDLE)

# write_not_writable = (state == L2_READ) & req_type & ~writable_bit & valid_bit
# read_not_readable = (state == L2_READ) & ~req_type & ~readable_bit & valid_bit

# error_code_bits = pyrtl.concat(read_not_readable, write_not_writable, page_fault)

# error_code_o <<= pyrtl.select(reset_i, pyrtl.Const(0, 3), error_code_bits)

# physical_page_number = read_data[0:20]
# final_physical_addr = pyrtl.concat(physical_page_number, offset3)

# walk_success = (state == L2_READ) & (error_code_bits == 0)
# walk_finished = (state == L2_READ) | ((state == L1_READ) & ~valid_bit)
# in_l2_state = (state == L2_READ)

# physical_addr_o <<= pyrtl.select(reset_i | ~walk_success, pyrtl.Const(0, 32), final_physical_addr)
# dirty_o <<= pyrtl.select(reset_i | ~in_l2_state, pyrtl.Const(0, 1), dirty_bit)
# valid_o <<= pyrtl.select(reset_i | ~in_l2_state, pyrtl.Const(0, 1), valid_bit)
# ref_o <<= pyrtl.select(reset_i | ~in_l2_state, pyrtl.Const(0, 1), ref_bit)
# finished_walk_o <<= pyrtl.select(reset_i, pyrtl.Const(0, 1), walk_finished)

# # Step 1 : Split input into the three offsets
# # Step 2 : UPDATE STATE according to state diagram in instructions
# # Step 3 : Determine physical address by walking the page table structure
# # Step 4 : Determine the outputs based on the last level of the page table wal


# if __name__ == "__main__":
#     """
#     These memory addresses correspond to the test that we walk through in the
#     instructions
#     This just does a basic walk from the first level to the last level where no
#     errors should occur
#     """
#     memory = {
#         4293918528: 0xC43FFC6B,
#         4294029192: 0xAC061D26,
#         1641180595: 0xDEADBEEF
#     }
#     sim_trace = pyrtl.SimulationTrace()
#     sim = pyrtl.Simulation(tracer=sim_trace, memory_value_map={main_memory:
#     memory})
#     for i in range(3):
#         sim.step({
#             req_new: 1,
#             reset_i: 0,
#             req_addr: 0xD0388DB3,
#             req_type: 0
#     })
#     sim_trace.render_trace(symbol_len=20)
#     assert (sim_trace.trace["physical_addr_o"][-1] == 0x61d26db3)
#     assert (sim_trace.trace["error_code_o"][-1] == 0x0)
#     assert (sim_trace.trace["dirty_o"][-1] == 0x0)




# import pyrtl

# main_memory = pyrtl.MemBlock(bitwidth=32, addrwidth=32, name="main_mem")
# req_addr = pyrtl.Input(bitwidth=32, name="req_addr")
# req_new = pyrtl.Input(bitwidth=1, name="req_new")
# reset_i = pyrtl.Input(bitwidth=1, name="reset_i")
# req_type = pyrtl.Input(bitwidth=1, name="req_type")
# physical_addr_o = pyrtl.Output(bitwidth=32, name="physical_addr_o")
# dirty_o = pyrtl.Output(bitwidth=1, name="dirty_o")
# valid_o = pyrtl.Output(bitwidth=1, name="valid_o")
# ref_o = pyrtl.Output(bitwidth=1, name="ref_o")
# error_code_o = pyrtl.Output(bitwidth=3, name="error_code_o")
# finished_walk_o = pyrtl.Output(bitwidth=1, name="finished_walk_o")

# page_fault = pyrtl.WireVector(bitwidth=1, name="page_fault")
# state = pyrtl.Register(bitwidth=2, name="state")
# base_register = pyrtl.Const(0x3FFBFF, bitwidth=22)

# addr = pyrtl.Register(32, 'addr')
# saved_req_type = pyrtl.Register(1, 'saved_req_type')

# offset1 = req_addr[22:32] 
# offset2 = req_addr[12:22] 
# offset3 = req_addr[0:12]  

# read_data = main_memory[addr]

# IDLE = pyrtl.Const(0b00, 2)
# L1_READ = pyrtl.Const(0b01, 2)
# L2_READ = pyrtl.Const(0b10, 2)

# with pyrtl.conditional_assignment:
#     with reset_i:
#         state.next |= IDLE
#         addr.next |= pyrtl.Const(0, 32)
#         saved_req_type.next |= pyrtl.Const(0, 1)
#     with ~reset_i:
#         with state == IDLE:
#             with req_new:
#                 addr.next |= pyrtl.concat(base_register, offset1)
#                 state.next |= L1_READ
#                 saved_req_type.next |= req_type
#             with ~req_new:
#                 state.next |= IDLE
#                 addr.next |= addr
#                 saved_req_type.next |= saved_req_type
        
#         with state == L1_READ:
#             with read_data[31]: 
#                 next_addr = pyrtl.concat(read_data[0:22], offset2)
#                 addr.next |= next_addr
#                 state.next |= L2_READ
#                 saved_req_type.next |= saved_req_type
#             with ~read_data[31]: 
#                 state.next |= IDLE
#                 addr.next |= addr
#                 saved_req_type.next |= saved_req_type
        
#         with state == L2_READ:
#             state.next |= IDLE
#             addr.next |= addr
#             saved_req_type.next |= saved_req_type

# valid_bit = read_data[31]
# writable_bit = read_data[30]
# readable_bit = read_data[29]
# dirty_bit = read_data[28]
# ref_bit = read_data[27]

# page_fault <<= ~valid_bit & (state != IDLE)

# write_not_writable = (state == L2_READ) & saved_req_type & ~writable_bit & valid_bit
# read_not_readable = (state == L2_READ) & ~saved_req_type & ~readable_bit & valid_bit

# error_code_bits = pyrtl.concat(read_not_readable, write_not_writable, page_fault)

# error_code_o <<= pyrtl.select(reset_i, pyrtl.Const(0, 3), error_code_bits)

# physical_page_number = read_data[0:20]  
# final_physical_addr = pyrtl.concat(physical_page_number, offset3)

# walk_success = (state == L2_READ) & (error_code_bits == 0)
# walk_finished = (state == L2_READ) | ((state == L1_READ) & ~valid_bit)

# physical_addr_o <<= pyrtl.select(reset_i | ~walk_success, pyrtl.Const(0, 32), final_physical_addr)
# dirty_o <<= pyrtl.select(reset_i | ~walk_finished, pyrtl.Const(0, 1), dirty_bit)
# valid_o <<= pyrtl.select(reset_i | ~walk_finished, pyrtl.Const(0, 1), valid_bit)
# ref_o <<= pyrtl.select(reset_i | ~walk_finished, pyrtl.Const(0, 1), ref_bit)
# finished_walk_o <<= pyrtl.select(reset_i, pyrtl.Const(0, 1), walk_finished)

# if __name__ == "__main__":
#     """
#     These memory addresses correspond to the test that we walk through in the
#     instructions
#     This just does a basic walk from the first level to the last level where no
#     errors should occur
#     """
#     memory = {
#         4293918528: 0xC43FFC6B, 
#         4294029192: 0xAC061D26,  
#         1641180595: 0xDEADBEEF 
#     }
#     sim_trace = pyrtl.SimulationTrace()
#     sim = pyrtl.Simulation(tracer=sim_trace, memory_value_map={main_memory: memory})

#     for i in range(4):  
#         sim.step({
#             req_new: 1 if i == 0 else 0, 
#             reset_i: 0,
#             req_addr: 0xD0388DB3,
#             req_type: 0
#         })
    
#     sim_trace.render_trace(symbol_len=20)
 
#     assert (sim_trace.trace["physical_addr_o"][2] == 0x61d26db3)
#     assert (sim_trace.trace["error_code_o"][2] == 0x0)
#     assert (sim_trace.trace["dirty_o"][2] == 0x0)
#     assert (sim_trace.trace["finished_walk_o"][2] == 0x1)
    
#     print("Basic test passed!")




















import pyrtl

main_memory = pyrtl.MemBlock(bitwidth=32, addrwidth=32, name="main_mem", asynchronous=True)
req_addr = pyrtl.Input(bitwidth=32, name="req_addr")
req_new = pyrtl.Input(bitwidth=1, name="req_new")
reset_i = pyrtl.Input(bitwidth=1, name="reset_i")
req_type = pyrtl.Input(bitwidth=1, name="req_type")
physical_addr_o = pyrtl.Output(bitwidth=32, name="physical_addr_o")
dirty_o = pyrtl.Output(bitwidth=1, name="dirty_o")
valid_o = pyrtl.Output(bitwidth=1, name="valid_o")
ref_o = pyrtl.Output(bitwidth=1, name="ref_o")
error_code_o = pyrtl.Output(bitwidth=3, name="error_code_o")
finished_walk_o = pyrtl.Output(bitwidth=1, name="finished_walk_o")

page_fault = pyrtl.WireVector(bitwidth=1, name="page_fault")
state = pyrtl.Register(bitwidth=2, name="state")
base_register = pyrtl.Const(0x3FFBFF, bitwidth=22)

addr = pyrtl.Register(32, 'addr')
saved_req_type = pyrtl.Register(1, 'saved_req_type')

offset1 = req_addr[22:32] 
offset2 = req_addr[12:22] 
offset3 = req_addr[0:12]  

read_data = main_memory[addr]

IDLE = pyrtl.Const(0b00, 2)
L1_READ = pyrtl.Const(0b01, 2)
L2_READ = pyrtl.Const(0b10, 2)

with pyrtl.conditional_assignment:
    with reset_i:
        state.next |= IDLE
        addr.next |= pyrtl.Const(0, 32)
        saved_req_type.next |= pyrtl.Const(0, 1)
    with ~reset_i:
        with state == IDLE:
            with req_new:
                addr.next |= pyrtl.concat(base_register, offset1)
                state.next |= L1_READ
                saved_req_type.next |= req_type
            with ~req_new:
                state.next |= IDLE
                addr.next |= addr
                saved_req_type.next |= saved_req_type
        
        with state == L1_READ:
            with read_data[31]: 
                next_addr = pyrtl.concat(read_data[0:22], offset2)
                addr.next |= next_addr
                state.next |= L2_READ
                saved_req_type.next |= saved_req_type
            with ~read_data[31]: 
                state.next |= IDLE
                addr.next |= addr
                saved_req_type.next |= saved_req_type
        
        with state == L2_READ:
            state.next |= IDLE
            addr.next |= addr
            saved_req_type.next |= saved_req_type

valid_bit = read_data[31]
writable_bit = read_data[30]
readable_bit = read_data[29]
dirty_bit = read_data[28]
ref_bit = read_data[27]

page_fault <<= ~valid_bit & (state != IDLE)

write_not_writable = (state == L2_READ) & saved_req_type & ~writable_bit & valid_bit
read_not_readable = (state == L2_READ) & ~saved_req_type & ~readable_bit & valid_bit

error_code_bits = pyrtl.concat(read_not_readable, write_not_writable, page_fault)

error_code_o <<= pyrtl.select(reset_i, pyrtl.Const(0, 3), error_code_bits)

physical_page_number = read_data[0:20]  
final_physical_addr = pyrtl.concat(physical_page_number, offset3)

walk_success = (state == L2_READ) & (error_code_bits == 0)
walk_finished = (state == L2_READ) | ((state == L1_READ) & ~valid_bit)

physical_addr_o <<= pyrtl.select(reset_i | ~walk_success, pyrtl.Const(0, 32), final_physical_addr)
dirty_o <<= pyrtl.select(reset_i | ~walk_finished, pyrtl.Const(0, 1), dirty_bit)
valid_o <<= pyrtl.select(reset_i | ~walk_finished, pyrtl.Const(0, 1), valid_bit)
ref_o <<= pyrtl.select(reset_i | ~walk_finished, pyrtl.Const(0, 1), ref_bit)
finished_walk_o <<= pyrtl.select(reset_i, pyrtl.Const(0, 1), walk_finished)

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
    sim = pyrtl.Simulation(tracer=sim_trace, memory_value_map={main_memory: memory})

    for i in range(4):  
        sim.step({
            req_new: 1 if i == 0 else 0, 
            reset_i: 0,
            req_addr: 0xD0388DB3,
            req_type: 0
        })
    
    sim_trace.render_trace(symbol_len=20)
 
    assert (sim_trace.trace["physical_addr_o"][2] == 0x61d26db3)
    assert (sim_trace.trace["error_code_o"][2] == 0x0)
    assert (sim_trace.trace["dirty_o"][2] == 0x0)
    assert (sim_trace.trace["finished_walk_o"][2] == 0x1)
    
    print("Basic test passed!")