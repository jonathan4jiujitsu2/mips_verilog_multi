// Testbench file: tb_MIPS32.v
`timescale 1ns / 1ps

module tb_MIPS32();
    // Inputs
    reg MAX10_CLK1_50;
    reg [0:0] KEY;
    
    // Instantiate the MIPS32_top module
    MIPS32_top uut (
        .MAX10_CLK1_50(MAX10_CLK1_50),
        .KEY(KEY)
    );
    
    // Clock generation
    initial begin
        MAX10_CLK1_50 = 0;
        forever #10 MAX10_CLK1_50 = ~MAX10_CLK1_50; // 50MHz clock (20ns period)
    end
    
    // Test sequence
    initial begin
        // Initialize and apply reset
        KEY[0] = 0; // Reset active low
        #50;
        KEY[0] = 1; // Release reset
        
        // Run for some cycles to observe behavior
        #2000;
        
        // End simulation
        $finish;
    end
    
    // Monitoring
    initial begin
        $monitor("Time: %t, Reset: %b, PC: %h, Instruction: %h", 
                 $time, KEY[0], uut.pc, uut.instr);
                 
        // Create VCD file for waveform viewing
        $dumpfile("mips32_sim.vcd");
        $dumpvars(0, tb_MIPS32);
    end
endmodule