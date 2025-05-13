
// File: id.v
`timescale 1ns / 1ps

module id(instr, op, func, rs, rt, rd, imm16, shamt, addr26);
    input [31:0] instr;
    output [5:0] op;
    output [5:0] func;
    output [4:0] rs, rt, rd;
    output [15:0] imm16;
    output [4:0] shamt;
    output [25:0] addr26;

    assign op = instr[31:26]; // Op = 6 bit
    assign rs = instr[25:21];
    assign rt = instr[20:16];
    assign rd = instr[15:11];
    assign shamt = instr[10:6];
    assign func = instr[5:0];

    assign imm16 = instr[15:0];

    assign addr26 = instr[25:0];
endmodule
