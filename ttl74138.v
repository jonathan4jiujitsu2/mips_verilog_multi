// File: ttl74138.v
`timescale 1ns / 1ps

module ttl74138(
    input a0, a1, a2, // Inputs
    input g1, g2a, g2b, // Enable inputs
    output y0, y1, y2, y3, y4, y5, y6, y7 // Outputs
);
    wire en;
    wire [2:0] ain;
    wire [7:0] yout;
    assign ain = {a2, a1, a0};

    // Generate active low enable logic
    assign en = (~g2a) & (~g2b) & g1;

    // Assign yout based on enable and input address
    assign yout = (en == 1'b0) ? 8'hFF : // If enable is off, all outputs are high
                 (ain == 3'd0) ? 8'b1111_1110 : 
                 (ain == 3'd1) ? 8'b1111_1101 : 
                 (ain == 3'd2) ? 8'b1111_1011 : 
                 (ain == 3'd3) ? 8'b1111_0111 : 
                 (ain == 3'd4) ? 8'b1110_1111 : 
                 (ain == 3'd5) ? 8'b1101_1111 : 
                 (ain == 3'd6) ? 8'b1011_1111 : 
                 8'b0111_1111; // Default case

    // Assign outputs y0, y1, ..., y7 from the yout vector
    assign {y7, y6, y5, y4, y3, y2, y1, y0} = yout;
endmodule