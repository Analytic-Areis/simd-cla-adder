`timescale 1ns / 1ps

// Registered SIMD 8-bit adder: input flip-flops, the adder, output flip-flops.
// en is a clock enable. Latency: inputs captured at edge k appear on the q outputs after edge k + 1.
module simd8_reg (
    input  wire       clk,
    input  wire       rst,
    input  wire       en,
    input  wire [7:0] d_a,
    input  wire [7:0] d_b,
    input  wire       d_cin,
    input  wire       d_mode,
    output reg  [7:0] q_s,
    output reg        q_cout,
    output reg        q_cout_lo,
    // adder inputs and outputs between the two register stages, for probing
    output reg  [7:0] a,
    output reg  [7:0] b,
    output reg        cin,
    output reg        simd_mode,
    output wire [7:0] s,
    output wire       cout,
    output wire       cout_lo,
    output wire       cin_hi
);

    simd8 adder (.a(a), .b(b), .cin(cin), .simd_mode(simd_mode),
                 .s(s), .cout(cout), .cout_lo(cout_lo), .cin_hi(cin_hi));

    always @(posedge clk) begin
        if (rst) begin
            {a, b, cin, simd_mode}      <= 18'd0;
            {q_s, q_cout, q_cout_lo}    <= 10'd0;
        end else if (en) begin
            {a, b, cin, simd_mode}      <= {d_a, d_b, d_cin, d_mode};
            {q_s, q_cout, q_cout_lo}    <= {s, cout, cout_lo};
        end
    end

endmodule
