`timescale 1ns / 1ps

module MIPS32_top (
    input MAX10_CLK1_50,
    input [0:0] KEY
);
    // Wire declarations
    wire [31:0] pc, instr;
    wire [5:0] op, func;
    wire [4:0] rs, rt, rd, shamt;
    wire [15:0] imm16;
    wire [25:0] addr26;
    wire [31:0] newpc, imm32;
    wire RegDst, ALUSrcA, MemtoReg, IorD;
    wire [1:0] ALUSrcB, ALUOp, PCSrc;
    wire RegWrite, IRWrite, MemWrite, MemRead, Zero, PCWriteCond, PCWrite;
    wire nrst;
    wire clk;
    
    // Additional wires needed for connections
    wire [31:0] alu_result, alu_out;
    wire [31:0] reg_data1, reg_data2;
    wire [31:0] reg_A, reg_B;
    wire [31:0] mem_addr;
    wire [31:0] mdr;
    wire [31:0] sign_extended;
    wire [4:0] write_reg_addr;
    wire [31:0] alu_b;
    wire pc_write_enable;
    wire [31:0] data;
    wire [31:0] DataIn;
    wire [2:0] ALUControl;
    wire [31:0] write_data; // Added for regfile wdata connection
    wire [31:0] write_reg_addr_padded; // Added for mux output connection
    
    // Address decoding
    wire [2:0] addr_high;
    wire rom_ce_n, ram_ce_n, io_ce_n;
    
    // Reset and clock connections
    assign nrst = KEY[0];
    assign pc_write_enable = PCWrite | (PCWriteCond & Zero);
    assign addr_high = mem_addr[15:13];
    
    // Generate write data for regfile
    assign write_data = MemtoReg ? mdr : alu_out;
    
    // Generate padded write register address
    assign write_reg_addr_padded = {27'b0, write_reg_addr};
    
    // Instantiate modules
    PLL U1 (.inclk0(MAX10_CLK1_50), .c0(clk)); // clk = 10kHz
    
    pc_reg U2 (
        .clk(clk), 
        .nrst(nrst), 
        .PCWrite(pc_write_enable), 
        .newpc(newpc), 
        .pc(pc)
    );
    
    id U3 (
        .instr(instr), 
        .op(op), 
        .func(func), 
        .rs(rs), 
        .rt(rt), 
        .rd(rd), 
        .imm16(imm16), 
        .shamt(shamt), 
        .addr26(addr26)
    );
    
    mux32b_2to1 U4 (
        .in0(pc), 
        .in1(alu_out), 
        .sel(IorD), 
        .out(mem_addr)
    );
    
    regfile U5 (
        .clk(clk), 
        .RegWrite(RegWrite), 
        .reg1(rs), 
        .reg2(rt), 
        .wreg(write_reg_addr), 
        .wdata(write_data), 
        .rdata1(reg_data1), 
        .rdata2(reg_data2)
    );
    
    dff32 U6 (
        .clk(clk), 
        .nrst(nrst), 
        .en(1'b1), 
        .di(reg_data1), 
        .dout(reg_A)
    );
    
    dff32 U7 (
        .clk(clk), 
        .nrst(nrst), 
        .en(1'b1), 
        .di(reg_data2), 
        .dout(reg_B)
    );
    
    signExt U8 (
        .int16(imm16), 
        .int32(sign_extended)
    );
    
    mux32b_2to1 U9 (
        .in0({27'b0, rt}), 
        .in1({27'b0, rd}), 
        .sel(RegDst), 
        .out(write_reg_addr_padded)
    );
    
    // Extract the register address from the padded value
    assign write_reg_addr = write_reg_addr_padded[4:0];
    
    mux32b_4to1 U10 (
        .in0(reg_B), 
        .in1(32'd4), 
        .in2(sign_extended), 
        .in3({sign_extended[29:0], 2'b00}), 
        .sel(ALUSrcB), 
        .out(alu_b)
    );
    
    ALU U11 (
        .aluA(ALUSrcA ? reg_A : pc), 
        .aluB(alu_b), 
        .ALUOp(ALUControl), 
        .zero(Zero), 
        .aluResult(alu_result)
    );
    
    mux32b_4to1 U12 (
        .in0(alu_result), 
        .in1(alu_out), 
        .in2({pc[31:28], addr26, 2'b00}), 
        .in3(32'h0), 
        .sel(PCSrc), 
        .out(newpc)
    );
    
    dff32 U13 (
        .clk(clk), 
        .nrst(nrst), 
        .en(1'b1), 
        .di(alu_result), 
        .dout(alu_out)
    );
    
    dff32 U14 (
        .clk(clk), 
        .nrst(nrst), 
        .en(1'b1), 
        .di(DataIn), 
        .dout(mdr)
    );
    
    dff32 U16 (
        .clk(clk), 
        .nrst(nrst), 
        .en(IRWrite), 
        .di(DataIn), 
        .dout(instr)
    );
    
    ttl74138 U17 (
        .a0(addr_high[0]), 
        .a1(addr_high[1]), 
        .a2(addr_high[2]), 
        .g1(1'b1), 
        .g2a(1'b0), 
        .g2b(1'b0), 
        .y0(rom_ce_n), 
        .y1(ram_ce_n), 
        .y2(io_ce_n), 
        .y3(), 
        .y4(), 
        .y5(), 
        .y6(), 
        .y7()
    );
    
    rom U18 (
        .nrst(nrst), 
        .addr(mem_addr[7:2]), 
        .nce(rom_ce_n), 
        .re(MemRead), 
        .data(data)
    );
    
    ram U19 (
        .clk(clk), 
        .nce(ram_ce_n), 
        .MemWrite(MemWrite), 
        .MemRead(MemRead), 
        .address(mem_addr[7:0]), 
        .wdata(reg_B), 
        .rdata(data)
    );
    
    outputModule U20 (
        .clk(clk), 
        .nrst(nrst), 
        .nce(io_ce_n), 
        .we(MemWrite), 
        .addr(mem_addr[10:0]), 
        .data(reg_B), 
        .portA()
    );
    
    switch_32b U21 (
        .data(data), 
        .in0(reg_B), 
        .out(DataIn), 
        .ctrl(MemRead)
    );
    
    // Control Unit
    controlUnit U22 (
        .clk(clk),
        .nrst(nrst),
        .op(op),
        .func(func),
        .Zero(Zero),
        .PCWrite(PCWrite),
        .PCWriteCond(PCWriteCond),
        .IorD(IorD),
        .MemRead(MemRead),
        .MemWrite(MemWrite),
        .IRWrite(IRWrite),
        .MemtoReg(MemtoReg),
        .RegDst(RegDst),
        .RegWrite(RegWrite),
        .ALUSrcA(ALUSrcA),
        .ALUSrcB(ALUSrcB),
        .ALUOp(ALUOp),
        .PCSrc(PCSrc)
    );
    
    // ALU Control Logic
    alu_control U23 (
        .ALUOp(ALUOp),
        .funct(func),
        .ALUControl(ALUControl)
    );
endmodule