// File: controlUnit.v
`timescale 1ns / 1ps

module controlUnit(
    input clk,
    input nrst,
    input [5:0] op,
    input [5:0] func,
    input Zero,
    output reg PCWrite,
    output reg PCWriteCond,
    output reg IorD,
    output reg MemRead,
    output reg MemWrite,
    output reg IRWrite,
    output reg MemtoReg,
    output reg RegDst,
    output reg RegWrite,
    output reg ALUSrcA,
    output reg [1:0] ALUSrcB,
    output reg [1:0] ALUOp,
    output reg [1:0] PCSrc
);
    // State definitions
    parameter S_FETCH = 4'd0;    // Instruction Fetch
    parameter S_DECODE = 4'd1;   // Instruction Decode
    parameter S_EXECUTE = 4'd2;  // Execution
    parameter S_MEMORY = 4'd3;   // Memory Access
    parameter S_WRITEBACK = 4'd4; // Write Back
    parameter S_BRANCH = 4'd5;   // Branch Completion
    parameter S_JUMP = 4'd6;     // Jump Completion
    
    // R-type opcodes and function codes
    parameter R_TYPE = 6'b000000;
    parameter LW = 6'b100011;
    parameter SW = 6'b101011;
    parameter BEQ = 6'b000100;
    parameter J = 6'b000010;
    
    reg [3:0] state, next_state;
    
    // State register
    always @(posedge clk or negedge nrst) begin
        if (!nrst)
            state <= S_FETCH;
        else
            state <= next_state;
    end
    
    // Next state logic
    always @(*) begin
        case (state)
            S_FETCH: next_state = S_DECODE;
            
            S_DECODE: begin
                case (op)
                    R_TYPE: next_state = S_EXECUTE;
                    LW, SW: next_state = S_EXECUTE;
                    BEQ: next_state = S_BRANCH;
                    J: next_state = S_JUMP;
                    default: next_state = S_FETCH;
                endcase
            end
            
            S_EXECUTE: begin
                case (op)
                    R_TYPE: next_state = S_WRITEBACK;
                    LW: next_state = S_MEMORY;
                    SW: next_state = S_MEMORY;
                    default: next_state = S_FETCH;
                endcase
            end
            
            S_MEMORY: begin
                case (op)
                    LW: next_state = S_WRITEBACK;
                    default: next_state = S_FETCH;
                endcase
            end
            
            S_WRITEBACK: next_state = S_FETCH;
            S_BRANCH: next_state = S_FETCH;
            S_JUMP: next_state = S_FETCH;
            
            default: next_state = S_FETCH;
        endcase
    end
    
    // Output logic
    always @(*) begin
        // Default control signals
        PCWrite = 0;
        PCWriteCond = 0;
        IorD = 0;
        MemRead = 0;
        MemWrite = 0;
        IRWrite = 0;
        MemtoReg = 0;
        RegDst = 0;
        RegWrite = 0;
        ALUSrcA = 0;
        ALUSrcB = 2'b00;
        ALUOp = 2'b00;
        PCSrc = 2'b00;
        
        case (state)
            S_FETCH: begin
                MemRead = 1;
                IRWrite = 1;
                ALUSrcA = 0;      // Select PC
                ALUSrcB = 2'b01;  // Select constant 4
                ALUOp = 2'b00;    // Add
                PCWrite = 1;      // Write PC
                PCSrc = 2'b00;    // Select ALU result
            end
            
            S_DECODE: begin
                ALUSrcA = 0;      // Select PC
                ALUSrcB = 2'b11;  // Select sign-extended, shifted immediate
                ALUOp = 2'b00;    // Add
            end
            
            S_EXECUTE: begin
                ALUSrcA = 1;      // Select A register
                case (op)
                    R_TYPE: begin
                        ALUSrcB = 2'b00;  // Select B register
                        ALUOp = 2'b10;    // R-type ALU operation
                    end
                    LW, SW: begin
                        ALUSrcB = 2'b10;  // Select sign-extended immediate
                        ALUOp = 2'b00;    // Add
                    end
                endcase
            end
            
            S_MEMORY: begin
                IorD = 1;         // Select ALU out for address
                case (op)
                    LW: MemRead = 1;
                    SW: MemWrite = 1;
                endcase
            end
            
            S_WRITEBACK: begin
                case (op)
                    R_TYPE: begin
                        RegDst = 1;       // Select rd for write register
                        RegWrite = 1;      // Enable register write
                        MemtoReg = 0;      // Select ALU out
                    end
                    LW: begin
                        RegDst = 0;        // Select rt for write register
                        RegWrite = 1;      // Enable register write
                        MemtoReg = 1;      // Select memory data
                    end
                endcase
            end
            
            S_BRANCH: begin
                ALUSrcA = 1;          // Select A register
                ALUSrcB = 2'b00;      // Select B register
                ALUOp = 2'b01;        // Subtract
                PCWriteCond = 1;      // Conditionally write PC
                PCSrc = 2'b01;        // Select branch address
            end
            
            S_JUMP: begin
                PCWrite = 1;          // Write PC
                PCSrc = 2'b10;        // Select jump address
            end
        endcase
    end
endmodule