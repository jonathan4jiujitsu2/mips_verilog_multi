`timescale 1ns / 1ps

module dff32(clk, nrst, en, di, dout);
    input clk, nrst, en;
    input [31:0] di;
    output [31:0] dout;
    reg [31:0] dout;

    always @(negedge clk or negedge nrst) begin
        if(nrst == 1'b0)begin
            dout <= 32'd0;
        end else begin
            if(en == 1'b1) begin
                dout <= di;
            end
        end
    end
endmodule