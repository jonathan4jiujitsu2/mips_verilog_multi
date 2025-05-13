// File: mux32b_4to1.v
`timescale 1ns / 1ps

module mux32b_4to1(in0, in1, in2, in3, sel, out);
    input [31:0] in0, in1, in2, in3;
    input [1:0] sel;
    output [31:0] out;
    
    assign out = (sel == 2'b00) ? in0 :
                (sel == 2'b01) ? in1 :
                (sel == 2'b10) ? in2 : in3;
endmodule