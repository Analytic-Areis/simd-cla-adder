`timescale 1ns / 1ps

// Boolean Board top for the registered SIMD-reconfigurable 8-bit adder (Part II).
//
// Switches
//   sw[7:0]   operand value (manual mode)
//   sw[14]    0 = sw[7:0] sets A, 1 = sw[7:0] sets B. The other operand keeps its last value.
//   sw[8]     Cin        (manual mode)
//   sw[9]     SIMD_MODE  (manual mode): 0 = one 8-bit add, 1 = two 4-bit adds
//   sw[13:12] step rate: 0 = 1.49 Hz, 1 = 95.4 Hz, 2 = 6.10 kHz, 3 = 781 kHz
//   sw[15]    0 = manual inputs, 1 = automatic self-test
//
// Automatic self-test, 256 steps per phase, phase shown on LED13..LED12:
//   phase 0: 8-bit mode,    A = 0xFF, B = 0x00, Cin toggling (worst carry path, Part II 4a)
//   phase 1: dual 4-bit mode, same vector: the carry must stop at the block boundary
//   phase 2: 8-bit mode, pseudo-random A, B, Cin
//   phase 3: pseudo-random A, B, Cin with SIMD_MODE switching every step
// Every result is checked against a behavioural model. Any mismatch lights LED6 and stays
// lit until the board goes back to manual mode.
//
// Displays: left D0 = A, B at the adder inputs.
//           right D1 = Cout, Cout of the lower block, S[7:4], S[3:0] at the adder outputs.
// LEDs:     LED0 Cin, LED1 SIMD_MODE, LED2 lower carry-out, LED3 gated carry into the upper block,
//           LED4 Cout, LED5 auto mode, LED6 error, LED13..12 test phase, LED14 step clock, LED15 pass.
// Scope header probes:
//   probe[0] step clock    probe[1] Cin at the adder    probe[2] S7 at the adder
//   probe[3] Cout at the adder    probe[4] gated carry into the upper block
module fpga_simd8_top #(parameter DIV_SHIFT = 0) (
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

    // ---------------- manual operand entry ----------------
    reg [7:0] man_a, man_b;
    always @(posedge clk) begin
        if (rst) begin
            man_a <= 8'h00;
            man_b <= 8'h00;
        end else if (sw[14]) man_b <= sw[7:0];
        else                 man_a <= sw[7:0];
    end

    // ---------------- test sequencer ----------------
    reg  [9:0]  step;
    wire [15:0] rnd;
    lfsr16 prng (.clk(clk), .rst(rst), .en(tick), .q(rnd));

    always @(posedge clk) begin
        if (rst || !auto) step <= 10'd0;
        else if (tick)    step <= step + 1'b1;
    end
    wire [1:0] phase = step[9:8];

    reg [7:0] t_a, t_b;
    reg       t_cin, t_mode;
    always @(*) begin
        case (phase)
            2'd0:    {t_a, t_b, t_cin, t_mode} = {8'hFF, 8'h00, step[0], 1'b0};
            2'd1:    {t_a, t_b, t_cin, t_mode} = {8'hFF, 8'h00, step[0], 1'b1};
            2'd2:    {t_a, t_b, t_cin, t_mode} = {rnd, step[3] ^ rnd[0], 1'b0};
            default: {t_a, t_b, t_cin, t_mode} = {rnd, step[3] ^ rnd[0], step[0]};
        endcase
    end

    wire [7:0] in_a    = auto ? t_a    : man_a;
    wire [7:0] in_b    = auto ? t_b    : man_b;
    wire       in_cin  = auto ? t_cin  : sw[8];
    wire       in_mode = auto ? t_mode : sw[9];

    // ---------------- registered adder ----------------
    wire [7:0] q_s, a, b, s;
    wire       q_cout, q_cout_lo, cin, simd_mode, cout, cout_lo, cin_hi;
    simd8_reg dut (.clk(clk), .rst(rst), .en(tick),
                   .d_a(in_a), .d_b(in_b), .d_cin(in_cin), .d_mode(in_mode),
                   .q_s(q_s), .q_cout(q_cout), .q_cout_lo(q_cout_lo),
                   .a(a), .b(b), .cin(cin), .simd_mode(simd_mode),
                   .s(s), .cout(cout), .cout_lo(cout_lo), .cin_hi(cin_hi));

    // ---------------- self-check ----------------
    // behavioural model written with '+', independent of the look-ahead equations
    wire [4:0] lo = a[3:0] + b[3:0] + cin;
    wire [4:0] hi = a[7:4] + b[7:4] + (simd_mode ? 1'b0 : lo[4]);

    reg [9:0] expect_q;   // {cout, cout_lo, s}
    reg [1:0] valid;
    reg       err;
    always @(posedge clk) begin
        if (rst) begin
            expect_q <= 10'd0;
            valid    <= 2'd0;
            err      <= 1'b0;
        end else begin
            if (tick) begin
                expect_q <= {hi[4], lo[4], hi[3:0], lo[3:0]};
                valid    <= {valid[0], 1'b1};
            end
            if (!auto)
                err <= 1'b0;
            else if (valid[1] && {q_cout, q_cout_lo, q_s} != expect_q)
                err <= 1'b1;
        end
    end

    // ---------------- outputs ----------------
    hex_display2x4 disp (
        .clk(clk), .rst(rst),
        .left_val({a, b}), .blank_l(4'b0000),
        .right_val({3'b000, cout, 3'b000, cout_lo, s}), .blank_r(4'b0000),
        .d0_a(d0_a), .d0_seg(d0_seg), .d1_a(d1_a), .d1_seg(d1_seg));

    assign led    = {err, auto, cout, cin_hi, cout_lo, simd_mode, cin};
    assign led_hi = {auto & ~err, tclk, phase};
    assign probe  = {cin_hi, cout, s[7], cin, tclk};

endmodule
