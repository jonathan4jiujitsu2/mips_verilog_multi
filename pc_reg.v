
// File: pc_reg.v
`timescale 1ns / 1ps

module pc_reg(clk, nrst, PCWrite, newpc, pc);
    input clk, nrst, PCWrite;
    input [31:0] newpc;
    output [31:0] pc;

    reg [31:0] pc;

    always @(negedge clk or negedge nrst) 
    begin
        if(nrst == 1'b0)
        begin
            pc <= 32'b0;
        end
        else if(PCWrite == 1'b1)
        begin
            pc <= newpc;
        end
    end
endmodule