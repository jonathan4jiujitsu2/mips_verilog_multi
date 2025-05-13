// File: signExt.v
`timescale 1ns / 1ps

module signExt(int16, int32);
    input [15:0] int16;
    output [31:0] int32;
    
    assign int32 = {{16{int16[15]}}, int16};
endmodule
