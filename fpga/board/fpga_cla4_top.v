`timescale 1ns / 1ps

// Boolean Board top for the registered 4-bit CLA (Part I).
//
// Switches
//   sw[3:0]   A          (manual mode)
//   sw[4]     not used, a gap between A and B
//   sw[8:5]   B          (manual mode)
//   sw[9]     not used, a gap between B and Cin
//   sw[10]    Cin        (manual mode)
//   sw[13:12] step rate: 0 = 1.49 Hz, 1 = 95.4 Hz, 2 = 6.10 kHz, 3 = 781 kHz
//   sw[15]    0 = manual inputs, 1 = automatic self-test
//
// Automatic self-test, 512 steps per phase, phase shown on LED13..LED12:
//   phase 0: A = 1111, B = 0000, Cin toggling every step (the hint vector)
//   phase 1: A = 0000, B = 1111, Cin toggling every step
//   phase 2: pseudo-random A, B, Cin
//   phase 3: all 512 input combinations in order
// Every result is checked against a + b + cin. Any mismatch lights LED6 and stays lit
// until the board goes back to manual mode.
//
// Displays, in decimal: left D0 shows A on its two left digits and B on its two right digits.
//           Right D1 shows S on its two right digits; its two left digits are off.
// LEDs:     LED0 Cin, LED3 Cout (C4), LED5 auto mode, LED6 error, LED13..12 test phase.
// Scope header probes:
//   probe[0] step clock    probe[1] Cin at the adder    probe[2] S3 at the adder
//   probe[3] C4 at the adder    probe[4] error flag
module fpga_cla4_top #(parameter DIV_SHIFT = 0) (
    input  wire        clk,
    input  wire [15:0] sw,
    output wire [3:0]  d0_a,
    output wire [7:0]  d0_seg,
    output wire [3:0]  d1_a,
    output wire [7:0]  d1_seg,
    output wire [6:0]  led,
    output wire [3:0]  led_hi,
    output wire [4:0]  probe
);

    wire rst;
    power_on_reset por (.clk(clk), .rst(rst));

    wire tick, tclk;
    step_clock #(.DIV_SHIFT(DIV_SHIFT)) stepper (.clk(clk), .rst(rst), .speed(sw[13:12]), .tick(tick), .tclk(tclk));

    wire auto = sw[15];

    // ---------------- test sequencer ----------------
    reg  [10:0] step;
    wire [15:0] rnd;
    lfsr16 prng (.clk(clk), .rst(rst), .en(tick), .q(rnd));

    always @(posedge clk) begin
        if (rst || !auto) step <= 11'd0;
        else if (tick)    step <= step + 1'b1;
    end
    wire [1:0] phase = step[10:9];

    reg [3:0] t_a, t_b;
    reg       t_cin;
    always @(*) begin
        case (phase)
            2'd0:    {t_a, t_b, t_cin} = {4'hF, 4'h0, step[0]};
            2'd1:    {t_a, t_b, t_cin} = {4'h0, 4'hF, step[0]};
            2'd2:    {t_a, t_b, t_cin} = rnd[8:0];
            default: {t_cin, t_b, t_a} = step[8:0];
        endcase
    end

    wire [3:0] in_a   = auto ? t_a   : sw[3:0];
    wire [3:0] in_b   = auto ? t_b   : sw[8:5];
    wire       in_cin = auto ? t_cin : sw[10];

    // ---------------- registered adder ----------------
    wire [3:0] q_s, a, b, s;
    wire       q_cout, cin, cout;
    cla4_reg dut (.clk(clk), .rst(rst), .en(tick), .d_a(in_a), .d_b(in_b), .d_cin(in_cin),
                  .q_s(q_s), .q_cout(q_cout), .a(a), .b(b), .cin(cin), .s(s), .cout(cout));

    // ---------------- self-check ----------------
    // expected result travels beside the output register, so both change on the same tick
    reg [4:0] expect_q;
    reg [1:0] valid;
    reg       err;
    always @(posedge clk) begin
        if (rst) begin
            expect_q <= 5'd0;
            valid    <= 2'd0;
            err      <= 1'b0;
        end else begin
            if (tick) begin
                expect_q <= a + b + cin;
                valid    <= {valid[0], 1'b1};
            end
            if (!auto)
                err <= 1'b0;
            else if (valid[1] && {q_cout, q_s} != expect_q)
                err <= 1'b1;
        end
    end

    // ---------------- outputs ----------------
    // 0..15 as two decimal digits, tens then ones
    function [7:0] to_decimal;
        input [3:0] v;
        to_decimal = (v >= 4'd10) ? {4'd1, v - 4'd10} : {4'd0, v};
    endfunction

    hex_display2x4 disp (
        .clk(clk), .rst(rst),
        .left_val({to_decimal(a), to_decimal(b)}), .blank_l(4'b0000),
        .right_val({8'h00, to_decimal(s)}), .blank_r(4'b1100),
        .d0_a(d0_a), .d0_seg(d0_seg), .d1_a(d1_a), .d1_seg(d1_seg));

    assign led    = {err, auto, 1'b0, cout, 2'b00, cin};
    assign led_hi = {2'b00, phase};
    assign probe  = {err, cout, s[3], cin, tclk};

endmodule
