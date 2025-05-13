`timescale 1ns / 1ps

module switch_32b (
    inout  [31:0] data,    // Bidirectional data bus
    input  [31:0] in0,     // Input data
    output [31:0] out,     // Output data
    input         ctrl     // Control signal: 1 for read, 0 for write
);
    // When ctrl is 1 (read), pass data to out
    // When ctrl is 0 (write), high impedance on out
    assign out = ctrl ? data : 32'hz;
    
    // When ctrl is 0 (write), pass in0 to data
    // When ctrl is 1 (read), high impedance on data
    assign data = ctrl ? 32'hz : in0;
endmodule