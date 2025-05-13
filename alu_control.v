// File: alu_control.v
`timescale 1ns / 1ps

module alu_control (
    input  [1:0] ALUOp,
    input  [5:0] funct,
    output reg [2:0] ALUControl
);
    parameter ALU_ADD = 3'b010;
    parameter ALU_SUB = 3'b110;
    parameter ALU_AND = 3'b000;
    parameter ALU_OR  = 3'b001;
    parameter ALU_SLT = 3'b111;
    
    parameter FUNC_ADD = 6'b100000;
    parameter FUNC_SUB = 6'b100010;
    parameter FUNC_AND = 6'b100100;
    parameter FUNC_OR  = 6'b100101;
    parameter FUNC_SLT = 6'b101010;
    
    always @(*) begin
        case(ALUOp)
            2'b00: ALUControl = ALU_ADD;  // Add (for lw/sw/addi)
            2'b01: ALUControl = ALU_SUB;  // Subtract (for beq)
            2'b10: begin                  // R-type instruction
                case(funct)
                    FUNC_ADD: ALUControl = ALU_ADD;
                    FUNC_SUB: ALUControl = ALU_SUB;
                    FUNC_AND: ALUControl = ALU_AND;
                    FUNC_OR:  ALUControl = ALU_OR;
                    FUNC_SLT: ALUControl = ALU_SLT;
                    default:  ALUControl = ALU_ADD; // Default to ADD
                endcase
            end
            default: ALUControl = ALU_ADD; // Default to ADD
        endcase
    end
endmodule