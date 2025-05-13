// File: ram.v
`timescale 1ns / 1ps

module ram(clk, nce, MemWrite, MemRead, address, wdata, rdata);
    input clk, nce, MemWrite, MemRead;
    input [7:0] address;
    input [31:0] wdata;
    output [31:0] rdata;

    reg [31:0] mem [0:255];
    assign rdata = ((nce == 1'b0)&&(MemRead == 1'b1))? mem[address] : 32'bz;

    always @(negedge clk) begin
        if((nce == 1'b0) && (MemWrite == 1'b1)) begin
            mem[address] <= wdata;
        end
    end
endmodule