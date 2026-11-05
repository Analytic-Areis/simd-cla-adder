`timescale 1ns / 1ps

// 4-bit carry look-ahead adder, behavioural description.
// Same equations as the Part I circuit: OR-type transmit t = a | b for the carries,
// XOR propagate p = a ^ b for the sums, and every carry computed from g, t and cin directly.
module cla4 (
    input  wire [3:0] a,
    input  wire [3:0] b,
    input  wire       cin,
    output wire [3:0] s,
    output wire       cout
);

    wire [3:0] g = a & b;    // generate
    wire [3:0] t = a | b;    // transmit (carries only)
    wire [3:0] p = a ^ b;    // propagate (sums only)

    // look-ahead carries: no carry waits for the one below it
    wire c1 = g[0] | (t[0] & cin);
    wire c2 = g[1] | (t[1] & g[0]) | (t[1] & t[0] & cin);
    wire c3 = g[2] | (t[2] & g[1]) | (t[2] & t[1] & g[0]) | (t[2] & t[1] & t[0] & cin);
    wire c4 = g[3] | (t[3] & g[2]) | (t[3] & t[2] & g[1]) | (t[3] & t[2] & t[1] & g[0])
                   | (t[3] & t[2] & t[1] & t[0] & cin);

    assign s    = p ^ {c3, c2, c1, cin};
    assign cout = c4;

endmodule
