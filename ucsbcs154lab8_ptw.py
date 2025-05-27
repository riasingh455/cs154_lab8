# import pyrtl
# main_memory = pyrtl.MemBlock(bitwidth=32, addrwidth=32, name="main_mem")
# virtual_addr_i = pyrtl.Input(bitwidth=32, name="virtual_addr_i")
# new_req_i = pyrtl.Input(bitwidth=1, name="new_req_i")
# reset_i = pyrtl.Input(bitwidth=1, name="reset_i")
# req_type_i = pyrtl.Input(bitwidth=1, name="req_type_i")
# physical_addr_o = pyrtl.Output(bitwidth=32,name="physical_addr_o")
# dirty_o = pyrtl.Output(bitwidth=1, name="dirty_o")
# valid_o = pyrtl.Output(bitwidth=1, name="valid_o")
# ref_o = pyrtl.Output(bitwidth=1, name="ref_o")
# error_code_o = pyrtl.Output(bitwidth=3, name="error_code_o")
# finished_walk_o = pyrtl.Output(bitwidth=1, name="finished_walk_o")
# page_fault = pyrtl.WireVector(bitwidth=1, name="page_fault")
# state = pyrtl.Register(bitwidth=2, name="state")
# base_register = pyrtl.Const(0x3FFBFF, bitwidth=22)
# #------------------------------------------------------------
# addr = pyrtl.Register(32, 'addr')
# saved_req_type_i = pyrtl.Register(1, 'saved_req_type_i')

# offset1 = virtual_addr_i[22:32] 
# offset2 = virtual_addr_i[12:22] 
# offset3 = virtual_addr_i[0:12]  

# #step1 split into offsets

# read_data = main_memory[addr]

# IDLE = pyrtl.Const(0b00, 2)
# L1_READ = pyrtl.Const(0b01, 2)
# L2_READ = pyrtl.Const(0b10, 2)

# with pyrtl.conditional_assignment:
#     with reset_i:
#         state.next |= IDLE
#         addr.next |= pyrtl.Const(0, 32)
#         saved_req_type_i.next |= pyrtl.Const(0, 1)
#     with ~reset_i:
#         with state == IDLE:
#             with new_req_i:
#                 addr.next |= pyrtl.concat(base_register, offset1)
#                 state.next |= L1_READ
#                 saved_req_type_i.next |= req_type_i
#             with ~new_req_i:
#                 state.next |= IDLE
#                 addr.next |= addr
#                 saved_req_type_i.next |= saved_req_type_i
        
#         with state == L1_READ:
#             with read_data[31]:
#                 next_addr = pyrtl.concat(read_data[0:22], offset2)
#                 addr.next |= next_addr
#                 state.next |= L2_READ
#                 saved_req_type_i.next |= saved_req_type_i
#             with ~read_data[31]: 
#                 state.next |= IDLE
#                 addr.next |= addr #TODO double check why not 0?
#                 saved_req_type_i.next |= saved_req_type_i
        
#         with state == L2_READ:
#             #TODO page fault check needs to be here (check valid)
#             state.next |= IDLE
#             addr.next |= addr
#             saved_req_type_i.next |= saved_req_type_i

# valid_bit = read_data[31]
# writable_bit = read_data[28]
# readable_bit = read_data[27]
# dirty_bit = read_data[30]
# ref_bit = read_data[29]

# page_fault <<= ~valid_bit & (state != IDLE)

# write_not_writable = (state == L2_READ) & req_type_i & ~writable_bit & valid_bit
# read_not_readable = (state == L2_READ) & ~req_type_i & ~readable_bit & valid_bit

# error_code_bits = pyrtl.concat(read_not_readable, write_not_writable, page_fault)

# error_code_o <<= pyrtl.select(reset_i, pyrtl.Const(0, 3), error_code_bits)

# physical_page_number = read_data[0:20]  
# final_physical_addr = pyrtl.concat(physical_page_number, offset3)

# walk_success = (state == L2_READ) & (error_code_bits == 0)
# walk_finished = (state == L2_READ) | ((state == L1_READ) & ~valid_bit) | page_fault

# physical_addr_o <<= pyrtl.select(reset_i | ~walk_success, pyrtl.Const(0, 32), final_physical_addr)
# dirty_o <<= pyrtl.select(reset_i | ~walk_finished, pyrtl.Const(0, 1), dirty_bit)
# valid_o <<= pyrtl.select(reset_i | ~walk_finished, pyrtl.Const(0, 1), valid_bit)
# ref_o <<= pyrtl.select(reset_i | ~walk_finished, pyrtl.Const(0, 1), ref_bit)
# finished_walk_o <<= pyrtl.select(reset_i, pyrtl.Const(0, 1), walk_finished)

# #------------------------------------------------------------------------------------------

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
#     sim = pyrtl.Simulation(tracer=sim_trace, memory_value_map={main_memory:memory})
#     for i in range(3):
#         sim.step({
#             new_req_i: 1,
#             reset_i: 1,
#             virtual_addr_i: 0xD0388DB3,
#             req_type_i: 0
#     })
#     for i in range(3):
#         sim.step({
#             new_req_i: 1,
#             reset_i: 0,
#             virtual_addr_i: 0xD0388DB3,
#             req_type_i: 0
#         })
#     sim_trace.render_trace(symbol_len=20)
#     assert (sim_trace.trace["physical_addr_o"][-1] == 0x61d26db3)
#     assert (sim_trace.trace["error_code_o"][-1] == 0x0)
#     assert (sim_trace.trace["dirty_o"][-1] == 0x0)
#     # assert (sim_trace.trace["physical_addr_o"][-1] == 0x0)
#     # assert (sim_trace.trace["error_code_o"][-1] == 0x0)
#     # assert (sim_trace.trace["dirty_o"][-1] == 0x0)

#     print("Basic test passed!")














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
#------------------------------------------------------------
addr = pyrtl.Register(bitwidth=32, name="addr")
saved_req_type_i = pyrtl.Register(bitwidth=1,  name="saved_req_type_i")

offset1 = virtual_addr_i[22:32]  
offset2 = virtual_addr_i[12:22] 
offset3 = virtual_addr_i[ 0:12]  

read_data = main_memory[addr]

IDLE = pyrtl.Const(0b00, bitwidth=2)
L1_READ = pyrtl.Const(0b01, bitwidth=2)
L2_READ = pyrtl.Const(0b10, bitwidth=2)

with pyrtl.conditional_assignment:
    with reset_i:
        state.next |= IDLE
        addr.next |= pyrtl.Const(0, 32)
        saved_req_type_i.next |= pyrtl.Const(0, 1)
    with ~reset_i:
        with state == IDLE:
            with new_req_i:
                addr.next |= pyrtl.concat(base_register, offset1)
                state.next |= L1_READ
                saved_req_type_i.next |= req_type_i
            with ~new_req_i:
                addr.next |= addr
                state.next |= IDLE
                saved_req_type_i.next |= saved_req_type_i
        with state == L1_READ:
            with read_data[31]:  
                next_addr = pyrtl.concat(read_data[0:22], offset2)
                addr.next |= next_addr
                state.next |= L2_READ
                saved_req_type_i.next |= saved_req_type_i
            with ~read_data[31]:
                addr.next |= addr
                state.next |= IDLE
                saved_req_type_i.next |= saved_req_type_i
        with state == L2_READ:
            addr.next |= addr
            state.next |= IDLE
            saved_req_type_i.next |= saved_req_type_i

valid_bit = read_data[31]
writable_bit = read_data[28]
readable_bit = read_data[27]
dirty_bit = read_data[30]
ref_bit = read_data[29]

page_fault <<= (~valid_bit) & (state != IDLE)

read_fault = (state == L2_READ) & (~readable_bit)  & valid_bit
write_fault = (state == L2_READ) & ( saved_req_type_i) & (~writable_bit) & valid_bit

error_bits = pyrtl.concat(read_fault, write_fault, page_fault)
error_code_o <<= pyrtl.select(reset_i, pyrtl.Const(0, 3), error_bits)

ppn = read_data[0:20]
final_phys_addr  = pyrtl.concat(ppn, offset3)
walk_success = (state == L2_READ) & (error_bits == 0)
physical_addr_o <<= pyrtl.select(reset_i | ~walk_success, pyrtl.Const(0, 32),final_phys_addr)

walk_finished = walk_success | page_fault
valid_o <<= pyrtl.select(reset_i | ~walk_finished, pyrtl.Const(0,1), valid_bit)
dirty_o <<= pyrtl.select(reset_i | ~walk_finished, pyrtl.Const(0,1), dirty_bit)
ref_o <<= pyrtl.select(reset_i | ~walk_finished, pyrtl.Const(0,1), ref_bit)
finished_walk_o <<= pyrtl.select(reset_i, pyrtl.Const(0,1), walk_finished)


#------------------------------------------------------------------------------------------

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
    sim = pyrtl.Simulation(tracer=sim_trace, memory_value_map={main_memory:memory})
    for i in range(3):
        sim.step({
            new_req_i: 1,
            reset_i: 1,
            virtual_addr_i: 0xD0388DB3,
            req_type_i: 0
    })
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
    # assert (sim_trace.trace["physical_addr_o"][-1] == 0x0)
    # assert (sim_trace.trace["error_code_o"][-1] == 0x0)
    # assert (sim_trace.trace["dirty_o"][-1] == 0x0)

    print("Basic test passed!")
    #tetstt