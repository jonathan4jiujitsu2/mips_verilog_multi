
// File: mux32b_2to1.v
`timescale 1ns / 1ps

module mux32b_2to1(in0, in1, sel, out);
    input [31:0] in0, in1;
    input sel;
    output [31:0] out;
    
    assign out = sel ? in1 : in0;
endmodule
