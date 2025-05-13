// File: regfile.v
`timescale 1ns / 1ps

module regfile(clk, RegWrite, reg1, reg2, wreg, wdata, rdata1, rdata2);
    input clk, RegWrite;
    input  [4:0] reg1, reg2, wreg;
    input  [31:0] wdata;
    output [31:0] rdata1, rdata2;

    reg [31:0] registers [0:31];

    initial begin
        registers[1] = 32'd11;
        registers[2] = 32'd22;
        registers[3] = 32'd33;
        registers[4] = 32'd44;
    end

    assign rdata1 = (reg1 == 5'd0)? 32'd0 : registers[reg1];
    assign rdata2 = (reg2 == 5'd0)? 32'd0 : registers[reg2];

    always @(negedge clk) begin
        if((RegWrite == 1'b1) && (wreg != 5'd0)) begin
            registers[wreg] <= wdata;
        end
    end
endmodule