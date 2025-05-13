// File: PLL.v
`timescale 1ns / 1ps

// Phase-Locked Loop module for clock generation
// This module is specific to the Intel MAX10 FPGA
module PLL (
    input  inclk0,   // Input clock (50MHz)
    output c0        // Output clock (10kHz)
);
    // Intel FPGA IP component for PLL
    // This is a placeholder for the actual Intel FPGA IP 
    // You would generate this file using Intel Quartus Prime's IP Catalog
    
    // Frequency ratio: 50MHz / 5000 = 10kHz
    reg [12:0] counter;
    reg c0_reg;
    
    assign c0 = c0_reg;
    
    initial begin
        counter = 0;
        c0_reg = 0;
    end
    
    always @(posedge inclk0) begin
        if (counter >= 2499) begin  // 5000 cycles total for full period (2500 high, 2500 low)
            counter <= 0;
            c0_reg <= ~c0_reg;      // Toggle output
        end
        else begin
            counter <= counter + 1;
        end
    end
    
    // For actual implementation, you would use the following code
    // and generate the PLL IP core using the Intel Quartus IP Catalog:
    /*
    pll_ip pll_inst (
        .inclk0(inclk0),  // 50 MHz input
        .c0(c0)           // 10 kHz output
    );
    */
endmodule