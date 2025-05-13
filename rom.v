
// File: rom.v
`timescale 1ns / 1ps

module rom(nrst, addr, nce, re, data);
    input [7:2] addr;
    input nrst, nce, re;
    output [31:0] data;
    tri [31:0] data;
    reg [31:0] mem [0:63];

    always @(*) begin
        if(nrst == 1'b0) begin
            // Initialize ROM with MIPS instructions
            mem[0] = 32'h00430820; // add $1, $2, $3
            mem[1] = 32'h00012020; // add $4, $0, $1
            mem[2] = 32'h00822022; // sub $4, $4, $2
            mem[3] = 32'h8C230004; // lw $3, 4($1)
            mem[4] = 32'hAC240008; // sw $4, 8($1)
            mem[5] = 32'h10240002; // beq $1, $4, 2
            mem[6] = 32'h08000008; // j 8
            // Add more instructions as needed
        end
    end

    assign data = ((nce == 1'b0) && (re == 1'b1)) ? mem[addr] : 32'bz;
endmodule