// File: outputModule.v
`timescale 1ns / 1ps

module outputModule(clk, nrst, nce, we, addr, data, portA);
    input clk, nrst, nce, we;
    input [10:0] addr;
    input [31:0] data;
    output [9:0] portA;

    reg [9:0] portA;
    always @ (posedge clk or negedge nrst) begin
        if(nrst == 1'b0) begin
            portA <= 10'b0;
        end
        else begin
            if( (nce == 1'b0) && (we == 1'b1) && (addr == 11'd0)) begin
                portA <= data[9:0];
            end
        end
    end
endmodule