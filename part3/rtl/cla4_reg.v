`timescale 1ns / 1ps

// Registered 4-bit CLA, as in Part I Figure 1(i): input flip-flops, the adder, output flip-flops.
// en is a clock enable, so the board can step the circuit slowly from its 100 MHz clock.
// Latency: inputs captured at edge k appear on q_s / q_cout after edge k + 1.
module cla4_reg (
    input  wire       clk,
    input  wire       rst,
    input  wire       en,
    input  wire [3:0] d_a,
    input  wire [3:0] d_b,
    input  wire       d_cin,
    output reg  [3:0] q_s,
    output reg        q_cout,
    // adder inputs and outputs between the two register stages, for probing
    output reg  [3:0] a,
    output reg  [3:0] b,
    output reg        cin,
    output wire [3:0] s,
    output wire       cout
);

    cla4 adder (.a(a), .b(b), .cin(cin), .s(s), .cout(cout));

    always @(posedge clk) begin
        if (rst) begin
            {a, b, cin}     <= 9'd0;
            {q_s, q_cout}   <= 5'd0;
        end else if (en) begin
            {a, b, cin}     <= {d_a, d_b, d_cin};
            {q_s, q_cout}   <= {s, cout};
        end
    end

endmodule
