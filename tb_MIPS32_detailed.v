`timescale 1ns / 1ps

module tb_MIPS32_detailed();
    // Inputs
    reg MAX10_CLK1_50;
    reg [0:0] KEY;
    
    // Internal signals for monitoring
    wire [31:0] pc, instr, alu_result, reg_data1, reg_data2;
    wire [5:0] op, func;
    wire [4:0] rs, rt, rd;
    
    // Instantiate the MIPS32_top module
    MIPS32_top uut (
        .MAX10_CLK1_50(MAX10_CLK1_50),
        .KEY(KEY)
    );
    
    // Connect internal signals for monitoring
    assign pc = uut.pc;
    assign instr = uut.instr;
    assign alu_result = uut.alu_result;
    assign reg_data1 = uut.reg_data1;
    assign reg_data2 = uut.reg_data2;
    assign op = uut.op;
    assign func = uut.func;
    assign rs = uut.rs;
    assign rt = uut.rt;
    assign rd = uut.rd;
    
    // Clock generation
    initial begin
        MAX10_CLK1_50 = 0;
        forever #10 MAX10_CLK1_50 = ~MAX10_CLK1_50; // 50MHz clock (20ns period)
    end
    
    // Test sequence
    initial begin
        // Initialize and apply reset
        KEY[0] = 0; // Reset active low
        #100;
        KEY[0] = 1; // Release reset
        
        // Run for a series of instructions
        // Execute enough cycles to see several instructions
        #5000;
        
        // End simulation
        $finish;
    end
    
    // Monitoring - print state of processor at each instruction
    always @(posedge uut.clk) begin
        if (KEY[0] && uut.U22.state == 4'd0) begin // Only print in fetch state
            $display("=====================================");
            $display("Time: %t, PC: %h", $time, pc);
            $display("Instruction: %h (op: %h, rs: %d, rt: %d, rd: %d, func: %h)", 
                     instr, op, rs, rt, rd, func);
            $display("RegData1: %h, RegData2: %h", reg_data1, reg_data2);
            $display("ALU Result: %h", alu_result);
            $display("Control State: %d", uut.U22.state);
            
            // Register file values
            $display("Register values:");
            $display("R1: %h, R2: %h, R3: %h, R4: %h", 
                     uut.U5.registers[1], uut.U5.registers[2], 
                     uut.U5.registers[3], uut.U5.registers[4]);
                     
            // Memory contents - just a few for demonstration
            $display("Memory values (first few addresses):");
            $display("RAM[0]: %h, RAM[1]: %h", uut.U19.mem[0], uut.U19.mem[1]);
        end
    end
    
    // Create VCD file for waveform viewing
    initial begin
        $dumpfile("mips32_detailed_sim.vcd");
        $dumpvars(0, tb_MIPS32_detailed);
    end
endmodule