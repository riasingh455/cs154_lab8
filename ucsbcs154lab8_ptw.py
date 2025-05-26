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

#add this 
readable_o = pyrtl.Output(bitwidth=1, name="readable_o")
# Step 1 : Split input into the three offsets

offset1 = virtual_addr_i[22:32]    
offset2 = virtual_addr_i[12:22]      
offset3 = virtual_addr_i[0:12] 
#splits up the virt add, first lev, sec lev, page off


# Step 2 : UPDATE STATE according to state diagram in instructions
#page_fault <<= pyrtl.Const(0)
#state = pyrtl.Register(bitwidth=2, name='state')

initial = pyrtl.Const(0b00, bitwidth=2)  
l1   = pyrtl.Const(0b01, bitwidth=2)   
l2   = pyrtl.Const(0b10, bitwidth=2)   
#diff states

with pyrtl.conditional_assignment:
    with reset_i:
        state.next |= initial                    
    with ~reset_i:
        with state == initial:
            with new_req_i:                  
                state.next |= l1
            with ~new_req_i:                 
                state.next |= initial
        with state == l1:
            with page_fault:
                state.next |= initial  
            with ~page_fault:
                state.next |= l2       
        with state == l2:
            state.next |= initial
#if inval go back to inital                

# Step 3 : Determine physical address by walking the page table structure



addr  = pyrtl.Register(32, name='addr') 
entr_reg = pyrtl.Register(32, name='entr_reg') 

read_data = main_memory[addr]          

with pyrtl.conditional_assignment:
    with reset_i:
        addr.next |= pyrtl.Const(0)
        entr_reg.next |= pyrtl.Const(0)
    with ~reset_i:
        with state == initial:
            addr.next |= pyrtl.select(new_req_i, pyrtl.concat(base_register, offset1), addr)                             
            entr_reg.next |= entr_reg            
        with state == l1:
            entr_reg.next |= read_data             
            next_l2_addr = pyrtl.concat(read_data[0:22], offset2)
            addr.next |= next_l2_addr
        with state == l2:
            entr_reg.next |= read_data          
            addr.next |= addr

# Step 4 : Determine the outputs based on the last level of the page table walk

paddr = read_data[0:20]   
val_bit = read_data[31]       
wr_bit = read_data[30]     


rd_bit = read_data[29]     
dirt = read_data[28]    
ref_bit = read_data[27]     

# page_fault_logic = (~val_bit) & (state != initial)
page_fault_logic = (~val_bit) & (state == l1) 
page_fault <<= page_fault_logic    

write_err = (state == l2) & req_type_i & (~wr_bit) 
read_err = (state == l2) & (~req_type_i) & (~rd_bit)


err_code = pyrtl.WireVector(3, name='err_code')
err_code <<= pyrtl.select(page_fault_logic, pyrtl.Const(0b001, 3), pyrtl.select(write_err,  pyrtl.Const(0b010, 3), pyrtl.select(read_err, pyrtl.Const(0b100, 3),pyrtl.Const(0b000, 3))))

err_code_reg = pyrtl.Register(3, name='err_code_reg')
with pyrtl.conditional_assignment:
    with new_req_i:
        err_code_reg.next |= pyrtl.Const(0)      
    with (state == l2) | page_fault_logic:      
        err_code_reg.next |= err_code
    with ~( (state == l2) | page_fault_logic | new_req_i ):
        err_code_reg.next |= err_code_reg  

error_code_o <<= err_code_reg  

phys_addr = pyrtl.concat(paddr, offset3)
dub = (state == l2) & (err_code == 0)      

physical_addr_o <<= pyrtl.select(dub, phys_addr, pyrtl.Const(0, 32))

dirty_o <<= pyrtl.select(state == l2, dirt, pyrtl.Const(0))
valid_o <<= pyrtl.select(state == l2, val_bit, pyrtl.Const(0))


ref_o <<= pyrtl.select(state == l2, ref_bit, pyrtl.Const(0))
readable_o <<= pyrtl.select(state == l2, rd_bit, pyrtl.Const(0))
finished_walk_o <<= (state == l2) | page_fault_logic




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
    for i in range(4):
        sim.step({
            new_req_i: 1 if i == 0 else 0,
            reset_i: 0,
            virtual_addr_i: 0xD0388DB3,
            req_type_i: 0
        })
    sim_trace.render_trace(symbol_len=20)
    assert (sim_trace.trace["physical_addr_o"][-2] == 0x61d26db3)
    assert (sim_trace.trace["error_code_o"][-2] == 0x0)
    assert (sim_trace.trace["dirty_o"][-2] == 0x0)
    assert (sim_trace.trace["readable_o"][-2] == 0x1)