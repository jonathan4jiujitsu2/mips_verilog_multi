
// File: ALU.v
`timescale 1ns / 1ps

module ALU(aluA, aluB, ALUOp, zero, aluResult);
    input [31:0] aluA, aluB;
    input [2:0] ALUOp;
    output zero;
    output [31:0] aluResult;
    reg [31:0] aluResult;

    assign zero = (aluResult == 32'b0);

    always @(*) begin
        case(ALUOp)
            3'b000: aluResult = aluA & aluB;    // AND
            3'b001: aluResult = aluA | aluB;    // OR
            3'b010: aluResult = aluA + aluB;    // ADD
            3'b110: aluResult = aluA - aluB;    // SUB
            3'b111: aluResult = (aluA < aluB) ? 32'd1 : 32'd0;  // SLT
            default: aluResult = 32'b0;
        endcase
    end
endmodule