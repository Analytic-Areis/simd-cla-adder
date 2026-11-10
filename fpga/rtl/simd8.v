`timescale 1ns / 1ps

// SIMD-reconfigurable 8-bit adder built from two 4-bit CLAs (Part II).
//   simd_mode = 0: one 8-bit add.  CLA0's carry-out feeds CLA1's carry-in.
//   simd_mode = 1: two 4-bit adds. The inter-block carry is forced to 0.
// cout_lo is CLA0's own carry-out, so the lower add's carry stays visible in dual mode.
module simd8 (
    input  wire [7:0] a,
    input  wire [7:0] b,
    input  wire       cin,
    input  wire       simd_mode,
    output wire [7:0] s,
    output wire       cout,      // carry-out of CLA1
    output wire       cout_lo,   // carry-out of CLA0, before gating
    output wire       cin_hi     // carry-in of CLA1, after gating
);

    cla4 cla0 (.a(a[3:0]), .b(b[3:0]), .cin(cin),    .s(s[3:0]), .cout(cout_lo));

    // carry-gating cell: an AND gate with the mode inverted
    assign cin_hi = cout_lo & ~simd_mode;

    cla4 cla1 (.a(a[7:4]), .b(b[7:4]), .cin(cin_hi), .s(s[7:4]), .cout(cout));

endmodule
