// File: MyDefines.v
`ifndef __MYDEFINES_V
`define __MYDEFINES_V

// Define registers
`define _R0     5'd0
`define _R1     5'd1
`define _R2     5'd2
`define _R3     5'd3
`define _R4     5'd4
`define _R5     5'd5
`define _R6     5'd6
`define _R7     5'd7
`define _R8     5'd8
`define _R9     5'd9
`define _R10     5'd10
`define _R11     5'd11
`define _R12     5'd12
`define _R13     5'd13
`define _R14     5'd14
`define _R15     5'd15
`define _R16     5'd16
`define _R17     5'd17
`define _R18     5'd18
`define _R19     5'd19
`define _R20     5'd20
`define _R21     5'd21
`define _R22     5'd22
`define _R23     5'd23
`define _R24     5'd24
`define _R25     5'd25
`define _R26     5'd26
`define _R27     5'd27
`define _R28     5'd28
`define _R29     5'd29
`define _R30     5'd30
`define _R31     5'd31

// MIPS register names
`define _ZERO    5'd0
`define _AT      5'd1

`define _V0     5'd2
`define _V1     5'd3

`define _A0     5'd4
`define _A1     5'd5
`define _A2     5'd6
`define _A3     5'd7

`define _T0     5'd8
`define _T1     5'd9
`define _T2     5'd10
`define _T3     5'd11
`define _T4     5'd12
`define _T5     5'd13
`define _T6     5'd14
`define _T7     5'd15

`define _S0     5'd16
`define _S1     5'd17
`define _S2     5'd18
`define _S3     5'd19
`define _S4     5'd20
`define _S5     5'd21
`define _S6     5'd22
`define _S7     5'd23

`define _T8     5'd24
`define _T9     5'd25

`define _K0     5'd26
`define _K1     5'd27

`define _GP     5'd28
`define _SP     5'd29
`define _FP     5'd30
`define _RA     5'd31

// Function Code
`define _FUNC_ADD  6'd32
`define _FUNC_ADDU 6'd33
`define _FUNC_SUB  6'd34
`define _FUNC_SUBU 6'd35
`define _FUNC_AND  6'd36
`define _FUNC_OR   6'd37
`define _FUNC_XNOR 6'd38
`define _FUNC_NOR  6'd39

`define _FUNC_SLT  6'b101010
`define _FUNC_SLL  6'b000000
`define _FUNC_SRL  6'b000010
`define _FUNC_SRA  6'b000011
`define _FUNC_SLLV 6'b000100
`define _FUNC_SRLV 6'b000110
`define _FUNC_SRAV 6'b000111

// ALU Operation Code
`define _ALUOP_BIT 5
`define _ALUOP_BUS  `_ALUOP_BIT-1:0
`define _ALUOP_AND  `_ALUOP_BIT'b00000
`define _ALUOP_OR   `_ALUOP_BIT'b00001
`define _ALUOP_ADD  `_ALUOP_BIT'b00010
`define _ALUOP_SUB  `_ALUOP_BIT'b00110
`define _ALUOP_SLT  `_ALUOP_BIT'b00111
`define _ALUOP_XOR  `_ALUOP_BIT'b01101
`define _ALUOP_NOR  `_ALUOP_BIT'b01100
`define _ALUOP_SLL  `_ALUOP_BIT'b01000
`define _ALUOP_SRL  `_ALUOP_BIT'b01001
`define _ALUOP_SRA  `_ALUOP_BIT'b01010

// OPCode (Operation Code)
`define _OP_RTYPE   6'd0
`define _OP_ADDI    6'b001000 
`define _OP_ANDI    6'b001100
`define _OP_ORI     6'b001101
`define _OP_XORI    6'b001110
`define _OP_LUI     6'b001111
`define _OP_LW      6'b100011
`define _OP_SW      6'b101011
`define _OP_BEQ     6'b000100
`define _OP_J       6'b000010

`endif